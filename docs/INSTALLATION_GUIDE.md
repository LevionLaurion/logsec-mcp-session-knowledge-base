# 🚀 LogSec 3.0 Installation Guide

## Quick Start

### 1. Prerequisites
- Python 3.8+ installed
- Git (optional, for version control)
- Claude Desktop (for MCP integration)

### 2. Installation Steps

#### Step 1: Clone or Download
```bash
# If you have Git:
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git LogSec
cd LogSec

# Or download and extract to C:\LogSec
```

#### Step 2: Install Dependencies
```bash
# Run the installation script
START_LYNNVEST.bat

# Or manually:
pip install -r requirements.txt
```

#### Step 3: Test Installation
```bash
python test_core_v3.py
```

You should see:
```
[SUCCESS] All tests passed! LogSec Core v3 is ready!
```

### 3. Claude Desktop Integration

#### Step 1: Locate Claude Config
Find your Claude Desktop configuration file:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

#### Step 2: Add LogSec MCP Server
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "logsec": {
      "command": "python",
      "args": ["C:\\LogSec\\logsec_core_v3.py"],
      "env": {}
    }
  }
}
```

#### Step 3: Restart Claude Desktop
Close and reopen Claude Desktop to load the MCP server.

### 4. Verify Integration

In Claude, you should now have access to:
- `lo_load` - Load project knowledge
- `lo_save` - Save with auto-tagging
- `lo_cont` - Continue from previous session

Test it:
```
lo_load("your_project_name")
```

## 📁 Directory Structure

```
C:\LogSec\
├── logsec_core_v3.py      # Main MCP server
├── database/              # SQLite databases
│   └── logsec_phase2.db   # Main knowledge base
├── sessions/              # Saved session files
├── modules/               # Feature modules
│   ├── auto_tagger.py
│   ├── extended_auto_tagger.py
│   └── knowledge_type_classifier.py
├── core/                  # Core components
│   └── continuation_parser.py
└── utils/                 # Utilities
```

## 🔧 Configuration

### Database Location
Default: `C:\LogSec\database\logsec_phase2.db`

To change, edit line 66 in `logsec_core_v3.py`:
```python
self.db_path = self.base_dir / "database" / "your_database.db"
```

### Session Storage
Default: `C:\LogSec\sessions\`

To change, edit line 233 in `logsec_core_v3.py`:
```python
session_dir = self.base_dir / "your_sessions_folder"
```

## 🎯 Usage Examples

### Save a Session
```python
# In Claude:
lo_save("""
# Today's Progress
- Implemented user authentication
- Fixed database connection bug
- Added API endpoints
""", "my_project")
```

### Load Project Knowledge
```python
# In Claude:
result = lo_load("my_project")
# Returns README + recent sessions
```

### Continue from Previous
```python
# In Claude:
lo_cont("""
STATUS: Authentication complete
POSITION: Working on user profiles
NEXT: Add profile picture upload
TODO:
- Image validation
- Storage backend
- API endpoint
CONTEXT: User management system
""")
```

## 🐛 Troubleshooting

### "Module not found" Error
```bash
# Ensure you're in the LogSec directory
cd C:\LogSec
python test_core_v3.py
```

### Database Errors
```bash
# Reset database
rm C:\LogSec\database\logsec_phase2.db
python test_core_v3.py  # Will recreate
```

### MCP Not Working in Claude
1. Check config file syntax (valid JSON)
2. Use absolute paths in config
3. Restart Claude Desktop
4. Check Claude logs for errors

## 📚 Further Documentation

- [README.md](README.md) - Project overview
- [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) - Feature details
- [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md) - Database schema

## 🤝 Support

- GitHub Issues: [Create an issue](https://github.com/yourusername/MCP-Session-Knowledge-Base/issues)
- Documentation: Check the `/docs` folder
- Tests: Run `python test_core_v3.py` for diagnostics

---

Happy coding with LogSec! 🚀
