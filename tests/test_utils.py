"""Tests for utility functions."""

import pytest
import tempfile
import os
import subprocess
from unittest.mock import patch, MagicMock
from yaml_changelog.utils import (
    get_git_remote_info,
    find_version_files,
    detect_start_version,
    create_makefile_target
)


class TestGetGitRemoteInfo:
    """Test git remote info extraction."""
    
    @patch('subprocess.run')
    def test_ssh_url(self, mock_run):
        """Test parsing SSH git URL."""
        mock_run.return_value = MagicMock(
            stdout="git@github.com:PolicyEngine/yaml-changelog.git\n",
            returncode=0
        )
        
        org, repo = get_git_remote_info()
        assert org == "PolicyEngine"
        assert repo == "yaml-changelog"
    
    @patch('subprocess.run')
    def test_https_url_with_git(self, mock_run):
        """Test parsing HTTPS git URL with .git suffix."""
        mock_run.return_value = MagicMock(
            stdout="https://github.com/PolicyEngine/yaml-changelog.git\n",
            returncode=0
        )
        
        org, repo = get_git_remote_info()
        assert org == "PolicyEngine"
        assert repo == "yaml-changelog"
    
    @patch('subprocess.run')
    def test_https_url_without_git(self, mock_run):
        """Test parsing HTTPS git URL without .git suffix."""
        mock_run.return_value = MagicMock(
            stdout="https://github.com/PolicyEngine/yaml-changelog\n",
            returncode=0
        )
        
        org, repo = get_git_remote_info()
        assert org == "PolicyEngine"
        assert repo == "yaml-changelog"
    
    @patch('subprocess.run')
    def test_no_git_repo(self, mock_run):
        """Test when not in a git repository."""
        mock_run.side_effect = subprocess.CalledProcessError(128, ['git'])
        
        org, repo = get_git_remote_info()
        assert org is None
        assert repo is None


class TestFindVersionFiles:
    """Test finding version files."""
    
    def test_find_setup_py(self):
        """Test finding setup.py with version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_path = os.path.join(tmpdir, "setup.py")
            with open(setup_path, "w") as f:
                f.write('setup(version="1.0.0")')
            
            # Change to temp directory
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                files = find_version_files()
                assert "setup.py" in files
            finally:
                os.chdir(old_cwd)
    
    def test_find_pyproject_toml(self):
        """Test finding pyproject.toml with version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = os.path.join(tmpdir, "pyproject.toml")
            with open(pyproject_path, "w") as f:
                f.write('[tool.poetry]\nversion = "1.0.0"')
            
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                files = find_version_files()
                assert "pyproject.toml" in files
            finally:
                os.chdir(old_cwd)
    
    def test_find_package_json(self):
        """Test finding package.json with version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_path = os.path.join(tmpdir, "package.json")
            with open(package_path, "w") as f:
                f.write('{"name": "test", "version": "1.0.0"}')
            
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                files = find_version_files()
                assert "package.json" in files
            finally:
                os.chdir(old_cwd)
    
    def test_find_init_py_in_package(self):
        """Test finding __init__.py with version in package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "mypackage"))
            init_path = os.path.join(tmpdir, "mypackage", "__init__.py")
            with open(init_path, "w") as f:
                f.write('__version__ = "1.0.0"')
            
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                files = find_version_files()
                assert "mypackage/__init__.py" in files
            finally:
                os.chdir(old_cwd)
    
    def test_no_version_files(self):
        """Test when no version files are found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files without version info
            with open(os.path.join(tmpdir, "README.md"), "w") as f:
                f.write("# Test Project")
            
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                files = find_version_files()
                assert len(files) == 0
            finally:
                os.chdir(old_cwd)


class TestDetectStartVersion:
    """Test detecting start version from changelog."""
    
    def test_detect_from_changelog(self):
        """Test detecting version from existing changelog."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump([
                {"bump": "minor", "changes": {"added": ["New"]}},
                {"bump": "patch", "changes": {"fixed": ["Bug"]}},
                {"version": "1.0.0", "changes": {"added": ["Initial"]}}
            ], f)
            f.flush()
            
            try:
                version = detect_start_version(f.name)
                assert version == "1.0.0"
            finally:
                os.unlink(f.name)
    
    def test_no_changelog(self):
        """Test when changelog doesn't exist."""
        version = detect_start_version("nonexistent.yaml")
        assert version == "0.0.0"
    
    def test_empty_changelog(self):
        """Test when changelog is empty."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            
            try:
                version = detect_start_version(f.name)
                assert version == "0.0.0"
            finally:
                os.unlink(f.name)


class TestCreateMakefileTarget:
    """Test Makefile target generation."""
    
    @patch('yaml_changelog.utils.get_git_remote_info')
    @patch('yaml_changelog.utils.find_version_files')
    @patch('yaml_changelog.utils.detect_start_version')
    def test_full_makefile_target(self, mock_version, mock_files, mock_git):
        """Test generating complete Makefile target."""
        mock_git.return_value = ("PolicyEngine", "test-repo")
        mock_files.return_value = ["setup.py", "package/__init__.py"]
        mock_version.return_value = "0.1.0"
        
        # Create mock template file
        with patch('os.path.exists', return_value=True):
            target = create_makefile_target()
        
        # Check all components are present
        assert "changelog:" in target
        assert "--start-from 0.1.0" in target
        assert "--org PolicyEngine --repo test-repo" in target
        assert "bump-version changelog.yaml setup.py package/__init__.py" in target
        assert "--template .github/changelog_template.md" in target
    
    @patch('yaml_changelog.utils.get_git_remote_info')
    @patch('yaml_changelog.utils.find_version_files')
    def test_minimal_makefile_target(self, mock_files, mock_git):
        """Test generating minimal Makefile target."""
        mock_git.return_value = (None, None)
        mock_files.return_value = []
        
        with patch('os.path.exists', return_value=False):
            target = create_makefile_target()
        
        # Should still have basic structure
        assert "changelog:" in target
        assert "build-changelog changelog.yaml" in target
        assert "touch changelog_entry.yaml" in target
        # Should not have org/repo or version files
        assert "--org" not in target
        assert "bump-version" not in target