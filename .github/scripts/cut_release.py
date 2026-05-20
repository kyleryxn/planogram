"""
Converts the [Unreleased] section into a versioned release section and
creates a fresh empty [Unreleased] above it.

Usage:
    python cut_release.py --version 1.2.3

The date is injected automatically as today's UTC date (YYYY-MM-DD).
Exits with an error if there is no content under [Unreleased] (nothing to release).
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CHANGELOG = Path("CHANGELOG.md")

UNRELEASED_HEADER = re.compile(r"^## \[Unreleased\]\n", re.MULTILINE)
RELEASE_HEADER = re.compile(r"^## \[\d", re.MULTILINE)

EMPTY_UNRELEASED = "## [Unreleased]\n"


def load() -> str:
    return CHANGELOG.read_text(encoding="utf-8")


def save(text: str) -> None:
    CHANGELOG.write_text(text, encoding="utf-8", newline="\n")


def cut(text: str, version: str, date: str) -> str:
    unreleased_match = UNRELEASED_HEADER.search(text)
    if not unreleased_match:
        sys.exit("ERROR: No [Unreleased] section found in CHANGELOG.md")

    unreleased_start = unreleased_match.start()
    body_start = unreleased_match.end()

    next_release = RELEASE_HEADER.search(text, body_start)
    body_end = next_release.start() if next_release else len(text)

    body = text[body_start:body_end]

    if not body.strip():
        sys.exit("ERROR: [Unreleased] section is empty — nothing to release.")

    release_header = f"## [{version}] - {date}\n"
    new_text = (
        text[:unreleased_start]
        + EMPTY_UNRELEASED
        + "\n"
        + release_header
        + body
        + text[body_end:]
    )
    return new_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, help="Semantic version, e.g. 1.2.3")
    args = parser.parse_args()

    version = args.version.lstrip("v")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    text = load()
    updated = cut(text, version, date)
    save(updated)
    print(f"Cut release [{version}] - {date}")


if __name__ == "__main__":
    main()
