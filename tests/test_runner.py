"""Tests for the runner module"""

import pytest
import tempfile
import subprocess
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from acor.runner import run_tool, RunnerResult
from acor.config import AcorConfig


class TestRunTool:
    """Test the run_tool function"""
    
    def test_run_python_tool_success(self):
        """Test running a Python tool successfully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple Python tool
            tool_path = Path(tmpdir) / "test.py"
            tool_path.write_text("""#!/usr/bin/env python3
import sys
print("## Status: Ready")
print("## Output")
print("Tool output")
print("## Status: Complete")
sys.exit(0)
""")
            tool_path.chmod(0o755)
            
            config = AcorConfig()
            
            # Run the tool
            result = run_tool(tool_path, ["arg1", "arg2"], config)
            
            assert result.success == True
            assert result.exit_code == 0
            assert result.timed_out == False
    
    def test_run_python_tool_with_error(self):
        """Test running a Python tool that returns error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "test.py"
            tool_path.write_text("""#!/usr/bin/env python3
import sys
print("## Status: Ready")
print("## Error: Something went wrong")
sys.exit(1)
""")
            tool_path.chmod(0o755)
            
            config = AcorConfig()
            result = run_tool(tool_path, [], config)
            
            assert result.success == False
            assert result.exit_code == 1
    
    def test_run_tool_with_timeout(self):
        """Test that tool times out properly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "slow.py"
            tool_path.write_text("""#!/usr/bin/env python3
import time
print("## Status: Ready")
time.sleep(10)  # Sleep longer than timeout
print("## Status: Complete")
""")
            tool_path.chmod(0o755)
            
            # Use very short timeout
            config = AcorConfig(timeout=1)
            result = run_tool(tool_path, [], config)
            
            # Tool should timeout
            assert result.success == False
            assert result.timed_out == True
    
    def test_run_tool_with_string_path(self):
        """Test that string paths are converted to Path objects"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "test.py"
            tool_path.write_text("""#!/usr/bin/env python3
print("## Status: Ready")
print("## Status: Complete")
""")
            tool_path.chmod(0o755)
            
            config = AcorConfig()
            
            # Pass as string instead of Path
            result = run_tool(str(tool_path), [], config)
            
            assert result.success == True
            assert result.exit_code == 0
    
    def test_run_nonexistent_tool(self):
        """Test handling when tool file doesn't exist"""
        config = AcorConfig()
        result = run_tool(Path("/nonexistent/tool.py"), [], config)
        
        # Should fail gracefully
        assert result.success == False
        assert result.error_message is not None
    
    def test_run_tool_passes_arguments(self):
        """Test that arguments are passed to tool correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = Path(tmpdir) / "test.py"
            tool_path.write_text("""#!/usr/bin/env python3
import sys
print(f"## Status: Ready")
print(f"## Output")
print(f"Args: {sys.argv[1:]}")
print("## Status: Complete")
""")
            tool_path.chmod(0o755)
            
            config = AcorConfig()
            result = run_tool(tool_path, ["arg1", "arg2", "arg3"], config)
            
            assert result.success == True
            assert result.exit_code == 0