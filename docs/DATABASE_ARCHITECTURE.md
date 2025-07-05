# LogSec Database Architecture

## Overview
LogSec uses multiple SQLite databases for different components. The system automatically initializes and synchronizes these databases on startup.

## Database Locations

### 1. Main Knowledge Graph
**Path**: `C:\LogSec\knowledge\shared\graph_memory\knowledge_graph.db`
- Primary graph database used by LogSecIntelligence
- Contains entities, relationships, and sessions
- Auto-created on first run

### 2. Vector Search Database
**Path**: `C:\LogSec\knowledge\graph_memory\knowledge_graph.db`
- Used by VectorSearchEngine for similarity links
- Synchronized with main database
- Required for FAISS vector operations

### 3. Legacy Database
**Path**: `C:\LogSec\knowledge\graph.db`
- Backward compatibility path
- Auto-synced from main database
- Can be removed in future versions

### 4. Brain Database
**Path**: `C:\LogSec\logsec_brain.db`
- Central session storage
- Project metadata and statistics
- Independent from graph databases

## Startup Process

1. **Run `start_logsec.bat`**:
   - Checks Python installation
   - Runs `init_databases.py`
   - Starts MCP server

2. **Database Initialization**:
   - Creates all missing databases
   - Ensures proper schema in each
   - Synchronizes content between databases

3. **Schema Structure**:
   ```sql
   -- Entities table
   CREATE TABLE entities (
       id INTEGER PRIMARY KEY,
       name TEXT NOT NULL,
       entity_type TEXT NOT NULL,
       project TEXT,
       metadata TEXT
   );
   
   -- Relationships table
   CREATE TABLE relationships (
       source_id INTEGER,
       target_id INTEGER,
       relationship_type TEXT,
       strength REAL
   );
   
   -- Sessions table
   CREATE TABLE sessions (
       session_id TEXT UNIQUE,
       project TEXT,
       tier TEXT,
       summary TEXT
   );
   ```

## Troubleshooting

### Database is empty (0 bytes)
Run: `python C:\LogSec\init_databases.py`

### "unable to open database file" error
1. Check if directories exist
2. Run `init_databases.py`
3. Verify file permissions

### Sync issues between databases
The system auto-syncs on startup, but you can force sync:
```bash
python C:\LogSec\init_databases.py
```

## Best Practices

1. **Always use `start_logsec.bat`** to ensure databases are initialized
2. **Don't manually delete databases** - use init script to recreate
3. **Backup regularly**: Copy entire `C:\LogSec\knowledge` folder
4. **Monitor size**: Databases grow with usage, check periodically

## Future Improvements

- Consolidate to single database location
- Add automatic backup functionality
- Implement database migration system
- Add health check endpoint
