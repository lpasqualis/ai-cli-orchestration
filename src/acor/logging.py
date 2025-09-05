"""Logging utilities for ACOR"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> logging.Logger:
    """Set up logging configuration for ACOR
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("acor")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler - only warnings and above to stderr
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging to {log_file}: {e}")
    
    return logger


def get_logger() -> logging.Logger:
    """Get the ACOR logger instance
    
    Returns:
        Logger instance
    """
    return logging.getLogger("acor")


# Security event logging functions
def log_security_event(event_type: str, message: str, **context):
    """Log a security-relevant event
    
    Args:
        event_type: Type of security event
        message: Event description
        **context: Additional context data
    """
    logger = get_logger()
    context_str = " ".join([f"{k}={v}" for k, v in context.items()])
    logger.warning(f"SECURITY [{event_type}]: {message} {context_str}")


def log_path_violation(path: Path, reason: str):
    """Log a path security violation
    
    Args:
        path: The problematic path
        reason: Why it was rejected
    """
    log_security_event("PATH_VIOLATION", f"Rejected path: {path}", reason=reason)


def log_interpreter_fallback(interpreter: str, found_path: str):
    """Log when using fallback interpreter discovery
    
    Args:
        interpreter: Name of interpreter
        found_path: Path that was found
    """
    log_security_event("INTERPRETER_FALLBACK", 
                      f"Using PATH lookup for {interpreter}", 
                      found=found_path)


# Output mode detection
def get_output_mode() -> str:
    """Get the current output mode (ai or human)
    
    Returns:
        "ai" for AI protocol mode, "human" for human-readable mode
    """
    from .constants import OUTPUT_MODE_AI, OUTPUT_MODE_HUMAN, DEFAULT_OUTPUT_MODE
    return os.environ.get('ACOR_OUTPUT_MODE', DEFAULT_OUTPUT_MODE).lower()


# AI Protocol-compliant output functions
def emit_error(title: str, details: Optional[str] = None, recovery: Optional[str] = None):
    """Emit an error message in ACOR protocol format or human format based on mode
    
    Args:
        title: Brief error description
        details: Optional detailed error information
        recovery: Optional recovery instructions for AI
    """
    from .constants import OUTPUT_MODE_AI
    
    mode = get_output_mode()
    if mode == OUTPUT_MODE_AI:
        # AI protocol format
        print(f"## Error: {title}")
        if details:
            print(f"**Details**: {details}")
        if recovery:
            print(f"**Recovery**: {recovery}")
        print()  # Empty line for readability
    else:
        # Human-readable format
        print(f"Error: {title}", file=sys.stderr)
        if details:
            print(f"  {details}", file=sys.stderr)
        if recovery:
            print(f"  Suggestion: {recovery}", file=sys.stderr)
    
    # Also log to traditional logger
    logger = get_logger()
    error_msg = f"{title}"
    if details:
        error_msg += f" - {details}"
    logger.error(error_msg)


def emit_warning(title: str, details: Optional[str] = None):
    """Emit a warning in ACOR protocol format or human format based on mode
    
    Args:
        title: Brief warning description
        details: Optional detailed warning information
    """
    from .constants import OUTPUT_MODE_AI
    
    mode = get_output_mode()
    if mode == OUTPUT_MODE_AI:
        # AI protocol format
        print(f"## Warning: {title}")
        if details:
            print(f"**Details**: {details}")
        print()
    else:
        # Human-readable format
        print(f"Warning: {title}", file=sys.stderr)
        if details:
            print(f"  {details}", file=sys.stderr)
    
    # Also log to traditional logger
    logger = get_logger()
    warning_msg = f"{title}"
    if details:
        warning_msg += f" - {details}"
    logger.warning(warning_msg)


def emit_status(state: str, message: Optional[str] = None):
    """Emit a status message in ACOR protocol format or human format based on mode
    
    Args:
        state: Status state (Ready, Working, Complete, Failed)
        message: Optional status message
    """
    from .constants import OUTPUT_MODE_AI
    
    mode = get_output_mode()
    if mode == OUTPUT_MODE_AI:
        # AI protocol format
        print(f"## Status: {state}")
        if message:
            print(message)
        print()
    else:
        # Human-readable format - only show meaningful status changes
        # In human mode, we typically don't need protocol status messages
        if message:
            print(message)


def emit_security_event(event_type: str, message: str, **context):
    """Emit a security event in both protocol and log format
    
    Args:
        event_type: Type of security event
        message: Event description
        **context: Additional context data
    """
    from .constants import OUTPUT_MODE_AI
    
    mode = get_output_mode()
    if mode == OUTPUT_MODE_AI:
        # Emit as warning in protocol format for AI
        details = " | ".join([f"{k}={v}" for k, v in context.items()]) if context else None
        emit_warning(f"Security: {event_type}", details=f"{message}. {details}" if details else message)
    else:
        # In human mode, log security events to stderr but less verbose
        logger = get_logger()
        logger.warning(f"Security: {message}")
    
    # Always log traditionally for monitoring
    log_security_event(event_type, message, **context)