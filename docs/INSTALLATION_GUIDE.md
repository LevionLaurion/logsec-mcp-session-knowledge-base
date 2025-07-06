# LogSec Installation Guide

## Prerequisites

- Python 3.8 or higher
- Git (optional)
- Claude Desktop
- Desktop Commander (for workspace features)

## Installation Steps

### 1. Download LogSec

Using Git:
```bash
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git LogSec
cd LogSec
```

Or download and extract the ZIP file.

### 2. Install Dependencies

Windows:
```bash
install_dependencies.bat
```

Linux/macOS:
```bash
pip install -r requirements.txt
```

### 3. Test Installation

```bash
python tests/test_core_v3.py
```

Expected output:
```
[SUCCESS] All tests passed! LogSec Core v3 is ready!
```

## Claude Desktop Configuration

### 1. Locate Config File

Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

macOS:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Linux:
```
~/.config/Claude/claude_desktop_config.json
```

### 2. Add LogSec MCP Server

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "desktop-commander"]
    },
    "logsec": {
      "command": "python",
      "args": ["C:\\LogSec\\src\\logsec_core_v3.py"],
      "env": {}
    }
  }
}
```

Note: Use absolute paths. Replace `C:\\LogSec` with your installation path.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP servers.

## Desktop Commander Setup

LogSec requires Desktop Commander for workspace context features.

### Log Access

LogSec needs read access to Desktop Commander logs:

Windows:
```
C:\Users\[Username]\.claude-server-commander-logs\
```

macOS/Linux:
```
~/.claude-server-commander-logs/
```

## Verification

Test all commands in Claude:

```python
# Basic test
lo_load("test_project")

# Save content
lo_save("test_project", "Test content")

# Start session
lo_start("test_project")
```

## Directory Structure

```
LogSec/
├── src/
│   ├── logsec_core_v3.py      # Main MCP server
│   ├── modules/               # Feature modules
│   └── core/                  # Core components
├── data/
│   ├── database/              # SQLite database
│   └── sessions/              # Session files
├── tests/                     # Test suite
├── docs/                      # Documentation
└── requirements.txt           # Python dependencies
```

## Troubleshooting

### Module not found

Ensure you're in the correct directory:
```bash
cd /path/to/LogSec
python tests/test_core_v3.py
```

### MCP server not loading

1. Check JSON syntax in `claude_desktop_config.json`
2. Use absolute paths
3. Restart Claude Desktop
4. Check Claude Desktop logs

### Desktop Commander not found

1. Install Desktop Commander: `npx -y desktop-commander`
2. Add to Claude Desktop config before LogSec
3. Verify it appears in Claude's MCP server list

### Database errors

Reset database (data loss warning):
```bash
rm data/database/logsec_phase3.db
python tests/test_core_v3.py
```

### Permission errors

Windows:
- Run as administrator if needed
- Check file permissions

macOS/Linux:
- Check file permissions: `ls -la`
- Fix permissions: `chmod 755 src/logsec_core_v3.py`

## Platform Notes

### Windows
- Use double backslashes in paths: `C:\\LogSec\\`
- Python must be in PATH

### macOS
- May need: `xcode-select --install`
- Use `python3` if `python` doesn't work

### Linux
- Install pip if missing: `sudo apt install python3-pip`
- May need to use `python3` instead of `python`

## Support

1. Check troubleshooting section
2. Run diagnostic: `python tests/test_core_v3.py`
3. Check Claude Desktop logs
4. Create GitHub issue with error details
