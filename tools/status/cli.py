#!/usr/bin/env python3
"""ACOR status command - Display system status and configuration"""

import sys
import os
from pathlib import Path
from acor import AcorTool
from acor.version import get_version_info
from acor.config import load_config
from acor.discovery import discover_tools


def show_status():
    """Display ACOR system status"""
    
    with AcorTool("status", version="1.0.0") as tool:
        tool.progress(10, "Gathering system information")
        
        # Load configuration
        config = load_config()
        
        tool.progress(30, "Scanning for tools")
        
        # Discover tools
        tools = discover_tools(config.tools_dirs)
        
        tool.progress(50, "Analyzing configuration")
        
        # Get version info
        version_info = get_version_info()
        
        # Build status information
        status_info = {
            "acor_version": version_info["version"],
            "acor_codename": version_info["codename"],
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "working_directory": str(Path.cwd()),
            "config_file": ".acor/config.yaml" if Path(".acor/config.yaml").exists() else "Using defaults",
            "configuration": {
                "protocol_version": config.version,
                "timeout": f"{config.timeout} seconds",
                "tools_directories": config.tools_dirs
            },
            "discovered_tools": {
                "count": len(tools),
                "tools": list(tools.keys()) if tools else []
            }
        }
        
        tool.progress(75, "Checking tool directories")
        
        # Check which directories exist
        existing_dirs = []
        missing_dirs = []
        for dir_path in config.tools_dirs:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                existing_dirs.append(str(path))
            else:
                missing_dirs.append(str(path))
        
        status_info["directories"] = {
            "existing": existing_dirs,
            "missing": missing_dirs
        }
        
        tool.progress(90, "Preparing output")
        
        # Output the status
        tool.output(status_info, format="json")
        
        tool.progress(100, "Status check complete")
        
        # Provide suggestions based on findings
        suggestions = []
        
        if not tools:
            suggestions.append("Create tools in one of the configured directories")
            suggestions.append("Check that tool directories contain valid entry points (cli.py, main.py, or tool.py)")
        
        if missing_dirs:
            suggestions.append(f"Create missing directories: {', '.join(missing_dirs)}")
        
        if len(tools) < 3:
            suggestions.append("Add more tools to expand ACOR capabilities")
        
        if config.timeout == 120:
            suggestions.append("Consider adjusting timeout in config for long-running tools")
        
        if suggestions:
            tool.suggestions(suggestions, title="Recommendations")
        
        # AI directives if issues found
        if not Path(".acor/config.yaml").exists():
            tool.ai_directive("Consider creating .acor/config.yaml for custom configuration")
        
        if not tools:
            tool.ai_directive("No tools found. Check tools_dirs configuration and ensure tools have proper entry points")


def main():
    """Main entry point"""
    show_status()


if __name__ == "__main__":
    main()