# LogSec 3.0 - Developer Quick Reference (Revised)

## 🚀 Current Server Commands

```bash
# Current (working)
lo_load project_name:"logsec"
lo_save content:"Your content here" project_name:"myproject"
lo_cont query:"STATUS: Working on feature X..."
```

## 🎯 New API Strategy: Intelligent Project Isolation

### Planned Commands (After Refactoring)
```bash
# Project-specific operations (project_name becomes REQUIRED)
lo_load logsec                    # Intelligent project overview
lo_load logsec "API integration"  # Semantic search within project
lo_start logsec                   # Quick-start last session
lo_save "content" logsec          # Save to specific project

# Project management
lo_list_projects                  # List all projects with stats
lo_delete_project myapp           # Delete complete project
lo_export_project logsec          # Export project data
```

## 🔧 Implementation Roadmap

### 1. Project Isolation (Phase 1 - Critical)

```python
# API Changes - project_name becomes REQUIRED
def lo_load(self, project_name: str, query: str = None) -> Dict:
    """Load project knowledge with strict isolation"""
    if query:
        # Semantic search within project only
        return self._search_project(project_name, query)
    else:
        # Intelligent project overview
        return self._get_project_overview(project_name)

def lo_save(self, content: str, project_name: str, session_id: str = None) -> Dict:
    """Save content with mandatory project assignment"""
    # Always enforce project_name

def lo_cont(self, query: str, project_name: str = None) -> Dict:
    """Continue from last session - auto-detect project if not specified"""
    if not project_name:
        project_name = self._detect_project_from_query(query)
```

### 2. Database Schema Extension

```sql
-- Enhanced session metadata
ALTER TABLE session_metadata 
ADD COLUMN project_isolation_enforced BOOLEAN DEFAULT 1;

-- New vector storage with project isolation
CREATE TABLE IF NOT EXISTS session_vectors (
    session_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,  -- Enforces project separation
    embedding BLOB,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES session_metadata(session_id)
);

-- Performance indices for project-specific queries
CREATE INDEX idx_project_knowledge ON session_metadata(project_name, knowledge_type, timestamp);
CREATE INDEX idx_project_vectors ON session_vectors(project_name);
CREATE INDEX idx_project_search ON session_metadata(project_name, timestamp DESC);
```

### 3. Vector Search Integration

```python
# In __init__:
from modules.vector_search import VectorSearchEngine
from modules.embedding_engine import EmbeddingEngine

self.embedding_engine = EmbeddingEngine()
self.vector_search = VectorSearchEngine()

# Project-aware search
def _search_project(self, project_name: str, query: str) -> Dict:
    """Semantic search within project boundaries"""
    # 1. Generate query embedding
    query_embedding = self.embedding_engine.generate_embedding(query)
    
    # 2. Search only within project
    results = self.vector_search.search_project(
        project_name=project_name,
        query_embedding=query_embedding,
        k=10
    )
    
    # 3. Group by knowledge_type and format
    return self._format_search_results(results, project_name, query)
```

### 4. Intelligent Project Overview

```python
def _get_project_overview(self, project_name: str) -> Dict:
    """Generate intelligent project overview with themes"""
    
    # Get all sessions for project
    sessions = self._get_project_sessions(project_name)
    
    # Group by knowledge_type
    themes = self._group_sessions_by_theme(sessions)
    
    # Generate suggestions
    suggestions = self._generate_query_suggestions(themes)
    
    return {
        "project": project_name,
        "total_sessions": len(sessions),
        "themes": themes,
        "suggestions": suggestions,
        "latest_activity": sessions[0]['timestamp'] if sessions else None
    }

def _generate_query_suggestions(self, themes: Dict) -> List[str]:
    """Generate helpful search suggestions based on project content"""
    suggestions = []
    
    theme_keywords = {
        "api_doc": ["API endpoints", "REST documentation", "OpenAPI"],
        "implementation": ["Python code", "implementation details", "functions"],
        "debug": ["error solutions", "debugging steps", "troubleshooting"],
        "schema": ["database schema", "data structure", "models"],
        "architecture": ["system design", "architecture", "components"]
    }
    
    for theme, sessions in themes.items():
        if theme in theme_keywords:
            suggestions.extend(theme_keywords[theme])
            
    return suggestions[:6]  # Limit to top 6 suggestions
```

## 📊 Database Queries (Updated)

