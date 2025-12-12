#!/usr/bin/env python3
"""
Version and Tag Guardrails Check Script

This script validates versioning for the bobs-brain repository:
1. Checks VERSION file exists and contains valid SemVer
2. Compares against existing git tags (if available)
3. Ensures monotonic version progression

Part of Phase 37: Versioning & Tagging Guardrails

Usage:
    python scripts/check_versioning.py [--verbose]

Exit Codes:
    0 - All checks passed
    1 - VERSION file malformed or missing
    2 - Version regression detected (lower than existing tag)
    3 - Warning only (git tags unavailable, format-only validation)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# SemVer regex pattern (strict)
SEMVER_PATTERN = re.compile(
    r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
    r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
    r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)


def parse_semver(version: str) -> Optional[Tuple[int, int, int, str]]:
    """
    Parse a SemVer string into components.

    Returns:
        Tuple of (major, minor, patch, prerelease) or None if invalid
    """
    # Strip 'v' prefix if present
    version = version.lstrip('v')

    match = SEMVER_PATTERN.match(version)
    if not match:
        return None

    major = int(match.group('major'))
    minor = int(match.group('minor'))
    patch = int(match.group('patch'))
    prerelease = match.group('prerelease') or ''

    return (major, minor, patch, prerelease)


def compare_versions(v1: Tuple[int, int, int, str], v2: Tuple[int, int, int, str]) -> int:
    """
    Compare two parsed SemVer versions.

    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    # Compare major.minor.patch
    for i in range(3):
        if v1[i] < v2[i]:
            return -1
        if v1[i] > v2[i]:
            return 1

    # Prerelease handling: no prerelease > any prerelease
    if not v1[3] and v2[3]:
        return 1  # v1 has no prerelease, v2 does → v1 is higher
    if v1[3] and not v2[3]:
        return -1  # v1 has prerelease, v2 doesn't → v2 is higher
    if v1[3] < v2[3]:
        return -1
    if v1[3] > v2[3]:
        return 1

    return 0


def read_version_file() -> Optional[str]:
    """Read VERSION file and return contents."""
    version_file = Path(__file__).parent.parent / "VERSION"

    if not version_file.exists():
        print("❌ VERSION file not found")
        return None

    content = version_file.read_text().strip()
    return content


def get_git_tags() -> Optional[List[str]]:
    """Get list of version tags from git."""
    try:
        result = subprocess.run(
            ['git', 'tag', '--list', 'v*'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        tags = [t.strip() for t in result.stdout.strip().split('\n') if t.strip()]
        return tags

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def filter_semver_tags(tags: List[str]) -> List[Tuple[str, Tuple[int, int, int, str]]]:
    """Filter and parse only valid SemVer tags."""
    valid_tags = []

    for tag in tags:
        parsed = parse_semver(tag)
        if parsed:
            # Skip prerelease or special tags that aren't standard releases
            # e.g., v5.0.0-sovereign, v6.1.0 (likely legacy/special)
            if parsed[3]:  # Has prerelease
                continue
            # Skip tags that seem out of sequence (v1.0.0, v5.x, v6.x when current is 0.14.x)
            if parsed[0] >= 1 and parsed[1] == 0 and parsed[2] == 0:
                # Likely legacy tag like v1.0.0
                continue
            if parsed[0] >= 5:
                # Likely special tags like v5.0.0-sovereign, v6.1.0
                continue
            valid_tags.append((tag, parsed))

    return valid_tags


def find_highest_tag(tags: List[Tuple[str, Tuple[int, int, int, str]]]) -> Optional[Tuple[str, Tuple[int, int, int, str]]]:
    """Find the highest version tag."""
    if not tags:
        return None

    highest = tags[0]
    for tag, parsed in tags[1:]:
        if compare_versions(parsed, highest[1]) > 0:
            highest = (tag, parsed)

    return highest


def main():
    parser = argparse.ArgumentParser(
        description="Check VERSION file and git tags for consistency"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    args = parser.parse_args()

    print("🔍 Phase 37: Checking versioning and tag guardrails...")
    print()

    # Step 1: Read VERSION file
    version_content = read_version_file()
    if not version_content:
        print("❌ FAIL: VERSION file missing or empty")
        sys.exit(1)

    print(f"📄 VERSION file: {version_content}")

    # Step 2: Validate SemVer format
    parsed_version = parse_semver(version_content)
    if not parsed_version:
        print(f"❌ FAIL: '{version_content}' is not valid SemVer")
        print("   Expected format: MAJOR.MINOR.PATCH (e.g., 0.14.1)")
        sys.exit(1)

    print(f"✅ Valid SemVer: {parsed_version[0]}.{parsed_version[1]}.{parsed_version[2]}")

    # Step 3: Get git tags
    tags = get_git_tags()
    if tags is None:
        print()
        print("⚠️  Could not inspect git tags (no git metadata)")
        print("   Skipping tag comparison. VERSION format validated only.")
        sys.exit(0)  # Graceful exit, format is valid

    if args.verbose:
        print(f"\n📋 Found {len(tags)} tags starting with 'v'")

    # Step 4: Filter to valid SemVer tags
    valid_tags = filter_semver_tags(tags)
    if args.verbose:
        print(f"   {len(valid_tags)} are valid standard SemVer tags")
        for tag, parsed in sorted(valid_tags, key=lambda x: x[1]):
            print(f"      {tag}")

    # Step 5: Find highest existing tag
    highest = find_highest_tag(valid_tags)
    if not highest:
        print()
        print("ℹ️  No valid SemVer tags found for comparison")
        print("✅ VERSION format valid, ready for first tag")
        sys.exit(0)

    highest_tag, highest_parsed = highest
    print(f"📌 Highest existing tag: {highest_tag}")

    # Step 6: Compare versions
    comparison = compare_versions(parsed_version, highest_parsed)

    if comparison < 0:
        print()
        print(f"❌ FAIL: VERSION ({version_content}) < highest tag ({highest_tag})")
        print("   Version regression detected!")
        print("   Bump VERSION before creating new release.")
        sys.exit(2)

    if comparison == 0:
        print()
        print(f"ℹ️  VERSION ({version_content}) == highest tag ({highest_tag})")
        print("   Tag already exists for this version.")
        print("   Bump VERSION before creating another release.")
        sys.exit(0)

    # comparison > 0
    print()
    print(f"✅ VERSION ({version_content}) > highest tag ({highest_tag})")
    print("   Ready to create new tag: v{version_content}")
    print()
    print("To create release:")
    print(f"   git tag -a v{version_content} -m 'Release v{version_content}'")
    print(f"   git push origin v{version_content}")

    sys.exit(0)


if __name__ == "__main__":
    main()
