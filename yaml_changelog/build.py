from argparse import ArgumentParser
from datetime import datetime, timedelta
import logging
import os
from typing import Union, List, Dict, Any, Optional
from pathlib import Path
import yaml
import requests


class VersionNumber:
    """Represents a semantic version number with major, minor, and patch components."""

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def bump_major(self) -> None:
        """Increment major version and reset minor and patch to 0."""
        self.major += 1
        self.minor = 0
        self.patch = 0

    def bump_minor(self) -> None:
        """Increment minor version and reset patch to 0."""
        self.minor += 1
        self.patch = 0

    def bump_patch(self) -> None:
        """Increment patch version."""
        self.patch += 1

    def bump(self, type: str) -> None:
        """Bump version based on type (major, minor, or patch).

        Args:
            type: Version bump type - 'major', 'minor', or 'patch'

        Raises:
            ValueError: If type is not one of the valid options
        """
        if type == "major":
            self.bump_major()
        elif type == "minor":
            self.bump_minor()
        elif type == "patch":
            self.bump_patch()
        else:
            raise ValueError(f"Unknown version bump type: {type}")

    def __repr__(self) -> str:
        """Return version string in format 'major.minor.patch'."""
        return f"{self.major}.{self.minor}.{self.patch}"


CHANGE_TYPES: List[str] = [
    "added",
    "changed",
    "deprecated",
    "removed",
    "fixed",
    "security",
]


