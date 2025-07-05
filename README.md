# 🧠 LogSec 3.0 - MCP Session Knowledge Base

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> A minimalist knowledge management system for seamless AI session continuity, built as a Model Context Protocol (MCP) server.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git
cd logsec-mcp-session-knowledge-base

# Install dependencies
pip install -r requirements.txt

# Test the installation
python tests/test_core_v3.py

# Configure in Claude Desktop (see Installation Guide)
```

## ✨ Features

### 🏷️ **Auto-Tagging System**
Automatically extracts relevant tags from your content using NLP techniques.

### 🧩 **Knowledge Type Classification**
Classifies content into 8 types: `api_doc`, `schema`, `implementation`, `architecture`, `milestone`, `error_solution`, `research`, `continuation`

### 🔄 **Structured Continuation**
Use the standardized format for perfect session handoffs:
```
STATUS: Current status
POSITION: Where you are
NEXT: What comes next
TODO: Outstanding tasks
CONTEXT: Additional context
```

### 📚 **Tier 2 README System**
Persistent project documentation with version tracking.

## 📋 Available Commands

### `lo_load(project_name?)`
Load project knowledge including README and recent sessions.

### `lo_save(content, project_name?, session_id?)`
Save content with automatic tagging and classification.

### `lo_cont(query, language?)`
Parse continuation context for seamless handoffs.

## 🏗️ Architecture

```
src/
├── logsec_core_v3.py    # Main MCP server
├── modules/             # Feature modules
│   ├── extended_auto_tagger.py
│   └── knowledge_type_classifier.py
└── core/               # Core components
    └── continuation_parser.py
```

## 📦 Installation

See [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) for detailed setup instructions.

### Quick MCP Config

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "logsec": {
      "command": "python",
      "args": ["path/to/src/logsec_core_v3.py"]
    }
  }
}
```

## 🧪 Testing

```bash
# Run all tests
python tests/test_core_v3.py

# Expected output:
# [SUCCESS] All tests passed! LogSec Core v3 is ready!
```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION_GUIDE.md) - Detailed setup instructions
- [Phase 1 Complete](docs/PHASE_1_COMPLETE.md) - Development milestones
- [Database Architecture](docs/DATABASE_ARCHITECTURE.md) - Technical details
- [Original Concept](docs/LOGSEC_3.0_KONZEPT.md) - Initial design (German)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License & Usage

**Proprietary Software** - All rights reserved.

This repository is **publicly available for evaluation and educational purposes only**.

### ✅ Permitted:
- Viewing and code review
- Educational study and learning  
- Technical assessment and evaluation
- Running tests in isolated environments

### ❌ Prohibited without permission:
- Commercial use or production deployment
- Redistribution, copying, or forking
- Modification or derivative works
- Integration into other software

### 💼 Commercial Licensing Available
For business use, contact **mail@felixlang.de** for:
- Enterprise licensing agreements
- Custom implementations and support
- White-label and OEM licensing
- Competitive rates for legitimate use

**Full license terms**: See [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built with ❤️ for the AI development community
- Thanks to Anthropic for the MCP protocol
- Special thanks to Claude for being an amazing development partner

---

**LogSec** - Professional AI Session Knowledge Management
