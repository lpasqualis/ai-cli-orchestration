"""ACOR - AI-CLI Orchestration Runner

Enable AI agents to orchestrate CLI tools through structured conversation protocol.
"""

from enum import Enum
from .version import VERSION, get_version, get_version_info

# Export version at package level
__version__ = VERSION


class ToolState(Enum):
    """Final states for tool completion"""
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


from .conversation import AcorTool

__all__ = ['AcorTool', 'ToolState', '__version__']