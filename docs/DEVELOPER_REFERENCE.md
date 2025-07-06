# LogSec 3.0 - Developer Reference

## 🚀 API Reference

LogSec 3.0 provides a knowledge management system for AI session continuity through MCP integration.

## 📋 Available Commands

### Core API Functions

#### `lo_load(project_name, query=None)`
**Load project knowledge with two-mode operation**

```python
# Mode 1: Project Overview (Summary)
lo_load("logsec")
# Returns: Project context + recent activity + theme overview

# Mode 2: Semantic Search  
lo_load("logsec", "API integration")
# Returns: Project context + vector search results
```

**Parameters:**
- `project_name` (str, required): Target project name
- `query` (str, optional): Search query for semantic search mode

**Returns:**
```python
{
    "project_context": {
        "name": "logsec",
        "description": "Knowledge management system...",
        "phase": "Active development",
        "total_sessions": 47,
        "last_activity": "2025-07-05T22:47"
    },
    "mode": "summary|search",
    # Mode 1: Summary
    "recent_activity": [...],
    "theme_overview": {...},
    # Mode 2: Search
    "search_results": [...],
    "query": "..."
}
```

#### `lo_save(project_name, content=None, session_id=None)`
**Save knowledge with auto-summary or specific content**

```python
# Mode 1: Request auto-summary from Claude
result = lo_save("logsec")
# Returns request for Claude to summarize the session

# Mode 2: Save specific content
lo_save("logsec", """
# API Integration Complete
- Implemented REST endpoints
- Added MCP server support
- Vector search operational
""")
```

**Parameters:**
- `project_name` (str, required): Target project (alphanumeric + _-)
- `content` (str, optional): Content to save. If omitted, requests summary
- `session_id` (str, optional): Custom session ID

**Returns (Mode 1 - Summary Request):**
```python
{
    "success": True,
    "action": "request_summary",
    "prompt": "Please create a summary of this session including...",
    "instructions": "After creating the summary, save it with: lo_save logsec \"[your summary]\"",
    "project_name": "logsec",
    "session_id": "session_20250706_120000"
}
```

**Returns (Mode 2 - Content Saved):**
```python
{
    "session_id": "session_20250706_120000",
    "project": "logsec",
    "knowledge_type": "milestone",
    "tags": ["api", "integration", "mcp", "vector_search"],
    "confidence": 0.89,
    "filepath": "C:\\LogSec\\data\\sessions\\session_20250706_120000_logsec.md"
}
```

#### `lo_cont(query, language="en")`
**Parse structured continuation context**

```python
lo_cont("""
STATUS: Implementing user authentication
POSITION: auth.py:line 45 - login_handler()
NEXT: Add password hashing
TODO: 
- Implement JWT tokens
- Add session management
CONTEXT: Building secure login system
""")
```

**Returns:**
```python
{
    "parsed": {
        "status": "Implementing user authentication",
        "position": "auth.py:line 45 - login_handler()",
        "next": "Add password hashing",
        "todo": ["Implement JWT tokens", "Add session management"],
        "context": "Building secure login system"
    },
    "suggestions": [...],
    "continuation_ready": True
}
```

#### `lo_start(project_name)`
**Session continuation with workspace context**

```python
lo_start("logsec")
```

**Returns:**
```python
{
    "project_status": "Active development (47 sessions)",
    "last_session": {
        "session_id": "session_20250705_225044",
        "timestamp": "2 hours ago",
        "type": "milestone"
    },
    "workspace_context": {
        "active_files": ["src/logsec_core_v3.py", "docs/README.md"],
        "working_directories": ["C:/LogSec/src", "C:/LogSec/docs"],
        "recent_commands": ["python test_core_v3.py", "git push"]
    },
    "continuation_ready": True
}
```

## 🛠️ Implementation Details

### Auto-Classification System

**Knowledge Types** (automatically detected):
```python
KNOWLEDGE_TYPES = {
    "api_doc": "API documentation, endpoints, integration guides",
    "implementation": "Code implementations, technical solutions", 
    "architecture": "System design, technical architecture",
    "schema": "Database schemas, data structures",
    "milestone": "Project milestones, version releases",
    "debug": "Bug fixes, troubleshooting sessions",
    "continuation": "Session handoffs with STATUS/NEXT format",
    "documentation": "General documentation, user guides"
}
```

**Classification Confidence:**
- `0.8-1.0`: High confidence (auto-classified)
- `0.6-0.8`: Medium confidence (user can override)
- `0.0-0.6`: Low confidence (defaults to 'documentation')

### Vector Search Engine

**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Similarity**: Cosine similarity with configurable threshold

**Search Process:**
1. Generate query embedding
2. Filter by project scope
3. Calculate similarities
4. Rank and format results

### Auto-Tagging System

**NLP Pipeline:**
```python
def generate_tags(content):
    # 1. Extract technical terms
    tech_terms = extract_technical_keywords(content)
    
    # 2. Identify programming languages
    languages = detect_programming_languages(content)
    
    # 3. Extract domain concepts
    concepts = extract_domain_concepts(content)
    
    # 4. Combine and rank
    return rank_tags(tech_terms + languages + concepts)
```

**Tag Categories:**
- **Technical**: API, REST, MCP, database, vector
- **Languages**: Python, JavaScript, SQL, JSON
- **Domains**: authentication, testing, deployment
- **Project-specific**: logsec, integration, session

## 🗃️ Database Queries

### Common Query Patterns

#### Project Statistics
```sql
SELECT 
    knowledge_type,
    COUNT(*) as count,
    MAX(timestamp) as latest
FROM session_metadata 
WHERE project_name = ?
GROUP BY knowledge_type
ORDER BY count DESC;
```