class Changelog:
    """Manages changelog entries and converts between YAML and Markdown formats."""

    entries: Optional[List[Dict[str, Any]]] = None
    starter: Optional[str] = None
    repo: Optional[str] = None
    org: Optional[str] = None
    start_from: str = "0.0.0"
    current_version: str = ""
    previous_version: str = ""

    def __init__(
        self,
        file: Union[str, Path],
        repo: Optional[str] = None,
        org: Optional[str] = None,
        template: Optional[str] = None,
        start_from: str = "0.0.0",
        update_last_date: bool = False,
        append: Optional[Union[str, Path]] = None,
    ) -> None:
        """Initialize a Changelog instance.

        Args:
            file: Path to the changelog file (YAML or Markdown)
            repo: GitHub repository name for generating comparison links
            org: GitHub organization name for generating comparison links
            template: Path to Markdown template file
            start_from: Starting version number (default: "0.0.0")
            update_last_date: Whether to update entries without dates to
            current timestamp
            append: Path to changelog entry file to append to main changelog

        Raises:
            NotImplementedError: If file type is not supported
            FileNotFoundError: If append file is specified but doesn't exist
            ValueError: If changelog entries are invalid
        """
        if isinstance(file, str):
            self.file = Path(file)

        self.repo = repo
        self.org = org
        self.template = template
        if start_from is not None:
            self.start_from = start_from
        self.update_last_date = update_last_date

        # if yaml file
        if self.file.suffix in (".yaml", ".yml"):
            self._parse_from_yaml(self.file, append)
        elif self.file.suffix in (".md", ".markdown"):
            self._parse_from_md(self.file)
        else:
            raise NotImplementedError("File type not supported")

        if self.update_last_date:
            for entry in self.entries:
                if "date" not in entry:
                    entry["date"] = datetime.now().replace(microsecond=0)

    def _get_github_merge_date(self, version: str) -> datetime:
        """Fetch the merge date of a version tag from GitHub API.

        Args:
            version: Version tag to look up

        Returns:
            DateTime when the version was tagged
        """
        link = requests.get(
            f"https://api.github.com/repos/policyengine/"
            f"policyengine/git/ref/tags/{version}"
        ).json()
        result = requests.get(link["object"]["url"]).json()["author"]["date"]
        return datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")

    def _parse_from_yaml(
        self, file: Path, appended_file: Optional[Path] = None
    ) -> None:
        """Parse changelog entries from a YAML file.

        Args:
            file: Path to the main YAML changelog file
            appended_file: Optional path to changelog entry file to append

        Raises:
            FileNotFoundError: If appended_file is specified but doesn't exist
            ValueError: If changelog entries are empty or invalid
        """
        with open(file) as f:
            self.entries = yaml.safe_load(f)
        for entry in self.entries:
            for change_type in CHANGE_TYPES:
                # Move insite entry["changes"]
                if change_type in entry:
                    if "changes" not in entry:
                        entry["changes"] = {}
                    entry["changes"][change_type] = entry[change_type]
                    del entry[change_type]
        if appended_file is not None:
            if not os.path.exists(appended_file):
                raise FileNotFoundError(
                    f"Error: changelog_entry.yaml not found at '{appended_file}'.\n\n"
                    f"When using --append-file (often in --release mode), "
                    f"you must create a changelog_entry.yaml file.\n\n"
                    f"Example changelog_entry.yaml:\n"
                    f"- bump: patch\n"
                    f"  fixed:\n"
                    f"    - Fixed bug X\n"
                    f"    - Resolved issue Y\n"
                    f"  added:\n"
                    f"    - Added feature Z\n\n"
                    f"Valid change types: {', '.join(CHANGE_TYPES)}\n"
                    f"Valid bump types: major, minor, patch"
                )
            with open(appended_file) as f:
                try:
                    self.entries.extend(yaml.safe_load(f))
                except TypeError:
                    raise ValueError(
                        f"You haven't provided a changelog entry in "
                        f"{appended_file}. It should look like this: \n\n"
                        f"- bump: minor\n  added:\n  - Some new feature."
                    )

        # Validate all entries
        self._validate_entries()

    def _parse_from_md(self, file: Path) -> None:
        """Parse changelog entries from a Markdown file.

        Args:
            file: Path to the Markdown changelog file

        Note:
            Expects changelog entries in the format:
            ## [version] - date
            ### Added/Changed/Fixed/etc
            - Change item
        """
        with open(file) as f:
            changelog = f.readlines()
        entries = []
        line_numbers = []
        # Identify line numbers for entries
        for i in range(len(changelog)):
            if changelog[i][:3] == "## ":
                line_numbers += [i]
        line_numbers += [len(changelog)]

        # Parse entries
        for start_line, end_line in zip(line_numbers[:-1], line_numbers[1:]):
            try:
                entry_lines = changelog[start_line:end_line]
                entry = {}
                entry["_version"] = entry_lines[0].split("[")[1].split("]")[0].strip()
                entry["date"] = datetime.fromisoformat(
                    entry_lines[0].split(" - ")[1].strip()
                )
                entry["changes"] = {}
                for change_type in CHANGE_TYPES:
                    change_name = change_type.capitalize()
                    entry["changes"][change_type] = []
                    for subline in range(len(entry_lines)):
                        if (
                            "###" in entry_lines[subline]
                            and change_name in entry_lines[subline]
                        ):
                            subline += 1
                            while (
                                subline < len(entry_lines)
                                and "###" not in entry_lines[subline]
                            ):
                                line = entry_lines[subline]
                                if len(line) > 1 and line[0] in ("*", "-"):
                                    entry["changes"][change_type].append(
                                        line[2:].strip()
                                    )
                                subline += 1
                    if len(entry["changes"][change_type]) == 0:
                        del entry["changes"][change_type]
                entries.append(entry)
            except Exception:
                logging.error(f"Error parsing entry at line {start_line}")
                raise

        # Validate dates
        last_date = datetime(2000, 1, 1)
        for entry in entries[::-1]:
            if "date" in entry:
                current_date = entry["date"]
                if entry["date"] <= last_date:
                    entry["date"] = last_date + timedelta(seconds=1)
                    logging.warning(
                        f"Invalid date: {current_date} for version "
                        f"{entry['_version']}: setting to {entry['date']}"
                    )
                    current_date = entry["date"]
                last_date = current_date

        entries = list(sorted(entries, key=lambda x: x.get("date", datetime.now())))

        for i in range(1, len(entries)):
            version = entries[i]["_version"]
            previous_version = entries[i - 1]["_version"]

            # Determine if major, minor or patch from string version numbers
            if version.split(".")[0] != previous_version.split(".")[0]:
                entries[i]["bump"] = "major"
            elif version.split(".")[1] != previous_version.split(".")[1]:
                entries[i]["bump"] = "minor"
            else:
                entries[i]["bump"] = "patch"
            del entries[i - 1]["_version"]

        del entries[-1]["_version"]

        entries[0]["version"] = self.start_from

        self.entries = entries

        # Validate all entries
        self._validate_entries()

    def _validate_entries(self) -> None:
        """Validate that all changelog entries have valid change types.

        Raises:
            ValueError: If an invalid change type is found
        """
        for i, entry in enumerate(self.entries):
            if "changes" in entry:
                for change_type in entry["changes"]:
                    if change_type not in CHANGE_TYPES:
                        # Find which entry this is (by version or index)
                        entry_desc = f"entry {i + 1}"
                        if "version" in entry:
                            entry_desc = f"version {entry['version']}"
                        elif "bump" in entry:
                            entry_desc = f"entry {i + 1} (bump: {entry['bump']})"

                        raise ValueError(
                            f"Invalid change type '{change_type}' in {entry_desc}. "
                            f"Valid change types are: {', '.join(CHANGE_TYPES)}"
                        )

    def _write_to_yaml(self) -> str:
        """Convert changelog entries to YAML format.

        Returns:
            YAML string representation of changelog entries
        """
        return yaml.safe_dump(self.entries)

    def _write_to_md(self) -> str:
        """Convert changelog entries to Markdown format.

        Returns:
            Markdown string representation of changelog with version comparison links

        Side effects:
            Sets self.current_version and self.previous_version attributes
        """
        md_entries = []
        links = []
        version = VersionNumber()

        # Sort entries by date, but if no dates exist, reverse the order
        # (self.entries is newest-first, but we need oldest-first for
        # version calculation)
        has_dates = any("date" in entry for entry in self.entries)
        if has_dates:
            entries = sorted(self.entries, key=lambda x: x.get("date", datetime.now()))
        else:
            # No dates, so reverse to get chronological order
            entries = list(reversed(self.entries))

        # Calculate all versions for the sorted entries
        versions = []

        # First, find the base version to start from
        # Look for the first explicit version in the entries
        base_version_found = False
        for entry in entries:
            if "version" in entry:
                version.major, version.minor, version.patch = [
                    int(x) for x in entry["version"].split(".")
                ]
                base_version_found = True
                break

        # Now process entries in order
        for i in range(len(entries)):
            entry = entries[i]

            if "bump" in entry:
                version.bump(entry["bump"])
            elif "version" in entry:
                # Only set version if this is the first one we see
                # or if we have dates (meaning proper chronological order)
                if not base_version_found or has_dates:
                    version.major, version.minor, version.patch = [
                        int(x) for x in entry["version"].split(".")
                    ]
                    base_version_found = True

            versions.append(str(version))

        # Store the final calculated version
        if versions:
            self.current_version = versions[-1]
        else:
            self.current_version = self.start_from

        # For bump-version command, we need to determine previous_version
        # The key insight: bump-version is used when we want to update version files
        # from their current version to a new version based on changelog entries

        # For bump-version, we need to handle the case where there's a new bump
        # that hasn't been applied to files yet
        #
        # The key is to find which entry has the newest bump and calculate
        # what version we're bumping FROM (previous) and TO (current)

        # For bump-version command: determine what version the files currently have
        # and what version they should be updated to

        # The previous_version is what's currently in the files
        # The current_version is what we want to update to

        # Look through entries to find the last explicit version
        last_explicit_version = None
        last_bump_index = None

        for i, entry in enumerate(entries):
            if "version" in entry:
                last_explicit_version = entry["version"]
            if "bump" in entry:
                last_bump_index = i

        if last_bump_index is not None:
            # We have a bump - need to determine what version to bump FROM
            if last_explicit_version is not None:
                # Use the last explicit version as the starting point
                self.previous_version = last_explicit_version
            else:
                # No explicit version found, use start_from
                self.previous_version = self.start_from
        else:
            # No bumps - files are already at current version
            self.previous_version = self.current_version

        # Now generate the markdown
        for i in range(len(entries)):
            entry = entries[i]
            entry_text = ""
            current_ver = versions[i]
            previous_ver = versions[i - 1] if i > 0 else "0.0.0"

            if self.repo is not None and i > 0:
                links += [
                    f"[{current_ver}]: https://github.com/{self.org}/"
                    f"{self.repo}/compare/{previous_ver}...{current_ver}"
                ]
            date_str = datetime.strftime(
                entry.get("date", datetime.now()), "%Y-%m-%d %H:%M:%S"
            )
            entry_text += f"## [{current_ver}] - {date_str}\n\n"
            for change_type, change_name in zip(
                ["added", "changed", "fixed"], ["Added", "Changed", "Fixed"]
            ):
                if change_type in entry["changes"]:
                    entry_text += f"### {change_name}\n\n"
                    for change in entry["changes"][change_type]:
                        entry_text += f"- {change}\n"
                    entry_text += "\n"
            md_entries.append(entry_text)

        output = "".join(md_entries[::-1]) + "\n\n" + "\n".join(links[::-1])
        if self.template is not None:
            with open(self.template) as f:
                template = f.read()
            output = template.replace("{{changelog}}", output)

        return output + "\n"

    def write_markdown(self, path: Union[str, Path] = "CHANGELOG.md") -> None:
        """Write changelog to a Markdown file.

        Args:
            path: Output file path (default: "CHANGELOG.md")
        """
        with open(path, "w") as f:
            f.write(self._write_to_md())

    def write_yaml(self, path: Union[str, Path] = "CHANGELOG.yaml") -> None:
        """Write changelog to a YAML file.

        Args:
            path: Output file path (default: "CHANGELOG.yaml")
        """
        with open(path, "w") as f:
            f.write(self._write_to_yaml())


