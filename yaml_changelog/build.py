from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
import logging
from typing import Union
from pathlib import Path
import yaml
import requests


class VersionNumber:
    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def bump_major(self):
        self.major += 1
        self.minor = 0
        self.patch = 0

    def bump_minor(self):
        self.minor += 1
        self.patch = 0

    def bump_patch(self):
        self.patch += 1

    def bump(self, type: str):
        if type == "major":
            self.bump_major()
        elif type == "minor":
            self.bump_minor()
        elif type == "patch":
            self.bump_patch()
        else:
            raise ValueError(f"Unknown version bump type: {type}")

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


class Changelog:
    entries = None
    starter = None
    repo: str = None
    org: str = None

    def __init__(
        self,
        file: Union[str, Path],
        repo: str = None,
        org: str = None,
        template: str = None,
        start_from: str = "0.0.0",
        update_last_date: bool = False,
    ):
        if isinstance(file, str):
            self.file = Path(file)

        self.repo = repo
        self.org = org
        self.template = template
        self.start_from = start_from
        self.update_last_date = update_last_date

        # if yaml file
        if self.file.suffix in (".yaml", ".yml"):
            self._parse_from_yaml(self.file)
        elif self.file.suffix in (".md", ".markdown"):
            self._parse_from_md(self.file)
        else:
            raise NotImplementedError("File type not supported")

        if self.update_last_date:
            for entry in self.entries:
                if "date" not in entry:
                    entry["date"] = datetime.now().replace(microsecond=0)

    def _get_github_merge_date(self, version: str):
        link = requests.get(
            f"https://api.github.com/repos/policyengine/policyengine/git/ref/tags/{version}"
        ).json()
        result = requests.get(link["object"]["url"]).json()["author"]["date"]
        return datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")

    def _parse_from_yaml(self, file: Path):
        with open(file) as f:
            self.entries = yaml.safe_load(f)

    def _parse_from_md(self, file: Path):
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
            entry_lines = changelog[start_line:end_line]
            entry = {}
            entry["_version"] = (
                entry_lines[0].split("[")[1].split("]")[0].strip()
            )
            entry["date"] = datetime.fromisoformat(
                entry_lines[0].split(" - ")[1].strip()
            )
            entry["changes"] = {}
            for change_type, change_name in zip(
                ["added", "changed", "fixed"], ["Added", "Changed", "Fixed"]
            ):
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
                            if len(line) > 1 and line[0] == "*":
                                entry["changes"][change_type].append(
                                    line[2:].strip()
                                )
                            subline += 1
                if len(entry["changes"][change_type]) == 0:
                    del entry["changes"][change_type]
            entries.append(entry)

        # Validate dates
        last_date = datetime(2000, 1, 1)
        for entry in entries[::-1]:
            if "date" in entry:
                current_date = entry["date"]
                if entry["date"] <= last_date:
                    entry["date"] = last_date + timedelta(seconds=1)
                    logging.warn(
                        f"Invalid date: {current_date} for version {entry['_version']}: setting to {entry['date']}"
                    )
                    current_date = entry["date"]
                last_date = current_date

        entries = list(
            sorted(entries, key=lambda x: x.get("date", datetime.now()))
        )

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

    def _write_to_yaml(self) -> str:
        return yaml.safe_dump(self.entries)

    def _write_to_md(self) -> str:
        md_entries = []
        links = []
        version = VersionNumber(major=1, minor=4)
        entries = sorted(
            self.entries, key=lambda x: x.get("date", datetime.now())
        )
        for i in range(len(entries)):
            entry = entries[i]
            previous_version = str(version)
            entry_text = ""
            if "bump" in entry:
                version.bump(entry["bump"])
            elif "version" in entry:
                version.major, version.minor, version.patch = [
                    int(x) for x in entry["version"].split(".")
                ]
            if self.repo is not None and i > 0:
                links += [
                    f"[{version}]: https://github.com/{self.org}/{self.repo}/compare/{previous_version}...{str(version)}"
                ]
            entry_text += f"## [{str(version)}] - {datetime.strftime(entry.get('date', datetime.now()), '%Y-%m-%d %H:%M:%S')}\n\n"
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
        self.current_version = str(version)
        self.previous_version = previous_version
        return output + "\n"

    def write_markdown(self, path: Path = "CHANGELOG.md"):
        with open(path, "w") as f:
            f.write(self._write_to_md())

    def write_yaml(self, path: Path = "CHANGELOG.yaml"):
        with open(path, "w") as f:
            f.write(self._write_to_yaml())


def main():
    parser = ArgumentParser()
    parser.add_argument("file", help="File to parse.")
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
    args = parser.parse_args()

    cl = Changelog(
        args.file,
        repo=args.repo,
        org=args.org,
        template=args.template,
        start_from=args.start_from,
        update_last_date=args.update_last_date,
    )
    if ".md" in args.output:
        cl.write_markdown(args.output)
    elif ".yaml" in args.output:
        cl.write_yaml(args.output)


if __name__ == "__main__":
    main()
