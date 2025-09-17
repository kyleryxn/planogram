from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Lazy toml loading to avoid hard dependency when not needed
try:
    import tomllib as tomli  # py311+
except Exception:
    try:
        import tomli  # type: ignore
    except Exception:
        tomli = None  # type: ignore


@dataclass(frozen=True)
class VersionSource:
    name: str
    path: Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
SETUP_CFG = ROOT / "setup.cfg"
VERSION_TXT = ROOT / "version.txt"
CHANGELOG = ROOT / "CHANGELOG.md"


def _read_version_from_pyproject() -> str | None:
    if not PYPROJECT.exists() or tomli is None:
        return None
    data = tomli.loads(PYPROJECT.read_text(encoding="utf-8"))
    v = (data.get("project", {}) or {}).get("version")
    if v:
        return v
    return (data.get("tool", {}) or {}).get("poetry", {}).get("version")


def _write_version_to_pyproject(new_version: str) -> bool:
    if not PYPROJECT.exists():
        return False
    text = PYPROJECT.read_text(encoding="utf-8")

    def replace_in_section(section_header: str, pattern: str) -> tuple[str, bool]:
        lines = text.splitlines()
        out, in_section, replaced = [], False, False
        for line in lines:
            if line.strip() == f"[{section_header}]":
                in_section = True
                out.append(line)
                continue
            if line.startswith("[") and line.strip() != f"[{section_header}]":
                in_section = False
            if in_section:
                new_line, n = re.subn(pattern, f'\\1"{new_version}"', line)
                if n:
                    out.append(new_line); replaced = True; continue
            out.append(line)
        return ("\n".join(out) + ("\n" if not text.endswith("\n") else "")), replaced

    # [project]
    new_text, replaced = replace_in_section("project", r'^(\s*version\s*=\s*)"(.*?)"\s*$')
    text = new_text

    # [tool.poetry]
    if not replaced:
        new_text, replaced = replace_in_section("tool.poetry", r'^(\s*version\s*=\s*)"(.*?)"\s*$')
        text = new_text

    if replaced:
        PYPROJECT.write_text(text, encoding="utf-8")
    return replaced


def _read_version_from_setup_cfg() -> str | None:
    if not SETUP_CFG.exists():
        return None
    m = re.search(r'(?mi)^\s*version\s*=\s*([^\s#]+)', SETUP_CFG.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def _write_version_to_setup_cfg(new_version: str) -> bool:
    if not SETUP_CFG.exists():
        return False
    txt = SETUP_CFG.read_text(encoding="utf-8")
    new_txt, n = re.subn(r'(?mi)^(\s*version\s*=\s*)([^\s#]+)', rf'\1{new_version}', txt, count=1)
    if n:
        SETUP_CFG.write_text(new_txt, encoding="utf-8")
        return True
    return False


def _read_version_from_version_txt() -> str | None:
    if VERSION_TXT.exists():
        return VERSION_TXT.read_text(encoding="utf-8").strip() or None
    return None


def _write_version_to_version_txt(new_version: str) -> bool:
    VERSION_TXT.write_text(new_version + "\n", encoding="utf-8")
    return True


def get_version() -> tuple[str, VersionSource]:
    for reader, src in (
        (_read_version_from_pyproject, VersionSource("pyproject", PYPROJECT)),
        (_read_version_from_setup_cfg, VersionSource("setup.cfg", SETUP_CFG)),
        (_read_version_from_version_txt, VersionSource("version.txt", VERSION_TXT)),
    ):
        v = reader()
        if v:
            return v, src
    raise SystemExit("ERROR: Could not find version in pyproject.toml, setup.cfg, or version.txt")


def set_version(new_version: str, source_hint: VersionSource | None) -> None:
    # Try hint first, then others
    order: list[VersionSource] = []
    if source_hint:
        order.append(source_hint)
    for src in (VersionSource("pyproject", PYPROJECT),
                VersionSource("setup.cfg", SETUP_CFG),
                VersionSource("version.txt", VERSION_TXT)):
        if not order or src.name != (order[0].name if order else ""):
            order.append(src)

    for src in order:
        ok = False
        if src.name == "pyproject":
            ok = _write_version_to_pyproject(new_version)
        elif src.name == "setup.cfg":
            ok = _write_version_to_setup_cfg(new_version)
        elif src.name == "version.txt":
            ok = _write_version_to_version_txt(new_version)
        if ok:
            return
    raise SystemExit("ERROR: Failed to write new version to any known source.")
