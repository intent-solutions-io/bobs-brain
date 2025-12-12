# Bob's Brain Versioning & Tagging Playbook

**Date:** 2025-12-12
**Type:** Runbook
**Audience:** Maintainers, Release Engineers

## Overview

This playbook documents versioning and tagging rules for Bob's Brain and serves as a reusable pattern for other IAM department repositories.

## Versioning Rules

### Semantic Versioning (SemVer)

All versions follow [SemVer 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

- MAJOR: Breaking changes to agent contracts or APIs
- MINOR: New features, backward compatible
- PATCH: Bug fixes, documentation updates
```

### Version Sources

| Source | Format | Example |
|--------|--------|---------|
| `VERSION` file | X.Y.Z | `0.14.1` |
| Git tags | vX.Y.Z | `v0.14.1` |
| CHANGELOG.md | vX.Y.Z | `## v0.14.1` |

**Single Source of Truth:** `VERSION` file

### Tag Format

- **Required:** `v` prefix + SemVer
- **Examples:** `v0.14.1`, `v1.0.0`
- **Annotated tags:** Recommended for releases

## How to Bump Versions

### 1. Determine Version Bump Type

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking API change | MAJOR | 0.14.1 → 1.0.0 |
| New feature (backward compatible) | MINOR | 0.14.1 → 0.15.0 |
| Bug fix, docs, refactor | PATCH | 0.14.1 → 0.14.2 |

### 2. Update VERSION File

```bash
# Check current version
cat VERSION
# Output: 0.14.1

# Update to new version
echo "0.14.2" > VERSION
```

### 3. Update CHANGELOG.md

Add a new section at the top:

```markdown
## v0.14.2 (2025-12-12)

### Fixed
- Fixed bug in XYZ component

### Changed
- Updated documentation for ABC
```

### 4. Commit Changes

```bash
git add VERSION CHANGELOG.md
git commit -m "chore(release): bump version to v0.14.2"
```

### 5. Create Annotated Tag

```bash
git tag -a v0.14.2 -m "Release v0.14.2"
```

### 6. Push Tag

```bash
git push origin v0.14.2
```

## Validation Script

### Running the Check

```bash
# Basic check
python scripts/check_versioning.py

# Verbose output
python scripts/check_versioning.py --verbose
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | VERSION file malformed or missing |
| 2 | Version regression detected |

### Example Output (Success)

```
🔍 Phase 37: Checking versioning and tag guardrails...

📄 VERSION file: 0.14.2
✅ Valid SemVer: 0.14.2
📌 Highest existing tag: v0.14.1

✅ VERSION (0.14.2) > highest tag (v0.14.1)
   Ready to create new tag: v0.14.2
```

### Example Output (Regression)

```
🔍 Phase 37: Checking versioning and tag guardrails...

📄 VERSION file: 0.14.0
✅ Valid SemVer: 0.14.0
📌 Highest existing tag: v0.14.1

❌ FAIL: VERSION (0.14.0) < highest tag (v0.14.1)
   Version regression detected!
   Bump VERSION before creating new release.
```

## CI Integration

The versioning check runs in CI:

```yaml
- name: Check versioning and tags (Phase 37)
  run: python scripts/check_versioning.py
```

**Behavior:**
- Runs on push to main
- Non-blocking if git tags unavailable (shallow clone)
- Fails if VERSION malformed or regression detected

## Adapting for Other Repos

### Copy Pattern

1. Copy `VERSION` file
2. Copy `scripts/check_versioning.py`
3. Add CI job as shown above
4. Copy this runbook and adapt

### What to Customize

| Item | Customization |
|------|---------------|
| VERSION file | Set initial version (e.g., `0.1.0`) |
| CHANGELOG.md | Create with initial entries |
| CI workflow | Adjust job name/triggers |

### Template Starting Version

For new IAM department repos:
- Start at `0.1.0`
- First production release: `1.0.0`

## Troubleshooting

### "VERSION file not found"

```bash
# Create VERSION file
echo "0.1.0" > VERSION
git add VERSION
git commit -m "chore: add VERSION file"
```

### "Version regression detected"

```bash
# Check current highest tag
git tag --list 'v*' | sort -V | tail -1

# Bump VERSION higher than that tag
```

### "Could not inspect git tags"

This happens in shallow clones (CI):
- The script validates format only
- Tags are checked when available

To fetch tags in CI:
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full clone with tags
```

## Release Checklist

- [ ] All tests passing
- [ ] CHANGELOG.md updated
- [ ] VERSION file bumped
- [ ] `python scripts/check_versioning.py` passes
- [ ] PR merged to main
- [ ] Tag created and pushed
- [ ] GitHub release created (optional)

## See Also

- `VERSION` - Current version file
- `CHANGELOG.md` - Release notes
- `scripts/check_versioning.py` - Validation script
- [SemVer 2.0.0 Specification](https://semver.org/)

---
**Last Updated:** 2025-12-12
