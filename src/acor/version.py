"""Version management for ACOR

Version format: MAJOR.MINOR.REVISION
- MAJOR: Breaking changes, incompatible API changes
- MINOR: New features, backwards compatible
- REVISION: Bug fixes, patches
"""

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