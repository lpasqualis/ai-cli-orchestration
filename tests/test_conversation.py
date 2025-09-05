"""Tests for the conversation module"""

import pytest
import json
import sys
from io import StringIO
from unittest.mock import patch
from acor.conversation import AcorTool


class TestAcorTool:
    """Test AcorTool conversation protocol"""
    
    def test_initialization(self):
        """Test AcorTool initialization"""
        tool = AcorTool("test_tool", version="1.0.0")
        assert tool.name == "test_tool"
        assert tool.version == "1.0.0"
        assert tool._started == False
    
    def test_context_manager_start_complete(self):
        """Test context manager lifecycle with successful completion"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            with AcorTool("test_tool") as tool:
                pass
        
        lines = output.getvalue().strip().split('\n')
        assert "## Status: Ready" in lines[0]
        assert "## Status: Complete" in lines[-1]
    
    def test_progress_output(self):
        """Test progress message output"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()  # Start the tool first
            tool.progress(50, "Halfway there")
        
        assert "## Progress: 50%" in output.getvalue()
        assert "Halfway there" in output.getvalue()
    
    def test_progress_percentage_validation(self):
        """Test progress percentage bounds"""
        tool = AcorTool("test_tool")
        tool.start()  # Start the tool
        
        # Valid percentages
        tool.progress(0, "Starting")
        tool.progress(100, "Complete")
        
        # Invalid percentages should be clamped
        output = StringIO()
        with patch('sys.stdout', output):
            tool.progress(-10, "Negative")
            assert "## Progress: 0%" in output.getvalue()
        
        output = StringIO()
        with patch('sys.stdout', output):
            tool.progress(150, "Over 100")
            assert "## Progress: 100%" in output.getvalue()
    
    def test_output_json(self):
        """Test JSON output formatting"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            tool.output({"key": "value", "number": 42})
        
        result = output.getvalue()
        assert "## Output Data" in result
        assert "```json" in result
        assert '"key": "value"' in result
        assert '"number": 42' in result
    
    def test_output_text(self):
        """Test text output formatting"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            tool.output("Simple text output", format="text")
        
        result = output.getvalue()
        assert "## Output" in result  # Text uses "## Output" not "## Output Data"
        assert "Simple text output" in result
    
    def test_error_output(self):
        """Test error message output"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            tool.error("E_TEST_ERROR", "Something went wrong", "Try again")
        
        result = output.getvalue()
        assert "## Error: Something went wrong" in result
        assert "**Recovery**: Try again" in result
    
    def test_input_needed(self):
        """Test input needed message"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            with pytest.raises(SystemExit) as exc_info:
                tool.input_needed("Please provide input")
            assert exc_info.value.code == 0
        
        result = output.getvalue()
        assert "## Input Needed" in result
        assert "Please provide input" in result
    
    def test_ai_directive(self):
        """Test AI directive message"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            tool.ai_directive("Process this data")
            tool.stop()  # AI directives only flush on stop
        
        result = output.getvalue()
        assert "## AI Directive" in result
        assert "Process this data" in result
    
    def test_suggestions(self):
        """Test suggestions output"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            tool.suggestions(["Option 1", "Option 2", "Option 3"])
        
        result = output.getvalue()
        assert "## Suggestions" in result
        assert "- Option 1" in result
        assert "- Option 2" in result
        assert "- Option 3" in result
    
    def test_suggestions_with_title(self):
        """Test suggestions with custom title"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            tool = AcorTool("test_tool")
            tool.start()
            tool.suggestions(["Do this", "Do that"], title="Next Steps")
        
        result = output.getvalue()
        assert "## Suggestions: Next Steps" in result  # Format is "## Suggestions: {title}"
        assert "- Do this" in result
        assert "- Do that" in result
    
    def test_context_manager_with_error(self):
        """Test context manager handles exceptions properly"""
        output = StringIO()
        
        with patch('sys.stdout', output):
            try:
                with AcorTool("test_tool") as tool:
                    raise ValueError("Test error")
            except ValueError:
                pass  # Expected
        
        lines = output.getvalue().strip().split('\n')
        # Should still have proper start
        assert "## Status: Ready" in lines[0]
        # But no complete status since exception occurred