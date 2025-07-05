# LogSec 3.0 - Implementation Plan (Final)

## 🎯 **Core Strategy: Two-Mode lo_load + Seamless Continuation**

**Ziel**: Claude bekommt strukturierte Projekt-Informationen für intelligente Antworten

## 📊 **API Design - Final**

### **lo_load - Zwei Modi mit Tier 2 immer dabei**
```python
def lo_load(self, project_name: str, query: str = None) -> Dict:
    """Load project knowledge - always include Tier 2 context for Claude"""
    
    # Tier 2 wird IMMER geladen (Claude braucht Projekt-Kontext)
    tier_2_context = self._get_project_context(project_name)
    
    if query:
        # MODUS 2: Tier 2 + Tier 3 Vector Search
        search_results = self._search_knowledge_base(project_name, query)
        return {
            "project_context": tier_2_context,  # IMMER dabei für Claude
            "search_results": search_results,
            "query": query,
            "mode": "search"
        }
    else:
        # MODUS 1: Tier 2 + Tier 1 Summary  
        recent_activity = self._get_recent_sessions(project_name, limit=3)
        return {
            "project_context": tier_2_context,  # IMMER dabei für Claude
            "recent_activity": recent_activity,
            "theme_overview": self._get_theme_stats(project_name),
            "mode": "summary"
        }
```

### **lo_start - Seamless Session Continuation**
```python
def lo_start(self, project_name: str) -> Dict:
    """Seamless session continuation with workspace context"""
    
    # Letzte Session mit vollem Kontext laden
    last_session = self._get_last_session(project_name)
    session_content = self._load_session_content(last_session['session_id'])
    
    # Desktop Commander Logs analysieren
    dc_operations = self.dc_parser.extract_operations(session_content)
    workspace = self.workspace_gen.generate_context(dc_operations, project_name)
    
    # Continuation Parser
    parsed = self.parser.parse(session_content)
    
    return {
        "session_context": {
            "session_id": last_session['session_id'],
            "status": parsed.get('status'),
            "position": parsed.get('position'), 
            "next_steps": parsed.get('next'),
            "problems": parsed.get('problem'),
            "tried": parsed.get('tried')
        },
        "workspace_context": {
            "active_files": list(workspace.get('files', []))[:8],
            "working_directories": list(workspace.get('directories', []))[:5],
            "last_commands": workspace.get('commands', [])[:5],
            "recent_edits": workspace.get('recent_edits', [])[:8
        },
        "continuation_ready": True
    }
```

### **lo_save - Knowledge Base Feeding**
```python
def lo_save(self, content: str, project_name: str, session_id: str = None) -> Dict:
    """Save content + feed search database"""
    
    # Auto-Classification
    knowledge_type = self.classifier.classify(content)
    tags = self.auto_tagger.generate_tags(content)
    
    # Save to SQLite
    session_metadata = {
        'session_id': session_id or self._generate_session_id(),
        'project_name': project_name,
        'knowledge_type': knowledge_type,
        'tags': json.dumps(tags),
        'confidence_score': self.classifier.confidence
    }
    self._save_session_metadata(session_metadata)
    
    # Generate Vector Embedding für Tier 3 Suche
    embedding = self.embedding_engine.generate_embedding(content)
    self._save_vector_embedding(session_id, project_name, embedding)
    
    # Save content file
    self._save_session_file(session_id, content)
    
    return {"success": True, "session_id": session_id, "knowledge_type": knowledge_type}
```

## 🔧 **Implementation Priority**

### **Phase 1: Core Two-Mode lo_load (2-3 Stunden)**

#### 1.1 Project Context (Tier 2) System ⭐⭐⭐⭐⭐
```python
def _get_project_context(self, project_name: str) -> Dict:
    """Get essential project context (Tier 2) - always included"""
    
    # README aus DB oder generiert
    readme = self._get_or_generate_readme(project_name)
    
    # Projekt-Statistiken
    stats = self._get_project_stats(project_name)
    
    return {
        "name": project_name,
        "description": readme.get('description', ''),
        "current_phase": readme.get('phase', ''),
        "tech_stack": readme.get('tech_stack', []),
        "key_components": readme.get('components', []),
        "total_sessions": stats.get('total_sessions', 0),
        "last_activity": stats.get('last_activity', None),
        "main_directories": self._get_project_directories(project_name)
    }
```

#### 1.2 Vector Search Integration ⭐⭐⭐⭐⭐
```python
def _search_knowledge_base(self, project_name: str, query: str) -> List[Dict]:
    """Search Tier 3 - Vector search within project boundaries"""
    
    # Generate query embedding
    query_embedding = self.embedding_engine.generate_embedding(query)
    
    # Search nur innerhalb des Projekts
    with sqlite3.connect(self.db_path) as conn:
        # Get vector embeddings for project
        cursor = conn.execute("""
            SELECT sv.session_id, sv.embedding, sm.knowledge_type, sm.timestamp, sm.tags
            FROM session_vectors sv
            JOIN session_metadata sm ON sv.session_id = sm.session_id
            WHERE sv.project_name = ?
            ORDER BY sm.timestamp DESC
        """, (project_name,))
        
        results = []
        for row in cursor:
            # Calculate similarity
            stored_embedding = np.frombuffer(row[1], dtype=np.float32)
            similarity = cosine_similarity([query_embedding], [stored_embedding])[0][0]
            
            if similarity > 0.6:  # Threshold
                results.append({
                    "session_id": row[0],
                    "similarity": similarity,
                    "knowledge_type": row[2],
                    "timestamp": row[3],
                    "tags": json.loads(row[4]) if row[4] else []
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:10]
```

