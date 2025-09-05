# ACOR - AI-CLI Orchestration Runner

Enable AI agents to orchestrate CLI tools through structured conversational protocol.

## Features

- 🤖 **AI-Native Protocol**: Markdown-based conversation between AI and tools
- 🔍 **Auto-Discovery**: Tools automatically become CLI commands
- 📊 **Progress Tracking**: Real-time progress updates
- 🛠️ **Simple Tool Development**: Write tools in Python with minimal boilerplate
- ⚙️ **Configurable**: YAML-based configuration

## Installation

```bash
# Quick install
./install.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Quick Start

```bash
# Activate environment
source venv/bin/activate

# Check status
acor status

# Run example tool
acor file_processor examples/sample.txt

# See all commands
acor --help
```

## Configuration

Create `.acor/config.yaml`:
```yaml
version: "1"
tools_dirs:
  - ".acor/tools"    # Project tools
  - "tools"          # Shared tools
  - "examples/tools" # Example tools
timeout: 120         # Seconds
```

## Writing Tools

Create a tool in any `tools_dirs` directory:

```python
#!/usr/bin/env python3
from acor import AcorTool

with AcorTool("my-tool") as tool:
    tool.progress(25, "Starting analysis")
    # Your logic here
    result = {"status": "complete", "items": 42}
    tool.output(result)
    tool.suggestions([
        "Review the results",
        "Generate a report",
        "Process additional files"
    ])
```

Save as `tools/my-tool/cli.py` and it's automatically available as `acor my-tool`.

## Protocol Messages

Tools communicate with AI using Markdown:
- `## Status`: Execution state
- `## Progress`: Work progress (0-100%)
- `## Output`: Results and data
- `## Error`: Problems with recovery hints
- `## Input Needed`: Request parameters
- `## AI Directive`: Request AI action
- `## Suggestions`: Optional next steps

See `examples/tools/file_processor/` for a complete example.

## Project Structure

```
ai-cli-orchestration/
├── src/acor/         # Core library
├── tools/            # Native commands (status)
├── examples/         # Example tools
├── install.sh        # Quick setup
├── install-dev.sh    # Install in other projects
└── .acor/           # Configuration
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for:
- Development setup
- Using ACOR in other projects  
- Writing custom tools
- Version management

## License

MIT
