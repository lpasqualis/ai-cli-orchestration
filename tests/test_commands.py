"""Tests for the commands module"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from acor.commands import status, new, process_template


class TestStatusCommand:
    """Test the status command"""
    
    def test_status_basic(self):
        """Test basic status command output"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create a basic config
            os.makedirs(".acor")
            config_file = Path(".acor/config.yaml")
            config_file.write_text("""
version: "1"
tools_dirs:
  - "tools"
timeout: 120
""")
            
            result = runner.invoke(status)
            assert result.exit_code == 0
            assert "ACOR Status" in result.output
            assert "Version:" in result.output
            assert "Python:" in result.output
            assert "Config:" in result.output
    
    def test_status_json_output(self):
        """Test status command with JSON output"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            result = runner.invoke(status, ['--json'])
            assert result.exit_code == 0
            
            # Should be valid JSON
            data = json.loads(result.output)
            assert "acor_version" in data
            assert "python_version" in data
            assert "configuration" in data
            assert "discovered_tools" in data
    
    def test_status_with_tools(self):
        """Test status command with discovered tools"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create tools directory with a tool
            tool_dir = Path("tools/my_tool")
            tool_dir.mkdir(parents=True)
            cli_file = tool_dir / "cli.py"
            cli_file.write_text("#!/usr/bin/env python3\nprint('test')")
            cli_file.chmod(0o755)
            
            result = runner.invoke(status)
            assert result.exit_code == 0
            assert "my_tool" in result.output
            assert "Discovered Tools (1)" in result.output


class TestNewCommand:
    """Test the new command"""
    
    def test_new_invalid_tool_name(self):
        """Test new command with invalid tool name"""
        runner = CliRunner()
        
        # Test with path separator
        result = runner.invoke(new, ['../bad_name'])
        assert result.exit_code == 6  # ErrorCodes.INVALID_ARGUMENT
        assert "Invalid tool name" in result.output
        
        # Test with backslash
        result = runner.invoke(new, ['bad\\name'])
        assert result.exit_code == 6  # ErrorCodes.INVALID_ARGUMENT
        assert "Invalid tool name" in result.output
        
        # Test with dot prefix
        result = runner.invoke(new, ['.hidden'])
        assert result.exit_code == 6  # ErrorCodes.INVALID_ARGUMENT
        assert "Invalid tool name" in result.output
    
    def test_new_tool_already_exists(self):
        """Test new command when tool directory already exists"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create existing tool directory
            os.makedirs("tools/existing_tool")
            
            result = runner.invoke(new, ['existing_tool', '--path', 'tools'])
            assert result.exit_code == 9  # ErrorCodes.VALIDATION_FAILED
            assert "already exists" in result.output
    
    def test_new_with_single_tools_dir(self):
        """Test new command with single configured tools directory"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create config with single tools directory
            os.makedirs(".acor")
            config_file = Path(".acor/config.yaml")
            config_file.write_text("""
version: "1"
tools_dirs:
  - "my_tools"
""")
            
            # Mock the template processing to avoid file system dependencies
            with patch('acor.commands.process_template') as mock_process:
                mock_process.return_value = "template content"
                
                result = runner.invoke(new, ['test_tool'])
                
                # Should succeed and use the configured directory
                assert result.exit_code == 0
                assert "Created new tool 'test_tool'" in result.output
                assert "my_tools/test_tool" in result.output
    
    def test_new_with_multiple_tools_dirs_no_path(self):
        """Test new command with multiple directories and no --path"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create config with multiple tools directories
            os.makedirs(".acor")
            config_file = Path(".acor/config.yaml")
            config_file.write_text("""
version: "1"
tools_dirs:
  - "tools1"
  - "tools2"
  - "tools3"
""")
            
            result = runner.invoke(new, ['test_tool'])
            
            # Should fail and show options
            assert result.exit_code == 6  # ErrorCodes.INVALID_ARGUMENT
            assert "Multiple tools directories configured" in result.output
            assert "tools1" in result.output
            assert "tools2" in result.output
            assert "tools3" in result.output
    
    def test_new_with_explicit_path(self):
        """Test new command with explicit --path"""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Mock the template processing
            with patch('acor.commands.process_template') as mock_process:
                mock_process.return_value = "template content"
                
                result = runner.invoke(new, ['test_tool', '--path', 'custom/path'])
                
                assert result.exit_code == 0
                assert "Created new tool 'test_tool'" in result.output
                assert "custom/path/test_tool" in result.output


class TestProcessTemplate:
    """Test template processing function"""
    
    def test_process_template_basic(self):
        """Test basic template processing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            f.write("Hello {{TOOL_NAME}}, welcome to {{TOOL_TITLE}}!")
            template_path = Path(f.name)
        
        try:
            result = process_template(template_path, "my_tool")
            assert result == "Hello my_tool, welcome to My Tool!"
        finally:
            os.unlink(template_path)
    
    def test_process_template_with_underscores(self):
        """Test template processing with underscored tool name"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            f.write("Tool: {{TOOL_NAME}}\nTitle: {{TOOL_TITLE}}")
            template_path = Path(f.name)
        
        try:
            result = process_template(template_path, "my_awesome_tool")
            assert result == "Tool: my_awesome_tool\nTitle: My Awesome Tool"
        finally:
            os.unlink(template_path)
    
    def test_process_template_no_macros(self):
        """Test template processing with no macros"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as f:
            f.write("This template has no macros")
            template_path = Path(f.name)
        
        try:
            result = process_template(template_path, "tool_name")
            assert result == "This template has no macros"
        finally:
            os.unlink(template_path)