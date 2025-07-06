# Changelog

All notable changes to LogSec MCP Session Knowledge Base will be documented in this file.

## [3.0.2] - 2025-01-06

### Changed
- **BREAKING**: Converted continuation system from database to file-based approach
- Continuation files now stored in `C:\LogSec\data\continuation\{project}_cont.md`
- One continuation file per project, overwritten on each `lo_cont` call
- Improved `lo_cont` to include Desktop Commander operations tracking
- Enhanced `lo_start` to load continuation files with full content display

### Fixed
- Fixed `_format_cont_output` to handle new "create_continuation" action
- Fixed `_format_start_output` to work with new data structure
- Removed "Unknown error" display issue in `lo_cont`

### Removed
- **BREAKING**: Removed `lo_cont_save` function - no longer needed
- Removed database-based continuation storage (`continuation_data` table)
- Removed complex session ID tracking for continuations

## [3.0.1] - 2025-01-06

### Changed
- Complete documentation overhaul - removed all marketing language and emojis
- LICENSE changed from proprietary to MIT with commercial restriction
- Removed fake performance metrics from documentation
- Added proper lo_cont_save API documentation
- Made all documentation factual and concise

### Fixed
- Corrected API parameter order in documentation
- Fixed inconsistencies between code and documentation

## [3.0.0] - 2025-01-06

### Added
- Two-mode lo_load system (summary mode vs. search mode)
- Vector search using SentenceTransformers
- lo_start command for session continuation
- Enhanced lo_cont with automatic session analysis
- lo_cont_save for storing continuation context
- Project isolation with database-level separation
- Auto-classification into 8 knowledge types
- Desktop Commander integration for workspace context
- Vector embeddings for semantic search

### Changed
- Simplified API to focus on core commands
- Improved session handoff format
- Enhanced error handling

### Removed
- Legacy features from version 2.x
- Redundant API endpoints
