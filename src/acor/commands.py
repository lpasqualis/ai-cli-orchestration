"""Built-in ACOR commands that are always available"""

import sys
import os
import re
from pathlib import Path
import click
import json

from .version import get_version_info
from .config import load_config
from .discovery import discover_tools
from .constants import (
    ErrorCodes,
    VALID_TOOL_NAME_PATTERN,
    MAX_TOOL_NAME_LENGTH,
    FORBIDDEN_TEMPLATE_PATTERNS
)


@click.command()
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
@click.pass_context
def status(ctx, output_json):
    """Display ACOR system status and configuration"""
    
    # Load configuration - respect the --config option if provided
    config_path = ctx.parent.params.get('config_path', None) if ctx.parent else None
    config = load_config(config_path)
    
    # Discover tools
    tools = discover_tools(config.tools_dirs)
    
    # Get version info
    version_info = get_version_info()
    
    # Check which directories exist and count tools in each
    from .discovery import discover_tools as discover_single_dir
    
    dir_info = []  # List of (path, exists, tool_count)
    existing_dirs = []
    missing_dirs = []
    
    for dir_path in config.tools_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            # Count tools in this specific directory
            tools_in_dir = discover_single_dir([str(path)])
            tool_count = len(tools_in_dir)
            dir_info.append((str(path), True, tool_count))
            existing_dirs.append(str(path))
        else:
            dir_info.append((str(path), False, 0))
            missing_dirs.append(str(path))
    
    # Build status information
    status_info = {
        "acor_version": version_info["version"],
        "acor_codename": version_info["codename"],
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "working_directory": str(Path.cwd()),
        "config_file": config_path if config_path else (".acor/config.yaml" if Path(".acor/config.yaml").exists() else "Using defaults"),
        "configuration": {
            "protocol_version": config.version,
            "timeout": config.timeout,
            "tools_directories": config.tools_dirs
        },
        "discovered_tools": {
            "count": len(tools),
            "tools": list(tools.keys()) if tools else []
        },
        "directories": {
            "existing": existing_dirs,
            "missing": missing_dirs,
            "details": [
                {
                    "path": path,
                    "exists": exists,
                    "tool_count": count
                } for path, exists, count in dir_info
            ]
        }
    }
    
    # Output based on format
    if output_json:
        # JSON output
        click.echo(json.dumps(status_info, indent=2))
    else:
        # Human-friendly output
        click.echo("ACOR Status")
        click.echo("═" * 50)
        click.echo(f"Version:    {status_info['acor_version']} ({status_info['acor_codename']})")
        click.echo(f"Python:     {status_info['python_version']}")
        click.echo(f"Config:     {status_info['config_file']}")
        click.echo(f"Directory:  {status_info['working_directory']}")
        click.echo()
        
        # Configuration section
        click.echo("Configuration")
        click.echo("─" * 50)
        click.echo(f"Protocol:   v{status_info['configuration']['protocol_version']}")
        click.echo(f"Timeout:    {status_info['configuration']['timeout']}s")
        click.echo()
        
        # Tools section
        click.echo(f"Discovered Tools ({status_info['discovered_tools']['count']})")
        click.echo("─" * 50)
        if status_info['discovered_tools']['tools']:
            for tool in sorted(status_info['discovered_tools']['tools']):
                click.echo(f"  ✓ {tool}")
        else:
            click.echo("  (none found)")
        click.echo()
        
        # Directories section
        click.echo("Tool Directories")
        click.echo("─" * 50)
        for path, exists, count in dir_info:
            if exists:
                # Format tool count with proper singular/plural
                tool_text = f"{count} tool" if count == 1 else f"{count} tools"
                # Pad the path to align the counts
                padded_path = f"{path:<20}"
                click.echo(f"  ✓ {padded_path} ({tool_text})")
            else:
                click.echo(f"  ✗ {path:<20} (missing)")
        
        # Recommendations if needed
        if missing_dirs or not tools or len(tools) < 2:
            click.echo()
            click.echo("Recommendations")
            click.echo("─" * 50)
            
            if not tools:
                click.echo("  • Create tools in one of the configured directories")
                click.echo("  • Ensure tools have entry points (cli.py, main.py, tool.py)")
            elif len(tools) < 2:
                click.echo("  • Add more tools to expand ACOR capabilities")
            
            if missing_dirs:
                click.echo(f"  • Create missing directories or update config")
            
            if not Path(".acor/config.yaml").exists():
                click.echo("  • Create .acor/config.yaml for project configuration")


