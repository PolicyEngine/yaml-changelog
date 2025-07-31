"""Integration tests for yaml-changelog."""

import tempfile
import os
import subprocess
import sys

import pytest


class TestCLIIntegration:
    """Test command-line interface integration."""

    def test_help_commands(self):
        """Test that help commands work."""
        commands = [
            "build-changelog",
            "yaml-changelog",
            "bump-version",
        ]

        for cmd in commands:
            result = subprocess.run([cmd, "--help"], capture_output=True, text=True)
            assert result.returncode == 0
            assert "usage:" in result.stdout.lower()

    def test_init_command(self):
        """Test yaml-changelog-init command separately."""
        # This test might be skipped in CI if the command isn't in PATH yet
        result = subprocess.run(
            ["yaml-changelog-init", "--help"], capture_output=True, text=True
        )
        if result.returncode == 0:
            assert "usage:" in result.stdout.lower()
        else:
            # Command not found, likely in CI before full install
            pytest.skip("yaml-changelog-init not in PATH (expected in CI)")

    def test_module_execution(self):
        """Test running as a module."""
        result = subprocess.run(
            [sys.executable, "-m", "yaml_changelog", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()

    def test_end_to_end_workflow(self):
        """Test a complete changelog workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial changelog
            changelog_path = os.path.join(tmpdir, "changelog.yaml")
            with open(changelog_path, "w") as f:
                f.write(
                    """- version: 1.0.0
  changes:
    added:
      - Initial release
"""
                )

            # Create changelog entry
            entry_path = os.path.join(tmpdir, "changelog_entry.yaml")
            with open(entry_path, "w") as f:
                f.write(
                    """- bump: minor
  changes:
    added:
      - New feature X
    fixed:
      - Bug Y
"""
                )

            # Create version files
            setup_path = os.path.join(tmpdir, "setup.py")
            with open(setup_path, "w") as f:
                f.write('setup(name="test", version="1.0.0")')

            pyproject_path = os.path.join(tmpdir, "pyproject.toml")
            with open(pyproject_path, "w") as f:
                f.write('[tool.poetry]\nversion = "1.0.0"')

            # First, update the changelog.yaml with the appended entry
            result = subprocess.run(
                [
                    "build-changelog",
                    changelog_path,
                    "--output",
                    changelog_path,
                    "--append-file",
                    entry_path,
                ],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0

            # Debug: check the updated changelog
            with open(changelog_path) as f:
                print("Updated changelog.yaml:")
                print(f.read())

            # Then build the markdown
            md_path = os.path.join(tmpdir, "CHANGELOG.md")
            result = subprocess.run(
                [
                    "build-changelog",
                    changelog_path,
                    "--output",
                    md_path,
                    "--org",
                    "TestOrg",
                    "--repo",
                    "test-repo",
                ],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert os.path.exists(md_path)

            # Check markdown content
            with open(md_path) as f:
                content = f.read()
            assert "New feature X" in content
            assert "Bug Y" in content

            # Bump versions
            result = subprocess.run(
                ["bump-version", changelog_path, setup_path, pyproject_path],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            # Debug output
            if result.stdout:
                print("Bump stdout:", result.stdout)

            # Check versions were updated
            with open(setup_path) as f:
                content = f.read()
                assert 'version="1.1.0"' in content or 'version = "1.1.0"' in content

            with open(pyproject_path) as f:
                content = f.read()
                assert 'version = "1.1.0"' in content or 'version="1.1.0"' in content

    def test_release_mode(self):
        """Test --release mode functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial changelog
            changelog_path = os.path.join(tmpdir, "changelog.yaml")
            with open(changelog_path, "w") as f:
                f.write(
                    """- version: 1.0.0
  changes:
    added:
      - Initial release
"""
                )

            # Create changelog entry
            entry_path = os.path.join(tmpdir, "changelog_entry.yaml")
            with open(entry_path, "w") as f:
                f.write(
                    """- bump: minor
  changes:
    added:
      - New feature
"""
                )

            # Run with --release flag
            result = subprocess.run(
                ["build-changelog", changelog_path, "--release"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

            # Check that changelog was updated
            with open(changelog_path) as f:
                content = f.read()
            assert "New feature" in content

            # Check that changelog_entry.yaml was removed
            assert not os.path.exists(entry_path)
