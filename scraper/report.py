"""Deterministic reporting: watermarks, the count-drop guard, changes/, context.md.

No model anywhere in this path. A deadline in context.md is a deadline a portal
actually published.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

import vault

STATE = "sync_state.json"
DROP_LIMIT = 0.5


class CountDrop(Exception):
    """A source lost over half its items: the frontend changed, the work did not."""


def load() -> dict:
    path = vault.guard(STATE)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save(state: dict) -> None:
    vault.write_text(STATE, json.dumps(state, indent=2, sort_keys=True) + "\n")


def check_count(state: dict, source: str, count: int) -> None:
    """Abort before a single note is written. Called with the full scrape in hand."""
    was = state.get("sources", {}).get(source, {}).get("count", 0)
    if was and count < was * DROP_LIMIT:
        raise CountDrop(
            f"{source}: got {count} items, last run had {was}. "
            f"Refusing to overwrite good data with a partial scrape."
        )


def diff(state: dict, items: list[dict]) -> tuple[list, list, list]:
    """New items, edited items, and items whose deadline moved."""
    old = state.get("items", {})
    new, edited, moved = [], [], []
    for item in items:
        prev = old.get(item["id"])
        if prev is None:
            new.append(item)
            continue
        if prev.get("hash") != vault.content_hash(item["body"]):
            edited.append(item)
        if (prev.get("due") or "") != (item.get("due") or ""):
            moved.append((item, prev.get("due")))
    return new, edited, moved


def _line(item: dict) -> str:
    due = f" — due {item['due']}" if item.get("due") else ""
    return f"- **{item['title']}** ({item['class']}, {item['type']}){due} — [open]({item.get('url', '')})"


def write_changes(new: list, edited: list, moved: list, when: str | None = None) -> str | None:
    """One file per sync day. A second run the same day appends, never replaces."""
    if not (new or edited or moved):
        return None
    when = when or date.today().isoformat()
    rel = f"changes/{when}.md"

    out = []
    if new:
        out += [f"## {len(new)} new", ""] + [_line(i) for i in new] + [""]
    if edited:
        out += [f"## {len(edited)} edited", ""] + [_line(i) for i in edited] + [""]
    if moved:
        out += [f"## {len(moved)} deadline moved", ""]
        out += [f"{_line(i)}  \n  was: {was or 'no date'}" for i, was in moved] + [""]

    path = vault.guard(rel)
    stamp = datetime.now(timezone.utc).strftime("%H:%M UTC")
    block = f"# Changes {when}\n\n_synced {stamp}_\n\n" + "\n".join(out)
    if path.exists():
        block = path.read_text(encoding="utf-8").rstrip() + "\n\n---\n\n" + block
    vault.write_text(rel, block)
    return rel


def write_context(items: list[dict], horizon_days: int = 14) -> None:
    today = date.today()
    cutoff = (today + timedelta(days=horizon_days)).isoformat()

    upcoming = sorted(
        (i for i in items if i.get("due") and today.isoformat() <= i["due"] <= cutoff),
        key=lambda i: i["due"],
    )
    latest: dict[str, dict] = {}
    for i in items:
        if i["type"] != "announcement":
            continue
        best = latest.get(i["class"])
        if best is None or (i.get("posted") or "") > (best.get("posted") or ""):
            latest[i["class"]] = i

    out = [
        "# Context",
        "",
        f"_Last sync: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}._",
        f"_{len(items)} items across {len({i['class'] for i in items})} class(es)._",
        "",
        f"## Due in the next {horizon_days} days",
        "",
    ]
    out += [
        f"- **{i['due']}** — {i['class']} — [{i['title']}]({i.get('url', '')})" for i in upcoming
    ] or ["_Nothing due._"]

    out += ["", "## Latest announcement per class", ""]
    for cls in sorted(latest):
        a = latest[cls]
        out += [
            f"### {cls}",
            f"**{a['title']}** — {a.get('author') or 'unknown'}, {a.get('posted') or '?'} "
            f"— [open]({a.get('url', '')})",
            "",
        ]
    if not latest:
        out += ["_None yet._", ""]

    vault.write_text("context.md", "\n".join(out) + "\n")


def update(state: dict, source: str, items: list[dict], track_count: bool = True) -> dict:
    """Watermark a source. A scoped run updates hashes but not the count it
    would otherwise poison, since it never claimed to fetch everything."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry = state.setdefault("sources", {}).setdefault(source, {})
    entry["last_sync"] = now
    if track_count:
        entry["count"] = len(items)
    state.setdefault("items", {})
    for i in items:
        state["items"][i["id"]] = {
            "hash": vault.content_hash(i["body"]),
            "due": i.get("due") or "",
            "updated": i.get("updated") or "",
        }
    state["last_sync"] = now
    return state


def commit_message(new: list, edited: list, moved: list) -> str:
    bits = []
    if new:
        bits.append(f"{len(new)} new")
    if edited:
        bits.append(f"{len(edited)} edited")
    if moved:
        bits.append(f"{len(moved)} deadline moved")
    subject = f"sync {date.today().isoformat()}: " + (", ".join(bits) or "no changes")
    body = [f"  new       {i['class']}  {i['title']}" for i in new]
    body += [f"  edited    {i['class']}  {i['title']}" for i in edited]
    body += [
        f"  deadline  {i['class']}  {i['title']}: {was or 'none'} -> {i.get('due') or 'none'}"
        for i, was in moved
    ]
    return subject + ("\n\n" + "\n".join(body) if body else "")
