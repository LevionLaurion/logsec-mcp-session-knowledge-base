# LogSec Examples

This directory contains example files demonstrating LogSec usage and output formats.

## Files

- `api_documentation_example.md` - Example of API documentation structure
- `python_project_example.md` - Example Python project documentation
- `README_local.md` - Example of locally generated README

## Usage Examples

### Basic Session Management

```bash
# Start a new project session
lo_start myproject

# Save important information
lo_save myproject "Database schema: users table has id, name, email fields"

# Search for specific information
lo_load myproject "database schema"

# Create continuation for next session
lo_cont myproject
```

### Project Documentation

```bash
# Generate project documentation
lo_update myproject

# This provides instructions for creating a comprehensive README
# The actual README is created by following the instructions
```

### Advanced Usage

```bash
# Search across multiple sessions
lo_load myproject "API endpoints"

# Continue from previous session
lo_start myproject  # Automatically loads continuation if exists
```

## Output Format

LogSec uses structured output for clarity:

```
📚 Project Knowledge: projectname

📄 Project README loaded from: path/to/readme.md
--------------------------------------------------
[README content]
--------------------------------------------------
  • Total Sessions: X

🔍 Search Results for: "query"
📋 Found X relevant sessions:
  • session_id - timestamp
```