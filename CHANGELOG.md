# Changelog

All notable changes to LogSec MCP Session Knowledge Base will be documented in this file.

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
