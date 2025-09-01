# ACOR MVP Configuration

## Overview

Minimal configuration for the MVP - just enough to avoid hardcoding.

## Configuration File

Location: `.acor/config.yaml`

## Schema

```yaml
# Protocol version
version: "1"

# Directories to search for tools (in order)
tools_dirs:
  - .acor/tools
  - tools
  
# Tool execution timeout in seconds
timeout: 120
```

## Features

### Environment Variable Expansion

Use `${VAR}` syntax to reference environment variables:

```yaml
tools_dirs:
  - ${HOME}/my-tools
  - ${PROJECT_ROOT}/tools
```

### Defaults

If no config file exists, these defaults are used:
- `version`: "1"
- `tools_dirs`: [".acor/tools"]
- `timeout`: 120

## Command Line Override

Use `--config` to specify alternate config file:
```bash
acor --config my-config.yaml run tool.py
```

## What We're NOT Configuring (Yet)

These are deferred until proven necessary:
- Security policies
- Discovery patterns
- Registry locations
- Storage paths
- Logging levels
- Network restrictions
- Resource limits
- Checkpoint settings

## Migration Path

The simple schema allows easy extension:
1. Add new fields with defaults
2. Old configs continue working
3. Document new fields as needed