"""The checks that matter: uv run scraper/selfcheck.py

Fails loudly if the path guard, the verbatim write, or the count-drop guard
ever regresses. Runs in CI before every scrape.
"""

import tempfile
from datetime import date, timedelta
from pathlib import Path

import report
import vault


def check_guard() -> None:
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


def check_verbatim() -> None:
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


def check_count_drop() -> None:
    state = {"sources": {"canvas:cs-hl": {"count": 100}}}
    report.check_count(state, "canvas:cs-hl", 100)
    report.check_count(state, "canvas:cs-hl", 50)          # exactly half is not a >50% drop
    report.check_count({}, "canvas:cs-hl", 1)              # first run has nothing to compare
    for collapsed in (49, 1, 0):
        try:
            report.check_count(state, "canvas:cs-hl", collapsed)
        except report.CountDrop:
            continue
        raise AssertionError(f"count guard allowed a drop to {collapsed} from 100")


def check_diff_and_changes() -> None:
    item = {"id": "canvas:assignment:9", "class": "cs-hl", "type": "assignment",
            "title": "Lab report", "body": "do the lab", "due": "2026-09-20", "url": "u"}
    new, edited, moved = report.diff({}, [item])
    assert (len(new), len(edited), len(moved)) == (1, 0, 0)

    state = report.update({}, "canvas:cs-hl", [item])
    new, edited, moved = report.diff(state, [item])
    assert (new, edited, moved) == ([], [], []), "an unchanged item must be silent"

    shifted = {**item, "due": "2026-09-27", "body": "do the lab, part two"}
    new, edited, moved = report.diff(state, [shifted])
    assert not new and len(edited) == 1 and len(moved) == 1
    assert moved[0][1] == "2026-09-20", "the old deadline must be reported"

    when = "2026-09-14"
    report.write_changes(new, edited, moved, when=when)
    report.write_changes([item], [], [], when=when)
    text = (vault.VAULT / f"changes/{when}.md").read_text(encoding="utf-8")
    assert "2026-09-20" in text and "Lab report" in text
    assert text.count("# Changes") == 2, "a second sync the same day must append, not replace"


def check_context() -> None:
    soon = (date.today() + timedelta(days=3)).isoformat()
    far = (date.today() + timedelta(days=90)).isoformat()
    items = [
        {"id": "a", "class": "cs-hl", "type": "assignment", "title": "Soon", "body": "",
         "due": soon, "url": "u"},
        {"id": "b", "class": "cs-hl", "type": "assignment", "title": "Far", "body": "",
         "due": far, "url": "u"},
        {"id": "c", "class": "cs-hl", "type": "announcement", "title": "Hello", "body": "",
         "author": "Mr X", "posted": "2026-09-10", "url": "u"},
    ]
    report.write_context(items)
    text = (vault.VAULT / "context.md").read_text(encoding="utf-8")
    assert "Soon" in text, "an item due inside the horizon is missing"
    assert "Far" not in text, "an item 90 days out leaked into the 14-day horizon"
    assert "Mr X" in text, "latest announcement per class is missing"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        vault.VAULT = Path(tmp).resolve()
        check_guard()
        check_verbatim()
        check_count_drop()
        check_diff_and_changes()
        check_context()
    print("guard + verbatim + count-drop + changes + context: ok")


if __name__ == "__main__":
    main()
