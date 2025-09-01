# ACOR MVP Technical Design

## Overview

Minimal technical design for the MVP - extract working code from the spec and make it reusable.

## Architecture

Simple, direct execution model:
```
CLI → Runner → Tool Process → Conversational Output
```

## Core Components

### 1. Runner (`src/acor/runner.py`)

**Purpose**: Execute tools and monitor their output.

**Key Functions**:
- `run_tool(tool_path, args, config)`: Main entry point for tool execution
- Process management with configurable timeout
- Conversational message streaming to stdout
- Exit code handling

**Extracted From**: Specification lines 253-459

### 2. Conversation Protocol (`src/acor/conversation.py`)

**Purpose**: Define Markdown-based conversational format and provide emission helpers for tools.

**Message Types (7 total)**:
1. **Status**: Tool execution state (Ready, Working, Complete, Failed)
2. **Progress**: Work progress with percentage (0-100)
3. **Output**: Results and data produced
4. **Error**: Problems with recovery guidance
5. **Input Needed**: Request information from AI/user
6. **AI Directive**: Request specific AI action
7. **Suggestions**: Optional next steps for AI consideration

**Key Functions**:
- `status(state, description)` - Emit ## Status: header
- `progress(percent, message)` - Emit ## Progress: header
- `output(data, format)` - Emit ## Output with code blocks
- `error(title, message, recovery)` - Emit ## Error: header
- `input_needed(question, context)` - Emit ## Input Needed header
- `ai_directive(action, details)` - Emit ## AI Directive: header
- `suggestions(options)` - Emit ## Suggestions header

**Protocol Features**:
- Pure Markdown output (no special parsing needed)
- Code blocks for JSON/YAML data
- File references for large content
- AI-native format that models understand

### 3. Configuration (`src/acor/config.py`)

**Purpose**: Load minimal configuration from YAML file.

**Config Structure**:
```yaml
version: "1"
tools_dirs: [".acor/tools", "tools"]  
timeout: 120
```

**Features**:
- Load from `.acor/config.yaml` or specified path
- Defaults if no config file exists
- Environment variable expansion with `${VAR}` syntax

### 4. CLI (`src/acor/cli.py`)

**Purpose**: Command-line interface using Click with dynamic tool registration.

**Interface**:
- `acor <tool_name> [args]`: Tools are direct commands
- `acor --help`: Shows all available tools
- `acor --version`: Show version
- `--config`: Override config file path

### 5. Discovery (`src/acor/discovery.py`)

**Purpose**: Find and register tools as CLI commands.

**Functions**:
- Scan configured `tools_dirs` for tool directories
- Identify entry points (`cli.py`, `main.py`, `tool.py`)
- Return mapping of tool names to paths
- Dynamic registration with Click at runtime

## Data Flow

1. User runs: `acor tool_name arg1 arg2`
2. CLI discovers available tools from configured directories
3. CLI resolves tool_name to actual path
4. CLI loads configuration (if present)
5. CLI calls runner with resolved tool path and arguments
6. Runner spawns tool process (stateless - no memory of previous runs)
7. Tool imports conversation library and emits prefixed messages
8. Runner streams conversational output to stdout
9. Runner returns exit code

**Stateless Architecture**: Each CLI invocation is completely independent. The runner maintains no state between invocations. If multi-step operations are needed, tools must explicitly handle session management through parameters (e.g., `--session-id`, `--checkpoint-file`) that the AI passes in subsequent invocations. This follows REST API principles where each request is self-contained.

## File System Layout

```
project/
├── .acor/
│   └── config.yaml       # Optional configuration
├── tools/                # Default tools directory
└── .runs/               # Future: execution artifacts
```

## Dependencies

- Python 3.8+ (broad compatibility)
- Click 8.0+ (CLI framework)
- PyYAML 6.0+ (config parsing)

## Error Handling

- Missing tool: Exit with error message
- Tool timeout: Kill process, emit timeout error
- Malformed messages: Pass through as-is (AI can handle)
- Config errors: Use defaults, warn user

## Security Considerations (MVP)

- No sandboxing in MVP (add later if needed)
- Tools run with current user permissions
- No network restrictions
- No resource limits beyond timeout

## Testing Strategy

Manual testing only for MVP:
1. Run example tool
2. Verify conversational output format
3. Test timeout behavior
4. Test missing file handling

## Tool Discovery Pattern

Following the established pattern from agentic_career, tools are:
- Organized in directories under configured `tools_dirs`
- Each tool is a directory containing an entry point file
- Discovery happens by scanning for valid tool directories
- Tools are referenced by directory name, not full path

### Tool Directory Structure
```
project/
├── tools/              # Or any configured tools_dir
│   ├── tool_name/     # Each tool in its own directory
│   │   ├── cli.py     # Standard entry point
│   │   └── ...        # Other modules
│   └── another_tool/
│       └── main.py    # Alternative entry point
```

### Discovery Rules
1. Scan each directory in `tools_dirs` from config
2. A valid tool directory contains: `cli.py`, `main.py`, or `tool.py`
3. Tool name = directory name
4. Execution: `acor tool_name [args]` (direct command, not subcommand)

## What We're NOT Including

These are deferred to post-MVP based on actual needs:
- Tool registry/manifests
- Multi-language support (Python only)
- Checkpoints
- Security sandboxing
- Metrics/observability
- Caching
- Complex error taxonomy

## Success Criteria

1. Can execute Python tools from command line
2. Tools can communicate via conversational protocol
3. Configuration is respected
4. System is simple enough to understand and modify