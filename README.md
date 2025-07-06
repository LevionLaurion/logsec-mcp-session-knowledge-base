# LogSec 3.0 - MCP Session Knowledge Management

[![License: MIT with restrictions](https://img.shields.io/badge/License-MIT%20with%20restrictions-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

Knowledge management system for AI session continuity, built as a Model Context Protocol (MCP) server.

## Features

- **Project Context Management**: Organize knowledge by project
- **Semantic Search**: Find relevant sessions using natural language  
- **Session Continuity**: Structured handoffs between sessions
- **Auto-Classification**: Automatic categorization into 8 knowledge types
- **Workspace Integration**: Analyzes Desktop Commander logs for context

## Quick Start

```bash
# Clone repository
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git
cd logsec-mcp-session-knowledge-base

# Install dependencies
install_dependencies.bat

# Test installation  
python tests/test_core_v3.py

# Configure Claude Desktop (see Installation Guide)
```

## Privacy Notice

Desktop Commander Integration: LogSec analyzes Desktop Commander logs to provide workspace context. Logs are stored at:
```
C:\Users\[Username]\.claude-server-commander-logs\
```

Consider using generic project names for sensitive work. See [SECURITY.md](SECURITY.md) for details.

## Core Commands

### lo_load
Load project knowledge with two modes:
```python
lo_load("project_name")              # Project overview + recent activity
lo_load("project_name", "query")     # Project context + semantic search
```

### lo_save
Save content with auto-classification:
```python
lo_save("project_name")              # Request summary from Claude
lo_save("project_name", "content")   # Save specific content
```

### lo_cont
Create continuation file for session handoff:
```python
lo_cont("project_name")              # Analyze current session
lo_cont("project_name", "mode")      # Focused extraction (debug/implement/refactor/document)
```
Creates/updates: `C:\LogSec\data\continuation\{project}_cont.md`

### lo_start
Start with continuation context:
```python
lo_start("project_name")             # Load continuation file + project context
```

## Architecture

```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py           # Main MCP server
│   ├── modules/                    # Feature modules
│   └── core/                       # Core components
├── data/
│   ├── database/
│   │   └── logsec_phase3.db       # SQLite database
│   └── sessions/                   # Session file storage
├── utilities/                      # Helper tools
└── docs/                          # Documentation
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

- [Installation Guide](docs/INSTALLATION_GUIDE.md) - Setup instructions
- [Developer Reference](docs/DEVELOPER_REFERENCE.md) - API documentation
- [Database Architecture](docs/DATABASE_ARCHITECTURE.md) - Technical details
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md) - Current state
- [Workspace Context](docs/WORKSPACE_CONTEXT.md) - Desktop Commander integration

## License

MIT License with Commercial Restriction

Free for personal, educational, and evaluation use.
Commercial use requires licensing. Contact: mail@laurion.de

See [LICENSE](LICENSE) for details.
