# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the ACOR (AI-CLI-Orchestration-Runner) project - a generic, reusable tool that implements the AI + CLI Orchestration Pattern. It enables any project to leverage AI-augmented systems where AI agents orchestrate deterministic CLI tools through a structured JSONL streaming protocol.

## Key Architecture Concepts

### Core Pattern
- **AI handles intelligence**: Understanding intent, making decisions, error recovery
- **CLI tools handle execution**: Deterministic operations, file I/O, transforms
- **JSONL protocol**: All communication between AI and tools uses streaming JSONL messages
- **Tool discovery**: Automatic discovery from configured directories (`.acor/config.yaml`)

### Project Structure (Planned)
```
src/acor/           # Main package code
  runner.py         # Universal tool runner (extracts from spec)
  protocol.py       # JSONL protocol implementation
  discovery.py      # Tool discovery system
  config.py         # Configuration management
templates/          # Tool templates for Python, Bash, Node.js
examples/           # Example tools demonstrating patterns
```

## Development Approach

### Extracting Code from Specification
The core implementation is embedded in `docs/spec/ai-cli-orchestration-pattern.md`. Key sections to extract:
- Universal runner: Lines 253-459 contain `tools/run.py`
- Protocol library: Lines 172-192 contain protocol emitter
- Example tools: Lines 644-952 contain working examples

### Configuration System
Projects using ACOR will have `.acor/config.yaml` with:
- `tools_dirs`: List of directories to discover tools (configurable, not just `.acor/tools/`)
- `discovery.patterns`: File patterns for each language
- `environment`: Timeouts, allowlists, limits
- `security`: Permission policies

### Multi-Language Support
Tools can be written in:
- **Python**: Entry points like `cli.py`, `main.py`, `tool.py`
- **Bash**: Entry points like `cli.sh`, `*.tool.sh`
- **Node.js**: Entry points like `cli.js`, `tool.js`

## Key Commands (To Be Implemented)

```bash
# Initialize project with ACOR
acor init

# List discovered tools
acor list

# Run a tool
acor run <tool> [args]

# Explain system to AI agents
acor explain --format markdown

# Validate tool manifests
acor validate
```

## Protocol Message Types

Tools emit these JSONL message types:
- `start`: Tool execution beginning
- `progress`: Percentage complete with message
- `heartbeat`: Keep-alive signal (required every 30s)
- `action_required`: Request AI decision
- `result`: Final success result
- `error`: Error with code and recovery hints
- `cancelled`: Cancellation acknowledgment

## Error Taxonomy

Errors follow a centralized taxonomy (`E_INPUT_NOT_FOUND`, `E_TRANSIENT_NET`, etc.) with:
- Error class (user_error, retryable, infra_error)
- Retryable flag
- Suggested AI actions

## Implementation Milestones

1. **Core Foundation**: Extract runner, create protocol library
2. **Configuration & Discovery**: Config loader, tool discovery
3. **CLI Interface**: Core commands (init, list, run, describe)
4. **Multi-Language**: Bash and Node.js protocol libraries
5. **Advanced Features**: Checkpoints, security, observability
6. **Testing & Documentation**: Test suite, user guides
7. **Packaging**: PyPI distribution

## Important Design Decisions

- **Tool Flexibility**: Tools can be anywhere in the project (configured via `tools_dirs`)
- **AI-Friendly**: `acor explain` command provides full system documentation for AI agents
- **Security First**: Sandboxed execution, explicit permissions in manifests
- **Protocol Version**: Currently v1, with version negotiation support
- **Python 3.8+**: For maximum compatibility

## Working with the Specification

The specification in `docs/spec/ai-cli-orchestration-pattern.md` is the source of truth. When implementing:
1. Extract code sections preserving the JSONL protocol exactly
2. Adapt hardcoded paths to use configuration
3. Maintain backward compatibility with the embedded pattern
4. Tools following the spec should work without modification

## Development Files

- `docs/dev/project-plan.md`: Vision and architecture overview
- `docs/dev/implementation-roadmap.md`: Detailed task breakdown
- `docs/dev/technical-design.md`: Component specifications and APIs
- `docs/dev/configuration-examples.md`: Configuration patterns and examples