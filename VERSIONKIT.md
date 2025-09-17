# Versioning Toolkit

This repository includes a small, opinionated **version bumper** that enforces **PEP 440** canonical versioning while 
following **Semantic Versioning (SemVer)** for the release part. It reads the current version from common 
sources, bumps or sets a new version, and optionally inserts a `## <version>` section in `CHANGELOG.md`.

## Overview

- `bump_version.py` — A convenience entry point so you can run `python bump_version.py …` without installing a package.
- `cli.py` — The command‑line interface (CLI). Parses commands, orchestrates I/O and spec helpers.
- `io.py` — Reads and writes the version in your project files (`pyproject.toml`, `setup.cfg`, or `version.txt`).
- `spec.py` — Validates and builds versions using **PEP 440** rules (via `packaging.Version`) and offers SemVer‑style bump helpers.
- `changelog.py` — Ensures your `CHANGELOG.md` has a `## <version>` header for the target version (adds it if missing).

> TL;DR: You run a command → CLI reads the version (I/O) → validates/normalizes (spec) → writes it back (I/O) → updates CHANGELOG (changelog).

## Setup

- Python 3.10+ recommended.
- `packaging` library (PEP 440 parsing/normalization).
- If you keep your version in `pyproject.toml`, you’ll need a TOML parser:
  - Python 3.11+: built‑in `tomllib` works out of the box.
  - Python ≤3.10: install `tomli` (read‑only) or `tomli-w`/`tomlkit` if writing is required by your setup.

Install dependencies (example):
```bash
pip install packaging tomli
```

## Version Sources

The tool looks in this order and writes back to the same place it read from (or the first writable location if you use 
`set` without a prior read context):

1. **`pyproject.toml`**
   - `[project].version = "1.2.3"` **or**
   - `[tool.poetry].version = "1.2.3"`
2. **`setup.cfg`**
   ```ini
   [metadata]
   version = 1.2.3
   ```
3. **`version.txt`** — a single line like `1.2.3`

> **Tip:** Keep exactly **one** authoritative source in your repo to avoid confusion.

## Usage

You can invoke the CLI in two ways:

- **Repo script (recommended for local use)**
  ```bash
  python bump_version.py <command> [options]
  ```

- **Module form** (if packaged / importable)
  ```bash
  python -m versionkit.cli <command> [options]
  ```

Run `-h` for help:
```bash
python bump_version.py -h
```

## Commands Overview

### Check
Validate the currently detected version is **canonical PEP 440** (no `+local` segment, normalized spelling).
```bash
python bump_version.py check
```
- Exits non‑zero on invalid/non‑canonical versions.
- Does not modify files.

### Set
Set an **exact** canonical PEP 440 version.
```bash
python bump_version.py set 2.1.0
python bump_version.py set 2.1.0 --dry-run   # preview only
```
- Writes back to the detected source.
- Ensures a `## 2.1.0` header exists in `CHANGELOG.md` (unless `--dry-run`).

**Valid examples:** `1.2.3`, `1.2.3a1`, `1.2.3b2`, `1.2.3rc1`, `1.2.3.dev4`, `1.2.3.post1`, `1.2` (treated as `1.2`).

### Finalize
Strip any pre/dev/post tags, keeping just the final release.
```bash
# 2.1.0rc3 -> 2.1.0
# 2.1.0.dev4 -> 2.1.0
python bump_version.py finalize
```

### Bump
SemVer‑style bump of the release number; clears pre/dev/post.
```bash
python bump_version.py bump major   # 1.4.2 -> 2.0.0
python bump_version.py bump minor   # 1.4.2 -> 1.5.0
python bump_version.py bump patch   # 1.4.2 -> 1.4.3
```

### Prerelease
Start or bump a pre‑release series for the current base (`a`=alpha, `b`=beta, `rc`=release candidate).
```bash
python bump_version.py prerelease a        # 1.2.3 -> 1.2.3a1 (or a2 if already alpha)
python bump_version.py prerelease rc       # 1.2.3 -> 1.2.3rc1
python bump_version.py prerelease b --start  # force start at b1
```

### Dev Releases
Set or bump the development release number, preserving any pre‑release tag.
```bash
python bump_version.py dev           # set .dev1 (or keep existing dev)
python bump_version.py dev --bump    # increment .devN
python bump_version.py dev --set 7   # set .dev7
```

