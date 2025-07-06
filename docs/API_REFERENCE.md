# LogSec API Reference

## Overview

LogSec implements the Model Context Protocol (MCP) and provides five core commands for knowledge management.

## Commands

### lo_start

Initialize a session with automatic continuation loading.

**Syntax:**
```
lo_start <project_name>
```

**Parameters:**
- `project_name` (required): Name of the project (case-insensitive)

**Returns:**
- Project context including README if exists
- Continuation file content if exists
- Session statistics

**Example:**
```
lo_start myproject
```

### lo_save

Save content to the project knowledge base.

**Syntax:**
```
lo_save <project_name> [content]
```

**Parameters:**
- `project_name` (required): Name of the project
- `content` (optional): Content to save. Auto-generates if not provided.

**Returns:**
- Confirmation with session ID
- Extracted tags
- Storage location

**Example:**
```
lo_save myproject "API endpoint /users returns user list"
```

### lo_load

Load project knowledge with optional search.

**Syntax:**
```
lo_load <project_name> [search_query]
```

**Parameters:**
- `project_name` (required): Name of the project
- `search_query` (optional): Keywords to search for

**Returns:**
- Project README if exists
- Search results if query provided
- Recent sessions if no query
- Total session count

**Example:**
```
lo_load myproject
lo_load myproject "database schema"
```

### lo_update

Generate instructions for creating/updating project documentation.

**Syntax:**
```
lo_update <project_name> [mode]
```

**Parameters:**
- `project_name` (required): Name of the project
- `mode` (optional): "normal" (default) or "deep" for comprehensive analysis

**Returns:**
- Instructions for creating project README
- Target save path

**Example:**
```
lo_update myproject
lo_update myproject deep
```

### lo_cont

Create continuation file for session handoff.

**Syntax:**
```
lo_cont <project_name> [mode]
```

**Parameters:**
- `project_name` (required): Name of the project
- `mode` (optional): "auto" (default), "debug", or "implement"

**Returns:**
- Instructions for creating continuation file
- Target save path

**Example:**
```
lo_cont myproject
lo_cont myproject implement
```

## Data Structures

### Session Storage

Sessions are stored in SQLite with the following schema:

```sql
CREATE TABLE session_metadata (
    session_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    content_text TEXT,
    knowledge_type TEXT,
    timestamp DATETIME,
    tags TEXT
);
```

### Project Structure

Each project has its own directory:
```
data/projects/{project_name}/
├── readme.md         # Project documentation
└── continuation.md   # Session continuation
```

### Response Format

All commands return structured responses:

```json
{
  "response": "Formatted response text with project information"
}
```

Error responses:
```json
{
  "error": "Error description"
}
```

## Configuration

Configuration via `src/config/config.json`:

```json
{
  "db_path": "path/to/database.db",
  "projects_dir": "path/to/projects",
  "templates_dir": "path/to/templates"
}
```

## Template System

Response templates are stored in `data/templates/`:
- `command_templates.json`: Response formatting  
- `update_universal.txt`: Default update instructions

Users can create custom templates:
- `update_deep.txt`: For comprehensive analysis (git-ignored)
- `*_custom.txt`: Personal templates (git-ignored)

See `data/templates/README.md` for template documentation.

## Error Handling

- Invalid project names are normalized (lowercase)
- Missing projects create new entries
- File operations have fallback error handling
- Database operations use transactions

## Limitations

- Project names should be alphanumeric with underscores/hyphens
- No external dependencies (Python stdlib only)
- Python 3.9+ required
- Single-user local operation only
- No concurrent access protection