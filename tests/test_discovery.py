"""Tests for the discovery module"""

import pytest
import tempfile
import os
from pathlib import Path
from acor.discovery import discover_tools, find_tool_entry


class TestFindToolEntry:
    """Test finding tool entry points"""
    
    def test_find_cli_py(self):
        """Test finding cli.py entry point"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_dir = Path(tmpdir)
            cli_file = tool_dir / "cli.py"
            cli_file.write_text("#!/usr/bin/env python3\nprint('test')")
            cli_file.chmod(0o755)
            
            entry_point = find_tool_entry(tool_dir)
            assert entry_point == cli_file
    
    def test_find_main_py(self):
        """Test finding main.py entry point"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_dir = Path(tmpdir)
            main_file = tool_dir / "main.py"
            main_file.write_text("#!/usr/bin/env python3\nprint('test')")
            main_file.chmod(0o755)
            
            entry_point = find_tool_entry(tool_dir)
            assert entry_point == main_file
    
    def test_find_tool_py(self):
        """Test finding tool.py entry point"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_dir = Path(tmpdir)
            tool_file = tool_dir / "tool.py"
            tool_file.write_text("#!/usr/bin/env python3\nprint('test')")
            tool_file.chmod(0o755)
            
            entry_point = find_tool_entry(tool_dir)
            assert entry_point == tool_file
    
    def test_prefer_cli_over_others(self):
        """Test that cli.py is preferred over other entry points"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_dir = Path(tmpdir)
            
            # Create all entry points
            cli_file = tool_dir / "cli.py"
            main_file = tool_dir / "main.py"
            tool_file = tool_dir / "tool.py"
            
            for f in [cli_file, main_file, tool_file]:
                f.write_text("#!/usr/bin/env python3\nprint('test')")
                f.chmod(0o755)
            
            entry_point = find_tool_entry(tool_dir)
            assert entry_point == cli_file
    
    def test_no_entry_point(self):
        """Test when no entry point exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_dir = Path(tmpdir)
            entry_point = find_tool_entry(tool_dir)
            assert entry_point is None


class TestDiscoverTools:
    """Test tool discovery functionality"""
    
    def test_discover_empty_directory(self):
        """Test discovering tools in empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools = discover_tools([tmpdir])
            assert tools == {}
    
    def test_discover_single_tool(self):
        """Test discovering a single tool"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a tool
            tool_dir = Path(tmpdir) / "my_tool"
            tool_dir.mkdir()
            cli_file = tool_dir / "cli.py"
            cli_file.write_text("#!/usr/bin/env python3\nprint('my_tool')")
            cli_file.chmod(0o755)
            
            tools = discover_tools([tmpdir])
            assert "my_tool" in tools
            # Compare resolved paths since discovery now resolves paths for security
            assert tools["my_tool"] == cli_file.resolve()
    
    def test_discover_multiple_tools(self):
        """Test discovering multiple tools"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple tools
            for i in range(3):
                tool_dir = Path(tmpdir) / f"tool_{i}"
                tool_dir.mkdir()
                cli_file = tool_dir / "cli.py"
                cli_file.write_text(f"#!/usr/bin/env python3\nprint('tool_{i}')")
                cli_file.chmod(0o755)
            
            tools = discover_tools([tmpdir])
            assert len(tools) == 3
            assert "tool_0" in tools
            assert "tool_1" in tools
            assert "tool_2" in tools
    
    def test_discover_from_multiple_directories(self):
        """Test discovering tools from multiple directories"""
        with tempfile.TemporaryDirectory() as tmpdir1, \
             tempfile.TemporaryDirectory() as tmpdir2:
            
            # Create tool in first directory
            tool1_dir = Path(tmpdir1) / "tool1"
            tool1_dir.mkdir()
            cli1_file = tool1_dir / "cli.py"
            cli1_file.write_text("#!/usr/bin/env python3\nprint('tool1')")
            cli1_file.chmod(0o755)
            
            # Create tool in second directory
            tool2_dir = Path(tmpdir2) / "tool2"
            tool2_dir.mkdir()
            cli2_file = tool2_dir / "cli.py"
            cli2_file.write_text("#!/usr/bin/env python3\nprint('tool2')")
            cli2_file.chmod(0o755)
            
            tools = discover_tools([tmpdir1, tmpdir2])
            assert len(tools) == 2
            assert "tool1" in tools
            assert "tool2" in tools
    
    def test_skip_directories_without_entry_points(self):
        """Test that directories without entry points are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory without entry point
            no_tool_dir = Path(tmpdir) / "not_a_tool"
            no_tool_dir.mkdir()
            (no_tool_dir / "readme.txt").write_text("This is not a tool")
            
            # Create valid tool
            tool_dir = Path(tmpdir) / "real_tool"
            tool_dir.mkdir()
            cli_file = tool_dir / "cli.py"
            cli_file.write_text("#!/usr/bin/env python3\nprint('real_tool')")
            cli_file.chmod(0o755)
            
            tools = discover_tools([tmpdir])
            assert len(tools) == 1
            assert "real_tool" in tools
            assert "not_a_tool" not in tools
    
    def test_skip_nonexistent_directories(self):
        """Test that non-existent directories are skipped gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create one valid tool
            tool_dir = Path(tmpdir) / "tool"
            tool_dir.mkdir()
            cli_file = tool_dir / "cli.py"
            cli_file.write_text("#!/usr/bin/env python3\nprint('tool')")
            cli_file.chmod(0o755)
            
            # Include non-existent directory in search
            tools = discover_tools([tmpdir, "/nonexistent/path"])
            assert len(tools) == 1
            assert "tool" in tools