#### Recent Sessions
```sql
SELECT session_id, timestamp, knowledge_type, tags
FROM session_metadata
WHERE project_name = ?
ORDER BY timestamp DESC
LIMIT 10;
```

#### Vector Search
```sql
SELECT sm.session_id, sm.knowledge_type, sm.tags, sm.timestamp
FROM session_metadata sm
WHERE sm.project_name = ?
AND sm.vector_embedding IS NOT NULL
ORDER BY sm.timestamp DESC;
```

#### Tag Analysis
```sql
SELECT t.tag, t.usage_count, COUNT(st.session_id) as project_usage
FROM tags t
JOIN session_tags st ON t.id = st.tag_id
JOIN session_metadata sm ON st.session_id = sm.session_id
WHERE sm.project_name = ?
GROUP BY t.tag
ORDER BY project_usage DESC;
```

## 🔧 MCP Tool Configuration

### Claude Desktop Integration

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

### Tool Definitions
```python
MCP_TOOLS = [
    {
        "name": "lo_load",
        "description": "Load project knowledge with optional semantic search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name (required)"},
                "query": {"type": "string", "description": "Search query (optional)"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "lo_save",
        "description": "Save content with auto-classification", 
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to save"},
                "project_name": {"type": "string", "description": "Project name (required)"},
                "session_id": {"type": "string", "description": "Session ID (optional)"}
            },
            "required": ["content", "project_name"]
        }
    },
    {
        "name": "lo_cont",
        "description": "Parse structured continuation context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Continuation context"},
                "language": {"type": "string", "description": "Language (en/de)", "default": "en"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "lo_start",
        "description": "Quick start with workspace context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name (required)"}
            },
            "required": ["project_name"]
        }
    }
]
```

## ⚡ Performance Optimization

### Caching Strategy
```python
# Project context caching
@lru_cache(maxsize=100)
def get_project_context(project_name):
    return self._load_project_context(project_name)

# Vector embedding caching  
@lru_cache(maxsize=1000)
def get_session_embedding(session_id):
    return self._load_vector_embedding(session_id)
```

### Batch Operations
```python
# Batch tag generation
def generate_tags_batch(contents):
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(self.auto_tagger.generate_tags, contents))

# Batch vector generation
def generate_embeddings_batch(contents):
    return self.embedding_engine.encode(contents, batch_size=32)
```

### Database Optimization
```python
# Connection pooling
def get_db_connection():
    if not hasattr(self, '_db_pool'):
        self._db_pool = sqlite3.connect(
            self.db_path, 
            check_same_thread=False,
            timeout=30.0
        )
    return self._db_pool

# Prepared statements
def prepare_statements():
    self.stmt_insert_session = self.conn.prepare(
        "INSERT INTO session_metadata (...) VALUES (?, ?, ?, ...)"
    )
```

## 🧪 Testing & Debugging

### Unit Tests
```python
def test_lo_load_summary_mode():
    result = lo_load("test_project")
    assert result["mode"] == "summary"
    assert "project_context" in result
    assert "recent_activity" in result

def test_lo_load_search_mode():
    result = lo_load("test_project", "API")
    assert result["mode"] == "search"
    assert "search_results" in result
    assert len(result["search_results"]) > 0

def test_auto_classification():
    content = "def api_endpoint(): return {'status': 'ok'}"
    result = lo_save(content, "test_project")
    assert result["knowledge_type"] == "implementation"
    assert "python" in result["tags"]
```

### Debug Commands
```python
# Check database status
def debug_database():
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM session_metadata")
        print(f"Total sessions: {cursor.fetchone()[0]}")

# Analyze project distribution
def debug_projects():
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("""
            SELECT project_name, COUNT(*) as sessions
            FROM session_metadata 
            GROUP BY project_name
        """)
        for row in cursor:
            print(f"{row[0]}: {row[1]} sessions")

# Test vector search
def debug_vector_search(project, query):
    result = lo_load(project, query)
    print(f"Found {len(result.get('search_results', []))} results")
    for r in result.get('search_results', [])[:3]:
        print(f"- {r['session_id']}: {r['similarity']:.3f}")
```

### Performance Monitoring
```python
import time
from functools import wraps

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}: {(end-start)*1000:.1f}ms")
        return result
    return wrapper

# Apply to key functions
@performance_monitor
def lo_load(self, project_name, query=None):
    # ... implementation
```

### Error Handling
```python
try:
    result = lo_load("project_name", "query")
except ProjectNotFoundError:
    # Handle missing project
    pass
except DatabaseError:
    # Handle database issues
    pass
except VectorSearchError:
    # Handle search failures
    pass
```

## 🔒 Security & Best Practices

### Data Security
- **Local Storage**: All data remains on local machine
- **No Network**: Database never transmitted externally
- **Access Control**: OS-level file permissions
- **Backup**: Regular automated backups recommended

### Best Practices
1. **Regular Backups**: Daily database backups
2. **Project Naming**: Use consistent, descriptive names
3. **Content Structure**: Use structured continuation format
4. **Performance**: Monitor database size and query performance
5. **Updates**: Keep LogSec updated for latest features

### Development Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure Claude Desktop
# Add MCP server configuration

# 3. Test installation
python tests/test_core_v3.py

# 4. Verify MCP integration
# Test commands in Claude Desktop

# 5. Setup backup schedule
# Configure daily database backups
```

---

**API Version**: 3.0  
**Last Updated**: 2025-07-05  
**Status**: ✅ Core functionality implemented