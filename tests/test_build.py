"""Tests for the build module."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from yaml_changelog.build import Changelog, VersionNumber, CHANGE_TYPES


class TestVersionNumber:
    """Test the VersionNumber class."""

    def test_init(self):
        """Test version initialization."""
        v = VersionNumber()
        assert str(v) == "0.0.0"

        v = VersionNumber(1, 2, 3)
        assert str(v) == "1.2.3"

    def test_bump_major(self):
        """Test major version bumping."""
        v = VersionNumber(1, 2, 3)
        v.bump_major()
        assert str(v) == "2.0.0"

    def test_bump_minor(self):
        """Test minor version bumping."""
        v = VersionNumber(1, 2, 3)
        v.bump_minor()
        assert str(v) == "1.3.0"

    def test_bump_patch(self):
        """Test patch version bumping."""
        v = VersionNumber(1, 2, 3)
        v.bump_patch()
        assert str(v) == "1.2.4"

    def test_bump_with_type(self):
        """Test bumping with type string."""
        v = VersionNumber(1, 0, 0)
        v.bump("patch")
        assert str(v) == "1.0.1"

        v.bump("minor")
        assert str(v) == "1.1.0"

        v.bump("major")
        assert str(v) == "2.0.0"

    def test_bump_invalid_type(self):
        """Test bumping with invalid type."""
        v = VersionNumber()
        with pytest.raises(ValueError, match="Unknown version bump type"):
            v.bump("invalid")


class TestChangelog:
    """Test the Changelog class."""

    def test_parse_yaml_simple(self):
        """Test parsing a simple YAML changelog."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
- bump: minor
  changes:
    added:
      - New feature
    fixed:
      - Bug fix

- version: 0.1.0
  changes:
    added:
      - Initial release
"""
            )
            f.flush()

            try:
                cl = Changelog(f.name)
                assert len(cl.entries) == 2
                assert cl.entries[0]["bump"] == "minor"
                assert "added" in cl.entries[0]["changes"]
                assert cl.entries[1]["version"] == "0.1.0"
            finally:
                os.unlink(f.name)

    def test_parse_yaml_with_append(self):
        """Test parsing YAML with append file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as main_file:
            main_file.write(
                """
- version: 0.1.0
  changes:
    added:
      - Initial release
"""
            )
            main_file.flush()

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as append_file:
                append_file.write(
                    """
- bump: patch
  changes:
    fixed:
      - Security fix
"""
                )
                append_file.flush()

                try:
                    cl = Changelog(main_file.name, append=append_file.name)
                    assert len(cl.entries) == 2
                    # The appended entry should be added to the list
                    assert any(entry.get("bump") == "patch" for entry in cl.entries)
                finally:
                    os.unlink(main_file.name)
                    os.unlink(append_file.name)

    def test_missing_append_file(self):
        """Test error when append file is missing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("- version: 0.1.0\n  changes:\n    added:\n      - Initial")
            f.flush()

            try:
                with pytest.raises(
                    FileNotFoundError, match="changelog_entry.yaml not found"
                ):
                    Changelog(f.name, append="missing.yaml")
            finally:
                os.unlink(f.name)

    def test_invalid_change_type(self):
        """Test validation of invalid change types."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
- bump: patch
  changes:
    fixes:  # Invalid - should be 'fixed'
      - Some fix
"""
            )
            f.flush()

            try:
                with pytest.raises(ValueError, match="Invalid change type 'fixes'"):
                    Changelog(f.name)
            finally:
                os.unlink(f.name)

    def test_valid_change_types(self):
        """Test that all valid change types are accepted."""
        changes = {}
        for change_type in CHANGE_TYPES:
            changes[change_type] = [f"Test {change_type}"]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump([{"bump": "patch", "changes": changes}], f)
            f.flush()

            try:
                cl = Changelog(f.name)  # Should not raise
                assert len(cl.entries) == 1
                assert cl.entries[0]["changes"] == changes
            finally:
                os.unlink(f.name)

    def test_write_markdown(self):
        """Test writing changelog to markdown."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
- bump: minor
  date: 2024-01-15 10:00:00
  changes:
    added:
      - New feature X
    fixed:
      - Bug Y

- version: 0.1.0
  date: 2024-01-10 10:00:00  
  changes:
    added:
      - Initial release
"""
            )
            f.flush()

            try:
                cl = Changelog(f.name, org="TestOrg", repo="test-repo")

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False
                ) as md:
                    cl.write_markdown(md.name)

                    # Read the generated markdown
                    with open(md.name) as mdf:
                        content = mdf.read()

                    # Check for expected content
                    assert "## [0.2.0]" in content
                    assert "New feature X" in content
                    assert "Bug Y" in content
                    assert (
                        "[0.2.0]: https://github.com/TestOrg/test-repo/compare/0.1.0...0.2.0"
                        in content
                    )

                    os.unlink(md.name)
            finally:
                os.unlink(f.name)

    def test_alternative_format(self):
        """Test alternative changelog format without nested 'changes'."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
- bump: patch
  fixed:
    - Direct fix entry
  added:
    - Direct add entry
"""
            )
            f.flush()

            try:
                cl = Changelog(f.name)
                assert len(cl.entries) == 1
                assert "fixed" in cl.entries[0]["changes"]
                assert "added" in cl.entries[0]["changes"]
                assert cl.entries[0]["changes"]["fixed"] == ["Direct fix entry"]
            finally:
                os.unlink(f.name)
