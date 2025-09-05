# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the ACOR (AI-CLI-Orchestration-Runner) project - a generic, reusable tool that implements the AI + CLI Orchestration Pattern. It enables any project to leverage AI-augmented systems where AI agents orchestrate deterministic CLI tools through a structured JSONL streaming protocol.

This tool will be used by agentic engineers who are building agentic systems that require deterministic behavious to help the AI perform various tasks. 

## Core Directives
- KEEP IT SIMPLE, do NOT build speculatively, more is not better!
- When we are done with the development of a new feature or capability, make sure there are unit tests covering the new feature.
- Keep the unit tests passing.

## Key Architecture Concepts

### Core Pattern
- **AI handles intelligence**: Understanding intent, making decisions, error recovery
- **CLI tools handle execution**: Deterministic operations, file I/O, transforms
- **Conversational protocol**: Markdown-based communication between AI and tools
- **Tool discovery**: Automatic discovery from configured directories (`.acor/config.yaml`)

### Project Structure (Implemented)
```
src/acor/           # Main package code
  cli.py            # CLI interface with dynamic tool registration
  runner.py         # Tool execution with timeout handling
  conversation.py   # AcorTool class for Markdown protocol
  discovery.py      # Tool discovery system
  config.py         # Configuration management
  version.py        # Version management (MAJOR.MINOR.REVISION)
tools/              # Native/built-in tools
  status/           # Status command
examples/           # Example tools demonstrating patterns
  tools/
    file_processor/ # Example tool with all protocol features
```

## Development Approach

### MVP Implementation (Complete)
The MVP is now implemented. Original design docs in `docs/mvp/`:
- MVP roadmap: `docs/mvp/mvp-roadmap.md`
- Technical design: `docs/mvp/mvp-technical-design.md`
- Conversation protocol: `docs/mvp/conversation-protocol.md`
- Library specification: `docs/mvp/library-spec.md`

### Configuration System
Projects using ACOR have `.acor/config.yaml` with:
- `version`: Protocol version (currently "1")
- `tools_dirs`: List of directories to discover tools
- `timeout`: Execution timeout in seconds (default: 120)

### Multi-Language Support (Python in MVP)
Tools can be written in:
- **Python**: Entry points like `cli.py`, `main.py`, `tool.py` (Implemented)
- **Bash**: Entry points like `cli.sh`, `*.tool.sh` (Future)
- **Node.js**: Entry points like `cli.js`, `tool.js` (Future)

## Key Commands (Implemented)

```bash
# Run a tool (tools are direct commands)
acor <tool_name> [args]

# Show status and configuration
acor status

# Show version
acor --version

# List all available tools
acor --help
```

## Protocol Message Types (Markdown-based)

Tools emit these Markdown message types:
- `## Status`: Tool execution state (Ready, Working, Complete, Failed)
- `## Progress`: Percentage complete with message
- `## Output`: Results and data produced
- `## Error`: Problems with recovery guidance
- `## Input Needed`: Request required parameters from AI
- `## AI Directive`: Request specific AI action
- `## Suggestions`: Optional next steps for AI consideration

## Current Implementation Status

### Completed (MVP)
- ✅ Core protocol library (`AcorTool` class)
- ✅ Configuration system (YAML-based)
- ✅ Tool discovery (automatic from directories)
- ✅ CLI interface (tools as direct commands)
- ✅ Runner with timeout handling
- ✅ Native commands (status)
- ✅ Example tools (file_processor)
- ✅ Development scripts (install.sh, reload.sh, install-dev.sh)
- ✅ Version management (semantic versioning)

### Future Enhancements
- Multi-language support (Bash, Node.js)
- Advanced error taxonomy
- Security sandboxing
- Tool manifests
- PyPI distribution

## Important Design Decisions

- **Tool Flexibility**: Tools can be anywhere in the project (configured via `tools_dirs`)
- **AI-Friendly**: `acor explain` command provides full system documentation for AI agents
- **Security First**: Sandboxed execution, explicit permissions in manifests
- **Protocol Version**: Currently v1, with version negotiation support
- **Python 3.8+**: For maximum compatibility

## Working with the MVP Documentation

The MVP implementation focuses on:
1. Core conversation protocol (`docs/mvp/conversation-protocol.md`)
2. Library specification (`docs/mvp/library-spec.md`)
3. Configuration examples (`docs/mvp/mvp-configuration.md`)
4. Phased implementation approach per the MVP roadmap

## Development Files

All current development documentation is in `docs/mvp/`:
- `docs/mvp/mvp-roadmap.md`: Phased implementation approach
- `docs/mvp/mvp-technical-design.md`: MVP component specifications
- `docs/mvp/conversation-protocol.md`: Core JSONL protocol definition
- `docs/mvp/library-spec.md`: Library implementation details
- `docs/mvp/mvp-configuration.md`: Configuration patterns
- `docs/mvp/example-interaction.md`: Example AI-tool interactions