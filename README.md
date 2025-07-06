# LogSec MCP - Model Context Protocol Session Knowledge Base

## 🚀 Quick Start

```bash
# Installation
mcp install src
mcp serve src

# In Claude
lo_start logsec     # Start with project context
lo_save logsec      # Save current session
lo_update logsec    # Update project documentation
```

## 📋 Overview

LogSec implements a **3-Tier Knowledge Architecture** for AI collaboration:

- **Tier 1**: Project summaries and recent activity (quick overview)
- **Tier 2**: Structured project documentation (README in DB)
- **Tier 3**: Full session database with vector search

## 🛠️ Core Features

### Session Management
- **Pure database storage** - No file clutter
- **Automatic tagging** - Smart classification of content
- **Desktop Commander integration** - Tracks all file operations
- **Vector search** - Semantic search across sessions (lazy loaded)

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `lo_start` | Load project context and continue | `lo_start logsec` |
| `lo_save` | Save current session to database | `lo_save logsec "bug fix"` |
| `lo_load` | Load project knowledge | `lo_load logsec` |
| `lo_load` + query | Search sessions | `lo_load logsec "error handling"` |
| `lo_cont` | Generate continuation context | `lo_cont logsec` |
| `lo_update` | Update project README | `lo_update logsec` |

## 🏗️ Architecture

```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py      # Main server
│   ├── config.py               # Configuration
│   └── modules/                # Feature modules
│       ├── log_sniffer.py      # DC log reader
│       └── ...                 # Other modules
├── data/
│   ├── database/
│   │   └── logsec_phase3.db   # Main database
│   └── continuation/           # Continuation files
└── docs/                       # Documentation
```

## 🗄️ Database Schema

All data stored in SQLite (`logsec_phase3.db`):
- `session_metadata` - Session content and metadata
- `dc_operations` - Desktop Commander operations tracking
- `session_vectors` - Vector embeddings for search
- `readme_store` - Tier 2 project documentation
- `tags`, `knowledge_types` - Classification data

## ⚡ Performance

- **Fast startup**: ~2 seconds (vector search lazy loaded)
- **No file I/O**: Everything in database
- **Duplicate prevention**: Unique constraints on operations

## 🔧 Configuration

Edit `src/config.py`:
```python
ENABLE_VECTOR_SEARCH = False  # Set True for semantic search
```

## 📝 License

MIT License - See LICENSE file for details.