def main() -> None:
    """Main entry point for the build-changelog command."""
    parser = ArgumentParser()
    parser.add_argument("file", help="File to parse.")
    parser.add_argument("--append-file", help="File to append to the main YAML file.")
    parser.add_argument("--org", help="Organization to use for GitHub links.")
    parser.add_argument("--repo", help="Repo to link to.")
    parser.add_argument(
        "--template",
        help="Template to use - a Markdown file starter.",
        default=Path(__file__).parent / "examples" / "template.md",
    )
    parser.add_argument("--start-from", help="Start from a specific version.")
    parser.add_argument("--output", help="Output file to write to.")
    parser.add_argument(
        "--update-last-date",
        help="Update the last date in the changelog.",
        action="store_true",
    )
    parser.add_argument(
        "--auto-detect",
        help="Auto-detect organization and repository from git remote.",
        action="store_true",
    )
    parser.add_argument(
        "--release",
        help="Release mode: append changelog_entry.yaml and update in place",
        action="store_true",
    )
    args = parser.parse_args()

    # Handle --release mode
    if args.release:
        # Release mode defaults
        if not args.append_file and os.path.exists("changelog_entry.yaml"):
            args.append_file = "changelog_entry.yaml"
        if not args.output:
            args.output = args.file
        if not args.update_last_date:
            args.update_last_date = True

    # Auto-detect org and repo if requested and not provided
    if args.auto_detect and (not args.org or not args.repo):
        from yaml_changelog.utils import get_git_remote_info

        detected_org, detected_repo = get_git_remote_info()
        if not args.org and detected_org:
            args.org = detected_org
        if not args.repo and detected_repo:
            args.repo = detected_repo

    cl = Changelog(
        args.file,
        repo=args.repo,
        org=args.org,
        template=args.template,
        start_from=args.start_from,
        update_last_date=args.update_last_date,
        append=args.append_file,
    )
    if ".md" in args.output:
        cl.write_markdown(args.output)
    elif ".yaml" in args.output:
        cl.write_yaml(args.output)
        
    # Remove changelog_entry.yaml after successful release
    if args.release and args.append_file and os.path.exists(args.append_file):
        os.remove(args.append_file)
        print(f"✓ Removed {args.append_file} after successful release")


if __name__ == "__main__":
    main()
