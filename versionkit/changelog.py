from __future__ import annotations

import re
import datetime

from .io import CHANGELOG


def ensure_changelog_has_version(version: str, dry_run: bool) -> None:
    """
    Inserts a new version section into CHANGELOG.md while preserving:
      - the top-level details block under the H1 title
      - an optional '## [Unreleased]' section at the very top (kept ahead of releases)

    Insertion rules:
      - If '## [Unreleased]' exists: insert *after its block* (i.e., before the next '## ' header).
      - Else: insert *before the first '## ' header* (which keeps the details block at the top).
      - If no '## ' header exists yet: append to the end.
    """
    if not CHANGELOG.exists():
        print("NOTE: CHANGELOG.md not found; skipping changelog update.")
        return

    text = CHANGELOG.read_text(encoding="utf-8")

    # Already present? Bail.
    existing_version_pat = re.compile(rf'(?m)^##\s*(\[{re.escape(version)}]|{re.escape(version)})(\s|$)' )

    if existing_version_pat.search(text):
        return

    # Build the version section to insert
    insertion = f"## [{version}] - {datetime.date.today()}\n\n- _Describe changes here._\n\n"

    # Find all H2 headers
    h2_pat = re.compile(r'(?m)^##\s*(\[.*?\]|.+?)\s*$')
    headers = list(h2_pat.finditer(text))

    # Helper: write out
    def _write(new_text: str) -> None:
        if dry_run:
            print(f"[dry-run] Would update CHANGELOG.md with:\n{insertion.strip()}\n")
            return
        CHANGELOG.write_text(new_text, encoding="utf-8")
        print("Inserted new version header into CHANGELOG.md")

    # No H2 headers yet → just append
    if not headers:
        new_text = text + ("" if text.endswith("\n") else "\n") + insertion
        _write(new_text)
        return

    # If the first H2 is [Unreleased], insert after its block (before the *next* H2)
    first_h2 = headers[0]
    first_h2_title = first_h2.group(1).strip()

    # Find where to insert
    insert_at = None
    if first_h2_title.lower() in ("[unreleased]", "unreleased"):
        # Look for the next H2; if none, append at end
        if len(headers) >= 2:
            insert_at = headers[1].start()
        else:
            insert_at = len(text)
    else:
        # Insert before the first H2 → keeps details block above all releases
        insert_at = first_h2.start()

    # Construct new text with clean spacing around the insertion
    before = text[:insert_at]
    after = text[insert_at:]
    if not before.endswith("\n"):
        before += "\n"
    # Ensure exactly one blank line before the insertion and let `insertion` end with two newlines
    if not before.endswith("\n\n"):
        before += "\n"

    new_text = before + insertion + after
    _write(new_text)
