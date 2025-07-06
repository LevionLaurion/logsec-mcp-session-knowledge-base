# LogSec Installation Guide

## Prerequisites

- Python 3.9 or higher
- Claude Desktop application
- Windows, macOS, or Linux operating system

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git C:\LogSec
cd C:\LogSec
```

For Unix/macOS:
```bash
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git ~/LogSec
cd ~/LogSec
```

### 2. Verify Installation

```bash
python --version  # Should show Python 3.9+
python src/logsec_core_v3.py  # Should start without errors, Ctrl+C to exit
```

### 3. Configure Claude Desktop

Add LogSec to your Claude Desktop configuration:

**Windows:**
1. Open `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the following configuration:

```json
{
  "mcpServers": {
    "logsec": {
      "command": "python",
      "args": ["C:\\LogSec\\src\\logsec_core_v3.py"],
      "cwd": "C:\\LogSec",
      "env": {
        "PYTHONPATH": "C:\\LogSec",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**macOS/Linux:**
1. Open `~/.config/Claude/claude_desktop_config.json`
2. Add the following configuration:

```json
{
  "mcpServers": {
    "logsec": {
      "command": "python3",
      "args": ["/home/username/LogSec/src/logsec_core_v3.py"],
      "cwd": "/home/username/LogSec",
      "env": {
        "PYTHONPATH": "/home/username/LogSec",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Close and restart Claude Desktop to load the MCP server.

### 5. Verify MCP Connection

In Claude, try:
```
lo_start test
```

You should see a response confirming the session start.

## Configuration

LogSec configuration is stored in `src/config/config.json`:

```json
{
  "db_path": "C:\\LogSec\\data\\database\\logsec_phase3.db",
  "projects_dir": "C:\\LogSec\\data\\projects",
  "templates_dir": "C:\\LogSec\\data\\templates"
}
```

Adjust paths as needed for your system.

## Troubleshooting

### MCP Server Not Found

- Ensure Python path is correct in `claude_desktop_config.json`
- Check that `logsec_core_v3.py` exists in the `src` directory
- Verify Python is in your system PATH

### Permission Errors

- Ensure you have write permissions to the LogSec directory
- On Unix systems, you may need to make the script executable:
  ```bash
  chmod +x src/logsec_core_v3.py
  ```

### Import Errors

- LogSec uses only Python standard library
- No external dependencies should be needed
- Ensure Python 3.9+ is installed

## Next Steps

See the main [README](../README.md) for usage instructions and examples.