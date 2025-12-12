#!/usr/bin/env python3
"""
Export IAM Department Template

This script exports the IAM department template to a new directory
for use in creating new agent department repositories.

Part of Phase 38: Template Export & Reuse Guide

Usage:
    python scripts/export_iam_template.py /path/to/destination
    python scripts/export_iam_template.py /path/to/destination --force

Options:
    --force     Overwrite destination if it exists

Exit Codes:
    0 - Success
    1 - Destination already exists (use --force)
    2 - Copy failed
"""

import argparse
import shutil
import sys
from pathlib import Path


# Patterns to exclude from export
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '.DS_Store',
    '*.egg-info',
    '.pytest_cache',
    '.mypy_cache',
    '.coverage',
    'htmlcov',
    '*.log',
]


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from export."""
    name = path.name

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            # Suffix match
            if name.endswith(pattern[1:]):
                return True
        else:
            # Exact match
            if name == pattern:
                return True

    return False


def copy_template(source: Path, destination: Path) -> int:
    """
    Copy template directory to destination.

    Args:
        source: Path to template directory
        destination: Path to destination directory

    Returns:
        Number of files copied
    """
    files_copied = 0

    for src_path in source.rglob('*'):
        # Skip excluded patterns
        if any(should_exclude(p) for p in src_path.parents) or should_exclude(src_path):
            continue

        # Calculate relative path
        rel_path = src_path.relative_to(source)
        dst_path = destination / rel_path

        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            files_copied += 1

    return files_copied


def print_next_steps(destination: Path):
    """Print next steps for the user."""
    print()
    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Navigate to your new project:")
    print(f"   cd {destination}")
    print()
    print("2. Initialize git repository:")
    print("   git init")
    print("   git add .")
    print('   git commit -m "chore: initialize from IAM department template"')
    print()
    print("3. Replace placeholders:")
    print("   - {{PROJECT_ID}} → Your GCP project ID")
    print("   - {{SPIFFE_ID}} → Your agent SPIFFE ID")
    print("   - {{ORG_NAME}} → Your organization name")
    print("   - {{DATE}} → Current date")
    print()
    print("4. Create required files:")
    print("   - README.md")
    print("   - CLAUDE.md")
    print("   - VERSION (e.g., echo '0.1.0' > VERSION)")
    print("   - CHANGELOG.md")
    print("   - requirements.txt")
    print("   - Makefile")
    print()
    print("5. Configure infrastructure:")
    print("   - Update infra/terraform/ variables")
    print("   - Set up WIF authentication")
    print("   - Configure GitHub secrets")
    print()
    print("6. Read the template docs:")
    print(f"   cat {destination}/000-docs/000-README-template-iam-department.md")
    print()
    print("=" * 60)
    print("Reference implementation: https://github.com/intent-solutions-io/bobs-brain")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Export IAM department template to a new directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Export to new directory
    python scripts/export_iam_template.py ~/projects/my-new-agents

    # Overwrite existing directory
    python scripts/export_iam_template.py ~/projects/my-new-agents --force
        """
    )

    parser.add_argument(
        'destination',
        help="Destination directory for template export"
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help="Overwrite destination if it exists"
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent
    template_source = repo_root / "template" / "iam-department"
    destination = Path(args.destination).resolve()

    # Validate template source exists
    if not template_source.exists():
        print(f"❌ Template source not found: {template_source}")
        print("   Run this script from the bobs-brain repository root.")
        sys.exit(2)

    # Check destination
    if destination.exists():
        if not args.force:
            print(f"❌ Destination already exists: {destination}")
            print("   Use --force to overwrite.")
            sys.exit(1)
        else:
            print(f"⚠️  Removing existing destination: {destination}")
            shutil.rmtree(destination)

    # Create destination
    destination.mkdir(parents=True, exist_ok=True)

    print(f"📦 Exporting IAM department template...")
    print(f"   Source: {template_source}")
    print(f"   Destination: {destination}")
    print()

    # Copy template
    try:
        files_copied = copy_template(template_source, destination)
        print(f"✅ Exported {files_copied} files to {destination}")
    except Exception as e:
        print(f"❌ Copy failed: {e}")
        sys.exit(2)

    # Print next steps
    print_next_steps(destination)

    sys.exit(0)


if __name__ == "__main__":
    main()
