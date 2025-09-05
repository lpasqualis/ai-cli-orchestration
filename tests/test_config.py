"""Tests for the config module"""

import pytest
import tempfile
import os
from pathlib import Path
from acor.config import AcorConfig, load_config


class TestAcorConfig:
    """Test AcorConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AcorConfig()
        
        assert config.version == "1"
        assert config.tools_dirs == [".acor/tools", "tools", "examples/tools"]
        assert config.timeout == 120
        
    def test_custom_config(self):
        """Test custom configuration"""
        config = AcorConfig(
            version="2",
            tools_dirs=["custom/tools", "other/tools"],
            timeout=300
        )
        
        assert config.version == "2"
        assert config.tools_dirs == ["custom/tools", "other/tools"]
        assert config.timeout == 300


class TestLoadConfig:
    """Test config loading functionality"""
    
    def test_load_default_config(self):
        """Test loading config with no file present"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary empty file path that doesn't exist
            fake_config = Path(tmpdir) / "nonexistent" / "config.yaml"
            
            # Load config from non-existent path should return defaults
            config = load_config(str(fake_config))
            assert config.version == "1"
            assert config.tools_dirs == [".acor/tools", "tools", "examples/tools"]
            assert config.timeout == 120
    
    def test_load_project_config(self):
        """Test loading config from explicit path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
version: "1"
tools_dirs:
  - "my_tools"
  - "lib/tools"
timeout: 60
""")
            config_path = f.name
        
        try:
            config = load_config(config_path)
            assert config.version == "1"
            assert config.tools_dirs == ["my_tools", "lib/tools"]
            assert config.timeout == 60
        finally:
            os.unlink(config_path)
    
    def test_load_explicit_config_path(self):
        """Test loading config from explicit path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
version: "1"
tools_dirs:
  - "explicit/tools"
timeout: 240
""")
            config_path = f.name
        
        try:
            config = load_config(config_path)
            assert config.version == "1"
            assert config.tools_dirs == ["explicit/tools"]
            assert config.timeout == 240
        finally:
            os.unlink(config_path)
    
    def test_invalid_config_path(self):
        """Test loading config from non-existent path"""
        config = load_config("/nonexistent/config.yaml")
        # Should return defaults when file doesn't exist
        assert config.version == "1"
        assert config.tools_dirs == [".acor/tools", "tools", "examples/tools"]
        assert config.timeout == 120