# ACOR Configuration Examples

## Default Configuration

When you run `acor init`, it creates a `.acor/config.yaml` with sensible defaults:

```yaml
# .acor/config.yaml
version: 1
project:
  name: my-project
  # Tools can be in multiple directories (searched in order)
  tools_dirs:
    - .acor/tools/     # Project-specific tools
    - tools/           # Common tools directory
  runs_dir: .runs/
  registry_dir: .acor/registry/

discovery:
  patterns:
    python: ["cli.py", "main.py", "tool.py"]
    bash: ["cli.sh", "main.sh", "tool.sh", "*.tool.sh"]
    node: ["cli.js", "main.js", "tool.js"]
  cache_ttl: 300
  auto_discover: true

environment:
  base_allowlist:
    - PATH
    - HOME
    - USER
    - LANG
    - TMPDIR
  timeout_s: 1800
  heartbeat_grace_s: 90

security:
  allow_network_egress: false
  workspace_isolation: true
```

## Custom Tool Locations

You can configure tools to be discovered from any location in your project:

```yaml
# .acor/config.yaml
version: 1
project:
  name: data-pipeline
  tools_dirs:
    - scripts/automation/      # Custom scripts directory
    - lib/tools/              # Library tools
    - vendor/third-party/     # Third-party tools
    - .acor/tools/           # ACOR-specific tools
    - /opt/shared/tools/     # System-wide shared tools (absolute path)
```

## Monorepo Configuration

For monorepos with multiple services, each with their own tools:

```yaml
# .acor/config.yaml
version: 1
project:
  name: monorepo
  tools_dirs:
    - services/*/tools/       # Each service's tools
    - shared/tools/          # Shared tools
    - devops/scripts/        # DevOps automation
    - .acor/tools/          # Project-wide tools
```

## Environment-Specific Configuration

Use environment variables to customize tool locations:

```yaml
# .acor/config.yaml
version: 1
project:
  name: adaptive-project
  tools_dirs:
    - ${CUSTOM_TOOLS_DIR:-tools}/     # Use env var or default
    - ${HOME}/.local/acor-tools/      # User-specific tools
    - .acor/tools/
```

## Tool Discovery Patterns

Customize how tools are discovered based on naming conventions:

```yaml
# .acor/config.yaml
discovery:
  patterns:
    python: 
      - "cli.py"
      - "*_tool.py"
      - "tools/*.py"
      - "run_*.py"
    bash:
      - "*.sh"
      - "bin/*"           # Any executable in bin/
    node:
      - "*.js"
      - "*.mjs"
      - "cli.ts"          # TypeScript tools
    ruby:                   # Add custom language support
      - "*.rb"
      - "tool.rb"
```

## Security-Conscious Configuration

For production environments with strict security requirements:

```yaml
# .acor/config.yaml
version: 1
project:
  name: secure-project
  tools_dirs:
    - .acor/tools/verified/    # Only verified tools
  registry_dir: .acor/registry/

security:
  allow_network_egress: false
  workspace_isolation: true
  drop_privileges: true
  require_manifest: true       # Only run tools with manifests
  allowed_languages:           # Restrict to specific languages
    - python
    - bash
  forbidden_paths:            # Paths tools cannot access
    - /etc/
    - /sys/
    - ~/.ssh/
  max_output_size: 10485760   # 10MB max output
  resource_limits:
    cpu_seconds: 300
    memory_mb: 1024
    max_processes: 10
```

## Development vs Production

Use different configurations for different environments:

### Development Configuration
```yaml
# .acor/config.dev.yaml
version: 1
project:
  name: my-project-dev
  tools_dirs:
    - tools/
    - test/tools/        # Include test tools
    - debug/tools/       # Include debug tools
    
environment:
  timeout_s: 3600        # Longer timeouts for debugging
  
security:
  allow_network_egress: true    # More permissive in dev
```

### Production Configuration
```yaml
# .acor/config.prod.yaml
version: 1
project:
  name: my-project-prod
  tools_dirs:
    - .acor/tools/prod/   # Only production-ready tools
    
environment:
  timeout_s: 300          # Strict timeouts
  
security:
  allow_network_egress: false
  require_manifest: true
  audit_mode: true        # Log all operations
```

Use with: `acor --config .acor/config.prod.yaml run <tool>`

## Tool Organization Best Practices

### By Purpose
```
project/
├── .acor/
│   └── tools/
│       ├── setup/        # Setup and initialization tools
│       ├── maintenance/  # Maintenance and cleanup tools
│       └── monitoring/   # Monitoring and health checks
├── data/
│   └── tools/           # Data processing tools
├── ml/
│   └── tools/           # Machine learning tools
└── api/
    └── tools/           # API management tools
```

### By Language
```
project/
├── .acor/
│   └── config.yaml
├── python-tools/        # Python tools
├── bash-tools/          # Shell scripts
├── node-tools/          # JavaScript/TypeScript tools
└── go-tools/           # Go tools (with custom handler)
```

### By Team
```
project/
├── .acor/
│   └── config.yaml
├── platform/
│   └── tools/          # Platform team tools
├── data/
│   └── tools/          # Data team tools
├── frontend/
│   └── tools/          # Frontend team tools
└── shared/
    └── tools/          # Shared tools across teams
```

## Integration with Existing Projects

### Adding ACOR to an Existing Project

1. Install ACOR:
```bash
pip install acor
```

2. Initialize with automatic discovery:
```bash
acor init --discover-existing
```

This will scan common locations and create a config with found tools:

```yaml
# Generated .acor/config.yaml
version: 1
project:
  name: legacy-project
  tools_dirs:
    - scripts/          # Found 5 bash scripts
    - bin/             # Found 3 executables
    - automation/      # Found 2 python scripts
    - .acor/tools/    # For new ACOR-specific tools
```

3. Validate discovered tools:
```bash
acor validate
acor list
```

## AI Agent Usage

When an AI agent needs to understand the project's tool configuration:

```bash
# AI can run this to understand the entire system
acor explain --format markdown --include-examples

# Output includes:
# - Current configuration
# - All discovered tools and their locations
# - How to run each tool
# - Protocol specification
# - Error handling guide
```

Example AI workflow:
```bash
# 1. AI discovers available tools
acor list --format json

# 2. AI gets detailed info about a specific tool
acor describe data_processor --manifest

# 3. AI runs the tool with proper error handling
acor run data_processor --input data.json --output result.json

# 4. AI monitors the JSONL output and responds to action_required events
```