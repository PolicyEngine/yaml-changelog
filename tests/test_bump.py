"""Tests for the bump module."""

import pytest
import tempfile
import os
from yaml_changelog.bump import find_version_patterns, bump_version_in_file, main
from yaml_changelog.build import Changelog
import yaml


class TestVersionPatterns:
    """Test version pattern generation."""
    
    def test_find_version_patterns(self):
        """Test that version patterns are generated correctly."""
        patterns = find_version_patterns("1.2.3", "1.2.4")
        
        # Should have patterns for different file types
        pattern_strings = [p[0] for p in patterns]
        
        # Check that patterns include escaping for dots
        assert any(r'1\.2\.3' in p for p in pattern_strings)
        
        # Check replacements
        replacements = [p[1] for p in patterns]
        assert 'version = "1.2.4"' in replacements
        assert '"version": "1.2.4"' in replacements


class TestBumpVersionInFile:
    """Test bumping versions in different file types."""
    
    def test_bump_setup_py(self):
        """Test version bumping in setup.py."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='setup.py', delete=False) as f:
            f.write('''from setuptools import setup

setup(
    name="test-package",
    version="1.2.3",
    description="Test package"
)''')
            f.flush()
            
            try:
                result = bump_version_in_file(f.name, "1.2.3", "1.2.4")
                assert result is True
                
                with open(f.name) as rf:
                    content = rf.read()
                assert 'version="1.2.4"' in content
                assert 'version="1.2.3"' not in content
            finally:
                os.unlink(f.name)
    
    def test_bump_pyproject_toml(self):
        """Test version bumping in pyproject.toml."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='pyproject.toml', delete=False) as f:
            f.write('''[tool.poetry]
name = "test-package"
version = "1.2.3"
description = "Test package"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"''')
            f.flush()
            
            try:
                result = bump_version_in_file(f.name, "1.2.3", "1.2.4")
                assert result is True
                
                with open(f.name) as rf:
                    content = rf.read()
                assert 'version = "1.2.4"' in content
                assert 'version = "1.2.3"' not in content
            finally:
                os.unlink(f.name)
    
    def test_bump_package_json(self):
        """Test version bumping in package.json."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='package.json', delete=False) as f:
            f.write('''{
  "name": "test-package",
  "version": "1.2.3",
  "description": "Test package",
  "main": "index.js"
}''')
            f.flush()
            
            try:
                result = bump_version_in_file(f.name, "1.2.3", "1.2.4")
                assert result is True
                
                with open(f.name) as rf:
                    content = rf.read()
                assert '"version": "1.2.4"' in content
                assert '"version": "1.2.3"' not in content
            finally:
                os.unlink(f.name)
    
    def test_bump_init_py(self):
        """Test version bumping in __init__.py."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='__init__.py', delete=False) as f:
            f.write('''"""Test package."""

__version__ = "1.2.3"
__author__ = "Test Author"

from .core import main''')
            f.flush()
            
            try:
                result = bump_version_in_file(f.name, "1.2.3", "1.2.4")
                assert result is True
                
                with open(f.name) as rf:
                    content = rf.read()
                assert '__version__ = "1.2.4"' in content
                assert '__version__ = "1.2.3"' not in content
                # Make sure other content is preserved
                assert '__author__ = "Test Author"' in content
            finally:
                os.unlink(f.name)
    
    def test_bump_no_version_found(self):
        """Test when no version pattern is found."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This file has no version information")
            f.flush()
            
            try:
                result = bump_version_in_file(f.name, "1.2.3", "1.2.4")
                assert result is False
                
                # File should be unchanged
                with open(f.name) as rf:
                    content = rf.read()
                assert content == "This file has no version information"
            finally:
                os.unlink(f.name)
    
    def test_no_unintended_replacements(self):
        """Test that version bumping doesn't replace unintended strings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''from package_1_2_3 import something
import another_1_2_3

__version__ = "1.2.3"

# This uses version 1.2.3 of the API
api_endpoint = "https://api.example.com/v1.2.3/data"
required_version = ">=1.2.3"
''')
            f.flush()
            
            try:
                result = bump_version_in_file(f.name, "1.2.3", "1.2.4")
                assert result is True
                
                with open(f.name) as rf:
                    content = rf.read()
                
                # Only __version__ should be updated
                assert '__version__ = "1.2.4"' in content
                
                # These should NOT be changed
                assert 'from package_1_2_3 import' in content
                assert 'import another_1_2_3' in content
                assert 'api.example.com/v1.2.3/data' in content
                assert 'required_version = ">=1.2.3"' in content
            finally:
                os.unlink(f.name)


class TestBumpMain:
    """Test the main bump-version command."""
    
    def test_bump_multiple_files(self):
        """Test bumping versions in multiple files at once."""
        # Create test changelog
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as changelog:
            yaml.dump([
                {"bump": "minor", "changes": {"added": ["New feature"]}},
                {"version": "1.2.3", "changes": {"added": ["Initial"]}}
            ], changelog)
            changelog.flush()
            
            # Create test files
            files = []
            
            # setup.py
            with tempfile.NamedTemporaryFile(mode='w', suffix='setup.py', delete=False) as f:
                f.write('setup(name="test", version="1.2.3")')
                f.flush()
                files.append(f.name)
            
            # pyproject.toml
            with tempfile.NamedTemporaryFile(mode='w', suffix='pyproject.toml', delete=False) as f:
                f.write('[tool.poetry]\nversion = "1.2.3"')
                f.flush()
                files.append(f.name)
            
            try:
                # Simulate command line args
                import sys
                old_argv = sys.argv
                sys.argv = ["bump-version", changelog.name] + files
                
                # Capture output
                import io
                from contextlib import redirect_stdout
                output = io.StringIO()
                
                with redirect_stdout(output):
                    main()
                
                # Check output
                output_str = output.getvalue()
                assert "Bumping from 1.2.3 to 1.3.0" in output_str
                
                # Check files were updated
                for fname in files:
                    with open(fname) as f:
                        content = f.read()
                    assert "1.3.0" in content
                    assert "1.2.3" not in content
                
            finally:
                sys.argv = old_argv
                os.unlink(changelog.name)
                for fname in files:
                    os.unlink(fname)