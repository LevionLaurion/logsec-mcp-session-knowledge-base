# LogSec Directory Structure

## Overview

LogSec follows a clean, organized directory structure designed for maintainability and clarity.

## Structure

```
C:\LogSec\
├── src/                         # Source code
│   ├── logsec_core_v3.py       # Main MCP server implementation (563 lines)
│   └── config/                  # Configuration files
│       └── config.json          # Main configuration
│
├── data/                        # All application data
│   ├── projects/                # Project-specific data
│   │   └── {project_name}/      # Individual project directory
│   │       ├── readme.md        # Project documentation (Tier 2)
│   │       └── continuation.md  # Session continuation file
│   │
│   ├── database/                # Database files
│   │   └── logsec_phase3.db     # Main SQLite database (Tier 3)
│   │
│   └── templates/               # Template files
│       ├── command_templates.json    # Command response templates
│       └── update_universal.txt      # Universal update instructions
│
├── tests/                       # Test suite
│   └── test_core_v3.py         # Core functionality tests
│
├── docs/                        # Documentation
│   └── DIRECTORY_STRUCTURE.md  # This file
│
├── examples/                    # Usage examples
│   ├── README.md               # Example documentation
│   └── *.md                    # Various example files
│
├── .github/                     # GitHub specific files
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   └── pull_request_template.md
│
└── archive/                     # Archived/old files (not in git)
    ├── old_modules/            # Removed modules
    ├── old_scripts/            # Removed scripts
    └── *.py                    # Backup files
```

## Key Directories

### `/src`
Contains the core application code. The main file `logsec_core_v3.py` implements the complete MCP server.

### `/data`
All runtime data is stored here:
- **projects/**: Individual project folders with documentation and continuation files
- **database/**: SQLite database for session storage
- **templates/**: Customizable response templates

### `/tests`
Unit tests for core functionality.

### `/docs`
Project documentation files.

### `/archive`
Contains old code and files removed during refactoring. This directory is git-ignored.

## Data Flow

1. **Session Storage**: Conversations are stored in `data/database/logsec_phase3.db`
2. **Project Documentation**: Generated READMEs are saved to `data/projects/{name}/readme.md`
3. **Continuations**: Session handoffs stored in `data/projects/{name}/continuation.md`
4. **Templates**: Response patterns loaded from `data/templates/`

## Configuration

Main configuration is stored in `src/config/config.json`:

```json
{
  "db_path": "C:\\LogSec\\data\\database\\logsec_phase3.db",
  "projects_dir": "C:\\LogSec\\data\\projects",
  "templates_dir": "C:\\LogSec\\data\\templates"
}
```