### Project-specific session retrieval
```sql
-- Get sessions by project and type
SELECT session_id, timestamp, knowledge_type, tags
FROM session_metadata
WHERE project_name = ?
AND knowledge_type IN ('api_doc', 'schema')
ORDER BY timestamp DESC
LIMIT 10;

-- Get project statistics
SELECT 
    knowledge_type,
    COUNT(*) as session_count,
    MAX(timestamp) as latest_activity
FROM session_metadata
WHERE project_name = ?
GROUP BY knowledge_type
ORDER BY session_count DESC;

-- Vector search within project
SELECT sm.session_id, sm.timestamp, sm.knowledge_type, sm.tags
FROM session_metadata sm
JOIN session_vectors sv ON sm.session_id = sv.session_id
WHERE sm.project_name = ?
AND sv.similarity_score > 0.7
ORDER BY sv.similarity_score DESC
LIMIT 10;
```

## 🔧 Tool Registration (Updated)

```python
# Updated tools for MCP
tools = [
    {
        "name": "lo_load",
        "description": "Load project knowledge with optional semantic search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                "query": {"type": "string", "description": "Semantic search query (optional)"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "lo_save", 
        "description": "Save content to specific project",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to save"},
                "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                "session_id": {"type": "string", "description": "Session ID (optional)"}
            },
            "required": ["content", "project_name"]
        }
    },
    {
        "name": "lo_start",
        "description": "Quick start - load last session with project context",
        "inputSchema": {
            "type": "object", 
            "properties": {
                "project_name": {"type": "string", "description": "Project name (REQUIRED)"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "lo_list_projects",
        "description": "List all available projects with statistics",
        "inputSchema": {"type": "object", "properties": {}}
    }
]
```

## 🔒 Project Isolation Implementation

### Validation Functions
```python
def _validate_project_access(self, project_name: str) -> bool:
    """Validate project exists and is accessible"""
    if not project_name or not project_name.strip():
        raise ValueError("Project name is required and cannot be empty")
        
    # Check if project exists
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM session_metadata WHERE project_name = ?",
            (project_name,)
        )
        count = cursor.fetchone()[0]
        return count > 0

def _ensure_project_isolation(self, project_name: str, operation: str):
    """Ensure no cross-project data leakage"""
    # Log all project operations for audit
    logger.info(f"Project operation: {operation} on {project_name}")
    
    # Additional security checks if needed
    if not self._validate_project_access(project_name):
        logger.warning(f"Access to non-existent project: {project_name}")
```

## 🐛 Debug Commands (Updated)

```bash
# Check project isolation
sqlite3 C:\LogSec\data\database\logsec_phase3.db "
SELECT project_name, COUNT(*) as sessions 
FROM session_metadata 
GROUP BY project_name;
"

# Verify vector isolation
sqlite3 C:\LogSec\data\database\logsec_phase3.db "
SELECT sm.project_name, COUNT(sv.session_id) as vectors
FROM session_metadata sm
LEFT JOIN session_vectors sv ON sm.session_id = sv.session_id
GROUP BY sm.project_name;
"

# Test project-specific search
lo_load logsec "API"
lo_load myproject "API"  # Should return different results
```

## ⚡ Performance Tips (Project-Aware)

1. **Project-specific indices**: Already implemented in schema
2. **Limit search scope**: Always filter by project_name first
3. **Cache project stats**: Store theme counts for quick overview
4. **Batch vector operations**: Process embeddings per project

## 🔍 Testing Project Isolation

```python
# Test strict project separation
def test_project_isolation():
    # Save to different projects
    lo_save("API doc for project A", "projectA")
    lo_save("API doc for project B", "projectB")
    
    # Search should return different results
    results_a = lo_load("projectA", "API")
    results_b = lo_load("projectB", "API")
    
    assert results_a != results_b
    assert all(r["project"] == "projectA" for r in results_a["sessions"])
    assert all(r["project"] == "projectB" for r in results_b["sessions"])

# Test project management
def test_project_management():
    projects = lo_list_projects()
    assert "logsec" in [p["name"] for p in projects["projects"]]
    
    # Test project overview
    overview = lo_load("logsec")
    assert "themes" in overview
    assert "suggestions" in overview
```

## 📁 File Locations (Unchanged)

- **Main server**: `C:\LogSec\src\logsec_core_v3_enhanced.py`
- **Test locally**: `python C:\LogSec\src\logsec_core_v3_enhanced.py`
- **Sessions**: `C:\LogSec\data\sessions\*.md`
- **Database**: `C:\LogSec\data\database\logsec_phase3.db`

## 🚀 Migration Steps

1. **Backup current database**
2. **Add vector tables** with project isolation
3. **Update API signatures** (project_name required)
4. **Integrate vector search** with project filtering  
5. **Add project management commands**
6. **Test isolation thoroughly**

---
**Next Priority**: Start with API refactoring for project isolation