### **Phase 2: lo_start Enhancement (1-2 Stunden)**

#### 2.1 Desktop Commander Log Parser ⭐⭐⭐⭐
```python
class DesktopCommanderParser:
    def extract_operations(self, session_content: str) -> Dict:
        """Extract workspace context from Desktop Commander logs"""
        
        operations = {
            'files': set(),
            'directories': set(),
            'commands': [],
            'recent_edits': []
        }
        
        # Parse DC function calls
        patterns = {
            'read_file': r'desktop-commander:read_file.*?"path":\s*"([^"]+)"',
            'write_file': r'desktop-commander:write_file.*?"path":\s*"([^"]+)"',
            'edit_block': r'desktop-commander:edit_block.*?"file_path":\s*"([^"]+)"',
            'execute_command': r'desktop-commander:execute_command.*?"command":\s*"([^"]+)"',
            'list_directory': r'desktop-commander:list_directory.*?"path":\s*"([^"]+)"'
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, session_content, re.MULTILINE)
            for match in matches:
                if pattern_name in ['read_file', 'write_file']:
                    operations['files'].add(match)
                    operations['directories'].add(os.path.dirname(match))
                elif pattern_name == 'edit_block':
                    operations['recent_edits'].append(match)
                elif pattern_name == 'execute_command':
                    operations['commands'].append(match)
                elif pattern_name == 'list_directory':
                    operations['directories'].add(match)
        
        return {
            'files': list(operations['files'])[-10:],  # Last 10 files
            'directories': list(operations['directories'])[-5:],  # Last 5 dirs
            'commands': operations['commands'][-5:],  # Last 5 commands
            'recent_edits': operations['recent_edits'][-8:]  # Last 8 edits
        }
```

### **Phase 3: Database Schema & Tools (1 Stunde)**

#### 3.1 Vector Storage Schema
```sql
-- Vector embeddings for Tier 3 search
CREATE TABLE IF NOT EXISTS session_vectors (
    session_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    embedding BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES session_metadata(session_id)
);

-- Project context storage (Tier 2)
CREATE TABLE IF NOT EXISTS project_context (
    project_name TEXT PRIMARY KEY,
    readme_content TEXT,
    description TEXT,
    current_phase TEXT,
    tech_stack TEXT,  -- JSON array
    key_components TEXT,  -- JSON array
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indices
CREATE INDEX IF NOT EXISTS idx_project_vectors ON session_vectors(project_name);
CREATE INDEX IF NOT EXISTS idx_project_knowledge ON session_metadata(project_name, knowledge_type, timestamp);
```

#### 3.2 MCP Tool Registration
```python
# Updated tool definitions
tools = [
    {
        "name": "lo_load",
        "description": "Load project knowledge - two modes: summary or search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                "query": {"type": "string", "description": "Search query for Tier 3 knowledge base (optional)"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "lo_start",
        "description": "Quick start - seamless session continuation with workspace context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name (REQUIRED)"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "lo_save",
        "description": "Save content with auto-classification and vector embedding",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to save"},
                "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                "session_id": {"type": "string", "description": "Session ID (optional)"}
            },
            "required": ["content", "project_name"]
        }
    }
]
```

## 📊 **Expected Output Examples**

### **lo_load logsec** (Modus 1: Summary)
```json
{
    "project_context": {
        "name": "logsec",
        "description": "Knowledge management system with MCP integration",
        "current_phase": "Phase 3 - Vector search implementation", 
        "tech_stack": ["Python", "SQLite", "MCP", "FAISS"],
        "total_sessions": 47,
        "last_activity": "2 hours ago"
    },
    "recent_activity": [
        {"session": "Vector search testing", "timestamp": "2h ago"},
        {"session": "Database schema update", "timestamp": "4h ago"},
        {"session": "MCP integration debug", "timestamp": "1d ago"}
    ],
    "theme_overview": {
        "api_doc": 8,
        "implementation": 12,
        "debug": 5,
        "architecture": 3
    },
    "mode": "summary"
}
```

### **lo_load logsec "API integration"** (Modus 2: Search)
```json
{
    "project_context": {
        "name": "logsec",
        "description": "Knowledge management system with MCP integration",
        "current_phase": "Phase 3 - Vector search implementation",
        "tech_stack": ["Python", "SQLite", "MCP", "FAISS"]
    },
    "search_results": [
        {
            "session_id": "sess_001",
            "similarity": 0.89,
            "knowledge_type": "api_doc",
            "timestamp": "2 hours ago",
            "tags": ["MCP", "REST", "integration"]
        },
        {
            "session_id": "sess_045", 
            "similarity": 0.76,
            "knowledge_type": "implementation",
            "timestamp": "1 day ago",
            "tags": ["API", "endpoints", "Python"]
        }
    ],
    "query": "API integration",
    "mode": "search"
}
```

## 🚀 **Migration Steps**

1. **Backup aktuelle DB**
2. **Schema erweitern** (Vector tables)
3. **Vector Search Module integrieren**
4. **lo_load zwei Modi implementieren**
5. **lo_start Desktop Commander Parser**
6. **Testing mit realem LogSec-Projekt**

## 🎯 **Success Criteria**

- ✅ `lo_load logsec` → Projekt-Kontext + Recent Activity (< 1s)
- ✅ `lo_load logsec "MCP"` → Projekt-Kontext + Relevante Sessions (< 2s)  
- ✅ `lo_start logsec` → Nahtlose Fortsetzung mit Workspace (< 1s)
- ✅ Claude bekommt strukturierte Informationen für intelligente Antworten

---
**Ready für Implementation!** 🚀
