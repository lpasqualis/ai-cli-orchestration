"""Tool discovery system for ACOR"""

import os
from pathlib import Path
from typing import Dict, List, Optional


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
    
    for tools_dir in tools_dirs:
        dir_path = Path(tools_dir)
        
        # Skip if directory doesn't exist
        if not dir_path.exists() or not dir_path.is_dir():
            continue
        
        # Check each subdirectory as a potential tool
        for item in dir_path.iterdir():
            if not item.is_dir():
                continue
                
            # Look for entry point files
            tool_path = find_tool_entry(item)
            if tool_path:
                tool_name = item.name
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


def get_tool_command(tool_path: Path) -> List[str]:
    """Get the command to execute a tool based on its file type
    
    Args:
        tool_path: Path to the tool's entry point
        
    Returns:
        List of command parts to execute the tool
    """
    suffix = tool_path.suffix
    
    if suffix == '.py':
        return ['python', str(tool_path)]
    elif suffix == '.sh':
        return ['bash', str(tool_path)]
    elif suffix == '.js':
        return ['node', str(tool_path)]
    else:
        # Assume it's directly executable
        return [str(tool_path)]