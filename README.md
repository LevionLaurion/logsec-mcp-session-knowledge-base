# LogSec MCP - Session Knowledge Management

[![MCP](https://img.shields.io/badge/MCP-2024--11--05-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production--Ready-success)](https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base)
[![Last Commit](https://img.shields.io/github/last-commit/LevionLaurion/logsec-mcp-session-knowledge-base)](https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base/commits/master)

Knowledge management system for AI session continuity, built as a Model Context Protocol (MCP) server.

## Overview

LogSec helps Claude maintain context across sessions by providing project knowledge management, semantic search, and structured session continuation.

### Core Features

- **Project Context Management**: Organize knowledge by project with automatic classification
- **Desktop Commander Integration**: Automatic tracking of file operations from DC logs
- **Semantic Search**: Find relevant sessions using natural language queries
- **Session Continuity**: Structured handoffs between sessions with continuation files
- **Auto-Classification**: Automatic categorization into 8 knowledge types

## Quick Start

```bash
# Clone the repository
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git C:\LogSec
cd C:\LogSec

# Install dependencies
pip install -r requirements.txt

# Test installation
python tests/test_core_v3.py

# Configure Claude Desktop (see Installation Guide)
```

## Basic Usage

```python
lo_start("project_name")              # Quick start with context
lo_save("project_name", "content")    # Save session with DC tracking
lo_load("project_name")               # Load project overview
lo_load("project_name", "query")      # Search sessions
lo_cont("project_name")               # Generate continuation context
lo_update("project_name")             # Update project documentation
```

## Architecture

LogSec implements a 3-tier knowledge architecture:

1. **Tier 1**: Quick summaries and recent activity
2. **Tier 2**: Structured project documentation (README in database)
3. **Tier 3**: Full session database with semantic search

### Directory Structure

```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py          # Main MCP server
│   ├── config.py                  # Configuration
│   └── modules/                   # Feature modules
│       ├── log_sniffer.py         # DC log reader
│       ├── embedding_engine.py    # Lazy loaded vectors
│       └── ...                    # Other modules
├── data/
│   ├── logsec.db                 # SQLite database
│   └── continuation/             # Continuation files
└── docs/                         # Documentation
```

## Desktop Commander Integration

LogSec automatically reads Desktop Commander logs to track file operations:

- Reads from: `%APPDATA%\Claude\logs\mcp-server-desktop-commander.log`
- Tracks: read_file, write_file, edit_block, execute_command, etc.
- Stores in `dc_operations` table with duplicate prevention
- No configuration needed - works automatically when DC is active

## Knowledge Types

Automatically categorizes content into 8 types:

- **milestone** - Major achievements and releases
- **implementation** - Code implementations and features
- **error_solution** - Bug fixes and troubleshooting
- **technical_decision** - Architecture and design choices
- **research_exploration** - Technical investigations
- **documentation** - Documentation and guides
- **optimization** - Performance improvements
- **general_progress** - Other project updates

## Performance

- Lazy-loaded vector search (loads on first use)
- Pure database storage - no file I/O overhead
- Duplicate prevention via UNIQUE constraints

## Configuration

Edit `src/config.py`:

```python
ENABLE_VECTOR_SEARCH = False  # Set True for semantic search (slower startup)
```

## Installation

See [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) for detailed setup instructions.

Add to your `claude_desktop_config.json`:

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

## Documentation

- [Installation Guide](docs/INSTALLATION_GUIDE.md) - Step-by-step setup
- [Developer Reference](docs/DEVELOPER_REFERENCE.md) - Complete API documentation
- [Database Architecture](docs/DATABASE_ARCHITECTURE.md) - Schema and design
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md) - Current features
- [Workspace Context](docs/WORKSPACE_CONTEXT.md) - DC integration details

## Testing

```bash
# Run test suite
python tests/test_core_v3.py
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome. Please follow existing code style and include tests for new features.

## Support

For issues or questions, please use GitHub issues or contact via repository.
