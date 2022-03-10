from argparse import ArgumentParser
from yaml_changelog.build import Changelog


def main():
    parser = ArgumentParser(
        description="Bump version numbers from changelog.yaml"
    )
    parser.add_argument("changelog_file", help="Path to changelog.yaml")
    parser.add_argument(
        "files", nargs="*", help="Paths to files to bump version numbers in"
    )
    args = parser.parse_args()

    changelog = Changelog(args.changelog_file)
    changelog._write_to_md()
    print(
        f"Bumping from {changelog.previous_version} to {changelog.current_version}"
    )

    for file in args.files:
        with open(file, "r") as f:
            content = f.read()
        content = content.replace(
            changelog.previous_version, changelog.current_version
        )
        with open(file, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
