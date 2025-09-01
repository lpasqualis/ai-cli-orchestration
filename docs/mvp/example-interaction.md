# Example AI + Tool Interaction (MVP)

## How AI Agents Use ACOR Tools

### 1. Discovering Available Tools

```bash
$ acor --help
Usage: acor [OPTIONS] COMMAND [ARGS]...

  ACOR - AI CLI Orchestration Runner

Options:
  --version     Show version
  --config PATH Override config file location
  --help        Show this message and exit

Commands:
  document_analyzer  Analyze documents and extract structured data
  file_processor    Process files with configurable transformations
  text_summarizer   Generate summaries from text content
```

### 2. Simple Tool Execution

**AI runs a tool:**

```bash
$ acor document_analyzer report.pdf --extract-sections
```

**Tool outputs (Markdown format):**

```markdown
## Status: Ready

## Progress: 10%
Opening report.pdf

## Progress: 25%
Parsing PDF structure

## Progress: 50%
Extracting text from 12 pages

## Progress: 75%
Identifying sections and headings

## Progress: 90%
Building document structure

## Status: Complete

## Output Data
```json
{
  "sections": ["Executive Summary", "Introduction", "Methodology", "Results", "Conclusion"],
  "page_count": 12,
  "word_count": 4523,
  "extracted_file": "tmp/report_sections.json"
}
```

## Suggestions
You might want to:
- Generate summary: `acor text_summarizer tmp/report_sections.json`
- Create visualization: `acor visualize_structure tmp/report_sections.json`
- Export to Word: `acor export_doc tmp/report_sections.json --format docx`
```

### 3. Error Handling with Recovery

**When something goes wrong:**

```bash
$ acor file_processor missing.txt
```

```markdown
## Status: Ready

## Error: File Not Found
Cannot open missing.txt in current directory

**Recovery**: 
- Check if file exists: `ls *.txt`
- Specify full path: `acor file_processor /path/to/file.txt`
- Use --input flag: `acor file_processor --input correct_file.txt`
```

### 4. Interactive Workflow (Input Needed)

**Tool needs information:**

```bash
$ acor data_processor large_dataset.csv
```

```markdown
## Status: Ready

## Progress: 10%
Analyzing data structure

## Input Needed
Primary key column required for deduplication

**Run this command with your choice:**
```bash
acor data_processor large_dataset.csv --key "<choose_one>"
```

**Valid options**: 
- `user_id` (98% unique values)
- `email` (95% unique values)  
- `account_number` (100% unique values)
```

**AI chooses and runs the exact command provided:**

```bash
$ acor data_processor large_dataset.csv --key "user_id"
```

```markdown
## Status: Working
Deduplicating on user_id column

## Progress: 50%
Removed 127 duplicate records

## Status: Complete

## Output Files
- `output/deduplicated.csv` - Clean dataset
- `output/duplicates_removed.log` - Removed records
```

### 5. AI Directive Example

**Tool requests AI action:**

```bash
$ acor project_analyzer ./src
```

```markdown
## Status: Complete

## Output
Found 3 configuration issues that need fixing

## AI Directive: Fix Configuration
Please fix the following configuration issues:

1. Missing environment variable in `.env`:
   ```
   DATABASE_URL=postgresql://localhost/myapp
   ```

2. Invalid JSON in `config/settings.json` (line 23):
   ```json
   "api_key": "YOUR_KEY_HERE",  // <- missing comma
   "timeout": 30
   ```

3. Create missing config file `config/database.yaml`:
   ```yaml
   development:
     adapter: postgresql
     host: localhost
     database: myapp_dev
   ```

## Suggestions
After fixing the configuration:
- Validate config: `acor validate_config ./config`
- Run tests: `acor test_suite --config`
- Deploy: `acor deploy --environment development`
```

### 6. Multi-Tool Orchestration

**AI chains tools together based on suggestions:**

```bash
# Step 1: Process raw data
$ acor file_processor data.csv --clean
```

```markdown
## Status: Ready
## Progress: 50%
Cleaning data
## Status: Complete

## Output Files
- `tmp/cleaned_data.csv` - Processed dataset

## Output Data
```json
{"rows_processed": 1000, "errors_fixed": 23}
```

## Suggestions
Now you can:
- Analyze the cleaned data: `acor analyze_data tmp/cleaned_data.csv`
- Generate summary: `acor text_summarizer tmp/cleaned_data.csv`
- Create visualizations: `acor plot_data tmp/cleaned_data.csv`
```

**AI chooses from suggestions:**

```bash
$ acor text_summarizer tmp/cleaned_data.csv --format markdown
```

```markdown
## Status: Ready
## Progress: 30%
Analyzing patterns
## Progress: 80%
Generating summary
## Status: Complete

## Output Data
```markdown
# Data Summary

- **Total Records**: 1000
- **Errors Corrected**: 23
- **Key Finding**: Strong correlation between user engagement and feature adoption
- **Recommendation**: Focus on improving onboarding flow
```

## Suggestions
Final steps:
- Email report: `acor email_report summary.md --to team@example.com`
- Archive results: `acor archive . --tag "q4-analysis"`
- Generate presentation: `acor create_slides summary.md`
```

## Benefits of Markdown Protocol

1. **AI-Native**: Models trained on Markdown understand it naturally
2. **Human-Readable**: Easy to debug and read logs
3. **No Special Parsing**: Standard Markdown headers and code blocks
4. **Rich Output**: Tables, lists, code blocks, emphasis
5. **Clear Structure**: Headers provide obvious message boundaries

## What AI Agents See

From the AI's perspective:
- **Headers indicate message type**: `## Status:`, `## Progress:`, etc.
- **Code blocks contain data**: JSON/YAML in triple backticks
- **Suggestions are optional**: AI can choose to follow or ignore
- **Directives are requests**: AI should act on these
- **Input Needed requires response**: AI must provide the requested information
- **File paths are actionable**: Can be used in subsequent commands

## Tool Implementation

A minimal tool using ACOR's conversation library:

```python
#!/usr/bin/env python3
from acor.conversation import status, progress, output, error, suggestions
import sys

def main():
    status("Ready")
    
    progress(25, "Loading input file")
    progress(50, "Processing data")
    progress(75, "Generating results")
    
    status("Complete")
    
    output({
        "processed": 100,
        "result": "success"
    }, format="json")
    
    suggestions([
        "View results: `acor view_results output.json`",
        "Generate report: `acor create_report output.json`"
    ])
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

The tool outputs clean Markdown that both humans and AI can understand easily.