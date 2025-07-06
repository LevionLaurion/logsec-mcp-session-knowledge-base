# LogSec 3.0 - Developer Reference

## Overview

LogSec MCP implements a 3-tier knowledge architecture with automatic Desktop Commander operations tracking.

## Core Components

### LogSniffer
- Reads Desktop Commander log file from `C:\Users\{USER}\AppData\Roaming\Claude\logs\mcp-server-desktop-commander.log`
- Extracts operations (read_file, write_file, edit_block, etc.)
- Automatically activated on every `lo_save`
- Stores operations in `dc_operations` table with duplicate prevention

### Vector Search (Lazy Loaded)
- Only loads when needed (first search query)
- Configurable via `src/config.py`: `ENABLE_VECTOR_SEARCH = True/False`
- Reduces startup time from ~20s to ~2s

## API Reference

### lo_start

Quick start with project context and continuation.

**Syntax:**
```python
lo_start(project_name: str) -> Dict
```

**Features:**
- Loads Tier 2 project context
- Checks for continuation file
- Provides last session summary if no continuation exists

### lo_load

Load project knowledge with two modes.

**Mode 1 - Summary (no query):**
```python
lo_load("logsec")
```
Returns:
- Project context (Tier 2)
- Recent activity (last 3 sessions)
- Knowledge theme overview
- No vector search needed

**Mode 2 - Search (with query):**
```python
lo_load("logsec", "error handling")
```
Returns:
- Project context (Tier 2)  
- Search results with similarity scores
- Triggers lazy loading of vector search on first use

### lo_save

Save session with automatic DC operations tracking.

**Syntax:**
```python
lo_save(project_name: str, content: str = None, session_id: str = None) -> Dict
```

**Features:**
- Extracts DC operations from log file via LogSniffer
- Auto-tags content
- Classifies knowledge type
- Stores in database (no files)
- Triggers auto-update of Tier 2 README

**DC Operations Tracking:**
- Reads actual Desktop Commander logs
- Stores: operation_type, path, timestamp, project
- Prevents duplicates via UNIQUE index

### lo_cont

Generate continuation context using real DC operations.

**Syntax:**
```python
lo_cont(project_name: str, mode: str = "auto") -> Dict
```

**Modes:**
- `auto` - General continuation
- `debug` - Focus on errors
- `implement` - Focus on implementation
- `refactor` - Focus on code structure  
- `document` - Focus on documentation

**Features:**
- Uses DC operations from database (not text parsing)
- Shows actual edited files (write_file, edit_block)
- Lists executed commands
- Identifies working directories

### lo_update

Update Tier 2 README from all sessions.

**Syntax:**
```python
lo_update(project_name: str) -> Dict
```

**Features:**
- Analyzes all sessions in database
- Extracts directories from DC operations
- Generates knowledge type distribution
- Updates project documentation
- No vector search required

## Database Schema

### session_metadata
```sql
CREATE TABLE session_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    project_name TEXT,
    timestamp TEXT,
    tags TEXT,  -- JSON array
    knowledge_type TEXT,
    confidence_score REAL,
    content_text TEXT,  -- Full session content
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### dc_operations
```sql
CREATE TABLE dc_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    project_name TEXT,
    operation_type TEXT,  -- read_file, write_file, etc.
    path TEXT,
    details TEXT,
    timestamp TIMESTAMP,
    UNIQUE(timestamp, operation_type, path)  -- Prevent duplicates
)
```

### session_vectors
```sql
CREATE TABLE session_vectors (
    session_id TEXT PRIMARY KEY,
    project_name TEXT,
    embedding BLOB,  -- Binary vector data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### readme_store
```sql
CREATE TABLE readme_store (
    project_name TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Configuration

Edit `src/config.py`:
```python
# Disable for fast startup, enable for semantic search
ENABLE_VECTOR_SEARCH = False
```

**Performance Optimizations**

1. **Lazy Loading**: Vector search only loads when needed
2. **Duplicate Prevention**: UNIQUE index on DC operations
3. **Pure DB Storage**: No file I/O overhead
4. **Batch Operations**: Efficient SQL queries

## Error Handling

All methods return error dict on failure:
```python
{"error": "Error description"}
```

Common errors:
- "project_name is required"
- "Project 'name' not found"
- "Could not save DC operations: ..."

## Module Structure

```
src/
├── logsec_core_v3.py       # Main server implementation
├── config.py               # Configuration settings
└── modules/
    ├── log_sniffer.py      # DC log reader
    ├── continuation_parser.py
    ├── extended_auto_tagger.py
    ├── knowledge_type_classifier.py
    ├── embedding_engine.py  # Lazy loaded
    └── vector_search.py     # Lazy loaded
```
