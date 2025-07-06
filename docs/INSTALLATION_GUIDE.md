# LogSec Installation Guide

## Prerequisites

- Python 3.9 or higher
- Claude Desktop
- Desktop Commander MCP server (for DC operations tracking)

## Quick Install

### 1. Clone Repository

```bash
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git C:\LogSec
cd C:\LogSec
```

Or download and extract ZIP to `C:\LogSec`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- mcp==1.1.0
- sentence-transformers
- numpy
- nltk

### 3. Claude Desktop Configuration

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

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

### 4. Verify Installation

1. Restart Claude Desktop
2. Look for "logsec" in the 🔌 menu
3. Test with: `lo_start test_project`

## Desktop Commander Integration

LogSec automatically reads DC logs from:
```
%APPDATA%\Claude\logs\mcp-server-desktop-commander.log
```

No additional configuration needed - just ensure Desktop Commander is installed and active.

## Configuration Options

Edit `src/config.py` to customize:

```python
# Performance settings
ENABLE_VECTOR_SEARCH = False  # Set True for semantic search (slower startup)

# Logging
LOG_FILE = "logsec.log"
LOG_LEVEL = logging.INFO
```

## Directory Structure

```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py      # Main server
│   ├── config.py              # Settings
│   └── modules/               # Core modules
├── data/
│   ├── logsec.db             # Main database
│   └── continuation/         # Continuation files
└── docs/                     # Documentation
```

## Troubleshooting

### "logsec not found" in Claude
1. Check config.json syntax (valid JSON)
2. Verify Python path
3. Restart Claude Desktop

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### DC operations not tracked
1. Verify Desktop Commander is running
2. Check log file exists at `%APPDATA%\Claude\logs\`
3. Ensure write permissions

### Slow startup with vector search
Normal behavior when `ENABLE_VECTOR_SEARCH = True`
- First load: ~20 seconds
- Solution: Set to `False` for fast startup

## Updating LogSec

```bash
cd C:\LogSec
git pull
pip install -r requirements.txt --upgrade
```

## Uninstalling

1. Remove from claude_desktop_config.json
2. Delete C:\LogSec directory
3. (Optional) Remove continuation files from Documents
