from __future__ import annotations

import argparse

from .changelog import ensure_changelog_has_version
from .io import get_version, set_version
from .spec import parse_canonical, ensure_semver_base, build_version, bump_release_part


def _cmd_check(args):
    v, _src = get_version()
    parsed = parse_canonical(v)
    print(f"OK: version '{parsed}' is canonical PEP 440 (no local segment).")


def _cmd_set(args):
    target = args.version.strip()
    parsed = parse_canonical(target)
    if not args.dry_run:
        set_version(str(parsed), source_hint=None)
        ensure_changelog_has_version(str(parsed), args.dry_run)
    print(str(parsed))


def _cmd_finalize(args):
    v, src = get_version()
    p = parse_canonical(v)
    major, minor, patch = ensure_semver_base(p)
    new = build_version((major, minor, patch), pre=None, post=None, dev=None)
    if args.dry_run:
        print(new); return
    set_version(new, source_hint=src)
    ensure_changelog_has_version(new, args.dry_run)
    print(new)


def _cmd_bump(args):
    v, src = get_version()
    p = parse_canonical(v)
    new = bump_release_part(p, args.part)
    if args.dry_run:
        print(new); return
    set_version(new, source_hint=src)
    ensure_changelog_has_version(new, args.dry_run)
    print(new)


def _cmd_prerelease(args):
    v, src = get_version()
    p = parse_canonical(v)
    major, minor, patch = ensure_semver_base(p)

    tag = args.tag  # 'a', 'b', or 'rc'
    current = p.pre  # ('a', 1) / ('b', 2) / ('rc', 1) / None

    if args.start:
        new = build_version((major, minor, patch), pre=(tag, 1), post=None, dev=None)
    else:
        if current and current[0] == tag:
            new = build_version((major, minor, patch), pre=(tag, current[1] + 1), post=None, dev=None)
        else:
            new = build_version((major, minor, patch), pre=(tag, 1), post=None, dev=None)

    if args.dry_run:
        print(new); return
    set_version(new, source_hint=src)
    ensure_changelog_has_version(new, args.dry_run)
    print(new)


def _cmd_dev(args):
    v, src = get_version()
    p = parse_canonical(v)
    major, minor, patch = ensure_semver_base(p)
    dev_n = p.dev

    if args.set is not None:
        if args.set < 0:
            raise SystemExit("dev number must be >= 0")
        new = build_version((major, minor, patch), pre=p.pre, post=None, dev=args.set)
    elif args.bump:
        new = build_version((major, minor, patch), pre=p.pre, post=None, dev=(dev_n + 1 if dev_n else 1))
    else:
        new = build_version((major, minor, patch), pre=p.pre, post=None, dev=(dev_n or 1))

    if args.dry_run:
        print(new); return
    set_version(new, source_hint=src)
    ensure_changelog_has_version(new, args.dry_run)
    print(new)


def _cmd_post(args):
    v, src = get_version()
    p = parse_canonical(v)
    major, minor, patch = ensure_semver_base(p)
    post_n = p.post

    if args.set is not None:
        if args.set < 0:
            raise SystemExit("post number must be >= 0")
        new = build_version((major, minor, patch), pre=None, post=args.set, dev=None)
    elif args.bump:
        new = build_version((major, minor, patch), pre=None, post=(post_n + 1 if post_n else 1), dev=None)
    else:
        new = build_version((major, minor, patch), pre=None, post=(post_n or 1), dev=None)

    if args.dry_run:
        print(new); return
    set_version(new, source_hint=src)
    ensure_changelog_has_version(new, args.dry_run)
    print(new)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bump version (SemVer discipline, PEP 440 encoding)."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("check", help="Validate current version (PEP 440 canonical, no +local).")
    s.set_defaults(func=_cmd_check)

    s = sub.add_parser("set", help="Set exact version (must be canonical PEP 440).")
    s.add_argument("version")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_set)

    s = sub.add_parser("finalize", help="Strip any pre/dev/post to finalize a release.")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_finalize)

    s = sub.add_parser("bump", help="Bump release part and clear pre/dev/post.")
    s.add_argument("part", choices=["major", "minor", "patch"])
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_bump)

    s = sub.add_parser("prerelease", help="Start or bump a pre-release (a/b/rc).")
    s.add_argument("tag", choices=["a", "b", "rc"], help="alpha/beta/rc")
    s.add_argument("--start", action="store_true", help="Start at <tag>1 regardless of current pre.")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_prerelease)

    s = sub.add_parser("dev", help="Set or bump a dev release (.devN).")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--set", type=int, help="Set dev number to N.")
    g.add_argument("--bump", action="store_true", help="Increment dev number.")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_dev)

    s = sub.add_parser("post", help="Set or bump a post release (.postN).")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--set", type=int, help="Set post number to N.")
    g.add_argument("--bump", action="store_true", help="Increment post number.")
    s.add_argument("--dry-run", action="store_true")
    s.set_defaults(func=_cmd_post)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
