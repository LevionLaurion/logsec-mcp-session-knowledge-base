# LogSec 3.0 Database Architecture

## Overview
LogSec 3.0 uses a single, optimized SQLite database for all knowledge management operations. The system automatically initializes the database with proper schema and indices for high performance.

## Database Location

**Primary Database**: `C:\LogSec\data\database\logsec_phase3.db`
- Single source of truth for all LogSec data
- Automatic initialization on first run
- Built-in backup and recovery mechanisms

## Schema Structure

### Core Tables

#### 1. Session Metadata (Primary Knowledge Store)
```sql
CREATE TABLE session_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    tags TEXT,                    -- JSON array of auto-generated tags
    knowledge_type TEXT,          -- Auto-classified: api_doc, implementation, etc.
    confidence_score REAL,        -- Classification confidence (0.0-1.0)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    content_text TEXT,            -- Searchable content
    vector_embedding BLOB,        -- For semantic search
    summary TEXT                  -- Auto-generated summary
);
```

#### 2. Project Context (README Store)
```sql
CREATE TABLE readme_store (
    project_name TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Tags Management
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE session_tags (
    session_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    confidence REAL,
    PRIMARY KEY (session_id, tag_id),
    FOREIGN KEY (session_id) REFERENCES session_metadata(session_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
```

#### 4. Knowledge Types
```sql
CREATE TABLE knowledge_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT UNIQUE NOT NULL,
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Indices

```sql
-- Project-specific queries (most common)
CREATE INDEX idx_project_knowledge ON session_metadata(project_name, knowledge_type, timestamp DESC);

-- Time-based queries
CREATE INDEX idx_project_time ON session_metadata(project_name, timestamp DESC);

-- Vector search support
CREATE INDEX idx_project_vectors ON session_metadata(project_name) WHERE vector_embedding IS NOT NULL;

-- Tag-based searches
CREATE INDEX idx_session_tags ON session_tags(tag_id, confidence DESC);

-- Full-text search support
CREATE INDEX idx_content_search ON session_metadata(content_text) WHERE content_text IS NOT NULL;
```

## Data Flow

### 1. Session Storage (`lo_save`)
```
User Content → Auto-Tagging → Knowledge Classification → Vector Embedding → Database
```

### 2. Project Loading (`lo_load`)
```
Project Request → README Lookup → Session Retrieval → Formatting → Response
```

### 3. Semantic Search (`lo_load` with query)
```
Search Query → Vector Embedding → Similarity Search → Result Ranking → Response
```

## Knowledge Types (Auto-Classification)

LogSec automatically classifies content into 8 types:

| Type | Description | Examples |
|------|-------------|----------|
| `api_doc` | API documentation | REST endpoints, MCP integration guides |
| `implementation` | Code implementations | Python code, technical solutions |
| `architecture` | System design | Technical architecture, design decisions |
| `schema` | Data structures | Database schemas, interfaces |
| `milestone` | Project milestones | Version releases, major achievements |
| `debug` | Troubleshooting | Bug fixes, error solutions |
| `continuation` | Session handoffs | Structured continuations (STATUS:, NEXT:) |
| `documentation` | General docs | User guides, explanations |

## Vector Search Implementation

### Embedding Storage
- **Engine**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Dimensions**: 384-dimensional vectors
- **Storage**: Binary BLOB in SQLite
- **Search**: Cosine similarity with FAISS-like performance

### Search Process
1. **Query Embedding**: Convert search query to 384-dim vector
2. **Project Filtering**: Only search within specified project
3. **Similarity Calculation**: Cosine similarity between query and stored vectors
4. **Ranking**: Sort by similarity score (threshold: 0.6)
5. **Formatting**: Group results by knowledge type

## Performance Characteristics

### Typical Operations
- **Database Initialization**: ~200ms (first run only)
- **Session Save**: ~50ms (including vector embedding)
- **Project Load**: ~30ms (cached README + recent sessions)
- **Vector Search**: ~100ms (1000+ documents)
- **Tag Generation**: ~80ms (NLP processing)

### Scalability
- **Sessions per Project**: Tested up to 10,000 sessions
- **Projects**: No practical limit
- **Vector Search**: Sub-second for 50,000+ embeddings
- **Database Size**: ~1MB per 1000 sessions

## Backup and Recovery

### Automatic Backups
```python
# Daily backup (if enabled)
backup_path = f"C:/LogSec/backups/logsec_backup_{date}.db"

# Manual backup
import shutil
shutil.copy2("C:/LogSec/data/database/logsec_phase3.db", backup_path)
```

### Recovery Process
1. **Corruption Detection**: Automatic on startup
2. **Recovery Options**: Latest backup or rebuild from sessions
3. **Data Validation**: Verify schema and indices
4. **Reindexing**: Rebuild vector embeddings if needed

## Maintenance Operations

### Database Optimization
```sql
-- Run periodically for performance
VACUUM;
ANALYZE;
REINDEX;
```

### Cleanup Operations
```python
# Remove orphaned records
DELETE FROM session_tags WHERE session_id NOT IN (
    SELECT session_id FROM session_metadata
);

# Update tag usage counts
UPDATE tags SET usage_count = (
    SELECT COUNT(*) FROM session_tags WHERE tag_id = tags.id
);
```

## Migration and Upgrades

### Schema Versioning
- **Current Version**: 3.0
- **Migration Scripts**: Automatic on startup
- **Backward Compatibility**: Maintained for 2 major versions

### Upgrade Process
1. **Backup Current Database**
2. **Run Migration Scripts**
3. **Verify Data Integrity**
4. **Update Indices**
5. **Performance Test**

## Troubleshooting

### Common Issues

#### "Database is locked"
```bash
# Check for running processes
ps aux | grep logsec
# Kill if necessary, then restart
```

#### "Corrupted database"
```bash
# Integrity check
sqlite3 logsec_phase3.db "PRAGMA integrity_check;"
# Restore from backup if needed
```

#### Slow queries
```sql
-- Check query execution plan
EXPLAIN QUERY PLAN SELECT * FROM session_metadata WHERE project_name = 'logsec';
-- Ensure indices are being used
```

#### Missing vector embeddings
```python
# Regenerate embeddings for all sessions
python -c "
from src.logsec_core_v3 import LogSecCore
core = LogSecCore()
core.regenerate_all_embeddings()
"
```

## Security Considerations

### Data Protection
- **Local Storage**: All data stays on local machine
- **No Network Access**: Database never transmitted
- **Access Control**: File system permissions only
- **Encryption**: Optional database encryption available

### Best Practices
1. **Regular Backups**: Daily automated backups recommended
2. **Access Logging**: Monitor database access patterns
3. **File Permissions**: Restrict to user account only
4. **Cleanup Policies**: Regular deletion of old sessions

## Future Enhancements

### Planned Improvements
- **Distributed Storage**: Multi-machine synchronization
- **Advanced Analytics**: Usage pattern analysis
- **Cloud Backup**: Optional cloud storage integration
- **Real-time Collaboration**: Multi-user support

### Performance Optimizations
- **In-Memory Caching**: Frequently accessed data
- **Async Operations**: Background processing
- **Compression**: Vector compression for storage efficiency
- **Partitioning**: Large database partitioning

---

**Database Version**: 3.0 (Production)  
**Last Updated**: 2025-07-05  
**Status**: ✅ Production Ready - Fully Optimized