@click.command()
@click.argument('tool_name')
@click.option('--path', default=None, help='Directory to create the tool in')
@click.option('--ai/--human', default=True, help='Create tool for AI agents (default) or human use')
@click.pass_context
def new(ctx, tool_name, path, ai):
    """Create a new ACOR tool with minimal template"""
    
    # Validate tool name (security hardening against path traversal)
    if not tool_name or not VALID_TOOL_NAME_PATTERN.match(tool_name):
        click.echo(f"Error: Invalid tool name '{tool_name}'", err=True)
        click.echo("Tool names must contain only letters, numbers, underscores, and hyphens", err=True)
        sys.exit(ErrorCodes.INVALID_ARGUMENT)
    
    # Check tool name length
    if len(tool_name) > MAX_TOOL_NAME_LENGTH:
        click.echo(f"Error: Tool name too long (max {MAX_TOOL_NAME_LENGTH} characters)", err=True)
        sys.exit(ErrorCodes.INVALID_ARGUMENT)
    
    # Load configuration to get tools directories
    config_path = ctx.parent.params.get('config_path', None) if ctx.parent else None
    config = load_config(config_path)
    
    # Determine which directory to use
    if path:
        # User specified a path explicitly
        tool_dir = Path(path) / tool_name
    else:
        # Use configured tools directories
        if not config.tools_dirs:
            click.echo("Error: No tools directories configured", err=True)
            click.echo("Please configure tools_dirs in .acor/config.yaml", err=True)
            sys.exit(ErrorCodes.INVALID_CONFIG)
        elif len(config.tools_dirs) == 1:
            # Single directory configured - use it as default
            tool_dir = Path(config.tools_dirs[0]) / tool_name
        else:
            # Multiple directories - user must choose
            click.echo("Error: Multiple tools directories configured. Please specify one with --path:", err=True)
            click.echo()
            for dir_path in config.tools_dirs:
                click.echo(f"  • {dir_path}")
            click.echo()
            click.echo(f"Example: acor new {tool_name} --path {config.tools_dirs[0]}")
            sys.exit(ErrorCodes.INVALID_ARGUMENT)
    
    # Check if it already exists
    if tool_dir.exists():
        click.echo(f"Error: Directory '{tool_dir}' already exists", err=True)
        sys.exit(ErrorCodes.VALIDATION_FAILED)
    
    try:
        # Create directory
        tool_dir.mkdir(parents=True, exist_ok=False)
        
        # Load and process templates
        template_dir = Path(__file__).parent / "templates" / "tool"
        
        # Choose CLI template based on target user
        if ai:
            cli_template_path = template_dir / "ai" / "cli.py.template"
        else:
            cli_template_path = template_dir / "human" / "cli.py.template"
        
        # Read and process CLI template
        cli_content = process_template(cli_template_path, tool_name)
        cli_file = tool_dir / "cli.py"
        cli_file.write_text(cli_content)
        
        # Make it executable
        os.chmod(cli_file, 0o755)
        
        # Read and process README template
        readme_template_path = template_dir / "README.md.template"
        readme_content = process_template(readme_template_path, tool_name)
        readme_file = tool_dir / "README.md"
        readme_file.write_text(readme_content)
        
        # Success message
        click.echo(f"✓ Created new tool '{tool_name}' in {tool_dir}")
        click.echo()
        click.echo("Files created:")
        click.echo(f"  • {cli_file}")
        click.echo(f"  • {readme_file}")
        click.echo()
        click.echo("Next steps:")
        click.echo(f"  1. Edit {cli_file} to implement your tool logic")
        click.echo(f"  2. Update {readme_file} with documentation")
        click.echo(f"  3. Test with: acor {tool_name} --help")
        
    except Exception as e:
        click.echo(f"Error creating tool: {e}", err=True)
        # Clean up if partially created
        if tool_dir.exists():
            import shutil
            shutil.rmtree(tool_dir)
        sys.exit(ErrorCodes.GENERAL_ERROR)


def validate_template_content(content: str) -> bool:
    """Validate template content for security issues
    
    Args:
        content: Template content to validate
        
    Returns:
        True if template is safe, False otherwise
    """
    # Check for forbidden patterns
    for pattern in FORBIDDEN_TEMPLATE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return False
    return True

def process_template(template_path: Path, tool_name: str) -> str:
    """Process a template file, replacing macros with values
    
    Args:
        template_path: Path to the template file
        tool_name: Name of the tool being created
        
    Returns:
        Processed template content
        
    Raises:
        ValueError: If template contains forbidden patterns
    """
    # Read template
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Validate template content for security
    if not validate_template_content(content):
        raise ValueError(f"Template contains forbidden patterns: {template_path}")
    
    # Define macro replacements
    replacements = {
        '{{TOOL_NAME}}': tool_name,
        '{{TOOL_TITLE}}': tool_name.replace('_', ' ').title()
    }
    
    # Replace all macros
    for macro, value in replacements.items():
        content = content.replace(macro, value)
    
    return content