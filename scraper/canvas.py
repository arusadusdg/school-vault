"""Canvas REST adapter.

Raw JSON hits disk before a single field is read, so a parser bug is always
recoverable from what the server actually said.
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import httpx

import vault


def _cfg() -> dict:
    return {
        "base": os.environ["CANVAS_BASE_URL"].rstrip("/"),
        "course": os.environ["CANVAS_COURSE_ID"],
        "slug": os.environ.get("CANVAS_CLASS_SLUG", "cs-hl"),
        "term_start": os.environ.get("TERM_START", "2026-08-01"),
        "max_bytes": int(os.environ.get("MAX_ATTACHMENT_MB", "50")) * 1024 * 1024,
    }


def client() -> httpx.Client:
    cfg = _cfg()
    return httpx.Client(
        base_url=f"{cfg['base']}/api/v1",
        headers={"Authorization": f"Bearer {os.environ['CANVAS_TOKEN']}"},
        timeout=30.0,
        follow_redirects=True,
    )


def get_all(c: httpx.Client, path: str, name: str, **params) -> list:
    """Every page of a paginated endpoint. Raw response saved before parsing."""
    root = f"canvas/{_cfg()['slug']}/raw"
    params.setdefault("per_page", 100)
    items, url, page = [], path, 1
    while url:
        r = c.get(url, params=params)
        r.raise_for_status()
        vault.write_text(f"{root}/{name}-{page:02d}.json", r.text)
        items += r.json()
        url = r.links.get("next", {}).get("url")
        params = None  # the next link already carries them
        page += 1
    return items


def _download(c: httpx.Client, url: str, filename: str, max_bytes: int) -> str | None:
    head = c.head(url)
    size = int(head.headers.get("content-length") or 0)
    if size > max_bytes:
        return None
    r = c.get(url)
    r.raise_for_status()
    if len(r.content) > max_bytes:
        return None
    return vault.save_attachment(r.content, filename)


def _attachments(c: httpx.Client, raw: list, max_bytes: int) -> list[str]:
    out = []
    for a in raw or []:
        rel = _download(c, a["url"], a.get("filename") or a.get("display_name") or "", max_bytes)
        if rel:
            out.append(rel)
    return out


def items(c: httpx.Client):
    """Yield every Canvas item as a vault-ready dict."""
    cfg = _cfg()
    cid, slug, mb = cfg["course"], cfg["slug"], cfg["max_bytes"]

    for a in get_all(c, f"/courses/{cid}/assignments", "assignments"):
        yield {
            "id": f"canvas:assignment:{a['id']}",
            "dir": "assignments",
            "type": "assignment",
            "title": a.get("name") or "Untitled",
            "posted": (a.get("created_at") or "")[:10],
            "due": (a.get("due_at") or "")[:10],
            "updated": a.get("updated_at"),
            "url": a.get("html_url"),
            "body": vault.html_to_md(a.get("description")),
        }

    # Canvas defaults this endpoint to the last 14 days, so both dates are required.
    end = (date.today() + timedelta(days=365)).isoformat()
    for n in get_all(
        c,
        "/announcements",
        "announcements",
        **{"context_codes[]": f"course_{cid}", "start_date": cfg["term_start"], "end_date": end},
    ):
        yield {
            "id": f"canvas:announcement:{n['id']}",
            "dir": "announcements",
            "type": "announcement",
            "title": n.get("title") or "Untitled",
            "author": (n.get("author") or {}).get("display_name"),
            "posted": (n.get("posted_at") or n.get("created_at") or "")[:10],
            "updated": n.get("posted_at") or n.get("created_at"),
            "url": n.get("html_url"),
            "attachments": _attachments(c, n.get("attachments"), mb),
            "body": vault.html_to_md(n.get("message")),
        }

    for m in get_all(c, f"/courses/{cid}/modules", "modules", **{"include[]": "items"}):
        lines = [
            f"- [{i.get('title')}]({i.get('html_url')}) — {i.get('type')}"
            for i in m.get("items") or []
        ]
        yield {
            "id": f"canvas:module:{m['id']}",
            "dir": "modules",
            "type": "material",
            "title": m.get("name") or "Untitled",
            "url": m.get("items_url"),
            "body": "\n".join(lines),
        }

    for f in get_all(c, f"/courses/{cid}/files", "files"):
        name = f.get("display_name") or f.get("filename") or "file"
        rel = _download(c, f["url"], name, mb) if f.get("url") else None
        yield {
            "id": f"canvas:file:{f['id']}",
            "dir": "materials",
            "type": "material",
            "title": name,
            "posted": (f.get("created_at") or "")[:10],
            "updated": f.get("updated_at"),
            "url": f.get("url", "").split("?")[0],
            "attachments": [rel] if rel else [],
            "body": f"Attachment: `{name}` ({f.get('size', 0)} bytes)"
            + ("" if rel else "\n\nNot downloaded: over MAX_ATTACHMENT_MB."),
        }


def scrape() -> list[dict]:
    slug = _cfg()["slug"]
    with client() as c:
        return [{**i, "source": "canvas", "class": slug} for i in items(c)]
