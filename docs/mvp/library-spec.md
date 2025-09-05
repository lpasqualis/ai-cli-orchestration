# ACOR Library API Specification

## Overview

The ACOR library provides a clean, collision-free API for tool developers to communicate with AI agents using the ACOR conversational protocol. The primary interface is the `AcorTool` class, which handles all protocol messaging through structured Markdown output.

## Installation

```python
from acor import AcorTool, ToolState
```

## State Enumeration

```python
class ToolState(Enum):
    COMPLETE = "complete"
    FAILED = "failed" 
    CANCELLED = "cancelled"
```

## Core Class: AcorTool

### Initialization

```python
tool = AcorTool(name: str, version: str = "1.0.0")
```

**Parameters:**
- `name`: The tool identifier (required)
- `version`: Tool version (optional, defaults to "1.0.0" or auto-detected from manifest.json)

### Usage Patterns

#### Pattern 1: Manual Lifecycle Management

```python
from acor import AcorTool

tool = AcorTool("document-analyzer")
tool.start()
tool.progress(25, "Processing document")

if error_condition:
    tool.error("E_INPUT_NOT_FOUND", "File missing")
    tool.stop()
    return

tool.result({"processed": True})
tool.stop()
```

#### Pattern 2: Context Manager (Recommended)

```python
from acor import AcorTool

with AcorTool("document-analyzer") as tool:
    tool.progress(25, "Processing document")
    tool.status("working", "Analyzing sections")
    tool.output({"sections": 5, "pages": 12})
    # Automatic start() and stop() handling
```

## Complete Method Reference

### 1. Lifecycle Methods

#### `start() -> AcorTool`
Initializes the tool and emits ready status.

**Output:** `## Status: Ready`

**Example:**
```python
tool.start()
```

#### `stop(state: ToolState = ToolState.COMPLETE) -> AcorTool`
Completes tool execution and emits final status.

**Parameters:**
- `state`: Final state - `ToolState.COMPLETE`, `ToolState.FAILED`, or `ToolState.CANCELLED`

**Output:** `## Status: Complete` (or `Failed`/`Cancelled` based on state)

**Notes:** 
- Idempotent (safe to call multiple times)
- Automatically called when using context manager
- Context manager uses `ToolState.COMPLETE` by default, or `ToolState.FAILED` if exception occurred

**Example:**
```python
tool.stop()  # Defaults to ToolState.COMPLETE
tool.stop(state=ToolState.FAILED)
tool.stop(state=ToolState.CANCELLED)
```

### 2. Status Methods

#### `status(state: str, message: str = "") -> AcorTool`
Reports the current operational state.

**Parameters:**
- `state`: One of "ready", "working", "complete", "failed"
- `message`: Optional descriptive message

**Output:** `## Status: {State}`

**Example:**
```python
tool.status("working", "Processing large dataset")
```

### 3. Progress Methods

#### `progress(percentage: Union[int, float], message: str = "") -> AcorTool`
Reports work progress as a percentage.

**Parameters:**
- `percentage`: Progress value (0-100 as int, or 0.0-1.0 as float)
- `message`: Optional progress description

**Output:** `## Progress: {percentage}%`

**Example:**
```python
tool.progress(50, "Halfway through processing")  # 50%
tool.progress(0.75, "Three quarters done")       # 75%
```

### 4. Output Methods

#### `output(data: Any, format: str = "auto") -> AcorTool`
Emits the primary output/result data.

**Parameters:**
- `data`: The output data (dict, list, string, etc.)
- `format`: Output format - "auto", "json", "yaml", "text", "markdown"

**Output:** `## Output` or `## Output Data` with formatted content

**Example:**
```python
# Simple text output
tool.output("Analysis complete. Generated 3 reports.")

# Structured data
tool.output({"processed": 1000, "errors": 3}, format="json")

# Including file information in output
tool.output({
    "status": "complete",
    "files_created": ["report.pdf", "summary.csv"],
    "records_processed": 1000
})
```

### 5. Error Methods

#### `error(code: str, message: str, recovery: str = None, details: str = None) -> AcorTool`
Reports an error condition with recovery guidance.

**Parameters:**
- `code`: Error code (e.g., "E_FILE_NOT_FOUND")
- `message`: Human-readable error message
- `recovery`: Optional recovery instructions
- `details`: Optional technical details

**Output:** `## Error: {message}` with recovery guidance

**Example:**
```python
tool.error(
    "E_FILE_NOT_FOUND", 
    "Cannot locate input.csv",
    recovery="Check file path or use --input flag",
    details="Searched in: /data, /input, ."
)
```

### 6. Input Request Methods

#### `input_needed(message: str) -> None`
Requests required input from the AI. **Note: Tool exits after calling this method.**

**Parameters:**
- `message`: Complete message explaining what's needed and how to provide it

**Output:** `## Input Needed` followed by the message

**Note:** The tool is responsible for constructing the full message with instructions, options, and examples as needed.

**Example:**
```python
# Simple case
tool.input_needed("Database connection string required. Run: acor db_tool --connection '<your_connection_string>'")

# With options
tool.input_needed("""
Primary key column required for deduplication.

Run this command with your choice:
acor data_processor data.csv --key "<choose_one>"

Valid options: user_id, email, account_number
""")

# Tool exits after emitting the message
```

### 7. AI Directive Methods

#### `ai_directive(message: str) -> AcorTool`
Requests specific action from the AI agent. Multiple calls accumulate into a single directive section.

