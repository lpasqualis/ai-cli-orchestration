# ACOR Conversational Protocol Specification

## Overview

ACOR uses a Markdown-based conversational protocol where tools communicate with AI agents through structured Markdown output. This approach is human-readable, AI-native, and supports complex data without parsing confusion.

## Core Principles

1. **Markdown-Native**: All output is valid Markdown
2. **AI-Friendly**: Uses patterns AI models understand naturally
3. **Human-Readable**: Easy to debug and understand
4. **Structured**: Consistent header patterns for reliable parsing
5. **Progressive**: Supports partial completion and resumption

## Message Types (MVP)

The MVP supports exactly 7 message types, each with a specific purpose:

### 1. Status Messages

Report the current state of tool execution.

```markdown
## Status: Ready
Tool initialized and ready to process

## Status: Working
Currently processing input file

## Status: Complete
Successfully processed all records

## Status: Failed
Unable to complete operation
```

### 2. Progress Updates

Show work progress with percentage and description.

```markdown
## Progress: 25%
Processed 250 of 1000 records

## Progress: 50%
Validating data integrity

## Progress: 100%
All validations complete
```

### 3. Output/Results

Present the actual results or data produced.

```markdown
## Output
Processing complete. Results saved to `output/results.json`

## Output Data
```json
{
  "processed": 1000,
  "errors": 3,
  "duration": "45s"
}
```

## Output Files
- `report.pdf` - Full analysis report
- `summary.csv` - Statistical summary
- `errors.log` - Error details
```

### 4. Error Messages

Report problems with recovery guidance.

```markdown
## Error: File Not Found
Cannot locate `input.csv` in current directory

**Recovery**: Check file path or use --input flag

## Error: Invalid Format
The input file is not valid JSON

**Details**: Unexpected token at line 23, column 15
**Recovery**: Fix JSON syntax or use --validate to check file
```

### 5. Input Needed

Request required parameters - tells AI exactly how to re-run the tool with the missing information.

**Important**: Input Needed messages must provide the EXACT command for the AI to run next. The tool exits after emitting this message, and the AI re-runs it with the provided parameters.

**Stateless Design**: The CLI is completely stateless. Each invocation is independent with no memory of previous runs. Tools must provide complete information for the next command, including any session context if needed (e.g., `--session-id abc123` for multi-step operations).

```markdown
## Input Needed
Primary key column required for deduplication

**Run this command with your choice:**
```bash
acor data_processor data.csv --key "<choose_one>"
```

**Valid options**: user_id, email, account_number
```

For multiple parameters:
```markdown
## Input Needed
Configuration required

**Run this command with all parameters:**
```bash
acor db_migrator --database "<connection_string>" --mode "<fast|safe>" --backup <yes|no>
```

**Example:**
```bash
acor db_migrator --database "postgresql://localhost/mydb" --mode "safe" --backup yes
```
```

When there are alternative approaches:
```markdown
## Input Needed
Choose ONE of these approaches:

**Option A - Use config file:**
```bash
acor analyzer --config myconfig.yaml
```

**Option B - Use flags:**
```bash
acor analyzer --threshold 0.8 --mode strict
```
```

**Key Rule**: Each "Input Needed" message should result in exactly ONE command that the AI will run next, not multiple commands or ambiguous instructions.

### 6. AI Directives

Request specific actions from the AI.

```markdown
## AI Directive: Create File
Create a configuration file at `config/settings.yaml` with:
```yaml
database:
  host: localhost
  port: 5432
  name: analytics
```

## AI Directive: Run Tool
Execute the validator on the processed output:
```bash
acor data_validator output/processed.csv --strict
```

## AI Directive: Analyze
Review the error log and identify patterns:
- File: `logs/errors.log`
- Focus: Database timeout errors
- Goal: Determine root cause
```

### 7. Suggestions

Provide optional next steps for AI consideration.

```markdown
## Suggestions
Based on the analysis, you might want to:
- Generate visualizations: `acor plot data.csv --type histogram`
- Export for review: `acor export data.csv --format excel`
- Run deep analysis: `acor deep_analyze data.csv --correlations`

## Suggestions: Next Steps
The report has been generated. Available commands:
- `acor email_report report.pdf --to team` - Share with team
- `acor summarize report.pdf --length brief` - Create summary
- `acor archive report.pdf --tag q4-2024` - Archive with metadata
```

## Complete Example

Here's a full conversation showing all message types:

```markdown
## Status: Ready

## Progress: 10%
Loading configuration files

## Progress: 25%
Connecting to database

## Input Needed
Tables must be specified for analysis

**Run this command with your selected tables:**
```bash
acor analyzer --tables "<comma_separated_list>"
```

**Available tables**: users, orders, products, inventory
**Example**: `acor analyzer --tables "users,orders"`
```

*AI runs: `acor analyzer --tables "users,orders"`*

```markdown
## Status: Working
Analyzing users and orders tables

## Progress: 50%
Extracted 10,000 user records

## Progress: 75%
Processing order history

## Status: Complete

## Output Data
```json
{
  "users_analyzed": 10000,
  "orders_processed": 45000,
  "insights_generated": 12
}
```

## Output Files
- `analysis/user_segments.csv` - User segmentation data
- `analysis/order_patterns.json` - Order pattern analysis

## Suggestions
You can now:
- Visualize segments: `acor visualize analysis/user_segments.csv`
- Generate report: `acor create_report analysis/ --format pdf`
- Deep dive on segment: `acor analyze_segment analysis/user_segments.csv --segment "high_value"`

## AI Directive: Create Summary
Generate an executive summary from the analysis results and save to `summary.md`
```

## Implementation Guidelines

### For Tool Developers

1. **Use Markdown headers** (`##`) for message types
2. **Be consistent** with header formats (e.g., `## Status: Ready`)
3. **Use code blocks** for structured data (JSON, YAML, commands)
4. **Provide context** in messages to help AI understand
5. **Include recovery steps** in error messages
6. **Make suggestions actionable** with specific commands
7. **Input Needed vs Suggestions**:
   - **Input Needed**: Tool CANNOT proceed without this. Provide exact command to run next.
   - **Suggestions**: Tool completed successfully. These are optional next steps.

### For AI Agents

1. **Parse headers** to identify message types
2. **Extract code blocks** for structured data
3. **Execute directives** as requested
4. **Consider suggestions** but they're optional
5. **Respond to input requests** with appropriate data
6. **Track progress** to show users what's happening

## Why Markdown?

- **No special parsing**: AI models already understand Markdown
- **Clear boundaries**: Headers and code blocks provide structure
- **Rich formatting**: Tables, lists, emphasis, code blocks
- **Human-friendly**: Developers can read logs easily
- **Complex data support**: JSON/YAML in code blocks without escaping
- **Standard format**: Universal documentation format

## Session Management (Post-MVP)

For future multi-step operations requiring context:

```markdown
## Session: abc123
Resuming from previous state

## Session Checkpoint: data_loaded
State saved. Can resume from this point.
```

**Note**: Even with session support, the CLI remains stateless. Session IDs would be passed as explicit parameters (e.g., `--session abc123`) and any state would be stored externally (files, database) not in the CLI process memory. This ensures the CLI can be scaled, restarted, or run from different machines while maintaining the same behavior.

## MVP Implementation Priority

1. **Essential**: Status, Output, Error (minimum viable)
2. **Important**: Progress, Input Needed (better UX)
3. **Valuable**: AI Directive, Suggestions (enables richer interaction)