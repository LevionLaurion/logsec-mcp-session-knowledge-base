# Contributing to LogSec

We welcome contributions to LogSec. This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/logsec-mcp-session-knowledge-base.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `python -m unittest tests/test_core_v3.py`
6. Commit with clear messages: `git commit -m "feat: add new feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
cd LogSec
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Unix/macOS

# No external dependencies required - uses Python stdlib only
```

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all functions
- Keep functions focused and small
- Maximum line length: 100 characters

## Testing

All changes must include appropriate tests:

```bash
python -m unittest discover tests/
```

## Commit Messages

Follow conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/maintenance tasks

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Update CHANGELOG.md
4. Ensure code follows project style
5. Request review from maintainers

## Project Structure

```
LogSec/
├── src/
│   ├── logsec_core_v3.py    # Main MCP server
│   └── config/              # Configuration
├── data/
│   ├── projects/            # Project data
│   ├── database/            # SQLite storage
│   └── templates/           # Response templates
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## Questions?

Open an issue for discussion or clarification.