"""Core runner for executing tools and monitoring output"""

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import signal
import os


@dataclass
class RunnerResult:
    """Result from running a tool"""
    success: bool
    exit_code: int
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
    command = get_tool_command(tool_path) + args
    
    # Set environment variables
    env = os.environ.copy()
    env['ACOR_VERSION'] = config.version
    
    try:
        # Start the process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            universal_newlines=True
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
                print(f"\n## Error: Tool Failed")
                print(f"Exit code: {process.returncode}")
                if stderr:
                    print(f"\n**Details**: {stderr}")
                
                return RunnerResult(
                    success=False,
                    exit_code=process.returncode,
                    error_message=stderr
                )
            
            # Success
            return RunnerResult(
                success=process.returncode == 0,
                exit_code=process.returncode
            )
            
        except subprocess.TimeoutExpired:
            # Kill the process on timeout
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            print("## Error: Tool Timeout")
            print(f"Tool exceeded {config.timeout} second timeout")
            print("\n**Recovery**: Consider breaking the operation into smaller chunks or increasing timeout")
            
            return RunnerResult(
                success=False,
                exit_code=-1,
                error_message=f"Tool exceeded {config.timeout}s timeout",
                timed_out=True
            )
            
    except FileNotFoundError as e:
        error_msg = f"Tool executable not found: {tool_path}"
        print(f"## Error: {error_msg}")
        print(f"\n**Recovery**: Ensure the tool is properly installed")
        
        return RunnerResult(
            success=False,
            exit_code=-1,
            error_message=error_msg
        )
        
    except PermissionError as e:
        error_msg = f"Permission denied executing tool: {tool_path}"
        print(f"## Error: {error_msg}")
        print(f"\n**Recovery**: Check file permissions (chmod +x)")
        
        return RunnerResult(
            success=False,
            exit_code=-1,
            error_message=error_msg
        )
        
    except Exception as e:
        error_msg = f"Unexpected error running tool: {e}"
        print(f"## Error: {error_msg}")
        
        return RunnerResult(
            success=False,
            exit_code=-1,
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
    
    # Check if it's a script that needs an interpreter
    if tool_path.suffix in ['.py', '.sh', '.js']:
        # These are OK - will be run with interpreter
        return True, None
    
    # Otherwise check if it's executable
    if not os.access(tool_path, os.X_OK):
        return False, f"Tool is not executable: {tool_path}"
    
    return True, None