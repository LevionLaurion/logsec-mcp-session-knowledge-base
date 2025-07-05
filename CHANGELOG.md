# Changelog

All notable changes to LogSec MCP Session Knowledge Base will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [3.0.0] - 2025-07-05

### 🎉 Major Release - Enhanced MCP Integration

#### Added
- **Two-Mode lo_load System**: Summary mode vs. Vector Search mode
- **Real Vector Search**: SentenceTransformers + FAISS integration with semantic similarity
- **lo_start Command**: Seamless session continuation with workspace context
- **Enhanced lo_cont**: Improved continuation parsing with STATUS/POSITION/NEXT
- **Project Isolation**: Strict project-based data separation
- **Tier 2 Context**: Project context always included for Claude
- **Auto-Classification**: Intelligent knowledge type detection
- **Desktop Commander Integration**: Workspace context extraction
- **Vector Embeddings**: 384-dimensional embeddings with cosine similarity
- **Performance Optimization**: Stored embeddings + database indices

#### Enhanced
- **MCP Protocol**: Full compliance with Model Context Protocol
- **Database Schema**: Extended with content_text and session_vectors tables
- **Error Handling**: Robust fallbacks and graceful degradation
- **Code Quality**: Removed test blocks, cleaned structure
- **Documentation**: Complete rewrite for 3.0 features

#### Technical Details
- **Vector Search Engine**: all-MiniLM-L6-v2 model (384 dimensions)
- **Similarity Threshold**: Configurable (default 0.1)
- **Project Required**: All commands now require project_name parameter
- **Database**: Enhanced session_metadata + session_vectors tables
- **Real-time Embeddings**: Generated and stored during lo_save

#### Breaking Changes
- `project_name` parameter is now required for lo_load and lo_save
- Removed manual tier system (3.1, 3.2, 3.3) in favor of intelligent search
- Old knowledge structure moved to archive

## [2.0.0] - 2025-07-04

### Initial MCP Implementation
- Basic lo_load, lo_save, lo_cont commands
- SQLite database integration
- Auto-tagging system
- Knowledge type classification
- README management

## [1.0.0] - Previous Versions
- Legacy LogSec implementations
- Foundation work (archived)
