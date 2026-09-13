"""Run the scrapers and write the vault.

    uv run scraper/sync.py
"""

from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

import canvas
import vault

META_KEYS = ("id", "source", "class", "type", "title", "author",
             "posted", "due", "updated", "url", "attachments")


def path_for(item: dict) -> str:
    # The id tail keeps two items with the same title from fighting over a filename.
    tail = item["id"].rsplit(":", 1)[1]
    return f"canvas/{item['class']}/{item['dir']}/{vault.slug(item['title'])}-{tail}.md"


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
    missing = [k for k in ("CANVAS_BASE_URL", "CANVAS_COURSE_ID", "CANVAS_TOKEN")
               if not os.environ.get(k)]
    if missing:
        sys.exit(f"missing from .env: {', '.join(missing)}")  # names only, never values

    try:
        items = canvas.scrape()
    except httpx.HTTPStatusError as e:
        hint = {
            401: "Canvas token rejected. Make a new one: Canvas -> Account -> Settings.",
            403: "Canvas refused access. Check CANVAS_COURSE_ID and that you are enrolled.",
            404: "No such course. Check CANVAS_COURSE_ID.",
        }.get(e.response.status_code, "")
        sys.exit(f"Canvas returned {e.response.status_code}. {hint}")

    tally = write_all(items)
    print(f"canvas: {len(items)} items — "
          f"{tally['new']} new, {tally['changed']} changed, {tally['same']} unchanged")


if __name__ == "__main__":
    main()
