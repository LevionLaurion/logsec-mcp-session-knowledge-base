# Contributing to LogSec

Thank you for your interest in contributing to LogSec! This document provides guidelines for contributing to the LogSec Knowledge Management System.

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/LevionLaurion/logsec-mcp-session-knowledge-base.git
   cd logsec-mcp-session-knowledge-base
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   python tests/test_core_v3.py
   ```

### MCP Development Setup

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "logsec": {
      "command": "python",
      "args": ["C:\\path\\to\\LogSec\\src\\logsec_core_v3.py"],
      "cwd": "C:\\path\\to\\LogSec",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\LogSec",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## 📋 Code Style Guidelines

### Python Code Style
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to all functions and classes
- Include type hints where appropriate

### Database Changes
- Always create migration scripts for schema changes
- Test migrations on sample data
- Document breaking changes in CHANGELOG.md

### LogSec-Specific Conventions
- Use `lo_` prefix for all MCP tool functions
- Maintain project isolation in all operations
- Include proper error handling and logging

## 🔄 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Update documentation as needed
   - Follow the coding style guidelines

3. **Test your changes**
   ```bash
   python tests/test_core_v3.py
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🧪 Testing

### Core Functionality Tests
- Test all `lo_*` commands (save, load, cont, start)
- Verify project separation works correctly
- Check MCP integration functionality

### Database Tests
- Verify schema migrations work
- Test data integrity across operations
- Check performance with large datasets

## 📚 Documentation

- Update README.md for user-facing changes
- Add technical details to relevant docs/ files
- Include examples for new features
- Update CHANGELOG.md with your changes

## 🐛 Bug Reports

When reporting bugs, please include:
- Steps to reproduce the issue
- Expected vs actual behavior
- LogSec version and environment details
- Relevant log files or error messages

## 💡 Feature Requests

For new features:
- Check existing issues to avoid duplicates
- Provide clear use cases and requirements
- Consider backward compatibility
- Discuss implementation approach

## 📄 License

By contributing to LogSec, you agree that your contributions will be licensed under the same proprietary license as the project.

## 🤝 Code of Conduct

- Be respectful and constructive
- Focus on the technical merits
- Help maintain a welcoming environment
- Follow the project's coding standards

---

**Questions?** Feel free to open an issue or reach out to the maintainers!
