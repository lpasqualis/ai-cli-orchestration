"""Configuration management for ACOR"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import yaml


@dataclass
class AcorConfig:
    """ACOR configuration with sensible defaults"""
    version: str = "1"
    tools_dirs: List[str] = field(default_factory=lambda: [".acor/tools", "tools"])
    timeout: int = 120  # seconds
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AcorConfig':
        """Create config from dictionary"""
        config = cls()
        
        if 'version' in data:
            config.version = str(data['version'])
        
        if 'tools_dirs' in data:
            config.tools_dirs = data['tools_dirs']
            
        if 'timeout' in data:
            config.timeout = int(data['timeout'])
            
        return config
    
    def expand_paths(self) -> None:
        """Expand environment variables in paths"""
        expanded = []
        for path in self.tools_dirs:
            expanded_path = os.path.expandvars(path)
            expanded.append(expanded_path)
        self.tools_dirs = expanded


def load_config(config_path: Optional[str] = None) -> AcorConfig:
    """Load configuration from YAML file
    
    Args:
        config_path: Optional path to config file. Defaults to .acor/config.yaml
        
    Returns:
        AcorConfig instance with loaded or default values
    """
    # Determine config path
    if config_path is None:
        config_path = ".acor/config.yaml"
    
    config_file = Path(config_path)
    
    # Use defaults if no config file exists
    if not config_file.exists():
        config = AcorConfig()
        config.expand_paths()
        return config
    
    try:
        # Load and parse YAML
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        # Create config from loaded data
        config = AcorConfig.from_dict(data)
        
        # Expand environment variables
        config.expand_paths()
        
        return config
        
    except Exception as e:
        # If there's an error loading config, use defaults and warn
        print(f"Warning: Error loading config from {config_path}: {e}")
        print("Using default configuration")
        config = AcorConfig()
        config.expand_paths()
        return config