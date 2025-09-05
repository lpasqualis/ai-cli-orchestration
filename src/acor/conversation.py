"""ACOR Conversational Protocol Implementation

Provides the AcorTool class for tool-to-AI communication using structured Markdown output.
"""

import json
import sys
import threading
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from contextlib import contextmanager


class ToolState(Enum):
    """Final states for tool completion"""
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AcorTool:
    """Main interface for ACOR tool communication"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize an ACOR tool
        
        Args:
            name: Tool identifier
            version: Tool version (defaults to "1.0.0")
        """
        self.name = name
        self.version = version
        self._started = False
        self._stopped = False
        self._lock = threading.Lock()
        self._ai_directives = []
        
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic error handling"""
        if exc_type is not None:
            # Check if it's a SystemExit with code 0 (normal exit from input_needed)
            if exc_type is SystemExit and exc_val.code == 0:
                # This is expected from input_needed(), don't treat as error
                return False
            
            # An actual error occurred
            self.error(
                "E_EXCEPTION",
                f"Tool failed with {exc_type.__name__}: {exc_val}",
                recovery="Check error details and retry"
            )
            self.stop(state=ToolState.FAILED)
        else:
            # Normal completion
            self.stop(state=ToolState.COMPLETE)
        # Don't suppress the exception
        return False
    
    def _emit(self, message: str) -> None:
        """Thread-safe emission of messages to stdout"""
        with self._lock:
            print(message, flush=True)
            sys.stdout.flush()
    
    def start(self) -> 'AcorTool':
        """Initialize tool and emit ready status
        
        Returns:
            self for method chaining
        """
        if self._started:
            return self
        self._started = True
        self._emit("## Status: Ready")
        return self
    
    def stop(self, state: ToolState = ToolState.COMPLETE) -> 'AcorTool':
        """Complete tool execution and emit final status
        
        Args:
            state: Final state (COMPLETE, FAILED, or CANCELLED)
            
        Returns:
            self for method chaining
        """
        if self._stopped:
            return self
            
        # Flush any pending AI directives
        self._flush_ai_directives()
        
        self._stopped = True
        status_map = {
            ToolState.COMPLETE: "Complete",
            ToolState.FAILED: "Failed", 
            ToolState.CANCELLED: "Cancelled"
        }
        self._emit(f"## Status: {status_map[state]}")
        return self
    
    def status(self, state: str, message: str = "") -> 'AcorTool':
        """Report current operational state
        
        Args:
            state: One of "ready", "working", "complete", "failed"
            message: Optional descriptive message
            
        Returns:
            self for method chaining
        """
        self._validate_started()
        state_capitalized = state.capitalize()
        self._emit(f"## Status: {state_capitalized}")
        if message:
            self._emit(message)
        return self
    
    def progress(self, percentage: Union[int, float], message: str = "") -> 'AcorTool':
        """Report work progress
        
        Args:
            percentage: Progress (0-100 as int, or 0.0-1.0 as float)
            message: Optional progress description
            
        Returns:
            self for method chaining
        """
        self._validate_started()
        
        # Convert float (0.0-1.0) to percentage if needed
        if isinstance(percentage, float) and percentage <= 1.0:
            percentage = int(percentage * 100)
        
        # Ensure percentage is within bounds
        percentage = max(0, min(100, int(percentage)))
        
        self._emit(f"## Progress: {percentage}%")
        if message:
            self._emit(message)
        return self
    
    def output(self, data: Any, format: str = "auto") -> 'AcorTool':
        """Emit primary output/result data
        
        Args:
            data: Output data (dict, list, string, etc.)
            format: Output format ("auto", "json", "yaml", "text", "markdown")
            
        Returns:
            self for method chaining
        """
        self._validate_started()
        
        if isinstance(data, str):
            # Simple text output
            self._emit("## Output")
            self._emit(data)
        else:
            # Structured data
            self._emit("## Output Data")
            
            # Auto-detect format
            if format == "auto":
                format = "json"  # Default to JSON for structured data
            
            if format == "json":
                self._emit("```json")
                self._emit(json.dumps(data, indent=2))
                self._emit("```")
            elif format == "yaml":
                # Simple YAML formatting (full yaml library not required for MVP)
                self._emit("```yaml")
                self._emit(self._to_simple_yaml(data))
                self._emit("```")
            elif format == "markdown":
                self._emit(str(data))
            else:
                # Plain text
                self._emit(str(data))
        
        return self
    
    def error(self, code: str, message: str, recovery: str = None, details: str = None) -> 'AcorTool':
        """Report error condition with recovery guidance
        
        Args:
            code: Error code (e.g., "E_FILE_NOT_FOUND")
            message: Human-readable error message
            recovery: Optional recovery instructions
            details: Optional technical details
            
        Returns:
            self for method chaining
        """
        # Remove error code prefix from message if it's there
        display_message = message.replace(code + ": ", "").replace(code, "")
        
        self._emit(f"## Error: {display_message}")
        
        if details:
            self._emit(f"\n**Details**: {details}")
            
        if recovery:
            self._emit(f"\n**Recovery**: {recovery}")
        
        return self
    
    def input_needed(self, message: str) -> None:
        """Request required input from AI - tool exits after this
        
        Args:
            message: Complete message with instructions and examples
        """
        self._emit("## Input Needed")
        self._emit(message)
        # Tool is expected to exit after requesting input
        sys.exit(0)
    
    def ai_directive(self, message: str) -> 'AcorTool':
        """Request specific action from AI agent
        
        Multiple calls accumulate into a single directive section.
        
        Args:
            message: Clear instruction for the AI
            
        Returns:
            self for method chaining
        """
        self._validate_started()
        self._ai_directives.append(message)
        return self
    
    def suggestions(self, suggestions: List[str], title: str = None) -> 'AcorTool':
        """Provide optional next steps for AI consideration
        
        Args:
            suggestions: List of suggested actions
            title: Optional section title
            
        Returns:
            self for method chaining
        """
        self._validate_started()
        
        if title:
            self._emit(f"## Suggestions: {title}")
        else:
            self._emit("## Suggestions")
        
        for suggestion in suggestions:
            self._emit(f"- {suggestion}")
        
        return self
    
    def _validate_started(self) -> None:
        """Ensure tool has been started before emitting messages"""
        if not self._started:
            raise RuntimeError(
                "Tool must be started before emitting messages. "
                "Call start() or use context manager."
            )
        if self._stopped:
            raise RuntimeError("Cannot emit messages after stop() has been called")
    
    def _flush_ai_directives(self) -> None:
        """Flush accumulated AI directives"""
        if self._ai_directives:
            self._emit("## AI Directive")
            for directive in self._ai_directives:
                self._emit(f"- {directive}")
            self._ai_directives = []
    
    def _to_simple_yaml(self, data: Any, indent: int = 0) -> str:
        """Convert data to simple YAML format (MVP implementation)"""
        spaces = "  " * indent
        
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{spaces}{key}:")
                    lines.append(self._to_simple_yaml(value, indent + 1))
                else:
                    lines.append(f"{spaces}{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(f"{spaces}-")
                    lines.append(self._to_simple_yaml(item, indent + 1))
                else:
                    lines.append(f"{spaces}- {item}")
            return "\n".join(lines)
        else:
            return f"{spaces}{data}"