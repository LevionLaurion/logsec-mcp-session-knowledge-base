# 🚀 LogSec 3.0 Installation Guide

## Quick Start

### 1. Prerequisites
- **Python 3.8+** installed
- **Git** (optional, for version control)
- **Claude Desktop** (for MCP integration)
- **Desktop Commander** (for workspace context features)

### 2. Installation Steps

#### Step 1: Clone or Download
```bash
# If you have Git:
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git LogSec
cd LogSec

# Or download and extract to your preferred location
```

#### Step 2: Install Dependencies
```bash
# Windows:
install_dependencies.bat

# Linux/macOS:
pip install -r requirements.txt
```

#### Step 3: Test Installation
```bash
python tests/test_core_v3.py
```

You should see:
```
[SUCCESS] All tests passed! LogSec Core v3 is ready!
```

### 3. Desktop Commander Integration (Required for Workspace Features)

**⚠️ Important**: LogSec uses Desktop Commander for workspace context analysis. You need to configure access to Desktop Commander logs.

#### Enable Desktop Commander in Claude Desktop

Add Desktop Commander to your `claude_desktop_config.json` **before** LogSec:

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "desktop-commander"]
    },
    "logsec": {
      "command": "python", 
      "args": ["/absolute/path/to/LogSec/src/logsec_core_v3.py"]
    }
  }
}
```

#### Configure Log Access Permissions

LogSec needs read access to Desktop Commander logs for workspace context:

**Windows:**
```
Log Location: C:\Users\[Username]\.claude-server-commander-logs\
Required: Read permissions to this directory
```

**macOS:**
```
Log Location: ~/.claude-server-commander-logs/
Required: Read permissions to this directory
```

**Linux:**
```
Log Location: ~/.claude-server-commander-logs/
Required: Read permissions to this directory
```

### 4. Claude Desktop MCP Configuration

#### Step 1: Locate Claude Config File

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

#### Step 2: Add LogSec MCP Server

Add LogSec to your `claude_desktop_config.json` with **absolute paths**:

**Windows Example:**
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

**macOS/Linux Example:**
```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "npx", 
      "args": ["-y", "desktop-commander"]
    },
    "logsec": {
      "command": "python",
      "args": ["/home/username/LogSec/src/logsec_core_v3.py"],
      "env": {}
    }
  }
}
```

#### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to load both MCP servers.

### 5. Verify Complete Integration

Test all LogSec commands in Claude:

```bash
# Basic project loading
lo_load("test_project")

# Save with workspace context
lo_save("Test content", "test_project")

# Session continuation (requires Desktop Commander logs)
lo_start("test_project")

# Structured continuation parsing
lo_cont("""
STATUS: Testing LogSec installation
POSITION: Installation guide
NEXT: Verify all features work
""")
```

## 📁 Directory Structure

```
LogSec/
├── src/
│   ├── logsec_core_v3.py      # Main MCP server
│   ├── modules/               # Feature modules
│   └── core/                  # Core components
├── data/
│   ├── database/              # SQLite databases
│   │   └── logsec_phase3.db   # Main knowledge base
│   └── sessions/              # Saved session files
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Dependencies
└── install_dependencies.bat   # Windows installer
```

## 🔧 Advanced Configuration

### Database Location

**Default Locations:**
- **Windows**: `C:\LogSec\data\database\logsec_phase3.db`
- **macOS/Linux**: `~/LogSec/data/database/logsec_phase3.db`

To change, edit `src/logsec_core_v3.py`:
```python
self.db_path = Path("your/custom/path/logsec_phase3.db")
```

### Session Storage

**Default Locations:**
- **Windows**: `C:\LogSec\data\sessions\`
- **macOS/Linux**: `~/LogSec/data/sessions/`

### Desktop Commander Log Access

LogSec automatically detects Desktop Commander logs at:

**Windows:**
```
C:\Users\[Username]\.claude-server-commander-logs\
```

**macOS/Linux:**
```
~/.claude-server-commander-logs/
```

If logs are in a different location, set environment variable:
```bash
export CLAUDE_COMMANDER_LOGS="/custom/path/to/logs"
```

## 🎯 Usage Examples

### Basic Project Management
```python
# Save project content
lo_save("""
# Project Setup Complete
- Database configured
- API endpoints ready
- Tests passing
""", "my_project")

