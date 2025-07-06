# LogSec 3.0 - Developer Reference

## API Reference

### lo_load

Load project knowledge with two-mode operation.

**Syntax:**
```python
lo_load(project_name: str, query: str = None) -> Dict
```

**Parameters:**
- `project_name` (required): Target project name
- `query` (optional): Search query for semantic search mode

**Returns:**

Mode 1 (Summary):
```python
{
    "project": "project_name",
    "project_context": {...},
    "recent_activity": [...],
    "theme_overview": {...},
    "mode": "summary"
}
```

Mode 2 (Search):
```python
{
    "project": "project_name",
    "project_context": {...},
    "search_results": [...],
    "query": "search query",
    "mode": "search"
}
```

### lo_save

Save content with auto-classification.

**Syntax:**
```python
lo_save(project_name: str, content: str = None, session_id: str = None) -> Dict
```

**Parameters:**
- `project_name` (required): Target project (alphanumeric + _-)
- `content` (optional): Content to save. If omitted, requests summary
- `session_id` (optional): Custom session ID

**Returns (Summary Request):**
```python
{
    "success": True,
    "action": "request_summary",
    "prompt": "...",
    "project_name": "project_name",
    "session_id": "session_20250107_120000"
}
```

**Returns (Content Saved):**
```python
{
    "session_id": "session_20250107_120000",
    "project": "project_name",
    "knowledge_type": "implementation",
    "tags": ["python", "api", "mcp"],
    "confidence": 0.89,
    "filepath": "C:\\LogSec\\data\\sessions\\session_20250107_120000_project.md"
}
```

### lo_cont

Generate prompt for Claude to analyze current session.

**Syntax:**
```python
lo_cont(project_name: str, mode: str = "auto") -> Dict
```

**Parameters:**
- `project_name` (required): Target project
- `mode` (optional): Focus mode
  - `"auto"`: Extract all relevant information (default)
  - `"debug"`: Focus on errors and debugging
  - `"implement"`: Focus on implementation tasks
  - `"refactor"`: Focus on code structure
  - `"document"`: Focus on documentation

**Returns:**
```python
{
    "success": True,
    "action": "request_analysis",
    "prompt": "...",
    "project": "project_name",
    "mode": "auto",
    "instructions": "Claude will analyze the session and save the continuation data."
}
```

### lo_cont_save

Save continuation data analyzed by Claude.

**Syntax:**
```python
lo_cont_save(project_name: str, continuation_data: Dict) -> Dict
```

**Parameters:**
- `project_name` (required): Target project
- `continuation_data` (required): Analyzed data with structure:
  ```python
  {
      "task": "Description of what was worked on",
      "result": "What was accomplished",
      "position": "file.py:line or location",
      "next": "Next logical step",
      "files": [{"path": "path/to/file", "relevance": "edited|viewed"}],
      "commands": [{"cmd": "command", "status": "success|failed"}],
      "context": "Important context"
  }
  ```

**Returns:**
```python
{
    "success": True,
    "project": "project_name",
    "continuation_saved": {...},
    "message": "Continuation context saved for project_name. Use lo_start('project_name') to resume."
}
```

### lo_start

Load project with continuation context.

**Syntax:**
```python
lo_start(project_name: str) -> Dict
```

**Parameters:**
- `project_name` (required): Target project

**Returns:**
```python
{
    "project_context": {...},
    "continuation_data": {...},
    "continuation_ready": True,
    "project": "project_name",
    "source": "enhanced_continuation"
}
```

## Database Operations

### Session Storage

Sessions are stored with:
- Automatic timestamp generation
- Project association
- Knowledge type classification
- Tag extraction
- Vector embedding generation
- Confidence scoring

### Vector Search

- Model: sentence-transformers/all-MiniLM-L6-v2
- Similarity: Cosine similarity
- Threshold: 0.6

### Knowledge Types

| Type | Description |
|------|-------------|
| api_doc | API documentation, endpoints |
| implementation | Code implementations |
| architecture | System design |
| schema | Data structures |
| milestone | Version releases |
| debug | Bug fixes |
| continuation | Session handoffs |
| documentation | General docs |

## Configuration

### MCP Server Setup

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "logsec": {
      "command": "python",
      "args": ["C:\\LogSec\\src\\logsec_core_v3.py"],
      "env": {}
    }
  }
}
```

### Database Location
- Default: `C:\LogSec\data\database\logsec_phase3.db`
- Sessions: `C:\LogSec\data\sessions\`

### Desktop Commander Integration
- Log location: `C:\Users\[Username]\.claude-server-commander-logs\`
- Required for workspace context features

## Error Handling

All functions return error dictionaries on failure:
```python
{"error": "error message"}
```

Common errors:
- Missing project_name
- Invalid project name format
- Database access issues
- File not found
- Vector search failures

## Implementation Notes

- Database indices for common queries
- Vector embeddings cached in memory
- Batch operations for tag generation
- Connection pooling for SQLite

## Testing

Run test suite:
```bash
python tests/test_core_v3.py
```

Tests cover:
- Database initialization
- API functionality
- Vector search accuracy
- Classification accuracy
- Error handling
