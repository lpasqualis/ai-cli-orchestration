"""Command-line interface for ACOR"""

import os
import sys
from pathlib import Path
import click

from . import __version__
from .config import load_config
from .discovery import discover_tools
from .runner import run_tool, validate_tool_path
from .commands import status as status_command, new as new_command
from .constants import ErrorCodes
from .logging import setup_logging


class AcorCLI(click.MultiCommand):
    """Dynamic command loader that discovers tools as commands"""
    
    # Native commands that ship with ACOR
    NATIVE_COMMANDS = ['status', 'new']
    
    def __init__(self, config_path=None, **kwargs):
        super().__init__(**kwargs)
        self.config_path = config_path
        self._tools = None
        self._config = None
    
    @property
    def config(self):
        """Lazy load configuration"""
        if self._config is None:
            self._config = load_config(self.config_path)
        return self._config
    
    @property
    def tools(self):
        """Lazy load discovered tools"""
        if self._tools is None:
            self._tools = discover_tools(self.config.tools_dirs)
        return self._tools
    
    def list_commands(self, ctx):
        """List all available commands (built-in + discovered tools)"""
        # Combine native commands with discovered tools
        all_commands = set(self.NATIVE_COMMANDS) | set(self.tools.keys())
        return sorted(all_commands)
    
    def format_commands(self, ctx, formatter):
        """Format the list of commands with categories"""
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue
            # Get help text - built-in commands already have it
            if hasattr(cmd, 'help'):
                help_text = cmd.help or ''
            else:
                help_text = ''
            commands.append((subcommand, help_text))
        
        if commands:
            # Separate native and tool commands
            native_cmds = [(name, help_text) for name, help_text in commands if name in self.NATIVE_COMMANDS]
            tool_cmds = [(name, help_text) for name, help_text in commands if name not in self.NATIVE_COMMANDS]
            
            # Format native commands
            if native_cmds:
                with formatter.section('Native Commands'):
                    formatter.write_dl(native_cmds)
            
            # Format tool commands
            if tool_cmds:
                with formatter.section('Tools'):
                    formatter.write_dl(tool_cmds)
    
    def get_command(self, ctx, name):
        """Get a command for a specific tool or built-in command"""
        
        # Check if it's a built-in command
        if name == 'status':
            return status_command
        elif name == 'new':
            return new_command
        
        # Otherwise, check discovered tools
        if name not in self.tools:
            return None
        
        tool_path = self.tools[name]
        config = self.config
        
        @click.command(name=name, 
                      context_settings=dict(
                          ignore_unknown_options=True,
                          allow_extra_args=True,
                      ))
        @click.pass_context
        def tool_command(ctx):
            """Execute the tool with provided arguments"""
            # Get all arguments passed to the tool
            args = ctx.args
            
            # Validate tool path
            is_valid, error_msg = validate_tool_path(tool_path)
            if not is_valid:
                click.echo(f"## Error: {error_msg}", err=True)
                sys.exit(ErrorCodes.VALIDATION_FAILED)
            
            # Run the tool
            result = run_tool(tool_path, args, config)
            
            # Exit with tool's exit code
            sys.exit(result.exit_code)
        
        # Set the help text
        if name in self.NATIVE_COMMANDS:
            tool_command.help = f"Display ACOR {name}"
        else:
            tool_command.help = f"Run the {name} tool"
        
        return tool_command


@click.command(cls=AcorCLI)
@click.option('--config', 'config_path', 
              help='Path to configuration file',
              type=click.Path(exists=False))
@click.version_option(version=__version__, prog_name='ACOR', message='%(prog)s version %(version)s')
@click.pass_context
def main(ctx, config_path):
    """ACOR - AI-CLI Orchestration Runner
    
    Execute tools that communicate with AI agents via conversational protocol.
    
    Tools are discovered from configured directories and exposed as commands.
    """
    # Initialize logging
    log_level = os.environ.get('ACOR_LOG_LEVEL', 'WARNING')
    log_file = os.environ.get('ACOR_LOG_FILE')
    log_file_path = Path(log_file) if log_file else None
    setup_logging(log_level=log_level, log_file=log_file_path)
    
    # Store config path for the custom command class
    ctx.obj = AcorCLI(config_path=config_path)


# For use when installed as console script
if __name__ == '__main__':
    main()