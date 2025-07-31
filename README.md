# yaml-changelog

A lightweight Python package to manage changelogs in YAML format and convert them to Markdown. Used by PolicyEngine projects for automated changelog management.

## Installation

```bash
pip install yaml-changelog
```

## Changelog Structure

yaml-changelog uses a structured YAML format for managing changelog entries:

### Main Changelog (changelog.yaml)

```yaml
# Entries are listed in reverse chronological order (newest first)
- bump: minor
  date: 2024-01-15 10:30:00  # Optional, will be set automatically
  changes:
    added:
      - New feature X
      - API endpoint for Y
    fixed:
      - Bug in authentication
    changed:
      - Improved performance of data processing

- version: 1.0.0  # Explicit version instead of bump
  date: 2024-01-10 14:20:00
  changes:
    added:
      - Initial release
```

### Entry File (changelog_entry.yaml)

For new changes, create a `changelog_entry.yaml`:

```yaml
# Can be a list for multiple entries
- bump: patch  # major, minor, or patch
  changes:
    fixed:
      - Critical security issue
      
# Alternative format (single entry)
bump: minor
added:
  - New dashboard component
fixed:
  - Memory leak in worker process
```

### Valid Change Types

- `added`: New features or functionality
- `changed`: Changes to existing functionality
- `deprecated`: Features marked for removal
- `removed`: Features that have been removed
- `fixed`: Bug fixes
- `security`: Security-related changes

### Version Management

- **Semantic Versioning**: Follows [semver](https://semver.org/) (MAJOR.MINOR.PATCH)
- **Bump Types**:
  - `major`: Breaking changes (1.0.0 → 2.0.0)
  - `minor`: New features, backwards compatible (1.0.0 → 1.1.0)
  - `patch`: Bug fixes (1.0.0 → 1.0.1)
- **Version Sources**: Can use explicit `version` field or `bump` relative to previous

### Date Handling

- Dates are optional and will be set to current timestamp if omitted
- Format: `YYYY-MM-DD HH:MM:SS` (ISO 8601)
- Use `--update-last-date` flag to update entries without dates
- Dates are validated and must be in chronological order

## Quick Start

### Basic Usage

Convert a YAML changelog to Markdown:

```bash
# Using the main command
build-changelog changelog.yaml --output CHANGELOG.md

# Or use the package name alias
yaml-changelog changelog.yaml --output CHANGELOG.md

# Or run as a Python module
python -m yaml_changelog changelog.yaml --output CHANGELOG.md
```

### YAML Changelog Format

Create a `changelog.yaml` file with your changes:

```yaml
- bump: minor
  date: 2024-01-15 10:30:00
  changes:
    added:
      - New feature X with configuration options
      - Support for Y file format
    fixed:
      - Bug in Z component that caused crashes
      - Memory leak in data processing

- bump: patch
  date: 2024-01-10 14:20:00
  changes:
    fixed:
      - Typo in error messages
      - Incorrect validation for user input
```

### Alternative format (without nested `changes`):

```yaml
- bump: minor
  date: 2024-01-15 10:30:00
  added:
    - New feature X with configuration options
    - Support for Y file format
  fixed:
    - Bug in Z component that caused crashes
    - Memory leak in data processing
```

## Commands

### build-changelog / yaml-changelog

Convert YAML changelogs to Markdown format.

```bash
build-changelog <changelog.yaml> --output <output.md> [options]
```

**Arguments:**
- `file`: Path to the YAML changelog file (required)

**Options:**
- `--output`: Output file path (required, `.md` or `.yaml`)
- `--org`: GitHub organization name (for generating comparison links)
- `--repo`: GitHub repository name (for generating comparison links)
- `--append-file`: Path to changelog entry file to append (e.g., `changelog_entry.yaml`)
- `--template`: Path to Markdown template file (default: built-in template)
- `--start-from`: Starting version number (default: "0.0.0")
- `--update-last-date`: Update the last entry's date to current timestamp
- `--auto-detect`: Auto-detect git organization and repository names
- `--release`: Release mode - automatically uses changelog_entry.yaml, updates in place, removes entry file after success

**Example with GitHub links:**
```bash
yaml-changelog changelog.yaml \
  --output CHANGELOG.md \
  --org PolicyEngine \
  --repo policyengine-us
```

**Release Mode Example:**
```bash
# Instead of:
build-changelog changelog.yaml --append-file changelog_entry.yaml --output changelog.yaml --update-last-date

# Simply use:
build-changelog changelog.yaml --release
```

### bump-version

Update version numbers in your project files.

```bash
bump-version [--major|--minor|--patch]
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/build-changelog.yml`:

```yaml
name: Update Changelog
on:
  push:
    branches: [main]

jobs:
  update-changelog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install yaml-changelog
        run: pip install yaml-changelog
        
      - name: Build changelog
        run: |
          build-changelog changelog.yaml \
            --output CHANGELOG.md \
            --append-file changelog_entry.yaml \
            --org ${{ github.repository_owner }} \
            --repo ${{ github.event.repository.name }}
            
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add CHANGELOG.md changelog.yaml
          git commit -m "Update changelog" || echo "No changes"
          git push
```

### Release Workflow

1. Create a `changelog_entry.yaml` in your PR:
   ```yaml
   - bump: patch
     changes:
       fixed:
         - Critical bug in authentication flow
       added:
         - New API endpoint for user profiles
   ```

2. The CI/CD pipeline appends this entry to the main `changelog.yaml`

3. The tool generates an updated `CHANGELOG.md` with proper versioning

## Advanced Usage

### Custom Templates

Create a custom Markdown template:

```markdown
# My Project Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

{{changelog}}
```

Use it with:
```bash
yaml-changelog changelog.yaml \
  --output CHANGELOG.md \
  --template my-template.md
```

### Programmatic Usage

```python
from yaml_changelog import Changelog

# Load and convert changelog
cl = Changelog(
    "changelog.yaml",
    org="PolicyEngine",
    repo="policyengine-us",
    start_from="0.1.0"
)

# Write Markdown
cl.write_markdown("CHANGELOG.md")

# Access version info
print(f"Current version: {cl.current_version}")
print(f"Previous version: {cl.previous_version}")
```

## Changelog Entry Types

The following change types are supported:
- `added`: New features
- `changed`: Changes in existing functionality
- `deprecated`: Soon-to-be removed features
- `removed`: Removed features
- `fixed`: Bug fixes
- `security`: Security fixes

## Version Bumping

Version bumps follow [Semantic Versioning](https://semver.org/):
- `major`: Breaking changes (1.0.0 → 2.0.0)
- `minor`: New features, backward compatible (1.0.0 → 1.1.0)
- `patch`: Bug fixes, backward compatible (1.0.0 → 1.0.1)

## Common Issues

### Missing changelog_entry.yaml in CI

If you see an error about missing `changelog_entry.yaml` in CI:
1. Create the file with your changes
2. Use the format shown in examples above
3. Commit it with your PR

### Invalid change types

Ensure you use only the supported change types: `added`, `changed`, `deprecated`, `removed`, `fixed`, `security`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

AGPL-3.0 License - see LICENSE file for details.