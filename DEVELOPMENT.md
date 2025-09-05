# ACOR Development Guide

## Quick Start

### First Time Setup
```bash
./install.sh          # Creates venv, installs everything
source venv/bin/activate
acor --version        # Should show: ACOR version 0.1.0
```

### Daily Development
```bash
source venv/bin/activate    # Activate environment
# ... make your changes ...
./reload.sh                 # Reload after changes (optional)
```

## Using ACOR in Other Projects

### Method 1: Link to Development Version
From your other project:
```bash
cd ~/my-project
~/ai-cli-orchestration/install-dev.sh --venv
```

This links to ACOR source - changes are immediate, no reinstall needed.

### Method 2: Direct Execution
```bash
# Use ACOR directly without installing
~/ai-cli-orchestration/venv/bin/acor status
```

## Project Structure

```
ai-cli-orchestration/
├── src/acor/           # Core library
│   ├── cli.py          # Command-line interface
│   ├── conversation.py # Protocol for AI communication
│   ├── runner.py       # Tool execution
│   └── version.py      # Version management
├── tools/              # Built-in tools
│   └── status/         # Status command
├── examples/           # Example tools
├── install.sh          # Setup script
├── reload.sh           # Quick reload for development
└── install-dev.sh      # Install in other projects
```

## Writing Tools

Create a tool in any `tools_dirs` directory:

```python
#!/usr/bin/env python3
from acor import AcorTool

with AcorTool("my-tool") as tool:
    tool.progress(50, "Working...")
    tool.output({"result": "success"})
```

Tool is automatically available as: `acor my-tool`

## Version Management

Edit `src/acor/version.py`:
```python
MAJOR = 0
MINOR = 1
REVISION = 0
```

Then reload:
```bash
./reload.sh
```

## Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `install.sh` | Full setup | First time, clean install |
| `reload.sh` | Quick reload | After version/metadata changes |
| `install-dev.sh` | Link to other projects | Testing ACOR in other projects |

## Common Tasks

**Check ACOR status:**
```bash
acor status
```

**See all commands:**
```bash
acor --help
```

**Run a tool:**
```bash
acor file_processor examples/sample.txt
```

**Test in another project:**
```bash
cd ~/other-project
~/ai-cli-orchestration/install-dev.sh
acor status  # Uses development version
```

## Tips

- Changes to Python code take effect immediately (no reload needed)
- Changes to version or package metadata need `./reload.sh`
- Each project can have its own `.acor/config.yaml`
- Tools are discovered from directories in config