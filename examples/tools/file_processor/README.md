# File Processor Tool

An example ACOR tool that demonstrates the conversational protocol for AI-tool communication.

## Features

- File validation and error handling
- Progress reporting during processing  
- Structured output in JSON format
- AI directives for edge cases
- Suggestions for next steps

## Usage

```bash
# Process a file
acor file_processor <filepath>

# Example
acor file_processor data.txt
```

## Protocol Messages

This tool demonstrates all ACOR protocol message types:

1. **Status** - Tool readiness state
2. **Progress** - Processing progress (0-100%)
3. **Output** - File statistics in JSON
4. **Error** - File not found or read errors
5. **Input Needed** - When no file is provided
6. **AI Directive** - Guidance for empty/large files
7. **Suggestions** - Next steps for analysis

## Error Handling

- `E_FILE_NOT_FOUND` - File doesn't exist
- `E_READ_ERROR` - Cannot read file (permissions, etc.)

## Output Format

```json
{
  "filename": "data.txt",
  "path": "/full/path/to/data.txt",
  "size_bytes": 1024,
  "lines": 50,
  "words": 200,
  "characters": 1024,
  "average_line_length": 20.48
}
```