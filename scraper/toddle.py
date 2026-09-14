"""Toddle adapter. GraphQL, reverse-engineered from one captured browser session.

The queries in toddle_queries.json are the app's own, lifted verbatim from a HAR.
That is deliberate: this endpoint has no documentation, so a hand-written query
guessing at the schema would break silently. Personal ids are tokenised out of
that file and injected at runtime, mostly from the saved session itself.

Auth is cookies on .toddleapp.com. Playwright saves a logged-in session once,
the workflow restores it, and httpx replays the cookies.
"""

from __future__ import annotations

import base64
import binascii
import json
import mimetypes
import os
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import httpx

import vault

API = "https://eu-west-1-production-apis.toddleapp.com/graphql"
QUERIES = json.loads((Path(__file__).parent / "toddle_queries.json").read_text(encoding="utf-8"))

# A school platform being hit by a student account. One request per 2 seconds.
RATE_LIMIT = 2.0

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

_last_call = 0.0


class ToddleAuthError(Exception):
    """The saved session is dead. Fail the run loudly rather than write nothing."""


def _storage_state() -> dict:
    """Playwright's saved session, from the GitHub secret or a local file."""
    raw = os.environ.get("TODDLE_STORAGE_STATE", "").strip()
    if raw:
        try:
            return json.loads(base64.b64decode(raw))
        except (binascii.Error, ValueError) as e:
            raise ToddleAuthError(
                "TODDLE_STORAGE_STATE is not valid base64-encoded JSON."
            ) from e
    path = Path(os.environ.get("TODDLE_STORAGE_FILE", "storage_state.json"))
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raise ToddleAuthError(
        "No Toddle session found. Set TODDLE_STORAGE_STATE, or create "
        "storage_state.json with: playwright codegen --save-storage=storage_state.json"
    )


def configured() -> bool:
    """Is a Toddle session available at all? Absent is skippable; dead is fatal."""
    return bool(os.environ.get("TODDLE_STORAGE_STATE", "").strip()) or Path(
        os.environ.get("TODDLE_STORAGE_FILE", "storage_state.json")).exists()


def client() -> httpx.Client:
    state = _storage_state()
    cookies = {
        c["name"]: c["value"]
        for c in state.get("cookies", [])
        if c.get("domain", "").endswith("toddleapp.com")
    }
    if not cookies:
        raise ToddleAuthError("The saved session has no toddleapp.com cookies in it.")
    return httpx.Client(
        headers={
            "content-type": "application/json",
            "origin": "https://web.toddleapp.com",
            "referer": "https://web.toddleapp.com/",
            "x-tod-source": "WEB",
            "x-tod-lang": "en",
            "user-agent": UA,
        },
        cookies=cookies,
        timeout=30.0,
        follow_redirects=False,
    )


def _ids() -> dict[str, str]:
    """Account ids for the query templates.

    Three of them ride along in the saved session, so they re-derive themselves
    every time you re-authenticate. Only the academic year has to be configured,
    and that changes once a year.
    """
    store = {
        kv["name"]: kv["value"]
        for o in _storage_state().get("origins", [])
        if "toddle" in o.get("origin", "")
        for kv in o.get("localStorage", [])
    }
    try:
        info = json.loads(store["userInfo"])
        program = json.loads(store["currentCurriculumProgram"])
    except (KeyError, ValueError) as e:
        raise ToddleAuthError(
            "The saved session has no userInfo in it. Re-run the Playwright login "
            "and make sure Toddle finished loading before you closed the window."
        ) from e

    year = os.environ.get("TODDLE_ACADEMIC_YEAR_ID", "").strip()
    if not year:
        raise ToddleAuthError("missing from .env: TODDLE_ACADEMIC_YEAR_ID")

    return {
        "{{USER_ID}}": str(info["id"]),
        "{{ORG_ID}}": str(info["org_id"]),
        "{{CURRICULUM_PROGRAM_ID}}": str(program["id"]),
        "{{ACADEMIC_YEAR_ID}}": year,
    }


def variables(op: str, **overrides) -> dict:
    text = json.dumps(QUERIES[op]["variables"])
    for token, real in _ids().items():
        text = text.replace(token, real)
    return {**json.loads(text), **overrides}


