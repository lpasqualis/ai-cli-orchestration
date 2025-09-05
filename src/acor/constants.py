"""Constants and configuration defaults for ACOR"""

import os
from typing import List

# Version and compatibility
PROTOCOL_VERSION = "1"
MIN_PYTHON_VERSION = (3, 8)

# Default configuration values
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_TOOLS_DIRS = [".acor/tools", "tools", "examples/tools"]
DEFAULT_CONFIG_PATH = ".acor/config.yaml"

# Process management
PROCESS_KILL_TIMEOUT_SECONDS = 1  # Time to wait after SIGKILL
PROCESS_GROUP_TIMEOUT_MS = 1000   # Milliseconds

# Environment variables
# Whitelist of environment variables that can be safely expanded in paths
ALLOWED_ENV_VARS = frozenset([
    "HOME",
    "USER",
    "ACOR_HOME",
    "ACOR_TOOLS",
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
])

# Whitelist of environment variables passed to subprocesses
SUBPROCESS_ENV_VARS = frozenset([
    "PATH",
    "HOME", 
    "USER",
    "LANG",
    "LC_ALL",
    "PYTHONPATH",
    "NODE_PATH",
    "ACOR_VERSION",
    "ACOR_OUTPUT_MODE",  # Allow tools to inherit output mode
])

# Output modes
OUTPUT_MODE_AI = "ai"
OUTPUT_MODE_HUMAN = "human"
DEFAULT_OUTPUT_MODE = OUTPUT_MODE_AI  # Default to AI mode for backward compatibility

# Error codes (standardized across the application)
class ErrorCodes:
    """Standardized error codes for ACOR"""
    SUCCESS = 0
    GENERAL_ERROR = 1
    TOOL_NOT_FOUND = 2
    INVALID_CONFIG = 3
    TIMEOUT = 4
    PERMISSION_DENIED = 5
    INVALID_ARGUMENT = 6
    EXECUTION_FAILED = 7
    FILE_NOT_FOUND = 8
    VALIDATION_FAILED = 9

# File patterns
ENTRY_POINT_PATTERNS = [
    'cli.py',
    'main.py', 
    'tool.py',
    'cli.sh',
    'tool.sh',
    'cli.js',
    'tool.js'
]

# Validation patterns
import re
VALID_TOOL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
MAX_TOOL_NAME_LENGTH = 50

# Template validation
FORBIDDEN_TEMPLATE_PATTERNS = [
    r'exec\s*\(',           # exec() calls
    r'eval\s*\(',           # eval() calls  
    r'__import__',          # Dynamic imports
    r'compile\s*\(',        # compile() calls
    r'globals\s*\(',        # globals() access
    r'locals\s*\(',         # locals() access
    r'open\s*\([^)]*[\'"]w', # File write operations in templates
]

# Progress percentages (for consistency)
PROGRESS_START = 0
PROGRESS_QUARTER = 25
PROGRESS_HALF = 50
PROGRESS_THREE_QUARTERS = 75
PROGRESS_COMPLETE = 100

def get_default_tools_dirs() -> List[str]:
    """Get default tools directories, with environment variable support"""
    # Check for ACOR_TOOLS environment variable
    if "ACOR_TOOLS" in os.environ:
        custom_dirs = os.environ["ACOR_TOOLS"].split(os.pathsep)
        return custom_dirs + DEFAULT_TOOLS_DIRS
    return DEFAULT_TOOLS_DIRS.copy()

def is_safe_env_var(var_name: str) -> bool:
    """Check if an environment variable is safe to expand"""
    # Extract variable name from ${VAR} or $VAR format
    var_name = var_name.strip("${}")
    return var_name in ALLOWED_ENV_VARS

def get_subprocess_env() -> dict:
    """Get a safe environment dictionary for subprocesses"""
    env = {}
    for var in SUBPROCESS_ENV_VARS:
        if var in os.environ:
            env[var] = os.environ[var]
    return env