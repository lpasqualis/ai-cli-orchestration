"""Configuration management for ACOR"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import yaml

from .constants import (
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_CONFIG_PATH,
    PROTOCOL_VERSION,
    ALLOWED_ENV_VARS,
    get_default_tools_dirs,
    is_safe_env_var
)
from .logging import get_logger, log_path_violation


@dataclass
class AcorConfig:
    """ACOR configuration with sensible defaults"""
    version: str = PROTOCOL_VERSION
    tools_dirs: List[str] = field(default_factory=get_default_tools_dirs)
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    
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
        """Expand environment variables in paths (with security validation)"""
        expanded = []
        env_var_pattern = re.compile(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?')
        
        for path in self.tools_dirs:
            # Check all environment variables in the path
            env_vars = env_var_pattern.findall(path)
            
            # Validate each environment variable
            safe_to_expand = True
            for var in env_vars:
                if not is_safe_env_var(var):
                    logger = get_logger()
                    logger.warning(f"Skipping unsafe environment variable ${var} in path: {path}")
                    log_path_violation(Path(path), f"Unsafe environment variable: ${var}")
                    safe_to_expand = False
                    break
            
            if safe_to_expand:
                # Only expand if all variables are safe
                expanded_path = os.path.expandvars(path)
            else:
                # Use the path as-is if it contains unsafe variables
                expanded_path = path
                
            # Ensure the path doesn't escape to parent directories
            if ".." in expanded_path:
                logger = get_logger()
                logger.warning(f"Skipping path with parent directory reference: {expanded_path}")
                log_path_violation(Path(expanded_path), "Contains parent directory reference (..)")
                continue
                
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
        config_path = DEFAULT_CONFIG_PATH
    
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
        
    except FileNotFoundError:
        # Config file doesn't exist - this is expected
        logger = get_logger()
        logger.info(f"Config file not found at {config_path}, using defaults")
        config = AcorConfig()
        config.expand_paths()
        return config
    except yaml.YAMLError as e:
        # YAML parsing error
        logger = get_logger()
        logger.error(f"Invalid YAML in config file {config_path}: {e}")
        logger.warning("Using default configuration due to YAML error")
        config = AcorConfig()
        config.expand_paths()
        return config
    except (OSError, IOError) as e:
        # File access error
        logger = get_logger()
        logger.error(f"Cannot read config file {config_path}: {e}")
        logger.warning("Using default configuration due to file access error") 
        config = AcorConfig()
        config.expand_paths()
        return config
    except Exception as e:
        # Unexpected error - log it but don't crash
        logger = get_logger()
        logger.error(f"Unexpected error loading config from {config_path}: {type(e).__name__}: {e}")
        logger.warning("Using default configuration due to unexpected error")
        config = AcorConfig()
        config.expand_paths()
        return config