# LogSec MCP - Session Knowledge Management

[![MCP](https://img.shields.io/badge/MCP-2024--11--05-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Knowledge management system for AI session continuity, built as a Model Context Protocol (MCP) server.

## Overview

LogSec provides persistent memory for AI assistants through a clean 3-tier architecture. The system enables context preservation across conversations with minimal overhead.

### Core Features

- **Session Persistence**: SQLite-based storage for conversation history
- **Project Organization**: Isolated knowledge bases per project
- **Search Capability**: Keyword-based content retrieval
- **Continuation System**: Structured session handoffs
- **Template Engine**: Customizable response patterns

## Installation

```bash
# Clone repository
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git
cd LogSec

# Configure Claude Desktop
# Add to %APPDATA%\Claude\claude_desktop_config.json:
{
  "mcpServers": {
    "logsec": {
      "command": "python",
      "args": ["C:\\LogSec\\src\\logsec_core_v3.py"],
      "cwd": "C:\\LogSec"
    }
  }
}

# Restart Claude Desktop
```

## Usage

### Basic Commands

```
lo_start <project>     # Initialize session with continuation
lo_save <project>      # Save current context
lo_load <project>      # Load project knowledge
lo_update <project>    # Generate project documentation
lo_cont <project>      # Create continuation file
```

### Examples

```
lo_start myproject
lo_save myproject "Implementation details for the API endpoint"
lo_load myproject "API"
```

## Architecture

### Directory Structure

```
LogSec/
├── src/
│   ├── logsec_core_v3.py    # Main MCP server (563 lines)
│   └── config/
│       └── config.json      # Configuration
├── data/
│   ├── projects/            # Project data
│   │   └── {project}/
│   │       ├── readme.md
│   │       └── continuation.md
│   ├── database/
│   │   └── logsec_phase3.db # Session storage
│   └── templates/           # Response templates
└── docs/
    └── DIRECTORY_STRUCTURE.md
```

### Implementation

The system implements the Model Context Protocol with:
- JSON-RPC message handling
- Tool registration and dispatch
- Error handling and logging
- Template-based responses

## Configuration

Configuration via `src/config/config.json`:

```json
{
  "db_path": "C:\\LogSec\\data\\database\\logsec_phase3.db",
  "projects_dir": "C:\\LogSec\\data\\projects",
  "templates_dir": "C:\\LogSec\\data\\templates"
}
```

## Development

### Requirements

- Python 3.9+
- No external dependencies (uses stdlib only)
- Windows/Linux/macOS compatible

### Testing

```bash
python -m unittest discover tests/
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License - see LICENSE file for details.