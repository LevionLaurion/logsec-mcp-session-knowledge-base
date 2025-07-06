# Workspace Context Integration

## Overview

LogSec provides advanced Desktop Commander integration through LogSniffer, tracking all file operations and commands directly from DC log files.

## Status

✅ **Fully Implemented** - LogSniffer reads actual DC logs for accurate operation tracking.

## Architecture

### Core Components

1. **LogSniffer** (`modules/log_sniffer.py`)
   - Reads from: `%APPDATA%\Claude\logs\mcp-server-desktop-commander.log`
   - Parses JSON-formatted DC operations
   - Extracts: operation type, paths, timestamps
   - Handles duplicate prevention

2. **DC Operations Storage**
   - Table: `dc_operations`
   - Automatic project detection from paths
   - UNIQUE constraint prevents duplicates
   - Indexed for fast queries

3. **Continuation Context** (`lo_cont`)
   - Uses real DC operations from database
   - Groups by operation type
   - Shows actual edited files
   - Lists executed commands

## Tracked Operations

### File Operations
- **read_file**: Files viewed/analyzed
- **write_file**: Files created/modified
- **edit_block**: Surgical file edits
- **move_file**: File relocations
- **get_file_info**: File metadata checks

### Directory Operations
- **list_directory**: Folders explored
- **create_directory**: Folders created
- **search_files**: File searches
- **search_code**: Code pattern searches

### Command Operations
- **execute_command**: Shell commands run
- **read_output**: Command output reading
- **force_terminate**: Process termination

## Usage Examples

### Automatic Tracking
```python
# Every lo_save automatically tracks DC operations
lo_save("myproject", "Session summary")
# → Reads DC log
# → Extracts operations since last save
# → Stores in database
```

### Continuation Context
```python
# Get workspace context for continuation
lo_cont("myproject")
# Returns:
# - Recently edited files
# - Executed commands
# - Working directories
# - Session summaries
```

### Query Operations
```sql
-- Find all files edited in project
SELECT DISTINCT path FROM dc_operations 
WHERE project_name = 'myproject' 
AND operation_type = 'write_file';

-- Get command history
SELECT details FROM dc_operations
WHERE operation_type = 'execute_command'
ORDER BY timestamp DESC;
```

## Implementation Details

### Log Parsing
```python
# LogSniffer reads JSON lines from DC log
{"timestamp": "2025-07-06T10:30:45", "operation": "write_file", "path": "C:\\Project\\file.py"}
```

### Project Detection
- Extracts project from path structure
- Handles Windows/Unix paths
- Configurable project root patterns

### Performance
- Incremental log reading (only new entries)
- Batch inserts for efficiency
- Low overhead per save operation

## Configuration

No configuration needed - works automatically when Desktop Commander is active.

Optional settings in `config.py`:
```python
# Customize project detection patterns
PROJECT_PATTERNS = {
    'logsec': r'C:\\LogSec',
    'myproject': r'C:\\Projects\\MyProject'
}
```

## Benefits

1. **Accurate History**: Real operations, not parsed text
2. **No Manual Tracking**: Automatic from DC logs
3. **Project Context**: Know exactly what was modified
4. **Command History**: Full shell command tracking
5. **Search Integration**: Find files by operation type

## Troubleshooting

### Operations Not Tracked
1. Ensure Desktop Commander is running
2. Check log file exists: `%APPDATA%\Claude\logs\`
3. Verify read permissions on log file

### Duplicate Operations
- Normal: UNIQUE constraint prevents duplicates
- Check timestamp precision if issues persist

### Missing Project Assignment
- Operations without clear project go to "unknown"
- Configure PROJECT_PATTERNS for custom detection
