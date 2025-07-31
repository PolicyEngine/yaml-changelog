"""Utility functions for yaml-changelog."""

import os
import re
import subprocess
from typing import Optional, Tuple, List
from pathlib import Path


def get_git_remote_info() -> Tuple[Optional[str], Optional[str]]:
    """Extract organization and repository name from git remote.

    Returns:
        Tuple of (organization, repository) or (None, None) if not found
    """
    try:
        # Get the remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Parse GitHub URL patterns
        # SSH: git@github.com:org/repo.git
        # HTTPS: https://github.com/org/repo.git or https://github.com/org/repo
        patterns = [
            r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$",
            r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$",
        ]

        for pattern in patterns:
            match = re.match(pattern, remote_url)
            if match:
                return match.group(1), match.group(2)

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None, None


def find_version_files() -> List[str]:
    """Find common version files in the current directory.

    Returns:
        List of file paths that likely contain version information
    """
    version_files = []

    # Common version file patterns
    patterns = [
        "setup.py",
        "pyproject.toml",
        "__init__.py",
        "*/__init__.py",
        "**/__init__.py",  # Also search deeper
        "*/version.py",
        "*/constants.py",
        "package.json",
        "Cargo.toml",
        "pom.xml",
    ]

    cwd = Path.cwd()  # Use cwd() instead of "." for better compatibility
    for pattern in patterns:
        # Handle both direct files and glob patterns
        if "*" in pattern:
            # It's a glob pattern
            matching_paths = list(cwd.glob(pattern))
            for path in matching_paths:
                if path.is_file():
                    # Check if file contains version string
                    try:
                        content = path.read_text()
                        # Match various version patterns:
                        # Python: version = "1.2.3", __version__ = "1.2.3"
                        # JSON: "version": "1.2.3"
                        # TOML: version = "1.2.3"
                        if re.search(
                            r'(?:__)?version(?:__)?["\']*\s*[=:]\s*["\']\d+\.\d+\.\d+',
                            content,
                            re.IGNORECASE,
                        ):
                            # Return relative path
                            version_files.append(str(path.relative_to(cwd)))
                    except Exception:
                        pass
        else:
            # It's a direct file path
            path = cwd / pattern
            if path.is_file():
                try:
                    content = path.read_text()
                    # Match various version patterns:
                    # Python: version = "1.2.3", __version__ = "1.2.3"
                    # JSON: "version": "1.2.3"
                    # TOML: version = "1.2.3"
                    if re.search(
                        r'(?:__)?version(?:__)?["\']*\s*[=:]\s*["\']\d+\.\d+\.\d+',
                        content,
                        re.IGNORECASE,
                    ):
                        # Return relative path
                        version_files.append(str(path.relative_to(cwd)))
                except Exception:
                    pass

    return sorted(set(version_files))


def detect_start_version(changelog_path: str = "changelog.yaml") -> str:
    """Detect the starting version from existing changelog.

    Args:
        changelog_path: Path to the changelog file

    Returns:
        Starting version string, defaults to "0.0.0" if not found
    """
    try:
        import yaml

        with open(changelog_path) as f:
            entries = yaml.safe_load(f)

        if entries and isinstance(entries, list):
            # Find the earliest entry with a version
            for entry in reversed(entries):
                if "version" in entry:
                    return entry["version"]
    except Exception:
        pass

    return "0.0.0"


def create_makefile_target() -> str:
    """Generate a Makefile changelog target based on detected configuration.

    Returns:
        Makefile target content
    """
    org, repo = get_git_remote_info()
    version_files = find_version_files()
    start_version = detect_start_version()

    # Build the Makefile target
    target = "changelog:\n"
    target += f"\tbuild-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from {start_version} --append-file changelog_entry.yaml\n"

    if org and repo:
        target += f"\tbuild-changelog changelog.yaml --org {org} --repo {repo} --output CHANGELOG.md"
    else:
        target += "\tbuild-changelog changelog.yaml --output CHANGELOG.md"

    if os.path.exists(".github/changelog_template.md"):
        target += " --template .github/changelog_template.md"
    target += "\n"

    if version_files:
        target += f"\tbump-version changelog.yaml {' '.join(version_files)}\n"

    target += "\trm changelog_entry.yaml || true\n"
    target += "\ttouch changelog_entry.yaml\n"

    return target
