# LogSec Database Architecture

## Overview

LogSec uses SQLite for all data storage with automatic initialization, indexing, and duplicate prevention.

## Database Location

`C:\LogSec\data\logsec.db` (single unified database)

## Schema Design

### session_metadata

Primary knowledge storage with full session content.

```sql
CREATE TABLE session_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    tags TEXT,                    -- JSON array of extracted tags
    knowledge_type TEXT,          -- 8 predefined types
    confidence_score REAL,        -- 0.0-1.0 classification confidence
    content_text TEXT,            -- Full session content
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_project_timestamp ON session_metadata(project_name, timestamp);
CREATE INDEX idx_knowledge_type ON session_metadata(knowledge_type);
```

### dc_operations

Desktop Commander operations tracking with duplicate prevention.

```sql
CREATE TABLE dc_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    project_name TEXT,
    operation_type TEXT,          -- read_file, write_file, etc.
    path TEXT,
    details TEXT,                 -- JSON with operation specifics
    timestamp TIMESTAMP,
    UNIQUE(timestamp, operation_type, path)  -- Prevent duplicates
);

CREATE INDEX idx_dc_project ON dc_operations(project_name);
CREATE INDEX idx_dc_operation ON dc_operations(operation_type);
```

### session_vectors

Embeddings for semantic search (lazy loaded).

```sql
CREATE TABLE session_vectors (
    session_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    embedding BLOB,               -- 384-dimensional binary vector
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES session_metadata(session_id)
);

CREATE INDEX idx_vectors_project ON session_vectors(project_name);
```

### readme_store

Tier 2 project documentation.

```sql
CREATE TABLE readme_store (
    project_name TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Knowledge Types

Eight predefined categories:
1. **milestone** - Major achievements
2. **implementation** - Code/features added
3. **error_solution** - Debugging/fixes
4. **technical_decision** - Architecture choices
5. **research_exploration** - Investigations
6. **documentation** - Docs/comments
7. **optimization** - Performance improvements
8. **general_progress** - Other updates

## Data Flow

1. **Session Save** - session_metadata + dc_operations + vectors
2. **DC Tracking** - LogSniffer to dc_operations table
3. **Search Query** - Lazy load vectors, similarity search
4. **Update Command** - Analyze sessions, update readme_store

## Performance Optimizations

### Indexes
- Project + timestamp for fast retrieval
- Operation type for DC analysis
- Knowledge type for categorization

### Lazy Loading
- Vectors only loaded on first search
- Embeddings generated on-demand
- 20s to 2s startup improvement

### Duplicate Prevention
- UNIQUE constraint on DC operations
- Prevents log replay issues
- Maintains data integrity

## Storage Structure

Per session stores:
- Metadata and timestamps
- Full content text
- Vector embeddings (384 dimensions)
- DC operations log

Database grows with usage.

## Migration Notes

From v2 to v3:
- Moved from file storage to pure DB
- Added dc_operations table
- Removed continuation_data table (uses files)
- Unified database location

## Backup Strategy

```bash
# Manual backup
copy C:\LogSec\data\logsec.db C:\LogSec\data\backup\logsec_backup.db

# Git tracking (recommended)
git add -A && git commit -m "Session backup"
```
