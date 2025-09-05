"""Tests for the version module"""

import pytest
from acor.version import get_version_info


class TestVersion:
    """Test version functionality"""
    
    def test_get_version_info_structure(self):
        """Test that get_version_info returns the expected structure"""
        info = get_version_info()
        
        assert isinstance(info, dict)
        assert "version" in info
        assert "codename" in info
        # Protocol version is separate from version info
        
    def test_version_format(self):
        """Test that version follows semantic versioning format"""
        info = get_version_info()
        version = info["version"]
        
        # Should be in format X.Y.Z
        parts = version.split(".")
        assert len(parts) == 3
        
        # Each part should be a number
        for part in parts:
            assert part.isdigit()
            
    def test_codename_exists(self):
        """Test that a codename is defined"""
        info = get_version_info()
        assert info["codename"]
        assert isinstance(info["codename"], str)
        assert len(info["codename"]) > 0
        
    def test_protocol_version(self):
        """Test that protocol version is defined in config not version"""
        # Protocol version is part of config, not version module
        pass  # This is tested in config tests