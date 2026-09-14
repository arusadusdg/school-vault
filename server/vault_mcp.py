"""MCP server over the vault.

The repo is the state. This process holds nothing but a cache it can rebuild
from a fresh clone in seconds, so losing the box loses nothing.

remember() is the only thing that writes to notes/, which is exactly what the
scraper's guard forbids. sync() reaches back to GitHub Actions.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
import yaml
from fastmcp import FastMCP

REPO = Path(os.environ.get("VAULT_REPO", Path(__file__).resolve().parent.parent))
PULL_EVERY = 60.0
SEARCH_DIRS = ("canvas", "toddle", "notes", "changes")
COLUMNS = ("id", "path", "class", "type", "title", "author", "posted", "due", "url", "body")
BODY_COL = COLUMNS.index("body")

mcp = FastMCP(
    "school-vault",
    instructions=(
        "The student's school vault: every page from Toddle and Canvas, verbatim. "
        "Call get_context() first in any school conversation. Quote teachers' own "
        "words from recall() and open_note(); never paraphrase a deadline."
    ),
)

_last_pull = 0.0
_db: sqlite3.Connection | None = None
_signature: tuple | None = None
_last_checked: str | None = None


def _pull() -> None:
    """Cheap freshness. A network blip must not take the tools down with it."""
    global _last_pull
    if time.monotonic() - _last_pull < PULL_EVERY:
        return
    _last_pull = time.monotonic()
    subprocess.run(
        ["git", "-C", str(REPO), "pull", "--quiet", "--ff-only"],
        capture_output=True, timeout=60, check=False,
    )


def _files() -> list[Path]:
    out: list[Path] = []
    for d in SEARCH_DIRS:
        base = REPO / d
        if base.exists():
            out += sorted(base.rglob("*.md"))
    return out


FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def _parse(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = FRONTMATTER.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return (meta if isinstance(meta, dict) else {}), m.group(2)


def _index() -> sqlite3.Connection:
    """Rebuild the FTS index only when a file actually changed.

    A few hundred files, so a full rebuild beats tracking deltas.
    """
    global _db, _signature
    _pull()
    files = _files()
    sig = tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in files)
    if _db is not None and sig == _signature:
        return _db

    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute(
        f"CREATE VIRTUAL TABLE notes USING fts5({', '.join(COLUMNS)}, "
        "tokenize='porter unicode61')"
    )
    rows = []
    for p in files:
        meta, body = _parse(p)
        rel = p.relative_to(REPO).as_posix()
        rows.append((
            str(meta.get("id") or rel), rel, str(meta.get("class") or ""),
            str(meta.get("type") or "note"), str(meta.get("title") or p.stem),
            str(meta.get("author") or ""), str(meta.get("posted") or ""),
            str(meta.get("due") or ""), str(meta.get("url") or ""), body,
        ))
    db.executemany(f"INSERT INTO notes VALUES ({','.join('?' * len(COLUMNS))})", rows)
    _db, _signature = db, sig
    return db


def _match(db: sqlite3.Connection, query: str, extra_sql: str, params: list) -> list:
    """FTS5 MATCH on model-supplied text. Bad syntax falls back to a token search."""
    sql = (
        "SELECT id, path, class, type, title, author, posted, due, url, "
        f"snippet(notes, {BODY_COL}, '**', '**', ' ... ', 24) AS snip, "
        "bm25(notes) AS score FROM notes WHERE notes MATCH ?" + extra_sql
    )
    try:
        return db.execute(sql, [query, *params]).fetchall()
    except sqlite3.OperationalError:
        safe = " OR ".join(f'"{t}"' for t in re.findall(r"\w+", query)) or '""'
        return db.execute(sql, [safe, *params]).fetchall()


def _rank(row) -> float:
    """bm25 is negative-better. Nudge upcoming deadlines and fresh posts up."""
    score = row["score"]
    today = date.today()
    try:
        if row["due"]:
            days = (date.fromisoformat(row["due"]) - today).days
            if 0 <= days <= 14:
                score -= 3.0
    except ValueError:
        pass
    try:
        if row["posted"] and (today - date.fromisoformat(row["posted"])).days <= 30:
            score -= 1.0
    except ValueError:
        pass
    return score


def _cite(row) -> str:
    bits = [f"**{row['title']}**", f"`{row['id']}`", row["class"] or "?"]
    if row["due"]:
        bits.append(f"due {row['due']}")
    if row["author"]:
        bits.append(row["author"])
    return " - ".join(b for b in bits if b)


@mcp.tool
def get_context() -> str:
    """The student's current school situation: what is due in the next 14 days,
    the latest announcement per class, and when the vault last synced.
    Call this first in any school conversation."""
    _pull()
    path = REPO / "context.md"
    return path.read_text(encoding="utf-8") if path.exists() else "No context.md yet - run a sync."


@mcp.tool
def recall(query: str, class_name: str | None = None, limit: int = 8) -> str:
    """Full-text search across every Toddle and Canvas page, plus your own notes.

    Returns the teacher's own words, never a summary. Filter with class_name
    (for example 'cs-hl').
    """
    db = _index()
    extra, params = "", []
    if class_name:
        extra, params = " AND class = ?", [class_name]
    rows = sorted(_match(db, query, extra, params), key=_rank)[: max(1, min(limit, 25))]
    if not rows:
        return f"Nothing in the vault matches {query!r}."
    return "\n\n".join(
        f"### {_cite(r)}\n{r['snip']}\n\nopen_note('{r['id']}') - [portal]({r['url']})"
        for r in rows
    )


@mcp.tool
def open_note(id: str) -> str:
    """The full verbatim text of one vault item, by its id (for example
    'canvas:assignment:38751'), plus anything that links to it."""
    db = _index()
    row = db.execute("SELECT path, title FROM notes WHERE id = ? LIMIT 1", [id]).fetchone()
    if row is None:
        return f"No item with id {id!r}. Use recall() to find one."
    text = (REPO / row["path"]).read_text(encoding="utf-8", errors="replace")
    stem = Path(row["path"]).stem
    links = [
        r["path"] for r in db.execute("SELECT path, body FROM notes").fetchall()
        if r["path"] != row["path"]
        and (f"[[{stem}]]" in r["body"] or f"[[{row['title']}]]" in r["body"])
    ]
    if links:
        text += "\n\n---\n\nLinked from: " + ", ".join(f"`{p}`" for p in links)
    return text


@mcp.tool
def whats_new(since: str | None = None) -> str:
    """What changed in the portals: new items, edited items, moved deadlines.

    since is a YYYY-MM-DD date and defaults to the last time you asked.
    """
    global _last_checked
    _pull()
    cutoff = since or _last_checked or (date.today() - timedelta(days=7)).isoformat()
    _last_checked = date.today().isoformat()

    folder = REPO / "changes"
    files = sorted(p for p in folder.glob("*.md") if p.stem >= cutoff) if folder.exists() else []
    if not files:
        return f"Nothing new since {cutoff}."
    return "\n\n".join(p.read_text(encoding="utf-8") for p in files)


@mcp.tool
def whats_due(days: int = 14) -> str:
    """Everything with a deadline in the next N days, soonest first, with class
    and links back to the portal."""
    db = _index()
    today = date.today().isoformat()
    until = (date.today() + timedelta(days=max(1, days))).isoformat()
    rows = db.execute(
        "SELECT id, class, title, due, url FROM notes "
        "WHERE due >= ? AND due <= ? ORDER BY due", [today, until],
    ).fetchall()
    if not rows:
        return f"Nothing due in the next {days} days."
    return "\n".join(
        f"- **{r['due']}** - {r['class']} - [{r['title']}]({r['url']}) - `{r['id']}`"
        for r in rows
    )


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, timeout=120, check=False)


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:60].strip("-") or "note"


@mcp.tool
def remember(title: str, text: str) -> str:
    """Save a note into the vault and push it to GitHub, so it survives this
    conversation and shows up on every device.

    For things worth keeping: a decision, a revision plan, a summary. Teacher
    material is already in the vault verbatim - do not copy it in here.
    """
    _pull()
    folder = (REPO / "notes").resolve()
    folder.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    stem = f"{today}-{_slug(title)}"
    path = folder / f"{stem}.md"
    for n in range(2, 50):
        if not path.exists():
            break
        path = folder / f"{stem}-{n}.md"

    # notes/ is the only place this tool may write, and nothing else writes here.
    if path.resolve().parent != folder:
        return "Refused: notes may only be written directly inside notes/."

    doc = (
        "---\n"
        f"id: note:{path.stem}\n"
        "source: note\n"
        "type: note\n"
        f"title: {json.dumps(title)}\n"
        f"posted: {today}\n"
        "---\n\n"
        f"# {title}\n\n{text}\n"
    )
    path.write_text(doc, encoding="utf-8")

    rel = path.relative_to(REPO).as_posix()
    _git("add", "--", rel)
    commit = _git("commit", "-m", f"note: {title}")
    if commit.returncode and "nothing to commit" not in commit.stdout:
        return f"Saved to {rel}, but the commit failed: {commit.stderr.strip()[:200]}"
    _git("pull", "--rebase", "--autostash", "--quiet")
    push = _git("push", "--quiet")
    if push.returncode:
        return (f"Saved and committed to {rel}, but the push failed: "
                f"{push.stderr.strip()[:200]}. It will go up on the next successful push.")
    return f"Saved to {rel} and pushed. Find it with recall(), or in Obsidian under notes/."


@mcp.tool
def sync(scope: str = "full", class_name: str | None = None) -> str:
    """Scrape both portals right now instead of waiting for the 06:00 run, then
    report what changed.

    scope is one of: full, announcements, tasks, class. Use class together with
    class_name (for example 'cs-hl') to refresh a single class.
    """
    token = os.environ.get("GITHUB_PAT", "").strip()
    if not token:
        return "No GITHUB_PAT on the server, so I cannot trigger a run. Ask for one to be added."
    repo = os.environ.get("GITHUB_REPO", "arusadusdg/school-vault")
    if scope not in ("full", "announcements", "tasks", "class"):
        return f"Unknown scope {scope!r}. Use full, announcements, tasks or class."

    api = f"https://api.github.com/repos/{repo}/actions/workflows/sync.yml"
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    started = datetime.now(timezone.utc).replace(microsecond=0)
    inputs = {"scope": scope, "class": class_name or ""}

    with httpx.Client(headers=headers, timeout=30.0) as c:
        r = c.post(f"{api}/dispatches", json={"ref": "main", "inputs": inputs})
        if r.status_code == 401:
            return "GitHub rejected the token. It has probably expired."
        if r.status_code != 204:
            return f"Could not start the sync: HTTP {r.status_code} {r.text[:200]}"

        # The dispatch returns no run id, so find the run it just created.
        deadline = time.monotonic() + 150
        run = None
        while time.monotonic() < deadline:
            time.sleep(5)
            runs = c.get(f"{api}/runs", params={"per_page": 5, "event": "workflow_dispatch"})
            for candidate in runs.json().get("workflow_runs", []):
                created = datetime.fromisoformat(candidate["created_at"].replace("Z", "+00:00"))
                if created >= started:
                    run = candidate
                    break
            if run and run["status"] == "completed":
                break
            if run:
                run = c.get(f"{api.rsplit('/workflows', 1)[0]}/runs/{run['id']}").json()

    if run is None:
        return "Started the sync, but no run appeared. Check the Actions tab."
    if run["status"] != "completed":
        return (f"Sync is still running ({run['html_url']}). "
                "Give it a minute, then call whats_new().")
    if run["conclusion"] != "success":
        return (f"The sync FAILED ({run['conclusion']}). Nothing was committed, so the vault "
                f"is unchanged. Logs: {run['html_url']}")

    global _last_pull
    _last_pull = 0.0  # force a pull rather than waiting out the throttle
    _pull()
    return "Sync finished.\n\n" + whats_new(since=date.today().isoformat())


if __name__ == "__main__":
    import uvicorn

    # Binding loopback makes FastMCP demand a loopback Host header, but the reverse
    # proxy forwards the real one. Without this the proxied request gets a 421.
    allowed = [h for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]

    # Loopback by default: Caddy terminates TLS and does the auth in front of this.
    uvicorn.run(
        mcp.http_app(path="/mcp", allowed_hosts=allowed or None),
        host=os.environ.get("MCP_HOST", "127.0.0.1"),
        port=int(os.environ.get("MCP_PORT", "8000")),
    )