**Parameters:**
- `message`: Clear instruction for the AI to execute

**Output:** `## AI Directive` followed by accumulated messages

**Note:** Multiple calls to `ai_directive` will batch the directives together in one section.

**Example:**
```python
# These will be combined into one AI Directive section
tool.ai_directive("Fix the JSON syntax errors in config.json")
tool.ai_directive("Create a .env file with DATABASE_URL=postgresql://localhost/myapp")
tool.ai_directive("Review output/report.pdf and email summary to team@example.com")

# Output will be:
# ## AI Directive
# - Fix the JSON syntax errors in config.json
# - Create a .env file with DATABASE_URL=postgresql://localhost/myapp  
# - Review output/report.pdf and email summary to team@example.com
```

### 8. Suggestion Methods

#### `suggestions(suggestions: List[str], title: str = None) -> AcorTool`
Provides optional next steps for AI consideration.

**Parameters:**
- `suggestions`: List of suggested actions (not commands)
- `title`: Optional section title

**Output:** `## Suggestions` or `## Suggestions: {Title}`

**Note:** Suggestions should describe what to do, not how to invoke tools. The AI agent will determine the appropriate commands based on available tools.

**Example:**
```python
tool.suggestions([
    "Visualize the correlation matrix in the output data",
    "Email the report to stakeholders",
    "Run deep analysis on anomalies found",
    "Archive results with appropriate tags"
])
```

## Method Chaining

All methods except `input_needed` return `self` for fluent chaining:

```python
tool.start() \
    .progress(0.25, "Loading data") \
    .status("working", "Processing") \
    .progress(0.75, "Analyzing results") \
    .output({"complete": True, "files": ["output.json"]}) \
    .ai_directive("Validate output.json for completeness") \
    .suggestions(["Visualize the results", "Generate report"]) \
    .stop()
```

## Error Handling

### Automatic Error Handling with Context Manager

```python
with AcorTool("processor") as tool:
    tool.progress(50, "Processing")
    # If exception occurs, tool automatically:
    # 1. Emits error message
    # 2. Calls stop() with failed status
```

### Manual Error Handling

```python
from acor import AcorTool, ToolState

tool = AcorTool("processor")
tool.start()

try:
    # Processing logic
    result = process_data()
    tool.output(result)
    tool.stop()  # Success
except ProcessingError as e:
    tool.error("E_PROCESSING_FAILED", str(e), 
               recovery="Check input format and retry")
    tool.stop(state=ToolState.FAILED)
```

## Implementation Notes

### Thread Safety
All output methods are synchronized for safe concurrent operations.

### Output Buffering
Output is flushed immediately to ensure real-time progress visibility.

### Parameter Validation
- Progress accepts 0-100 (int) or 0.0-1.0 (float), auto-converts to percentage
- Required parameters are validated
- Invalid states are prevented (e.g., progress before start)

### State Tracking
The tool tracks its lifecycle state to prevent invalid operations:
- Cannot emit progress before `start()`
- Cannot emit output after `stop()`
- Prevents duplicate `start()` calls

### Auto-Detection
When `manifest.json` exists in the tool directory:
- Tool name can be auto-detected
- Version can be auto-detected
- Defaults are used if manifest is missing

## Complete Example

```python
from acor import AcorTool, ToolState
import json

def analyze_data(input_file):
    with AcorTool("data-analyzer") as tool:
        # Start processing
        tool.progress(0.1, "Loading input file")
        
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            tool.error("E_FILE_NOT_FOUND", f"Cannot find {input_file}",
                      recovery="Ensure file exists and path is correct")
            # Context manager will call stop(state=ToolState.FAILED)
            return
        
        tool.progress(0.3, f"Loaded {len(data)} records")
        tool.status("working", "Analyzing data patterns")
        
        # Perform analysis
        results = perform_analysis(data)
        
        tool.progress(0.8, "Generating reports")
        
        # Save results
        save_results(results)
        
        tool.progress(1.0, "Analysis complete")
        
        # Emit results with file information
        tool.output({
            "summary": results["summary"],
            "files_created": ["report.pdf", "summary.csv"],
            "records_analyzed": len(data)
        })
        
        # Direct the AI (multiple directives batch together)
        tool.ai_directive("Email report.pdf to the analytics team with a brief summary")
        tool.ai_directive("Archive the raw data with today's date")
        
        # Provide next steps (as actions, not commands)
        tool.suggestions([
            "Visualize the trends in the summary data",
            "Compare these results with last month's analysis",
            "Deep dive into any anomalies detected"
        ])

if __name__ == "__main__":
    import sys
    analyze_data(sys.argv[1] if len(sys.argv) > 1 else "data.json")
```

## Future Features (Post-MVP)

### Session Management
```python
tool.session(session_id: str) -> AcorTool
tool.checkpoint(checkpoint_id: str, state: Dict) -> AcorTool
```

### Heartbeat for Long Operations
```python
tool.heartbeat() -> AcorTool  # Prevents timeout
```

### Advanced Progress
```python
tool.progress_bar(current: int, total: int, label: str) -> AcorTool
```

## Migration from Raw Protocol

If migrating from direct protocol emission:

**Before:**
```python
print("## Status: Ready")
print("## Progress: 50%")
print("Processing data")
```

**After:**
```python
tool = AcorTool("my-tool")
tool.start()
tool.progress(50, "Processing data")
```

The library handles all formatting, escaping, and protocol compliance automatically.