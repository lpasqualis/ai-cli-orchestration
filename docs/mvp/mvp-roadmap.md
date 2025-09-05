# ACOR MVP Roadmap

## Philosophy

Build only what's needed to prove the pattern works end-to-end. No speculation. No premature optimization. Test fundamental assumptions first.

## MVP Goal

A working system where:
1. An AI agent can execute a Python CLI tool via `acor` command
2. The tool communicates back via conversational protocol (structured text with prefixes)
3. The system is configurable via `.acor/config.yaml`
4. We can test and iterate on real usage
5. Installation creates a globally available `acor` command

## MVP Project Structure

```
acor-cli/
├── src/
│   └── acor/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point for 'python -m acor'
│       ├── cli.py               # Click CLI implementation
│       ├── runner.py            # Core runner extracted from spec
│       ├── conversation.py      # Conversational protocol implementation
│       ├── discovery.py         # Tool discovery system
│       └── config.py            # Configuration loader
├── examples/
│   └── tools/                  # Example tools directory
│       └── file_processor/     # Example tool (as directory)
│           ├── cli.py           # Tool entry point
│           └── README.md        # Tool documentation
├── tests/                       # Empty for MVP, add later
├── setup.py                     # Package configuration
├── pyproject.toml              # Modern Python packaging
├── requirements.txt            # Dependencies (Click, PyYAML)
└── README.md                   # Basic usage instructions
```

## Tool Organization Pattern

Tools follow this structure:
```
project/
├── .acor/
│   └── config.yaml             # Configuration specifying tools_dirs
├── tools/                      # Default tools directory
│   ├── my_tool/               # Each tool in its own directory
│   │   └── cli.py             # Standard entry point
│   └── another_tool/
│       └── main.py            # Alternative entry point
```

## Phase 1: Extract Core Runner

### What
Extract the working runner from `docs/spec/acor-cli-pattern.md` and make it reusable.

### Implementation Details
- Start with the runner code from lines 253-459 of the spec
- Key changes needed:
  - Replace hardcoded `TOOLS_DIR = ".acor/tools"` with configurable path
  - Extract timeout values to configuration (default 120 seconds)
  - Make protocol version configurable (default "1")
  - Add proper Python logging instead of stderr prints
  - Create RunnerResult dataclass for structured returns

### Core Runner Functions
The runner module will provide:
- Tool execution with configurable timeout
- Tool path validation
- Command construction based on file type
- Output monitoring with heartbeat detection
- Structured result returns

### Tasks
- [ ] Create `src/acor/__init__.py` with version info
- [ ] Extract `tools/run.py` from specification (lines 253-459)
- [ ] Refactor into `src/acor/runner.py` with configurability
- [ ] Create RunnerResult dataclass for return values
- [ ] Add logging configuration
- [ ] Test with a simple echo tool

### Definition of Done
Can run: `python -m acor.runner echo "hello"` and get conversational output

## Phase 2: Conversational Protocol Implementation

### What
Implement the conversational protocol for tool-to-AI communication.

### Implementation Details
Tools output structured text messages with semantic prefixes to stdout.

### Message Types (MVP)
The protocol supports exactly 7 message types using Markdown headers:
1. **Status**: Tool execution state (Ready, Working, Complete, Failed)
2. **Progress**: Work progress with percentage (0-100)
3. **Output**: Results and data produced
4. **Error**: Problems with recovery guidance
5. **Input Needed**: Request information from AI/user
6. **AI Directive**: Request specific AI action
7. **Suggestions**: Optional next steps for AI consideration

### Protocol Features
- Markdown-native format (no special parsing)
- AI-friendly patterns (headers and code blocks)
- Human-readable for easy debugging
- Complex data in code blocks (JSON/YAML)
- File references for large content

### Tasks
- [ ] Create `src/acor/conversation.py` with Markdown emitters
- [ ] Implement all 7 message types as Markdown headers
- [ ] Add helpers for: status(), progress(), output(), error(), input_needed(), ai_directive(), suggestions()
- [ ] Support code blocks for structured data (JSON/YAML)
- [ ] Create validation for progress percentages (0-100)
- [ ] Create a test tool that uses all message types

### Definition of Done
A Python tool can: `from acor.conversation import status, progress, data, error`

## Phase 3: Minimal CLI with Tool Discovery

### What
Create the CLI with tool discovery where each tool becomes a direct command.

### Implementation Details
Use Click for CLI framework. Dynamically register discovered tools as commands.

### CLI Interface
- `acor <tool_name> [args]`: Run a tool directly as a command
- `acor --help`: Show all available tools as commands
- `acor --version`: Show version
- `--config` option: Override config file location

### Tool Discovery
- Scan directories specified in `tools_dirs` config
- Each tool is a directory with `cli.py`, `main.py`, or `tool.py`
- Tools become direct commands (not subcommands)

### Dynamic Command Registration
- Discover tools at CLI initialization
- Register each tool as a Click command
- Pass through arguments directly to the tool

