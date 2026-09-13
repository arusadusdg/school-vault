"""Run the scrapers, write the vault, report what changed.

    uv run scraper/sync.py

Progress goes to stderr. Stdout is the commit message and nothing else, so the
workflow can pipe it straight into `git commit`.
"""

from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

import canvas
import report
import vault

META_KEYS = ("id", "source", "class", "type", "title", "author",
             "posted", "due", "updated", "url", "attachments")

REQUIRED = ("CANVAS_BASE_URL", "CANVAS_COURSE_ID", "CANVAS_TOKEN")

# Teacher titles contain emoji; a Windows console defaults to cp1252 and would die on them.
for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(encoding="utf-8", errors="replace")


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def path_for(item: dict) -> str:
    # The id tail stops two items with the same title fighting over a filename.
    tail = item["id"].rsplit(":", 1)[1]
    return f"{item['source']}/{item['class']}/{item['dir']}/{vault.slug(item['title'])}-{tail}.md"


def write_all(items: list[dict]) -> dict[str, int]:
    known = vault.index_ids()
    tally = {"new": 0, "changed": 0, "same": 0}
    for item in items:
        rel = path_for(item)
        if item["id"] in known:
            vault.relocate(known[item["id"]], rel)
        meta = {k: item.get(k) for k in META_KEYS}
        tally[vault.upsert(rel, meta, item["body"])] += 1
    return tally


def main() -> None:
    load_dotenv()
    missing = [k for k in REQUIRED if not os.environ.get(k)]
    if missing:
        sys.exit(f"missing from .env: {', '.join(missing)}")  # names only, never values

    state = report.load()

    try:
        items = canvas.scrape()
    except httpx.HTTPStatusError as e:
        hint = {
            401: "Canvas token rejected. Make a new one: Canvas -> Account -> Settings.",
            403: "Canvas refused access. Check CANVAS_COURSE_ID and that you are enrolled.",
            404: "No such course. Check CANVAS_COURSE_ID.",
        }.get(e.response.status_code, "")
        sys.exit(f"Canvas returned {e.response.status_code}. {hint}")

    source = f"canvas:{os.environ.get('CANVAS_CLASS_SLUG', 'cs-hl')}"
    try:
        report.check_count(state, source, len(items))
    except report.CountDrop as e:
        sys.exit(f"ABORT - {e}")

    new, edited, moved = report.diff(state, items)
    tally = write_all(items)
    report.write_changes(new, edited, moved)
    report.write_context(items)
    report.save(report.update(state, source, items))

    log(f"canvas: {len(items)} items - {tally['new']} new files, "
        f"{tally['changed']} rewritten, {tally['same']} untouched")
    print(report.commit_message(new, edited, moved))


if __name__ == "__main__":
    main()
