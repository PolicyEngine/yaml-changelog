"""Extract version information from changelog."""

from argparse import ArgumentParser
from yaml_changelog.build import Changelog


def get_version(changelog_file: str) -> str:
    """Get the current version from a changelog file.

    Args:
        changelog_file: Path to the changelog YAML file

    Returns:
        Current version string
    """
    cl = Changelog(changelog_file)
    cl._write_to_md()  # Calculate versions
    return cl.current_version


def main() -> None:
    """Main entry point for the get-version command."""
    parser = ArgumentParser(description="Extract version from changelog.yaml")
    parser.add_argument("file", help="Path to changelog.yaml file")
    args = parser.parse_args()

    version = get_version(args.file)
    print(version)


if __name__ == "__main__":
    main()