def gql(c: httpx.Client, op: str, vars_: dict, tag: str) -> dict:
    """One rate-limited call. Raw response hits disk before anything is parsed."""
    global _last_call
    wait = RATE_LIMIT - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()

    r = c.post(API, json={"operationName": op, "query": QUERIES[op]["query"],
                          "variables": vars_})
    vault.write_text(f"toddle/raw/{tag}.json", r.text)

    if r.status_code in (401, 403) or 300 <= r.status_code < 400:
        raise ToddleAuthError("Toddle re-auth needed - the saved session was rejected.")
    r.raise_for_status()

    try:
        body = r.json()
    except ValueError:
        raise ToddleAuthError(
            "Toddle returned a non-JSON response, which usually means a login page."
        ) from None

    if isinstance(body, list):
        body = body[0] if body else {}
    if body.get("errors"):
        msg = "; ".join(str(e.get("message", "")) for e in body["errors"])
        if any(w in msg.lower() for w in ("auth", "session", "forbidden", "login")):
            raise ToddleAuthError(f"Toddle re-auth needed: {msg}")
        raise RuntimeError(f"{op} failed: {msg}")
    return body.get("data") or {}


def _attachments(c: httpx.Client, node: dict, max_bytes: int) -> list[str]:
    """Banner plus any real attachments, content-hashed into attachments/."""
    found = []
    for item in [node.get("bannerV2")] + list(node.get("attachments") or []):
        if isinstance(item, dict) and item.get("url"):
            found.append(item)
    out = []
    for a in found:
        try:
            r = c.get(a["url"], follow_redirects=True)
            r.raise_for_status()
        except httpx.HTTPError:
            continue
        if len(r.content) <= max_bytes:
            out.append(vault.save_attachment(r.content, _filename(a)))
    return out


def _filename(a: dict) -> str:
    """Toddle's `name` is a human description, not a filename, so it usually has
    no extension. Recover one from the URL, then from the mime type."""
    name = a.get("name") or "file"
    if Path(name).suffix:
        return name
    suffix = Path(urlparse(a["url"]).path).suffix
    if not suffix:
        suffix = mimetypes.guess_extension(a.get("mimeType") or "") or ""
    return name + suffix


def _author(node: dict) -> str:
    who = node.get("publishedBy") or node.get("createdBy") or {}
    name = " ".join(p for p in (who.get("firstName"), who.get("lastName")) if p)
    return name.strip()


def scrape() -> list[dict]:
    max_bytes = int(os.environ.get("MAX_ATTACHMENT_MB", "50")) * 1024 * 1024
    term_start = os.environ.get("TERM_START", "2026-08-01")
    items: list[dict] = []

    with client() as c:
        courses = (gql(c, "getUserCourses", variables("getUserCourses"), "courses")
                   .get("node", {}).get("courses") or [])
        slugs = {co["id"]: vault.slug(co.get("title") or co["id"]) for co in courses}

        feed_vars = variables(
            "getAnnouncementsFeed",
            createdAfter=f"{term_start}T00:00:00.000Z",
            createdBefore=f"{date.fromisoformat(term_start).year + 1}-07-31T21:59:59.999Z",
        )
        feed = gql(c, "getAnnouncementsFeed", feed_vars, "announcements")
        edges = (feed.get("node", {}).get("circularFeedV3", {}).get("edges")) or []
        for edge in edges:
            n = edge.get("node") or {}
            items.append({
                "id": f"toddle:announcement:{n['id']}",
                "class": "school",
                "dir": "announcements",
                "type": "announcement",
                "title": n.get("title") or "Untitled",
                "author": _author(n),
                "posted": (n.get("publishedAt") or "")[:10],
                "updated": n.get("updatedAt") or n.get("publishedAt"),
                "url": "https://web.toddleapp.com/",
                "attachments": _attachments(c, n, max_bytes),
                "body": vault.html_to_md(n.get("description")),
            })

        task_vars = variables("getStudentTasks")
        task_vars["filters"]["courseIds"] = list(slugs)
        tasks = gql(c, "getStudentTasks", task_vars, "tasks")
        for edge in (tasks.get("node", {}).get("tasks", {}).get("edges") or []):
            n = edge.get("node") or {}
            course = (n.get("course") or {}).get("id")
            items.append({
                "id": f"toddle:task:{n['id']}",
                "class": slugs.get(course, "unknown-class"),
                "dir": "tasks",
                "type": "task",
                "title": n.get("title") or "Untitled",
                "author": _author(n),
                "posted": (n.get("publishedAt") or n.get("createdAt") or "")[:10],
                "due": (n.get("dueDate") or "")[:10],
                "updated": n.get("updatedAt"),
                "url": "https://web.toddleapp.com/",
                "attachments": _attachments(c, n, max_bytes),
                "body": vault.html_to_md(n.get("description") or n.get("body")),
            })

    return [{**i, "source": "toddle"} for i in items]
