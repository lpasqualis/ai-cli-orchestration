#!/usr/bin/env python3
"""Example file processor tool demonstrating ACOR conversation protocol"""

import sys
import json
import time
from pathlib import Path

# Import ACOR library
from acor import AcorTool, ToolState


def process_file(filepath: str):
    """Process a file and demonstrate ACOR communication"""
    
    with AcorTool("file_processor", version="1.0.0") as tool:
        # Start processing
        tool.progress(10, "Validating input file")
        
        # Check if file exists
        file_path = Path(filepath)
        if not file_path.exists():
            tool.error(
                "E_FILE_NOT_FOUND",
                f"Cannot locate file: {filepath}",
                recovery="Check the file path and ensure the file exists",
                details=f"Searched in current directory: {Path.cwd()}"
            )
            return
        
        tool.progress(25, "Reading file contents")
        
        try:
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
                
            lines = content.splitlines()
            char_count = len(content)
            word_count = len(content.split())
            
        except Exception as e:
            tool.error(
                "E_READ_ERROR",
                f"Failed to read file: {str(e)}",
                recovery="Ensure you have read permissions for the file"
            )
            return
        
        tool.progress(50, f"Analyzing {len(lines)} lines")
        
        # Simulate some processing
        time.sleep(0.5)  # Simulate work
        
        tool.progress(75, "Generating statistics")
        
        # Calculate statistics
        stats = {
            "filename": file_path.name,
            "path": str(file_path.absolute()),
            "size_bytes": file_path.stat().st_size,
            "lines": len(lines),
            "words": word_count,
            "characters": char_count,
            "average_line_length": char_count / len(lines) if lines else 0
        }
        
        tool.progress(90, "Preparing output")
        
        # Output the results
        tool.output(stats, format="json")
        
        tool.progress(100, "Processing complete")
        
        # Provide AI with directives if there are issues
        if len(lines) == 0:
            tool.ai_directive("The file is empty. Consider checking if this is expected.")
        elif len(lines) > 10000:
            tool.ai_directive(f"Large file detected ({len(lines)} lines). Consider processing in chunks for better performance.")
        
        # Suggest next steps
        tool.suggestions([
            "Analyze the content for specific patterns",
            "Compare with other files in the directory",
            "Generate a detailed report with visualizations",
            "Archive the processed results"
        ], title="Next Steps")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # Use the ACOR protocol to request input
        with AcorTool("file_processor") as tool:
            tool.input_needed("""File path required for processing.

Run this command with the file you want to process:
```bash
acor file_processor <filepath>
```

Example:
```bash
acor file_processor data.txt
```""")
        sys.exit(1)
    
    # Process the file
    filepath = sys.argv[1]
    process_file(filepath)


if __name__ == "__main__":
    main()