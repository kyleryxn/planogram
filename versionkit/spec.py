from __future__ import annotations

from packaging.version import Version, InvalidVersion


def parse_canonical(v: str) -> Version:
    try:
        parsed = Version(v)
    except InvalidVersion as e:
        raise SystemExit(f"ERROR: '{v}' is not PEP 440 compliant: {e}")
    canonical = str(parsed)
    if canonical != v:
        raise SystemExit(f"ERROR: '{v}' is not canonical PEP 440 form. Use '{canonical}'.")
    if parsed.local:
        raise SystemExit(f"ERROR: Local versions '+{parsed.local}' are not allowed for public releases.")
    return parsed


def ensure_semver_base(parsed: Version) -> tuple[int, ...]:
    parts = list(parsed.release)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])  # (major, minor, patch)


def build_version(
    parts: tuple[int, int, int],
    pre: tuple[str, int] | None = None,
    post: int | None = None,
    dev: int | None = None,
) -> str:
    major, minor, patch = parts
    s = f"{major}.{minor}.{patch}"
    if pre:
        tag, n = pre
        s += f"{tag}{n}"
    if post is not None:
        s += f".post{post}"
    if dev is not None:
        s += f".dev{dev}"
    # Normalize through packaging
    return str(Version(s))


def bump_release_part(parsed: Version, part: str) -> str:
    major, minor, patch = ensure_semver_base(parsed)
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    elif part == "patch":
        patch += 1
    else:
        raise SystemExit("Invalid part; choose major/minor/patch")
    return build_version((major, minor, patch), pre=None, post=None, dev=None)
