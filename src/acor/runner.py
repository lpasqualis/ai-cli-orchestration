"""Core runner for executing tools and monitoring output"""

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import signal
import os

from .constants import (
    ErrorCodes,
    PROCESS_KILL_TIMEOUT_SECONDS,
    get_subprocess_env,
    SUBPROCESS_ENV_VARS
)
from .logging import get_logger, log_security_event, emit_warning, emit_error, emit_security_event


@dataclass
class RunnerResult:
    """Result from running a tool"""
    success: bool
    exit_code: int  # Uses ErrorCodes constants
    error_message: Optional[str] = None
    timed_out: bool = False


def run_tool(tool_path: Path, args: List[str], config) -> RunnerResult:
    """Execute a tool and stream its conversational output
    
    Args:
        tool_path: Path to the tool executable
        args: Arguments to pass to the tool
        config: AcorConfig instance
        
    Returns:
        RunnerResult with execution details
    """
    from .discovery import get_tool_command
    
    # Build the command
    # Convert to Path if string
    if isinstance(tool_path, str):
        tool_path = Path(tool_path)
    
    # Security: Re-validate the tool path immediately before execution
    # This prevents TOCTOU (time-of-check/time-of-use) attacks where
    # a symlink could be changed between discovery and execution
    tool_path = tool_path.resolve()  # Resolve symlinks to real path
    
    # Re-validate that the tool is still within allowed directories
    # This check only applies if we have configured tools directories
    # If no tools_dirs are configured (e.g., in tests or direct execution),
    # we trust the explicitly provided path
    if config.tools_dirs:
        # Get the configured tool directories from config
        allowed_dirs = []
        for tools_dir in config.tools_dirs:
            try:
                allowed_dirs.append(Path(tools_dir).resolve())
            except (OSError, RuntimeError):
                continue
        
        # Only enforce directory restrictions if we have configured directories
        if allowed_dirs:
            # Check if tool path is within any allowed directory
            is_within_allowed = False
            for allowed_dir in allowed_dirs:
                if str(tool_path).startswith(str(allowed_dir)):
                    is_within_allowed = True
                    break
            
            if not is_within_allowed:
                # Emit protocol-compliant security warning for AI
                emit_security_event("TOOL_PATH_WARNING",
                                  f"Tool {tool_path.name} executed outside configured directories",
                                  path=str(tool_path),
                                  configured_dirs=str(allowed_dirs))
    
    # Get base command and add user arguments
    base_command = get_tool_command(tool_path)
    # When using subprocess with a list (not shell=True), arguments are passed
    # safely without risk of injection - no need for additional quoting
    command = base_command + args
    
    # Create minimal environment for subprocess (security hardening)
    # Only pass whitelisted environment variables
    env = get_subprocess_env()
    env['ACOR_VERSION'] = config.version
    
    try:
        # Start the process with security hardening:
        # - Use process groups for better cleanup
        # - Don't use shell=True to prevent injection
        # - Set up process group for signal handling
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            universal_newlines=True,
            # Create new process group for better signal handling
            preexec_fn=os.setsid if os.name != 'nt' else None
        )
        
        try:
            # Wait for completion with timeout
            stdout, stderr = process.communicate(timeout=config.timeout)
            
            # Stream the output
            if stdout:
                sys.stdout.write(stdout)
                sys.stdout.flush()
            
            # Check for errors
            if process.returncode != 0 and stderr:
                emit_error("Tool Failed",
                          details=f"Exit code: {process.returncode}. {stderr}",
                          recovery="Check tool implementation or input parameters")
                
                return RunnerResult(
                    success=False,
                    exit_code=process.returncode if process.returncode else ErrorCodes.EXECUTION_FAILED,
                    error_message=stderr
                )
            
            # Success
            return RunnerResult(
                success=process.returncode == 0,
                exit_code=process.returncode
            )
            
        except subprocess.TimeoutExpired:
            # Kill the entire process group immediately on timeout
            # This prevents resource exhaustion attacks
            if os.name != 'nt':
                # Unix: kill the entire process group
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    # Process already dead - log for monitoring
                    logger = get_logger()
                    logger.debug(f"Process {process.pid} already terminated during killpg")
            else:
                # Windows: use terminate then kill
                process.kill()
            
            # Clean up zombie process
            try:
                process.wait(timeout=PROCESS_KILL_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                # Process cleanup failed - log for monitoring
                logger = get_logger()
                logger.error(f"Failed to cleanup process {process.pid} after timeout - potential zombie process")
                log_security_event("PROCESS_CLEANUP_FAILED", f"Process {process.pid} may be a zombie", tool=str(tool_path))
            
            emit_error("Tool Timeout",
                      details=f"Tool exceeded {config.timeout} second timeout",
                      recovery="Consider breaking the operation into smaller chunks or increasing timeout")
            
            return RunnerResult(
                success=False,
                exit_code=ErrorCodes.TIMEOUT,
                error_message=f"Tool exceeded {config.timeout}s timeout",
                timed_out=True
            )
            
    except FileNotFoundError as e:
        error_msg = f"Tool executable not found: {tool_path}"
        emit_error("File Not Found",
                  details=error_msg,
                  recovery="Ensure the tool is properly installed")
        
        return RunnerResult(
            success=False,
            exit_code=ErrorCodes.FILE_NOT_FOUND,
            error_message=error_msg
        )
        
    except PermissionError as e:
        error_msg = f"Permission denied executing tool: {tool_path}"
        emit_error("Permission Denied",
                  details=error_msg,
                  recovery="Check file permissions (chmod +x)")
        
        return RunnerResult(
            success=False,
            exit_code=ErrorCodes.PERMISSION_DENIED,
            error_message=error_msg
        )
        
    except Exception as e:
        error_msg = f"Unexpected error running tool: {e}"
        emit_error("Unexpected Error",
                  details=error_msg,
                  recovery="Check system logs for more details")
        
        return RunnerResult(
            success=False,
            exit_code=ErrorCodes.GENERAL_ERROR,
            error_message=str(e)
        )


def validate_tool_path(tool_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate that a tool path exists and is accessible
    
    Args:
        tool_path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tool_path.exists():
        return False, f"Tool not found: {tool_path}"
    
    if not tool_path.is_file():
        return False, f"Tool path is not a file: {tool_path}"
    
    # Check file permissions based on file type
    if tool_path.suffix == '.py':
        # Python files just need to be readable
        if not os.access(tool_path, os.R_OK):
            return False, f"Python script is not readable: {tool_path}"
    elif tool_path.suffix == '.sh':
        # Shell scripts need to be readable and preferably executable
        if not os.access(tool_path, os.R_OK):
            return False, f"Shell script is not readable: {tool_path}"
        # Warn if not executable but don't fail (will run with bash)
        if not os.access(tool_path, os.X_OK):
            logger = get_logger()
            logger.warning(f"Shell script is not executable: {tool_path}")
    elif tool_path.suffix == '.js':
        # JavaScript files just need to be readable
        if not os.access(tool_path, os.R_OK):
            return False, f"JavaScript file is not readable: {tool_path}"
    else:
        # Binary executables must have execute permission
        if not os.access(tool_path, os.X_OK):
            return False, f"Tool is not executable: {tool_path}"
    
    return True, None