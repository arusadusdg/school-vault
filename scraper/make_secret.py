"""Turn a fresh Playwright login into the TODDLE_STORAGE_STATE secret.

    uv run scraper/make_secret.py

Keeps only what the scraper actually replays: toddleapp.com cookies and the
web.toddleapp.com origin. The Microsoft SSO cookies in the raw file are only
needed to log in, never to call the API, so they are dropped rather than
uploaded to GitHub. Prints sizes and names, never a value.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

SOURCE = Path("storage_state.json")
TARGET = Path("toddle_secret.b64")
GITHUB_SECRET_LIMIT = 48 * 1024


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(
            f"{SOURCE} not found. Capture a session first:\n"
            "  uv run --with playwright playwright codegen "
            "--save-storage=storage_state.json https://web.toddleapp.com"
        )

    state = json.loads(SOURCE.read_text(encoding="utf-8"))
    cookies = [c for c in state.get("cookies", [])
               if c.get("domain", "").endswith("toddleapp.com")]
    origins = [o for o in state.get("origins", [])
               if "toddleapp.com" in o.get("origin", "")]

    if not cookies:
        raise SystemExit("No toddleapp.com cookies in that file - the login did not finish.")
    if not any("userInfo" in {kv["name"] for kv in o.get("localStorage", [])} for o in origins):
        raise SystemExit(
            "No userInfo in that session. Let Toddle finish loading before closing the window."
        )

    blob = base64.b64encode(
        json.dumps({"cookies": cookies, "origins": origins}).encode("utf-8")
    ).decode("ascii")
    TARGET.write_text(blob, encoding="utf-8")

    dropped = len(state.get("cookies", [])) - len(cookies)
    print(f"kept {len(cookies)} toddleapp.com cookies: "
          f"{', '.join(sorted(c['name'] for c in cookies))}")
    print(f"dropped {dropped} cookies from other domains (Microsoft SSO and friends)")
    print(f"wrote {TARGET} - {len(blob)} chars "
          f"({'fits' if len(blob) < GITHUB_SECRET_LIMIT else 'TOO BIG for'} a GitHub secret)")


if __name__ == "__main__":
    main()