### Tasks
- [ ] Create `src/acor/cli.py` with Click framework
- [ ] Create `src/acor/__main__.py` for entry point
- [ ] Implement `src/acor/discovery.py` for tool discovery
- [ ] Dynamically register tools as commands
- [ ] Load config from `.acor/config.yaml` if it exists
- [ ] Pass config to runner
- [ ] Stream conversational messages directly to stdout

### Definition of Done
Can run: `acor my_tool arg1 arg2` (where my_tool becomes a direct command)

## Phase 4: Basic Configuration

### What
Make the system configurable without hardcoding.

### Config Schema (Minimal)
The configuration file (.acor/config.yaml) will support:
- **version**: Protocol version (default: "1")
- **tools_dirs**: List of directories to search for tools
- **timeout**: Execution timeout in seconds (default: 120)

### Config Implementation
The config module will:
- Define a configuration dataclass with sensible defaults
- Load YAML configuration from file if present
- Fall back to defaults if no config file exists
- Support environment variable expansion using ${VAR} syntax
- Validate configuration values on load

### Tasks
- [ ] Define AcorConfig dataclass with defaults
- [ ] Create `src/acor/config.py` with load_config function
- [ ] Add YAML parsing with PyYAML
- [ ] Support environment variable expansion (${VAR})
- [ ] Handle missing config file gracefully (use defaults)
- [ ] Create example `.acor/config.yaml` in project root

### Definition of Done
System loads config from `.acor/config.yaml` and uses it in runner

## Phase 5: Create Working Example

### What
Build a real tool that demonstrates the pattern.

### Example Tool Structure
The file_processor example will demonstrate:
- Standard tool directory structure
- Tool entry point in `cli.py`
- Importing and using the ACOR conversation library
- Emitting STATUS:READY message at start
- Sending progress updates at key processing stages (10%, 50%, 90%)
- Error handling with appropriate error codes
- Returning structured results as JSON
- Proper exit codes (0 for success, non-zero for errors)

The tool will accept a file path as argument, process it with visible progress updates, and output results using conversational protocol that AI agents can parse and understand.

### Tasks
- [ ] Create `examples/tools/file_processor/` directory
- [ ] Create `examples/tools/file_processor/cli.py` as entry point
- [ ] Implement file reading with error handling
- [ ] Add progress emissions at key stages
- [ ] Handle missing file error case
- [ ] Create sample input file
- [ ] Write README explaining usage
- [ ] Test with: `acor run examples/file_processor/tool.py sample.txt`

### Definition of Done
Can run the example and see progress updates in conversational format

## Phase 6: Package for Installation

### What
Make it installable so we can use it in real projects with just `acor` command.

### Package Configuration
The package setup will include:
- **setup.py**: Define package metadata, dependencies (Click, PyYAML), and console script entry point
- **pyproject.toml**: Modern Python packaging configuration with build system requirements
- **requirements.txt**: Direct dependency list for development
- **Entry point**: Register 'acor' as a console command pointing to the CLI module

### Installation and Testing
After packaging:
1. Create a fresh virtual environment for testing
2. Install the package in development mode (pip install -e .)
3. Verify the 'acor' command is available globally within the virtualenv
4. Test with the example tool to ensure end-to-end functionality
5. Confirm conversational output is properly formatted and parseable

### Tasks
- [ ] Create `setup.py` with entry_points for console_scripts
- [ ] Create `pyproject.toml` for modern packaging
- [ ] Create `requirements.txt` with Click and PyYAML
- [ ] Add package metadata (__version__ in __init__.py)
- [ ] Test installation in fresh virtualenv
- [ ] Verify `acor` command is available globally in venv
- [ ] Create basic README.md with installation instructions

### Definition of Done
After `pip install -e .`, can run `acor` from anywhere in the virtualenv

## Testing Strategy

### Not Yet
- Unit tests (add when we have stable interfaces)
- Integration tests (add when we have multiple components)
- CI/CD (add when we're ready to distribute)

### Now
- Manual testing with real tools
- Verify conversational protocol works with AI agents
- Test in actual project context

## What We're NOT Building (Yet)

These are in `docs/speculative/implementation-roadmap.md` for later:

- Multi-language support (Python only for MVP)
- Tool discovery (use explicit paths)
- Tool registry/manifests
- Checkpoint system
- Security sandboxing
- Fancy CLI features (colors, progress bars, completion)
- Performance optimization
- Metrics/observability
- Template generation
- PyPI distribution

## Success Criteria

1. **It works**: Can run a Python tool and get conversational output
2. **It's configurable**: Not hardcoded to specific paths
3. **It's testable**: Can iterate quickly on real usage
4. **It's focused**: Only essential features, no bloat

## Next Steps After MVP

Based on actual usage, we might add:
- Tool discovery if managing many tools becomes painful
- Bash support if we need shell scripts
- Error taxonomy if error handling gets complex
- Better CLI commands if current interface is limiting

But NOT until we prove we need them through real usage.