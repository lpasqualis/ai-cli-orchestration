# ACOR (AI-CLI-Orchestration-Runner) Project Plan

## Vision

ACOR is a generic, reusable tool that implements the AI + CLI Orchestration Pattern, enabling any project to leverage AI-augmented systems where Claude Code (or other AI agents) orchestrate deterministic CLI tools through a structured JSONL streaming protocol.

## Goals

1. **Extract and Generalize**: Transform the embedded implementation from the AI-CLI orchestration pattern specification into a standalone, installable package
2. **Multi-Project Support**: Enable any project to adopt the pattern by adding a simple `.acor/config.yaml` configuration
3. **Language Agnostic**: Support tools written in Python, Bash, Node.js, and other languages
4. **Production Ready**: Include security, logging, error handling, and observability features from day one
5. **Developer Friendly**: Provide templates, examples, and clear documentation for quick adoption

## Core Principles

- **Separation of Concerns**: AI handles intelligence and judgment; CLI tools handle deterministic execution
- **Protocol-Driven**: All communication via structured JSONL messages
- **Resumable Operations**: Built-in checkpointing and state management
- **Security by Default**: Sandboxed execution, permission manifests, and audit trails
- **Tool Discovery**: Automatic discovery of tools following naming conventions

## Architecture Overview

```
Project Using ACOR:
├── .acor/
│   ├── config.yaml          # Project-specific configuration
│   └── registry/            # Tool manifests and metadata
├── tools/                   # CLI tools (Python, Bash, Node.js)
├── .runs/                   # Execution artifacts and logs
└── [project files]

ACOR Package (installed globally or in venv):
├── acor/
│   ├── cli.py              # Main entry point
│   ├── runner.py           # Universal tool runner
│   ├── protocol.py         # JSONL protocol implementation
│   ├── discovery.py        # Tool discovery system
│   ├── config.py           # Configuration management
│   └── [other modules]
└── templates/              # Tool templates and examples
```

## Key Components

### 1. Universal Runner
- Cross-platform execution engine
- Process management with timeouts and heartbeats
- Environment isolation and security controls
- JSONL event streaming and persistence
- Adapted from `tools/run.py` in the specification

### 2. Protocol Library
- Message type definitions and schemas
- Helper functions for emitting JSONL events
- Implementations for Python, Bash, and Node.js
- Schema validation and error handling

### 3. Tool Discovery System
- Automatic scanning of configured directories
- Support for multiple entry point patterns
- Language detection based on file extensions
- Caching for performance

### 4. Configuration System
- YAML-based project configuration
- Tool manifests with permissions and requirements
- Error code taxonomy
- Security policies and resource limits

### 5. CLI Interface
Commands:
- `acor init` - Initialize a project with default configuration
- `acor list` - List discovered tools
- `acor describe <tool>` - Show tool manifest and capabilities
- `acor run <tool> [args]` - Execute a tool with the runner
- `acor validate` - Validate all tool manifests
- `acor logs <run-id>` - View run logs and artifacts
- `acor template <type>` - Generate tool templates

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- Extract and refactor the universal runner from the specification
- Create the protocol library with Python implementation
- Build configuration loading and validation
- Implement basic CLI with `run` and `list` commands

### Phase 2: Tool Discovery & Registry (Week 2)
- Implement automatic tool discovery
- Create manifest validation system
- Build error taxonomy management
- Add `describe` and `validate` commands

### Phase 3: Multi-Language Support (Week 3)
- Add Bash protocol library and helpers
- Add Node.js protocol library and helpers
- Implement language detection and runtime selection
- Create language-specific tool templates

### Phase 4: Advanced Features (Week 4)
- Implement checkpoint system for resumable operations
- Add security policies and permission validation
- Create observability features (logs, metrics, traces)
- Build Claude Code integration helpers

### Phase 5: Polish & Documentation (Week 5)
- Create comprehensive documentation
- Build example tools demonstrating patterns
- Add test suite with coverage targets
- Prepare for PyPI packaging and distribution

## Technical Decisions

### Packaging & Distribution
- **Primary**: Python package distributed via PyPI
- **Installation**: `pip install acor` (global or venv)
- **Dependencies**: Minimal core dependencies (PyYAML, Click)
- **Optional**: Language-specific protocol libraries as separate packages

### Configuration Format
- YAML for human readability and comments
- JSON Schema validation for manifests
- Environment variable expansion support
- Sensible defaults with override capability
- Support for multiple tool directories (configurable locations)

### Security Model
- No privileged operations by default
- Explicit permission declarations in manifests
- Filesystem access restricted to workspace
- Network egress requires allowlist
- Secrets passed via files, never environment

### Compatibility
- Python 3.8+ for maximum compatibility
- Cross-platform: Linux, macOS, Windows
- Shell-agnostic for Bash tools
- Node.js 14+ for JavaScript tools

## Success Metrics

1. **Adoption**: Easy to integrate into existing projects (< 5 minutes)
2. **Reliability**: 99%+ success rate for well-formed tools
3. **Performance**: < 100ms overhead for tool startup
4. **Security**: Zero security incidents from proper usage
5. **Developer Experience**: Clear error messages and helpful documentation

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complex installation | Low adoption | Single pip install, minimal dependencies |
| Language version conflicts | Runtime failures | Version detection, clear requirements |
| Security vulnerabilities | Trust issues | Security-first design, regular audits |
| Poor error messages | Developer frustration | Comprehensive error taxonomy, helpful hints |
| Performance overhead | Slow execution | Efficient runner, optional features |

## Next Steps

1. Create detailed technical design document
2. Set up project structure and development environment
3. Begin extraction of code from specification
4. Implement Phase 1 core components
5. Create initial test suite

## References

- [AI + CLI Orchestration Pattern Specification](../spec/ai-cli-orchestration-pattern.md)
- [JSONL Format](https://jsonlines.org/)
- [Python Packaging Guide](https://packaging.python.org/)