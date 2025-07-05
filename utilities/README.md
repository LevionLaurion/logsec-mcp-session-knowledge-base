# LogSec Utilities

This directory contains helpful utilities for LogSec users.

## Available Tools

### 1. Desktop Commander Log Cleanup
`dc_log_cleanup.py` - Manage privacy by cleaning Desktop Commander logs

**Features:**
- Show log statistics (file count, size, age)
- Clean logs older than X days
- Archive logs before deletion
- Dry run mode for safety

**Usage:**
```bash
# Show statistics
python utilities/dc_log_cleanup.py --stats

# Dry run - see what would be deleted (last 7 days kept)
python utilities/dc_log_cleanup.py --clean

# Actually clean logs older than 7 days
python utilities/dc_log_cleanup.py --clean --execute

# Keep last 30 days only
python utilities/dc_log_cleanup.py --clean --days 30 --execute

# Archive all logs first
python utilities/dc_log_cleanup.py --archive
```

**Privacy Note:** Desktop Commander logs all file operations. Regular cleanup is recommended for privacy.

## Future Utilities

Planned utilities:
- Session export/import tool
- Knowledge base backup utility
- Project migration assistant
- Performance analysis tool
