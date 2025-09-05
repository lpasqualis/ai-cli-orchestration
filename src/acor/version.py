"""Version management for ACOR

Version format: MAJOR.MINOR.REVISION
- MAJOR: Breaking changes, incompatible API changes
- MINOR: New features, backwards compatible
- REVISION: Bug fixes, patches
"""

from typing import Tuple, Optional
import sys

# Version components
MAJOR = 0
MINOR = 1
REVISION = 0

# Full version string (standard semantic versioning, no padding)
VERSION = f"{MAJOR}.{MINOR}.{REVISION}"

# Version metadata
VERSION_INFO = {
    "major": MAJOR,
    "minor": MINOR,
    "revision": REVISION,
    "version": VERSION,
    "release_date": "2025-01-05",
    "codename": "Genesis"  # Optional codename for major releases
}

def get_version():
    """Get the current version string"""
    return VERSION

def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO

def parse_version(version_string: str) -> Tuple[int, int, int]:
    """Parse a version string into components
    
    Args:
        version_string: Version string in format 'X.Y.Z'
        
    Returns:
        Tuple of (major, minor, revision)
        
    Raises:
        ValueError: If version string is invalid
    """
    try:
        parts = version_string.strip().split('.')
        if len(parts) != 3:
            raise ValueError(f"Version must have 3 parts (X.Y.Z), got: {version_string}")
        
        major = int(parts[0])
        minor = int(parts[1])
        revision = int(parts[2])
        
        if major < 0 or minor < 0 or revision < 0:
            raise ValueError(f"Version components must be non-negative, got: {version_string}")
        
        return (major, minor, revision)
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid version string '{version_string}': {e}")

def check_compatibility(required_version: str, current_version: Optional[str] = None) -> bool:
    """Check if current version is compatible with required version
    
    Compatibility rules:
    - Major version must match exactly (breaking changes)
    - Minor version must be >= required (backwards compatible)
    - Revision is ignored for compatibility (bug fixes only)
    
    Args:
        required_version: Minimum required version
        current_version: Current version (defaults to ACOR version)
        
    Returns:
        True if compatible, False otherwise
    """
    if current_version is None:
        current_version = VERSION
    
    try:
        req_major, req_minor, _ = parse_version(required_version)
        cur_major, cur_minor, _ = parse_version(current_version)
        
        # Major version must match exactly
        if cur_major != req_major:
            return False
        
        # Minor version must be >= required
        if cur_minor < req_minor:
            return False
        
        return True
    except ValueError:
        return False

def check_python_version(min_version: Tuple[int, int] = (3, 8)) -> bool:
    """Check if Python version meets minimum requirements
    
    Args:
        min_version: Minimum Python version as (major, minor)
        
    Returns:
        True if Python version is sufficient, False otherwise
    """
    return sys.version_info >= min_version

def get_version_string(major: int, minor: int, revision: int) -> str:
    """Format version components into a version string
    
    Args:
        major: Major version number
        minor: Minor version number  
        revision: Revision number
        
    Returns:
        Formatted version string
    """
    return f"{major}.{minor}.{revision}"

# Protocol version for the conversation protocol
PROTOCOL_VERSION = "1"

def check_protocol_compatibility(tool_protocol: str) -> bool:
    """Check if a tool's protocol version is compatible
    
    Currently only protocol version "1" is supported.
    Future versions will need compatibility logic.
    
    Args:
        tool_protocol: Protocol version used by the tool
        
    Returns:
        True if compatible, False otherwise
    """
    return tool_protocol == PROTOCOL_VERSION