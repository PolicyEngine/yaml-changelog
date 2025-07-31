from argparse import ArgumentParser
from typing import List, Tuple
import re
from yaml_changelog.build import Changelog


def find_version_patterns(
    previous_version: str, current_version: str
) -> List[Tuple[str, str]]:
    """Generate regex patterns to safely replace version numbers.

    Args:
        previous_version: The old version string (e.g., "1.2.3")
        current_version: The new version string (e.g., "1.2.4")

    Returns:
        List of (pattern, replacement) tuples for safe version replacement
    """
    # Escape dots in version strings for regex
    prev_escaped = re.escape(previous_version)

    # Common version patterns in different file types
    patterns = [
        # Python setup.py / pyproject.toml
        (
            rf'version\s*=\s*["\']({prev_escaped})["\']',
            f'version = "{current_version}"',
        ),
        (
            rf'version\s*=\s*["\']({prev_escaped})["\']',
            f"version = '{current_version}'",
        ),
        # package.json
        (rf'"version"\s*:\s*"({prev_escaped})"', f'"version": "{current_version}"'),
        # __init__.py or version files
        (
            rf'__version__\s*=\s*["\']({prev_escaped})["\']',
            f'__version__ = "{current_version}"',
        ),
        (
            rf'__version__\s*=\s*["\']({prev_escaped})["\']',
            f"__version__ = '{current_version}'",
        ),
        # VERSION or version.txt files
        (rf"^{prev_escaped}$", current_version),
        # Cargo.toml
        (rf'version\s*=\s*"({prev_escaped})"', f'version = "{current_version}"'),
        # Maven pom.xml
        (
            rf"<version>({prev_escaped})</version>",
            f"<version>{current_version}</version>",
        ),
    ]

    return patterns


def bump_version_in_file(
    file_path: str, previous_version: str, current_version: str
) -> bool:
    """Bump version in a single file using safe patterns.

    Args:
        file_path: Path to the file to update
        previous_version: The old version string
        current_version: The new version string

    Returns:
        True if any replacements were made, False otherwise
    """
    with open(file_path, "r") as f:
        content = f.read()

    original_content = content
    patterns = find_version_patterns(previous_version, current_version)

    # Try each pattern
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Only write if changes were made
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True

    return False


def main():
    parser = ArgumentParser(description="Bump version numbers from changelog.yaml")
    parser.add_argument("changelog_file", help="Path to changelog.yaml")
    parser.add_argument(
        "files", nargs="*", help="Paths to files to bump version numbers in"
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Use simple string replacement (unsafe, may replace unintended occurrences)",
    )
    args = parser.parse_args()

    changelog = Changelog(args.changelog_file)
    changelog._write_to_md()
    print(f"Bumping from {changelog.previous_version} to {changelog.current_version}")

    for file in args.files:
        if args.unsafe:
            # Legacy behavior - simple string replacement
            with open(file, "r") as f:
                content = f.read()
            content = content.replace(
                changelog.previous_version, changelog.current_version
            )
            with open(file, "w") as f:
                f.write(content)
            print(f"Updated {file} (unsafe mode)")
        else:
            # Safe pattern-based replacement
            if bump_version_in_file(
                file, changelog.previous_version, changelog.current_version
            ):
                print(f"Updated {file}")
            else:
                print(f"No version pattern found in {file} - skipping")


if __name__ == "__main__":
    main()
