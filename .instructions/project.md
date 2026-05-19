# Planogram — Project Instructions

## Changelog

This project follows the [Keep a Changelog](https://keepachangelog.com) format and [Semantic Versioning](https://semver.org).

### Unreleased Section

Keep an `Unreleased` section at the top to track upcoming changes.

This serves two purposes:

- People can see what changes they might expect in upcoming releases.
- At release time, you can move the `Unreleased` section changes into a new release version section.

### Guiding Principles

- Changelogs are for humans, not machines.
- There should be an entry for every single version.
- The same types of changes should be grouped.
- Versions and sections should be linkable.
- The latest version comes first.
- The release date of each version is displayed.
- Mention whether you follow Semantic Versioning.

### Types of Changes

- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Deprecated** for soon-to-be removed features.
- **Removed** for now removed features.
- **Fixed** for any bug fixes.
- **Security** in case of vulnerabilities.

## SCSS Compilation

IntelliJ's file watcher automatically compiles SCSS on save. Do not run `sass` commands manually.

## Dependency Formatting (`pyproject.toml`)

Use `>=` with a space between the package name and version.

```toml
"pydantic >= 2.13.4",
"pillow >= 12.2.0",
```

- No parentheses around the version specifier.
- Trailing comma on the last entry.