### Post Releases
Manage post releases for metadata fixes/repackaging after a final.
```bash
python bump_version.py post          # set .post1 (or keep existing post)
python bump_version.py post --bump   # increment .postN
python bump_version.py post --set 2  # set .post2
```

## Workflows

### Pre-release workflow
```bash
# Start prerelease
python bump_version.py bump minor         # 1.4.2 -> 1.5.0
python bump_version.py prerelease rc      # 1.5.0 -> 1.5.0rc1

# Iterate as needed
python bump_version.py prerelease rc      # rc1 -> rc2
python bump_version.py dev --bump         # 1.5.0rc2 -> 1.5.0rc2.dev1

# Finalize
python bump_version.py finalize           # -> 1.5.0
```

### Patch workflow
```bash
python bump_version.py bump patch         # 1.5.0 -> 1.5.1
```

### Post‑release metadata fix
```bash
python bump_version.py post               # 1.5.0 -> 1.5.0.post1
```

## Changelog

When you produce a new version, the tool ensures `CHANGELOG.md` includes a section:

```md
## <version>

- _Describe changes here._
```

**Placement rules:**
- If your changelog starts with a top title (e.g., `# Changelog`), the section is inserted immediately below the title 
(and above older versions).
- If there’s no top title, the new section is appended to the end.
- Use `--dry-run` to preview insertion without writing.

If `CHANGELOG.md` doesn’t exist, the tool prints a note and continues without failing your command.


## PEP 440 vs. SemVer (how they play together)

- **PEP 440** defines the *syntax and ordering* for Python package versions. This tool **enforces canonical PEP 440** 
(e.g., `1.2.3rc1`, not `1.2.3-rc.1`).
- **SemVer** is a *release discipline* you follow for `major.minor.patch`. The `bump` command implements exactly that behavior.
- Combine them: use SemVer for the base (`X.Y.Z`) while PEP 440 handles pre/dev/post segments.

**Examples (valid PEP 440):**
- Final: `2.3.0`
- Pre: `2.3.0a1`, `2.3.0b1`, `2.3.0rc2`
- Dev: `2.3.0.dev1`, `2.3.0a1.dev2`
- Post: `2.3.0.post1`

> **Note:** `+local` segments are intentionally **not** allowed here: the tool normalizes to canonical public versions for distribution.

## Tips

- Keep a single authoritative version source to avoid drift.
- If you store the version in `pyproject.toml` and are on Python ≤3.10, ensure `tomli` is installed.
- The tool normalizes whatever you pass using `packaging.Version`. If your input isn’t canonical, it will either 
normalize or fail fast with a clear message.
- `--dry-run` is your friend when validating CI behavior before writing files.

## CI

```bash
# Validate version on CI
python bump_version.py check

# On a tagged release job, set the version to the tag (e.g., v1.8.0)
python bump_version.py set ${GITHUB_REF_NAME#v}
```

You can also restrict changes to release branches and run `finalize` before building wheels/sdist.

## Troubleshooting

- **“Can’t find a version in project files.”**  
  Ensure one of the supported files exists and contains a version in a supported location.
- **“TOML read/write errors.”**  
  Install `tomli` (for read) or use Python 3.11+ (`tomllib`). Make sure the version key is a *string*.
- **“Version not canonical / invalid.”**  
  Adjust to valid PEP 440 (e.g., `1.2.3rc1`, not `1.2.3-rc.1`). Pre/dev/post must follow PEP 440’s ordering rules.
- **Changelog isn't updated.**  
  Run without `--dry-run`. Confirm file name is exactly `CHANGELOG.md` and that the repository permissions allow writing.

## Examples

```bash
# Inspect
python bump_version.py check

# Set exact versions
python bump_version.py set 1.0.0
python bump_version.py set 1.1.0rc1 --dry-run

# Bumps
python bump_version.py bump major
python bump_version.py bump minor
python bump_version.py bump patch

# Pre/dev/post
python bump_version.py prerelease a
python bump_version.py prerelease rc --start
python bump_version.py dev --bump
python bump_version.py post --set 3

# Finalize
python bump_version.py finalize
```

## Project Blurb (Optional)

> This project adheres to PEP 440 for version syntax and uses Semantic Versioning to guide breaking changes and release 
> increments. Versions are validated and normalized with `packaging.Version`, and the tool can maintain a matching 
> `## <version>` section in the changelog.
