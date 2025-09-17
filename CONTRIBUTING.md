# Contributing

Thank you for considering contributing to this project!

## Release & Versioning

This project uses [Semantic Versioning](https://semver.org/) (SemVer) for release discipline and encodes versions according to 
[PyPA Version Specifiers](https://packaging.python.org/specifications/version-specifiers/) 
(successor to [PEP 440](https://peps.python.org/pep-0440/)).

### Version number format

```
MAJOR.MINOR.PATCH[{aN|bN|rcN}][.postN][.devN]
```

- **MAJOR**: Increment for incompatible API changes (breaking changes).
- **MINOR**: Increment for added functionality in a backwards-compatible manner.
- **PATCH**: Increment for backwards-compatible bug fixes.

### Pre-releases
- `aN` → alpha (e.g. `2.0.0a1`)
- `bN` → beta (e.g. `2.0.0b2`)
- `rcN` → release candidate (e.g. `2.0.0rc1`)

### Post-releases
- `.postN` → republished release with no code changes (e.g. packaging fixes).
  - Example: `1.4.0.post1`

### Development releases
- `.devN` → development snapshots before the next planned release.
  - Example: `1.5.0.dev3`

### Local versions
- `+local` → only for internal builds (never uploaded to PyPI).
  - Example: `1.5.0+exp.sha.5114f85`

### Practical rules
- Follow SemVer for deciding **what** to bump.
- Encode in PEP 440 style so packaging tools (`pip`, `setuptools`, etc.) can parse and compare correctly.
- Never upload `+local` versions to PyPI.
- Update the **CHANGELOG.md** entry and tag the release in Git with the same version string.

### Examples

| Change type                | Example version |
|----------------------------|-----------------|
| Breaking API change        | `2.0.0`         |
| Backwards-compatible feat  | `1.5.0`         |
| Bug fix                    | `1.4.3`         |
| Alpha release              | `2.0.0a1`       |
| Release candidate          | `2.0.0rc1`      |
| Post release               | `1.4.0.post1`   |
| Dev snapshot               | `1.5.0.dev2`    |


When preparing a release, make sure to:
1. Update `CHANGELOG.md`.
2. Bump the version number in the project metadata (`pyproject.toml` or `setup.cfg`).
3. Commit the changes.
4. Tag the release in Git (`git tag vX.Y.Z`).
5. Push tags so that automated release workflows can pick them up.
