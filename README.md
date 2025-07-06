# LogSec MCP Session Knowledge Base

A Model Context Protocol (MCP) server for intelligent session knowledge management with a 3-tier architecture.

## 🚀 Features

### Three-Tier Knowledge System
- **Tier 1**: Working Memory - Last session for seamless continuation
- **Tier 2**: Project Context - Persistent project information (always loaded)
- **Tier 3**: Knowledge Base - Searchable session history with vector search

### Core Commands

#### `lo_load project_name [query]`
Load project knowledge with two modes:
- **Summary Mode**: `lo_load logsec` - Shows project context + recent activity
- **Search Mode**: `lo_load logsec "API"` - Vector search in knowledge base

Features:
- Displays numbered documentation list (1-8)
- Shows project root, GitHub URL, and directories
- Users can reference docs by number: "load 3"

#### `lo_save project_name [content]`
Save knowledge with flexible options:
- **Auto-summary**: `lo_save logsec` - Generates session summary
- **Specific content**: `lo_save logsec "implementation details"` - Saves exact content
- **Categorized**: `lo_save logsec "doku"` - Tagged saves (doku, bug, feature)

#### `lo_start project_name`
Seamless session continuation with:
- Tier 2 project context (root, GitHub, directories)
- Last session information
- Workspace context from Desktop Commander

#### `lo_cont query`
Parse structured continuation context:
```
STATUS: Current task
POSITION: file.py:line
NEXT: Next steps
```

## 🛠️ Tech Stack

- Python 3.x
- SQLite Database
- MCP (Model Context Protocol)
- Sentence Transformers for vector search
- Auto-classification system (8 knowledge types)

## 📁 Project Structure

```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py          # MCP server implementation
│   └── modules/                   # Feature modules
├── data/
│   ├── database/                  # SQLite database
│   └── sessions/                  # Session storage
└── docs/                          # Documentation
```

## 🔧 Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure Claude Desktop to use LogSec MCP server
4. Start using `lo_load`, `lo_save`, `lo_start` commands

## 📊 Performance

- `lo_start`: <50ms response time
- `lo_load`: <100ms including vector search
- `lo_save`: <100ms with auto-classification
- Vector search: Sub-second for 100k+ documents

## 🎯 Use Cases

- **Development Sessions**: Save and continue coding sessions
- **Documentation**: Track project documentation updates
- **Debugging**: Store error solutions and fixes
- **Knowledge Management**: Build searchable project knowledge base

## 📝 License

MIT License - see LICENSE file for details