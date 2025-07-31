"""Initialize yaml-changelog in a project."""

import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from yaml_changelog.utils import (
    get_git_remote_info,
    find_version_files,
    detect_start_version,
    create_makefile_target,
)


INITIAL_CHANGELOG = """# Initial changelog entry
- version: {version}
  changes:
    added:
      - Initial release
"""

CHANGELOG_TEMPLATE = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{{{{changelog}}}}
"""

GITHUB_WORKFLOW = """name: Check Changelog

on:
  pull_request:
    branches: [ main, master ]

jobs:
  check-changelog:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Check for changelog entry
      run: |
        if [ -f "changelog_entry.yaml" ]; then
          echo "✅ changelog_entry.yaml found"
          python -m pip install yaml-changelog
          python -c "import yaml; yaml.safe_load(open('changelog_entry.yaml'))"
        else
          echo "⚠️  No changelog_entry.yaml found"
          echo "Please add a changelog_entry.yaml file"
          exit 1
        fi
"""


def init_changelog():
    """Initialize yaml-changelog in the current project."""
    parser = ArgumentParser(description="Initialize yaml-changelog in your project")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Overwrite existing files"
    )
    parser.add_argument(
        "--start-version",
        default=None,
        help="Starting version (default: auto-detect or 0.0.0)",
    )
    args = parser.parse_args()

    # Detect configuration
    org, repo = get_git_remote_info()
    version_files = find_version_files()
    start_version = args.start_version or detect_start_version() or "0.0.0"

    print("🔍 Detected configuration:")
    if org and repo:
        print(f"  Organization: {org}")
        print(f"  Repository: {repo}")
    print(f"  Starting version: {start_version}")
    if version_files:
        print(f"  Version files: {', '.join(version_files)}")
    print()

    # Create changelog.yaml if it doesn't exist
    if not os.path.exists("changelog.yaml") or args.force:
        print("📝 Creating changelog.yaml...")
        with open("changelog.yaml", "w") as f:
            f.write(INITIAL_CHANGELOG.format(version=start_version))
    else:
        print("✓ changelog.yaml already exists")

    # Create empty changelog_entry.yaml
    if not os.path.exists("changelog_entry.yaml") or args.force:
        print("📝 Creating changelog_entry.yaml...")
        Path("changelog_entry.yaml").touch()
    else:
        print("✓ changelog_entry.yaml already exists")

    # Create changelog template
    os.makedirs(".github", exist_ok=True)
    if not os.path.exists(".github/changelog_template.md") or args.force:
        print("📝 Creating .github/changelog_template.md...")
        with open(".github/changelog_template.md", "w") as f:
            f.write(CHANGELOG_TEMPLATE)
    else:
        print("✓ .github/changelog_template.md already exists")

    # Create GitHub workflow
    os.makedirs(".github/workflows", exist_ok=True)
    if not os.path.exists(".github/workflows/check-changelog.yaml") or args.force:
        print("📝 Creating .github/workflows/check-changelog.yaml...")
        with open(".github/workflows/check-changelog.yaml", "w") as f:
            f.write(GITHUB_WORKFLOW)
    else:
        print("✓ .github/workflows/check-changelog.yaml already exists")

    # Add to Makefile if it exists
    if os.path.exists("Makefile"):
        with open("Makefile", "r") as f:
            makefile_content = f.read()

        if "changelog:" not in makefile_content:
            print("📝 Adding changelog target to Makefile...")
            with open("Makefile", "a") as f:
                f.write("\n" + create_makefile_target())
        else:
            print("✓ Makefile already has changelog target")
    else:
        print("\n💡 Add this to your Makefile:")
        print(create_makefile_target())

    # Show next steps
    print("\n✅ yaml-changelog initialized!")
    print("\nNext steps:")
    print("1. Edit changelog_entry.yaml to add your changes")
    print("2. Run 'make changelog' to update the changelog")
    print("3. Commit and push your changes")

    if not version_files:
        print(
            "\n⚠️  No version files detected. You may need to specify them manually in your Makefile."
        )


if __name__ == "__main__":
    init_changelog()
