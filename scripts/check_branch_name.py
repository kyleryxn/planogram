import re
import subprocess
import sys

# Patterns for allowed branch names
POLICIES = [
    re.compile(r"^(feat|fix|chore|docs|refactor|test|perf|build|ci)/[A-Za-z0-9._-]+$"),
    re.compile(r"^release/\d+\.\d+(\.\d+)?$"),  # e.g. release/1.2 or release/1.2.3
    re.compile(r"^hotfix/[A-Za-z0-9._-]+$"),  # e.g. hotfix/critical-bug
]

# Branches always allowed
EXEMPT = {"main", "master", "develop"}


def get_branch() -> str:
    out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out.decode().strip()


def matches_policy(branch: str) -> bool:
    return any(p.match(branch) for p in POLICIES)


def main() -> int:
    branch = get_branch()

    if branch in ("HEAD", ""):
        # Detached HEAD (e.g. CI checkout)
        return 0

    if branch in EXEMPT:
        return 0

    if not matches_policy(branch):
        print(f"Branch '{branch}' does not match policy.")
        print("\nAllowed formats:")
        print("  feat/<ticket-or-scope>-<slug>")
        print("  fix/<ticket-or-scope>-<slug>")
        print("  chore/<ticket-or-scope>-<slug>")
        print("  docs/<ticket-or-scope>-<slug>")
        print("  refactor/<ticket-or-scope>-<slug>")
        print("  test/<ticket-or-scope>-<slug>")
        print("  perf/<ticket-or-scope>-<slug>")
        print("  build/<ticket-or-scope>-<slug>")
        print("  ci/<ticket-or-scope>-<slug>")
        print("  release/<major>.<minor>[.<patch>]")
        print("  hotfix/<slug>")
        print("\nExempt branches:")
        print("  main, master, develop")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
