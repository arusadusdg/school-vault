"""The scraper's only way to touch disk.

Three hard rules live here as code, not as comments:
  * guard()  - the scraper may write only under ALLOWED_*. notes/ is the user's.
  * writes are atomic, so a crash or a killed workflow never leaves a half file.
  * nothing in this module shortens, wraps, reflows or rewrites teacher text.
"""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path

import yaml
from markdownify import markdownify

VAULT = Path(__file__).resolve().parent.parent

ALLOWED_DIRS = ("toddle", "canvas", "attachments", "changes")
ALLOWED_FILES = ("context.md", "sync_state.json")


class VaultGuard(Exception):
    """Raised when the scraper tries to write outside its own territory."""


def guard(rel: str | Path) -> Path:
    """Resolve rel inside the vault, refusing anything the scraper does not own.

    Every write and every delete in this codebase goes through here first.
    """
    rel = Path(rel)
    if rel.is_absolute():
        raise VaultGuard(f"absolute path refused: {rel}")
    path = (VAULT / rel).resolve()
    try:
        parts = path.relative_to(VAULT).parts
    except ValueError:
        raise VaultGuard(f"path escapes the vault: {rel}") from None
    if not parts:
        raise VaultGuard("refusing to write the vault root")
    if len(parts) == 1:
        if parts[0] not in ALLOWED_FILES:
            raise VaultGuard(f"not a scraper-owned file: {parts[0]}")
    elif parts[0] not in ALLOWED_DIRS:
        raise VaultGuard(f"not a scraper-owned directory: {parts[0]}/")
    return path


def _atomic(rel: str | Path, data: bytes) -> Path:
    path = guard(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return path


def write_text(rel: str | Path, text: str) -> Path:
    return _atomic(rel, text.encode("utf-8"))


def write_bytes(rel: str | Path, data: bytes) -> Path:
    return _atomic(rel, data)


def slug(text: str, limit: int = 60) -> str:
    """Filename hygiene only. The full title survives in frontmatter and the H1."""
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:limit].strip("-") or "untitled"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def html_to_md(html: str | None) -> str:
    """HTML -> markdown. A format conversion, never a summary and never a trim."""
    if not html:
        return ""
    return markdownify(html, heading_style="ATX").strip()


def _frontmatter(meta: dict) -> str:
    clean = {k: v for k, v in meta.items() if v not in (None, "", [])}
    body = yaml.safe_dump(clean, sort_keys=False, allow_unicode=True, width=10**6)
    return f"---\n{body}---\n"


ID_RE = re.compile(r"^id:\s*(\S+)\s*$", re.M)


def index_ids() -> dict[str, Path]:
    """Map stable id -> the file holding it.

    Lets a retitled item move to its new filename instead of quietly duplicating.
    A few hundred files, so a full walk is cheaper than another state file.
    """
    found: dict[str, Path] = {}
    for root in ("canvas", "toddle"):
        base = VAULT / root
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            head = md.read_text(encoding="utf-8", errors="replace")[:2000]
            m = ID_RE.search(head)
            if m:
                found[m.group(1)] = md
    return found


def upsert(rel: str | Path, meta: dict, body: str) -> str:
    """Write one note. Returns 'new', 'changed' or 'same'.

    Upsert-only: this never deletes a note it did not just relocate, so a partial
    run can leave the vault stale but never emptier than it was.
    """
    meta = {**meta, "content_hash": content_hash(body)}
    title = meta.get("title") or "Untitled"
    doc = f"{_frontmatter(meta)}\n# {title}\n\n{body}\n"
    path = guard(rel)
    if path.exists():
        if path.read_text(encoding="utf-8") == doc:
            return "same"
        status = "changed"
    else:
        status = "new"
    write_text(rel, doc)
    return status


def relocate(old: Path, rel: str | Path) -> None:
    """Drop the stale file when an item's title (and so its filename) changed."""
    new = guard(rel)
    if old == new or not old.exists():
        return
    guard(old.relative_to(VAULT))  # deletes are guarded too
    old.unlink()


def save_attachment(data: bytes, filename: str) -> str:
    """Content-hashed and append-only: same bytes, same path, never overwritten."""
    ext = "".join(c for c in Path(filename or "").suffix if c.isalnum() or c == ".")[:10]
    rel = f"attachments/sha256-{hashlib.sha256(data).hexdigest()[:16]}{ext}"
    if not guard(rel).exists():
        write_bytes(rel, data)
    return rel
