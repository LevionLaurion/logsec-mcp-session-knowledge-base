# LogSec 3.0 Database Architecture

## Overview

LogSec uses SQLite for all data storage with automatic initialization and indexing.

## Database Location

Primary: `C:\LogSec\data\database\logsec_phase3.db`

## Schema

### session_metadata

Primary knowledge storage table.

```sql
CREATE TABLE session_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    project_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    tags TEXT,                    -- JSON array
    knowledge_type TEXT,          -- 8 predefined types
    confidence_score REAL,        -- 0.0-1.0
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    content_text TEXT,
    vector_embedding BLOB,        -- 384-dimensional
    summary TEXT
);
```

### readme_store

Project context storage.

```sql
CREATE TABLE readme_store (
    project_name TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### continuation_data

Session continuation storage.

```sql
CREATE TABLE continuation_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    task TEXT,
    result TEXT,
    position TEXT,
    next_step TEXT,
    files TEXT,                   -- JSON array
    commands TEXT,                -- JSON array
    context TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### tags

Tag management.

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag TEXT UNIQUE NOT NULL,
    usage_count INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### session_tags

Many-to-many relationship.

```sql
CREATE TABLE session_tags (
    session_id TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    confidence REAL,
    PRIMARY KEY (session_id, tag_id),
    FOREIGN KEY (session_id) REFERENCES session_metadata(session_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);
```

## Indices

Database indices for common queries:

```sql
-- Project queries
CREATE INDEX idx_project_knowledge ON session_metadata(project_name, knowledge_type, timestamp DESC);
CREATE INDEX idx_project_time ON session_metadata(project_name, timestamp DESC);

-- Vector search
CREATE INDEX idx_project_vectors ON session_metadata(project_name) WHERE vector_embedding IS NOT NULL;

-- Tag searches
CREATE INDEX idx_session_tags ON session_tags(tag_id, confidence DESC);

-- Continuation data
CREATE INDEX idx_continuation_project ON continuation_data(project_name, created_at DESC);
```

## Data Types

### Knowledge Types
- `api_doc`: API documentation
- `implementation`: Code implementations
- `architecture`: System design
- `schema`: Data structures
- `milestone`: Project milestones
- `debug`: Bug fixes
- `continuation`: Session handoffs
- `documentation`: General docs

### Vector Embeddings
- Model: sentence-transformers/all-MiniLM-L6-v2
- Storage: Binary BLOB
- Search: Cosine similarity

## Operations

### Common Queries

Project statistics:
```sql
SELECT knowledge_type, COUNT(*) as count
FROM session_metadata 
WHERE project_name = ?
GROUP BY knowledge_type;
```

Recent sessions:
```sql
SELECT session_id, timestamp, knowledge_type
FROM session_metadata
WHERE project_name = ?
ORDER BY timestamp DESC
LIMIT 10;
```

Vector search preparation:
```sql
SELECT session_id, vector_embedding
FROM session_metadata
WHERE project_name = ?
AND vector_embedding IS NOT NULL;
```

## Maintenance

### Database Commands
```sql
VACUUM;
ANALYZE;
REINDEX;
```

### Cleanup
```sql
-- Remove orphaned tags
DELETE FROM session_tags 
WHERE session_id NOT IN (SELECT session_id FROM session_metadata);

-- Update tag counts
UPDATE tags SET usage_count = (
    SELECT COUNT(*) FROM session_tags WHERE tag_id = tags.id
);
```

## Backup

Recommended daily backup:
```python
import shutil
shutil.copy2("logsec_phase3.db", f"backup/logsec_{date}.db")
```

## Integrity

Check database health:
```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

## Migration

Schema versioning handled automatically on startup. Migrations applied incrementally.

## Database Details

No systematic testing has been conducted. The system uses standard SQLite functionality.

## Security

- Local storage only
- File system permissions for access control
- No encryption by default
- No network access
