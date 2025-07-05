# 🧠 LogSec 3.0 - MCP Session Knowledge Management

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
![GitHub stars](https://img.shields.io/github/stars/LevionLaurion/logsec-mcp-session-knowledge-base?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/LevionLaurion/logsec-mcp-session-knowledge-base)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> Knowledge management system for AI session continuity, built as a Model Context Protocol (MCP) server.

## 🎯 **Why LogSec?**

LogSec helps Claude maintain context across sessions by providing intelligent project knowledge management, semantic search, and structured session continuation.

### **Key Features**
- **Project Context Management**: Organize knowledge by project
- **Semantic Search**: Find relevant sessions using natural language
- **Session Continuity**: Structured handoffs between sessions
- **Auto-Classification**: Automatic categorization into 8 knowledge types
- **Workspace Integration**: Analyzes Desktop Commander logs for context

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git
cd logsec-mcp-session-knowledge-base

# Install dependencies (one-time setup)
install_dependencies.bat

# Test the installation  
python tests/test_core_v3.py

# Configure Claude Desktop (see Installation Guide)
```

## ⚠️ **Important Privacy Notice**

**Desktop Commander Integration**: LogSec analyzes Desktop Commander logs to provide workspace context. Be aware that Desktop Commander logs all file operations to:
```
C:\Users\[Username]\.claude-server-commander-logs\
```

**Privacy Implications:**
- File paths and search queries are logged in plain text
- Logs persist indefinitely and are not encrypted
- Consider using generic project names for sensitive work
- Use the included cleanup utility: `python utilities/dc_log_cleanup.py`

See [SECURITY.md](SECURITY.md) for detailed privacy recommendations.

## ✨ **Core Features**

### **Two-Mode Knowledge Loading**
```bash
lo_load("project_name")              # Project overview + recent activity
lo_load("project_name", "API docs") # Project context + semantic search
```

### **Auto-Classification System** 
Automatically categorizes content into 8 knowledge types:
- `api_doc` - API documentation, endpoints, integration guides
- `implementation` - Code implementations, technical solutions  
- `architecture` - System design, technical decisions
- `schema` - Database schemas, data structures
- `milestone` - Project milestones, version releases
- `debug` - Bug fixes, troubleshooting sessions
- `continuation` - Session handoffs (STATUS:, NEXT: format)
- `documentation` - General documentation, user guides

### **Vector-Powered Semantic Search**
- 384-dimensional embeddings using Sentence Transformers
- Project-scoped search (no cross-contamination)
- Cosine similarity with intelligent ranking
- FAISS integration for efficient similarity search

### **Structured Session Continuation**
Perfect handoffs using standardized format:
```
STATUS: Current development status
POSITION: file.py:line - method()
NEXT: Next steps to take
TODO: Outstanding tasks
CONTEXT: Additional context
```

### **Workspace Context Integration**
- Desktop Commander log analysis
- Real-time file validation
- Command history tracking
- Project auto-detection

### **NLP-Powered Auto-Tagging**
- Technical term extraction (APIs, frameworks, languages)
- Domain concept recognition (authentication, testing, deployment)
- Project-specific tagging

## 📋 **API Reference**

### Core Commands

#### `lo_save(content, project_name, session_id?)`
Save content with auto-processing
```python
result = lo_save("""
# API Integration Complete
- Implemented REST endpoints  
- Added MCP server support
- Vector search operational
""", "my_project")

# Returns: {"knowledge_type": "milestone", "tags": ["api", "rest", "mcp"], "confidence": 0.89}
```

#### `lo_load(project_name, query?)`
Load project knowledge with two modes
```python
# Mode 1: Project overview
overview = lo_load("my_project")

# Mode 2: Semantic search
results = lo_load("my_project", "API integration")
```

#### `lo_start(project_name)`  
Seamless session continuation
```python
context = lo_start("my_project")
# Returns: Last session + workspace context + file analysis
```

#### `lo_cont(query, language?)`
Parse structured continuation context
```python
parsed = lo_cont("""
STATUS: Implementing user authentication
POSITION: auth.py:45 - login_handler()  
NEXT: Add password hashing
""")
```

## 🏗️ **Architecture**

```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py           # Main MCP server
│   ├── modules/                    # Feature modules
│   │   ├── extended_auto_tagger.py     # NLP tagging engine
│   │   ├── knowledge_type_classifier.py # 8-type classification
│   │   ├── vector_search.py            # Semantic search engine  
│   │   └── embedding_engine.py         # Sentence Transformers
│   └── core/                       # Core components
│       ├── continuation_parser.py      # Structured parsing
│       └── workspace_context.py        # Desktop Commander integration
├── data/
│   ├── database/
│   │   └── logsec_phase3.db        # SQLite database
│   └── sessions/                   # Session file storage
├── utilities/                      # Helper tools
│   └── dc_log_cleanup.py          # Privacy cleanup tool
└── docs/                          # Documentation
```

## 📦 **Installation**

See [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) for detailed setup instructions.

### **Claude Desktop Integration**
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

## 🧪 **Testing**

```bash
# Run test suite
python tests/test_core_v3.py
```

## 📚 **Documentation**

- 📖 [Installation Guide](docs/INSTALLATION_GUIDE.md) - Step-by-step setup
- 🏗️ [Implementation Details](docs/IMPLEMENTATION_PLAN.md) - Architecture overview
- 💾 [Database Architecture](docs/DATABASE_ARCHITECTURE.md) - Technical deep dive
- 🔧 [Developer Reference](docs/DEVELOPER_REFERENCE.md) - Complete API documentation  
- 📁 [Workspace Integration](docs/PHASE_3_WORKSPACE_CONTEXT.md) - Desktop Commander features
- 🔒 [Security Guide](SECURITY.md) - Privacy and security considerations

## 🎯 **Use Cases**

- **Development Projects**: Track progress across multiple codebases
- **Research Sessions**: Organize technical documentation and findings
- **Debugging Workflows**: Document problem-solving approaches
- **API Documentation**: Organize and search endpoint documentation
- **Team Handoffs**: Structured session continuations

## 🤝 **Contributing**

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Bug reports and fixes
- Performance optimizations  
- Feature requests
- Documentation improvements

## 📄 **License**

**Proprietary Software** - All rights reserved.

This repository is publicly available for evaluation and educational purposes only.

### ✅ **Permitted:**
- Viewing source code and architecture
- Educational study and learning
- Technical assessment and evaluation  
- Running tests in isolated environments

### ❌ **Requires Permission:**
- Commercial use or production deployment
- Redistribution, copying, or forking
- Modification or derivative works
- Integration into other commercial software

### 💼 **Commercial Licensing**
For business use, contact **mail@laurion.de** for licensing options.

**Full license terms**: See [LICENSE](LICENSE) file.

## 🙏 **Acknowledgments**

- Built for the AI development community
- Thanks to Anthropic for the MCP protocol
- Developed in collaboration with Claude
- Inspired by real-world AI workflow challenges

---

**LogSec** - Intelligent session knowledge management for AI developers
