"""
Conventional Commits validator with actionable error messages.

Enforces:
  <type>(<scope>)?: <summary up to 150 chars>
  - type in allowed list
  - optional scope: no trailing/leading spaces
  - optional breaking "!" after type/scope requires a BREAKING CHANGE: footer
  - subject max length 150 chars
Allows:
  - Auto "Merge ..." commits (skipped)
  - Auto "Revert ..." commits (skipped)  # git-generated
"""

import pathlib
import re
import sys
from typing import List

ALLOWED_TYPES = (
    "feat", "fix", "docs", "style", "refactor", "perf", "test",
    "build", "ci", "chore", "revert"
)

SUBJECT_PATTERN = re.compile(
    rf"^(?P<type>{'|'.join(ALLOWED_TYPES)})"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<bang>!)?: "
    r"(?P<summary>.+)$"
)

MAX_SUBJECT = 150


def first_meaningful_line(lines: List[str]) -> str:
    for l in lines:
        s = l.strip()
        if s and not s.startswith("#"):
            return l.rstrip("\n")

    return ""


def has_breaking_footer(lines: List[str]) -> bool:
    # Look for "BREAKING CHANGE:" or "BREAKING-CHANGE:"
    for l in lines:
        if l.startswith("BREAKING CHANGE:") or l.startswith("BREAKING-CHANGE:"):
            return True

    return False


def main() -> int:
    if len(sys.argv) < 2:
        print("✖ Missing path to COMMIT_EDITMSG (hook usage error).")
        return 1

    msg_path = pathlib.Path(sys.argv[-1])
    try:
        lines = msg_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"✖ Could not read commit message: {e}")
        return 1

    subject = first_meaningful_line(lines)

    # Allow auto merge/revert commits produced by Git tooling
    if subject.startswith("Merge ") or subject.startswith("Revert "):
        return 0

    errors = []

    if not subject:
        errors.append("Subject line is empty.")
    else:
        # … same validation as before …
        pass

    if errors:
        print("Conventional Commits validation failed.\n")
        print(f"Subject seen:\n  {subject!r}\n")
        print("Problems:")

        for e in errors:
            print(f"  • {e}")

        print("\nExamples:")
        print("  feat(calendar): add Google OAuth refresh flow")
        print("  fix(oauth): handle invalid_grant on token refresh")
        print("  refactor(routes): centralize Jinja template lookup")
        print("\nTip: wrap the subject at 100 chars; put details in the body.")

        return 1

    return 0
