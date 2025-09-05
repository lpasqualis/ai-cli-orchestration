"""Tool discovery system for ACOR"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .logging import get_logger, log_security_event, log_interpreter_fallback, emit_warning


# Standard entry point filenames for tools
ENTRY_POINTS = [
    'cli.py',
    'main.py',
    'tool.py',
    'cli.sh',
    'tool.sh',
    'cli.js',
    'tool.js'
]


def discover_tools(tools_dirs: List[str]) -> Dict[str, Path]:
    """Discover available tools in configured directories
    
    Args:
        tools_dirs: List of directories to search for tools
        
    Returns:
        Dictionary mapping tool names to their executable paths
    """
    tools = {}
    
    # Validate tool name pattern (alphanumeric, underscore, hyphen only)
    VALID_TOOL_NAME = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    for tools_dir in tools_dirs:
        dir_path = Path(tools_dir).resolve()  # Resolve to absolute path
        
        # Skip if directory doesn't exist
        if not dir_path.exists() or not dir_path.is_dir():
            continue
        
        # Check each subdirectory as a potential tool
        for item in dir_path.iterdir():
            if not item.is_dir():
                continue
            
            tool_name = item.name
            
            # Security: Validate tool name to prevent path traversal
            if not VALID_TOOL_NAME.match(tool_name):
                # Skip tools with invalid names (could be malicious)
                logger = get_logger()
                logger.warning(f"Skipping tool with invalid name: {tool_name}")
                log_security_event("INVALID_TOOL_NAME", f"Tool name failed validation: {tool_name}", path=str(item))
                continue
            
            # Security: Ensure the tool directory is actually within the tools_dir
            # This prevents symlink attacks and directory traversal
            try:
                item_resolved = item.resolve()
                if not str(item_resolved).startswith(str(dir_path)):
                    # Tool directory escapes the configured tools directory
                    logger = get_logger()
                    logger.warning(f"Tool directory {item} escapes parent directory {dir_path}")
                    log_security_event("PATH_ESCAPE", f"Tool path escape attempt", tool=tool_name, path=str(item_resolved))
                    continue
            except (OSError, RuntimeError) as e:
                # Skip if we can't resolve the path (broken symlink, etc)
                logger = get_logger()
                logger.debug(f"Cannot resolve tool path {item}: {e}")
                continue
                
            # Look for entry point files
            tool_path = find_tool_entry(item)
            if tool_path:
                # Security: Validate that the tool path is within the tool directory
                try:
                    tool_path_resolved = tool_path.resolve()
                    if not str(tool_path_resolved).startswith(str(item_resolved)):
                        # Entry point escapes the tool directory
                        logger = get_logger()
                        logger.warning(f"Tool entry point {tool_path} escapes tool directory {item}")
                        log_security_event("ENTRY_POINT_ESCAPE", f"Entry point escape attempt", tool=tool_name, path=str(tool_path_resolved))
                        continue
                except (OSError, RuntimeError) as e:
                    logger = get_logger()
                    logger.debug(f"Cannot resolve entry point path {tool_path}: {e}")
                    continue
                
                # Don't overwrite if tool already found (first match wins)
                if tool_name not in tools:
                    tools[tool_name] = tool_path
    
    return tools


def find_tool_entry(tool_dir: Path) -> Optional[Path]:
    """Find the entry point file for a tool
    
    Args:
        tool_dir: Directory containing the tool
        
    Returns:
        Path to the entry point file, or None if not found
    """
    for entry_point in ENTRY_POINTS:
        entry_path = tool_dir / entry_point
        if entry_path.exists() and entry_path.is_file():
            # Make sure it's executable or a Python/JS file
            if entry_path.suffix in ['.py', '.js', '.sh']:
                return entry_path
            elif os.access(entry_path, os.X_OK):
                return entry_path
    
    return None


def _find_interpreter(name: str) -> Optional[str]:
    """Find the absolute path to an interpreter
    
    Args:
        name: Name of the interpreter (python, bash, node)
        
    Returns:
        Absolute path to the interpreter, or None if not found
    """
    # For Python, use the current Python interpreter
    if name == 'python':
        return sys.executable
    
    # For other interpreters, look in standard locations
    # This is more secure than using PATH lookup
    standard_paths = [
        '/usr/bin',
        '/bin',
        '/usr/local/bin',
        '/opt/homebrew/bin',  # macOS with Homebrew
    ]
    
    for path_dir in standard_paths:
        interpreter_path = Path(path_dir) / name
        if interpreter_path.exists() and os.access(interpreter_path, os.X_OK):
            return str(interpreter_path)
    
    # Fallback: use shutil.which() but log a warning
    which_result = shutil.which(name)
    if which_result:
        # Log this for security monitoring
        log_interpreter_fallback(name, which_result)
        return which_result
    
    return None


def get_tool_command(tool_path: Path) -> List[str]:
    """Get the command to execute a tool based on its file type
    
    Args:
        tool_path: Path to the tool's entry point
        
    Returns:
        List of command parts to execute the tool
        
    Raises:
        RuntimeError: If required interpreter is not found
    """
    suffix = tool_path.suffix
    
    if suffix == '.py':
        interpreter = _find_interpreter('python')
        if not interpreter:
            raise RuntimeError(f"Python interpreter not found for {tool_path}")
        return [interpreter, str(tool_path)]
    elif suffix == '.sh':
        interpreter = _find_interpreter('bash')
        if not interpreter:
            raise RuntimeError(f"Bash interpreter not found for {tool_path}")
        return [interpreter, str(tool_path)]
    elif suffix == '.js':
        interpreter = _find_interpreter('node')
        if not interpreter:
            raise RuntimeError(f"Node interpreter not found for {tool_path}")
        return [interpreter, str(tool_path)]
    else:
        # Assume it's directly executable
        return [str(tool_path)]