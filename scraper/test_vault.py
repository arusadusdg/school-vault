"""The one check that matters: uv run scraper/test_vault.py

Fails loudly if the path guard or the verbatim write ever regresses.
"""

import tempfile
from pathlib import Path

import vault


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        vault.VAULT = Path(tmp).resolve()

        for bad in ("notes/mine.md", "../escape.md", "README.md", "canvas/../notes/x.md",
                    ".github/workflows/sync.yml", "scraper/vault.py", "C:/Windows/evil.md"):
            try:
                vault.guard(bad)
            except vault.VaultGuard:
                continue
            raise AssertionError(f"guard let through: {bad}")

        for ok in ("canvas/cs-hl/assignments/x.md", "toddle/physics/tasks/y.md",
                   "attachments/sha256-ab.pdf", "changes/2026-09-14.md",
                   "context.md", "sync_state.json"):
            vault.guard(ok)

        body = ("Read pages 4-9.\n\n  indented\ttab kept\n\n\n"
                "three blank lines above, all of it survives. Ünïcode & <escaped>")
        meta = {"id": "canvas:assignment:1", "title": "Paper 2: mock"}
        rel = "canvas/cs-hl/assignments/t-1.md"
        assert vault.upsert(rel, meta, body) == "new"
        assert vault.upsert(rel, meta, body) == "same"
        assert vault.upsert(rel, meta, body + " edited") == "changed"

        written = (vault.VAULT / rel).read_text(encoding="utf-8")
        assert body in written, "teacher text was altered on the way to disk"
        assert "Paper 2: mock" in written, "a colon in a title broke the frontmatter"
        assert list(vault.index_ids()) == ["canvas:assignment:1"]

        vault.relocate(vault.VAULT / rel, "canvas/cs-hl/assignments/t-renamed-1.md")
        assert not (vault.VAULT / rel).exists(), "stale file left behind after a retitle"

        a = vault.save_attachment(b"pdf-bytes", "notes.pdf")
        assert a == vault.save_attachment(b"pdf-bytes", "other.pdf"), "same bytes must dedupe"

    print("vault guard + verbatim write + attachment dedupe: ok")


if __name__ == "__main__":
    main()