# Load project overview
overview = lo_load("my_project")

# Search within project
results = lo_load("my_project", "API endpoints")
```

### Workspace Context Features
```python
# Quick start with workspace analysis
context = lo_start("my_project")
# Analyzes recent Desktop Commander operations
# Shows files worked on, commands executed, etc.

# Structured continuation
lo_cont("""
STATUS: Implementing user authentication
POSITION: auth.py:45 - login_handler()
PROBLEM: Password hashing not working
TRIED: bcrypt, scrypt implementations
NEXT: Try argon2 library
TODO:
- Fix password hashing
- Add session management
- Update tests
CONTEXT: Building secure login system
""")
```

## 🐛 Troubleshooting

### Common Issues

#### "Desktop Commander not found"
1. Ensure Desktop Commander is installed: `npx -y desktop-commander`
2. Verify it's in your Claude Desktop config
3. Check Desktop Commander appears in Claude's MCP server list

#### "Cannot access log files"
1. Check log directory exists and has read permissions
2. Verify Desktop Commander is generating logs
3. For Windows: Ensure user has access to `%USERPROFILE%\.claude-server-commander-logs\`

#### "Module not found" Error
```bash
# Ensure you're in the correct directory
cd /path/to/LogSec
python tests/test_core_v3.py

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Database Errors
```bash
# Reset database (will lose data!)
rm data/database/logsec_phase3.db
python tests/test_core_v3.py  # Will recreate
```

#### MCP Server Not Loading
1. **Check JSON syntax** in `claude_desktop_config.json`
2. **Use absolute paths** for all file references
3. **Restart Claude Desktop** after config changes
4. **Check Claude Desktop logs** for error messages

### Platform-Specific Issues

#### Windows
- Use backslashes or double backslashes in paths: `C:\\LogSec\\`
- Ensure Python is in PATH: `python --version`
- Use Command Prompt or PowerShell for testing

#### macOS
- May need to install Xcode Command Line Tools: `xcode-select --install`
- Use forward slashes in paths: `/Users/username/LogSec/`
- Check Python 3 is default: `python3 --version`

#### Linux
- Ensure pip is installed: `sudo apt install python3-pip`
- May need to use `python3` instead of `python`
- Check file permissions: `chmod +x install_dependencies.sh`

## 🔍 Verification Checklist

✅ **Python 3.8+ installed and accessible**  
✅ **LogSec dependencies installed** (`pip install -r requirements.txt`)  
✅ **Desktop Commander installed** (`npx -y desktop-commander`)  
✅ **Both MCP servers in Claude Desktop config**  
✅ **Absolute paths used in configuration**  
✅ **Claude Desktop restarted after config changes**  
✅ **Log directory accessible** (`~/.claude-server-commander-logs/`)  
✅ **All LogSec commands working** (`lo_load`, `lo_save`, `lo_start`, `lo_cont`)  

## 📚 Further Documentation

- [README.md](../README.md) - Project overview and features
- [DEVELOPER_REFERENCE.md](DEVELOPER_REFERENCE.md) - Complete API documentation
- [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md) - Technical database details
- [LOGSEC_3.0_STATUS.md](LOGSEC_3.0_STATUS.md) - Current implementation status

## 🤝 Support

**Having Issues?**
1. Check this troubleshooting guide first
2. Run `python tests/test_core_v3.py` for diagnostics
3. Check Claude Desktop logs for MCP errors
4. Create a GitHub issue with your error logs

**Community:**
- GitHub Issues: [Report bugs or ask questions](https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base/issues)
- Documentation: Browse the `/docs` folder for detailed guides

---

🚀 **LogSec Installation Complete!**  
Ready for intelligent session management with workspace context analysis.
