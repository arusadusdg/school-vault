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
import toddle
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
    scraped: dict[str, list[dict]] = {}

    try:
        scraped[f"canvas:{os.environ.get('CANVAS_CLASS_SLUG', 'cs-hl')}"] = canvas.scrape()
    except httpx.HTTPStatusError as e:
        hint = {
            401: "Canvas token rejected. Make a new one: Canvas -> Account -> Settings.",
            403: "Canvas refused access. Check CANVAS_COURSE_ID and that you are enrolled.",
            404: "No such course. Check CANVAS_COURSE_ID.",
        }.get(e.response.status_code, "")
        sys.exit(f"Canvas returned {e.response.status_code}. {hint}")

    if toddle.configured():
        try:
            scraped["toddle"] = toddle.scrape()
        except toddle.ToddleAuthError as e:
            # A dead session must fail the run, never quietly write nothing.
            sys.exit(f"ABORT - Toddle re-auth needed. {e}")
    else:
        log("toddle: no session configured, skipped")

    # Every count is checked before a single note is written, so one collapsed
    # source cannot half-overwrite the vault before the other one aborts.
    for source, items in scraped.items():
        try:
            report.check_count(state, source, len(items))
        except report.CountDrop as e:
            sys.exit(f"ABORT - {e}")

    everything = [i for items in scraped.values() for i in items]
    new, edited, moved = report.diff(state, everything)
    tally = write_all(everything)
    report.write_changes(new, edited, moved)
    report.write_context(everything)
    for source, items in scraped.items():
        state = report.update(state, source, items)
    report.save(state)

    for source, items in scraped.items():
        log(f"{source}: {len(items)} items")
    log(f"files: {tally['new']} new, {tally['changed']} rewritten, {tally['same']} untouched")
    print(report.commit_message(new, edited, moved))


if __name__ == "__main__":
    main()
