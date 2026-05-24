"""
Inserts a bullet under the correct [Unreleased] subsection of CHANGELOG.md.

Usage:
    python update_changelog.py --section Added --title "Short description"

The script is idempotent for exact duplicates and a no-op if neither
--section nor --title are provided (allows safe invocation from CI when
a PR has no changelog label).
"""

import argparse
import re
import sys
from pathlib import Path

CHANGELOG = Path("CHANGELOG.md")

VALID_SECTIONS = {"Added", "Changed", "Fixed", "Removed", "Security"}

UNRELEASED_HEADER = re.compile(r"^## \[Unreleased\]", re.MULTILINE)
SUBSECTION_HEADER = re.compile(r"^### (.+)$", re.MULTILINE)
RELEASE_HEADER = re.compile(r"^## \[\d", re.MULTILINE)


def load() -> str:
    return CHANGELOG.read_text(encoding="utf-8")


def save(text: str) -> None:
    CHANGELOG.write_text(text, encoding="utf-8", newline="\n")


def insert_bullet(text: str, section: str, bullet: str) -> str:
    """Insert bullet under the named subsection inside [Unreleased]."""
    unreleased_match = UNRELEASED_HEADER.search(text)
    if not unreleased_match:
        sys.exit("ERROR: No [Unreleased] section found in CHANGELOG.md")

    unreleased_start = unreleased_match.end()

    # Find where [Unreleased] ends (next ## release header, or EOF)
    next_release = RELEASE_HEADER.search(text, unreleased_start)
    unreleased_end = next_release.start() if next_release else len(text)
    unreleased_block = text[unreleased_start:unreleased_end]

    # Look for the target subsection inside [Unreleased]
    sub_pattern = re.compile(rf"^### {re.escape(section)}$", re.MULTILINE)
    sub_match = sub_pattern.search(unreleased_block)

    bullet_line = f"- {bullet}"

    if sub_match:
        # Find the next subsection or end of [Unreleased]
        next_sub = SUBSECTION_HEADER.search(unreleased_block, sub_match.end())
        if next_sub:
            insert_pos = unreleased_start + next_sub.start()
            # Place bullet before the blank line that precedes the next subsection
            insert_text = bullet_line + "\n"
            return text[:insert_pos] + insert_text + text[insert_pos:]
        else:
            insert_pos = unreleased_end
            insert_text = bullet_line + "\n"
            # Ensure there's a trailing newline before EOF/next release
            return text[:insert_pos].rstrip("\n") + "\n" + insert_text + "\n" + text[insert_pos:]
    else:
        # Subsection doesn't exist — create it at the end of [Unreleased]
        insert_pos = unreleased_end
        new_block = f"\n### {section}\n{bullet_line}\n"
        return text[:insert_pos].rstrip("\n") + "\n" + new_block + "\n" + text[insert_pos:]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", default="")
    parser.add_argument("--title", default="")
    args = parser.parse_args()

    if not args.section or not args.title:
        print("No changelog section/title provided — skipping.")
        return

    if args.section not in VALID_SECTIONS:
        sys.exit(f"ERROR: invalid section '{args.section}' (choose from {sorted(VALID_SECTIONS)})")

    text = load()
    bullet = args.title.strip()

    # Idempotency: skip if bullet already present
    if f"- {bullet}" in text:
        print("Bullet already present — skipping.")
        return

    updated = insert_bullet(text, args.section, bullet)
    save(updated)
    print(f"Inserted under ### {args.section}: {bullet}")


if __name__ == "__main__":
    main()
