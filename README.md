# ACOR - AI-CLI Orchestration Runner

Enable AI agents to orchestrate CLI tools through structured conversational protocol, combining AI's intelligence with the reliability of deterministic tools.

## Why ACOR?

Building AI systems that need to perform real-world tasks? ACOR solves the fundamental challenge of AI-tool integration:

- **AI excels at understanding** intent, context, and making decisions
- **CLI tools excel at execution** with deterministic, reliable operations
- **ACOR bridges the gap** with a structured conversation protocol that lets AI and tools work together seamlessly

### Perfect for:
- 🤖 **Agentic Systems** - Building AI agents that need to manipulate files, run builds, or execute workflows
- 🔧 **Tool Integration** - Wrapping existing CLI tools for AI consumption without rewriting them
- 📊 **Data Processing** - AI-guided data pipelines with deterministic transformations
- 🚀 **Automation** - Complex workflows where AI makes decisions and tools execute them

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

### 1. See it in action
```bash
# Activate environment
source venv/bin/activate

# Check installation
acor status

# Try the example file processor
echo "Hello ACOR!" > test.txt
acor file_processor test.txt
```

### 2. Create your first tool
```python
#!/usr/bin/env python3
from acor import AcorTool

with AcorTool("hello") as tool:
    tool.output("Hello from my first ACOR tool!")
    tool.suggestions(["Try adding parameters", "Add progress tracking"])
```

Save as `tools/hello/cli.py`, then run:
```bash
acor hello  # Your tool is instantly available!
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
acor-cli/
├── src/acor/         # Core library
├── tools/            # Native commands (status)
├── examples/         # Example tools
├── install.sh        # Quick setup
├── install-dev.sh    # Install in other projects
└── .acor/           # Configuration
```

## Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and advanced usage
- **[Protocol Specification](docs/mvp/conversation-protocol.md)** - Complete protocol reference
- **[Library Documentation](docs/mvp/library-spec.md)** - API and library details
- **[Example Interactions](docs/mvp/example-interaction.md)** - See the protocol in action
- **[Configuration Guide](docs/mvp/mvp-configuration.md)** - Advanced configuration options

## Real-World Example

Imagine an AI agent that needs to process data files:

```python
# AI Agent: "Process all CSV files and generate summaries"
# ACOR handles the orchestration:

with AcorTool("csv-analyzer") as tool:
    # AI understands the request
    tool.input_needed("Which CSV files should I process?", 
                     ["file_pattern", "output_format"])
    
    # Tool performs deterministic operations
    for file in csv_files:
        tool.progress(percent, f"Processing {file}")
        result = process_csv(file)  # Your deterministic logic
        tool.output(result)
    
    # AI gets structured feedback
    tool.suggestions([
        "Generate visualization from results",
        "Export to different format",
        "Run statistical analysis"
    ])
```

The AI sees structured Markdown messages and can make intelligent decisions, while your tool handles the actual file operations reliably.

## Contributing

We welcome contributions! Please:
1. Check existing [issues](https://github.com/lpasqualis/acor-cli/issues) first
2. Follow the existing code style
3. Add tests for new features
4. Update documentation as needed

## License

MIT
