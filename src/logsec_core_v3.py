#!/usr/bin/env python3
"""
LogSec Core v3.0 Enhanced - Fixed MCP Implementation
Critical fixes for MCP protocol compliance
"""

import json
import sys
import os
import sqlite3
import re
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

# Add our modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import base components - wrapped in try/except for safety
try:
    from core.continuation_parser import ContinuationParser
    HAS_CONTINUATION_PARSER = True
except ImportError as e:
    print(f"Warning: Could not import ContinuationParser: {e}", file=sys.stderr)
    HAS_CONTINUATION_PARSER = False
    class ContinuationParser:
        def parse(self, query): return {"status": "fallback", "query": query}

try:
    from modules.extended_auto_tagger import ExtendedAutoTagger
    HAS_AUTO_TAGGER = True
except ImportError as e:
    print(f"Warning: Could not import ExtendedAutoTagger: {e}", file=sys.stderr)
    HAS_AUTO_TAGGER = False
    class ExtendedAutoTagger:
        def __init__(self, db): pass
        def generate_tags(self, content): return [("general", 0.5)]

try:
    from modules.knowledge_type_classifier import KnowledgeTypeClassifier
    HAS_CLASSIFIER = True
except ImportError as e:
    print(f"Warning: Could not import KnowledgeTypeClassifier: {e}", file=sys.stderr)
    HAS_CLASSIFIER = False
    class KnowledgeTypeClassifier:
        def classify_knowledge_type(self, content): return ("general", 0.5)

try:
    from modules.embedding_engine import EmbeddingEngine
    from modules.vector_search import VectorSearchEngine
    HAS_VECTOR_SEARCH = True
except ImportError as e:
    print(f"Warning: Could not import Vector Search modules: {e}", file=sys.stderr)
    HAS_VECTOR_SEARCH = False
    class EmbeddingEngine:
        def generate_embedding(self, text): return np.zeros(384)
    class VectorSearchEngine:
        def search_project(self, project, embedding): return []

class DesktopCommanderParser:
    """Extract Desktop Commander operations from session content"""
    
    DC_PATTERNS = {
        'read_file': r'<parameter name="path">(.*?)</parameter>',
        'write_file': r'<parameter name="path">(.*?)</parameter>',
        'list_directory': r'<parameter name="path">(.*?)</parameter>',
        'execute_command': r'<parameter name="command">(.*?)</parameter>',
        'edit_block': r'<parameter name="file_path">(.*?)</parameter>',
        'move_file': r'<parameter name="(?:source|destination)">(.*?)</parameter>',
        'create_directory': r'<parameter name="path">(.*?)</parameter>',
        'search_files': r'<parameter name="path">(.*?)</parameter>'
    }
    
    def __init__(self):
        self.operations = []
    
    def extract_operations(self, content: str) -> List[Dict]:
        """Extract all DC operations from content"""
        operations = []
        
        # Find all function calls
        function_pattern = r'<invoke name="desktop-commander:(\w+)">(.*?)</invoke>'
        matches = re.findall(function_pattern, content, re.DOTALL)
        
        for op_type, params in matches:
            if op_type in self.DC_PATTERNS:
                # Extract paths from parameters
                path_pattern = self.DC_PATTERNS.get(op_type, '')
                if path_pattern:
                    path_matches = re.findall(path_pattern, params)
                    for path in path_matches:
                        operations.append({
                            'type': op_type,
                            'path': path.strip(),
                            'timestamp': self._extract_timestamp(content, path)
                        })
        
        return operations
    
    def _extract_timestamp(self, content: str, near_text: str) -> Optional[str]:
        """Try to extract timestamp near the given text"""
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?)'
        
        pos = content.find(near_text)
        if pos > -1:
            start = max(0, pos - 500)
            end = min(len(content), pos + 500)
            context = content[start:end]
            
            matches = re.findall(timestamp_pattern, context)
            if matches:
                return matches[0]
        
        return None


class ProjectDetector:
    """Detect project from paths"""
    
    PROJECT_PATTERNS = {
        'logsec': [r'[Cc]:\\[Ll]ogion', r'/[Ll]ogion/', r'logsec_'],
        'lynnvest': [r'[Cc]:\\[Ll]ynnvest', r'/[Ll]ynnvest/', r'lynnvest_'],
        'laurion': [r'[Cc]:\\[Ll]aurion', r'/[Ll]aurion/', r'laurion_'],
        'nemesis': [r'[Cc]:\\nemesis', r'/nemesis/', r'nemesis_'],
        'rasputin': [r'[Cc]:\\rasputin', r'/rasputin/', r'rasputin_']
    }
    
    def detect_project(self, path: str) -> Optional[str]:
        """Detect project from path"""
        if not path:
            return None
            
        for project, patterns in self.PROJECT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    return project
        return None


class WorkspaceContextGenerator:
    """Generate current workspace context"""
    
    def __init__(self):
        self.project_detector = ProjectDetector()
        self._file_cache = {}
    
    @lru_cache(maxsize=1000)
    def file_exists_cached(self, path: str) -> bool:
        """Cache file existence checks"""
        try:
            return os.path.exists(path)
        except:
            return False
    
    def generate_context(self, operations: List[Dict], target_project: Optional[str] = None) -> Dict:
        """Generate current workspace context"""
        context = defaultdict(lambda: {
            'files': set(),
            'directories': set(),
            'commands': [],
            'deleted_files': set()
        })
        
        for op in operations:
            project = self.project_detector.detect_project(op['path'])
            if not project or (target_project and project != target_project):
                continue
            
            if op['type'] in ['read_file', 'write_file', 'edit_block']:
                path = op['path']
                if self.file_exists_cached(path):
                    context[project]['files'].add(path)
                else:
                    context[project]['deleted_files'].add(path)
            
            elif op['type'] == 'list_directory':
                context[project]['directories'].add(op['path'])
            
            elif op['type'] == 'execute_command':
                context[project]['commands'].append({
                    'command': op['path'],
                    'timestamp': op.get('timestamp')
                })
        
        return dict(context)


class EnhancedReadmeManager:
    """Simple README manager"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure README tables exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS readme_store (
                        project_name TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        version INTEGER DEFAULT 1,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create readme tables: {e}", file=sys.stderr)
    
    def get_readme(self, project_name: str) -> Optional[Dict]:
        """Get README for project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT content, version, updated_at FROM readme_store WHERE project_name = ?",
                    (project_name,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "content": row[0],
                        "version": row[1], 
                        "updated_at": row[2]
                    }
        except Exception as e:
            print(f"Warning: Could not get readme: {e}", file=sys.stderr)
        return None


class LogSecCore:
    """Enhanced LogSec Core v3 - Fixed for MCP"""
    
    def __init__(self):
        self.base_dir = Path("C:/LogSec")
        self.db_path = self.base_dir / "data" / "database" / "logsec_phase3.db"
        
        # Ensure directories exist
        self._ensure_structure()
        
        # Initialize components
        self.parser = ContinuationParser()
        self.readme_manager = EnhancedReadmeManager(self.db_path)
        self.tagger = ExtendedAutoTagger(str(self.db_path))
        self.classifier = KnowledgeTypeClassifier()
        self.dc_parser = DesktopCommanderParser()
        self.workspace_gen = WorkspaceContextGenerator()
        
        # Initialize Vector Search (if available)
        if HAS_VECTOR_SEARCH:
            self.embedding_engine = EmbeddingEngine()
            self.vector_search = VectorSearchEngine()
            print("Vector Search Engine initialized", file=sys.stderr)
        else:
            self.embedding_engine = None
            self.vector_search = None
            print("Vector Search not available - using fallback", file=sys.stderr)
    
    def _ensure_structure(self):
        """Ensure all directories exist"""
        dirs = [
            self.base_dir / "data" / "database",
            self.base_dir / "data" / "sessions",
            self.base_dir / "data" / "knowledge" / "projects",
            self.base_dir / "logs"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database if needed
        if not self.db_path.exists():
            self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS session_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        project_name TEXT,
                        timestamp TEXT,
                        tags TEXT,
                        knowledge_type TEXT,
                        confidence_score REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}", file=sys.stderr)
    
    def lo_load(self, project_name: str, query: str = None) -> Dict:
        """Load project knowledge - Two modes with Tier 2 always included for Claude"""
        try:
            if not project_name:
                return {"error": "project_name is required"}
            
            # Tier 2 wird IMMER geladen (Claude braucht Projekt-Kontext)
            tier_2_context = self._get_project_context(project_name)
            
            if query:
                # MODUS 2: Tier 2 + Tier 3 Vector Search
                search_results = self._search_knowledge_base(project_name, query)
                return {
                    "project": project_name,
                    "project_context": tier_2_context,  # IMMER dabei für Claude
                    "search_results": search_results,
                    "query": query,
                    "mode": "search"
                }
            else:
                # MODUS 1: Tier 2 + Tier 1 Summary  
                recent_activity = self._get_recent_sessions(project_name, limit=3)
                theme_overview = self._get_theme_stats(project_name)
                return {
                    "project": project_name,
                    "project_context": tier_2_context,  # IMMER dabei für Claude
                    "recent_activity": recent_activity,
                    "theme_overview": theme_overview,
                    "mode": "summary",
                    "display_instructions": "IMPORTANT: Please display the numbered documentation list (1-8) exactly as provided. Users can reference docs by number. Show the full structured output, especially the 📄 Documentation section with numbers."
                }
                
        except Exception as e:
            print(f"Error in lo_load: {e}", file=sys.stderr)
            return {"error": str(e)}
            return {"error": str(e)}
    
    def lo_save(self, project_name: str = None, content: str = None, session_id: str = None) -> Dict:
        """Save knowledge - with optional content or context-aware summary"""
        try:
            # NEUE VALIDIERUNG: Projekt ist immer erforderlich
            if not project_name:
                return {"error": "Project name required. Use: lo_save project_name [content]"}
            
            # Validate project name (alphanumeric + underscore/dash)
            if not re.match(r'^[a-zA-Z0-9_-]+$', project_name):
                return {"error": "Project name must be alphanumeric (plus _ or -)"}
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Wenn Content übergeben wurde, nutze ihn
            if content:
                # Spezifischer Content wurde angegeben
                # z.B. lo_save logsec "doku" → speichere Dokumentations-bezogene Inhalte
                content_header = f"# Specific Save: {content} - {timestamp}\n\n"
                
                # Hier könnte man basierend auf dem content-Parameter verschiedene Dinge tun
                if content.lower() in ["doku", "documentation", "docs"]:
                    content_header += "## Documentation Update\n\n"
                    content_header += "This save contains documentation-related content.\n\n"
                elif content.lower() in ["bug", "error", "fix"]:
                    content_header += "## Bug Fix / Error Solution\n\n"
                    content_header += "This save contains debugging or error resolution content.\n\n"
                elif content.lower() in ["feature", "implementation"]:
                    content_header += "## Feature Implementation\n\n"
                    content_header += "This save contains feature implementation details.\n\n"
                else:
                    content_header += f"## {content}\n\n"
                
                # Add context about what was saved
                content = content_header + f"Content type: {content}\nProject: {project_name}\n\n[Session content related to: {content}]"
                
            else:
                # Keine spezifische Angabe - Request Summary von Claude
                return {
                    "success": True,
                    "action": "request_summary",
                    "prompt": "Please create a summary of this session including:\n" +
                             "- Key implementations and fixes\n" +
                             "- Important technical decisions\n" +
                             "- Problems solved\n" +
                             "- Next steps",
                    "instructions": f"After creating the summary, save it with: lo_save {project_name} \"[your summary]\"",
                    "project_name": project_name,
                    "session_id": session_id or self._generate_session_id()
                }
            
            session_id = session_id or self._generate_session_id()
            
            # Auto-tag content
            tags = self.tagger.generate_tags(content)
            tag_list = [tag for tag, score in tags]
            
            # Classify knowledge type
            knowledge_type, confidence = self.classifier.classify_knowledge_type(content)
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO session_metadata 
                    (session_id, project_name, timestamp, tags, knowledge_type, confidence_score, content_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    project_name,
                    datetime.now().isoformat(),
                    json.dumps(tag_list),
                    knowledge_type,
                    confidence,
                    content  # Store content for vector search
                ))
                conn.commit()
            
            # Save content file
            session_dir = self.base_dir / "data" / "sessions"
            filename = f"{session_id}_{project_name}.md"
            filepath = session_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Generate and save vector embedding (if vector search available)
            if HAS_VECTOR_SEARCH and self.embedding_engine:
                try:
                    embedding = self.embedding_engine.generate_embedding(content)
                    # Convert to bytes for storage
                    embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
                    
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO session_vectors 
                            (session_id, project_name, embedding)
                            VALUES (?, ?, ?)
                        """, (session_id, project_name, embedding_bytes))
                        conn.commit()
                    
                    print(f"Vector embedding saved for session {session_id}", file=sys.stderr)
                except Exception as e:
                    print(f"Warning: Could not save vector embedding: {e}", file=sys.stderr)
            
            return {
                "session_id": session_id,
                "project": project_name,
                "tags": tag_list,
                "knowledge_type": knowledge_type,
                "confidence": confidence,
                "filepath": str(filepath)
            }
            
        except Exception as e:
            print(f"Error in lo_save: {e}", file=sys.stderr)
            return {"error": str(e)}
    
    def lo_cont(self, project_name: str, mode: str = "auto") -> Dict:
        """Generate continuation file for seamless session handoff
        
        Args:
            project_name: Target project name
            mode: "auto" (default) or focus mode ("debug", "implement", "refactor", "document")
        
        Returns:
            Instructions for Claude to create continuation file
        """
        try:
            if not project_name:
                return {"error": "project_name is required"}
            
            # Ensure continuation directory exists
            cont_dir = self.base_dir / "data" / "continuation"
            cont_dir.mkdir(parents=True, exist_ok=True)
            
            # Create prompt for Claude to analyze current session
            analysis_prompt = f"""Analyze the current session for project '{project_name}' and create a continuation file.

Focus on the CURRENT CONVERSATION and extract:

1. **STATUS**: What was being worked on? (Current task/feature)
2. **POSITION**: Where in the code/project? (file:line or location)
3. **PROBLEM**: What issue/blocker was encountered?
4. **TRIED**: What solutions were attempted?
5. **NEXT**: What should be done next?
6. **FILES**: Key files involved (with what was done)
7. **COMMANDS**: Desktop Commander operations executed
8. **CONTEXT**: Important details for continuation

IMPORTANT: Analyze ALL Desktop Commander operations in this session:
- Every desktop-commander:read_file → note the path
- Every desktop-commander:write_file → note the path and action
- Every desktop-commander:edit_block → note the file and what was changed
- Every desktop-commander:execute_command → note the command
- Every desktop-commander:create_directory → note the path
- Every desktop-commander:list_directory → note the path
- Every desktop-commander:search_code → note path and search term

{f"Mode: {mode} - " if mode != "auto" else ""}{"Focus on debugging" if mode == "debug" else "Focus on implementation" if mode == "implement" else "Focus on refactoring" if mode == "refactor" else "Focus on documentation" if mode == "document" else ""}

Create a clear, structured continuation document and save it to:
{cont_dir / f"{project_name}_cont.md"}

Format it like this:

```markdown
# {project_name.upper()} Continuation - {datetime.now().strftime("%Y-%m-%d %H:%M")}

## STATUS
[What was being worked on]

## POSITION
[Current file/location]

## PROBLEM
[Current blocker/issue]

## TRIED
- [Attempt 1]
- [Attempt 2]

## NEXT
- [Next step 1]
- [Next step 2]

## FILES
- path/to/file1.py - [what was done: read/written/edited]
- path/to/file2.py - [what was done: read/written/edited]

## COMMANDS
- `command executed` - [result/purpose]
- `another command` - [result/purpose]

## WORKSPACE
Desktop Commander operations from this session:
- Read: [list all files read with full paths]
- Written: [list all files written/edited with full paths]
- Created: [list all directories created]
- Searched: [list all search operations with paths]
- Executed: [list all shell commands]

## CONTEXT
[Any important context for continuation]
```"""

            return {
                "success": True,
                "action": "create_continuation",
                "prompt": analysis_prompt,
                "continuation_path": str(cont_dir / f"{project_name}_cont.md"),
                "project": project_name,
                "mode": mode,
                "instructions": f"Claude will create continuation file at: {cont_dir / f'{project_name}_cont.md'}"
            }
            
        except Exception as e:
            print(f"Error in lo_cont: {e}", file=sys.stderr)
            return {"error": str(e)}
    
    # REMOVED lo_cont_save - no longer needed with file-based approach
    
    def lo_start(self, project_name: str) -> Dict:
        """Load continuation from simple file for seamless session resumption"""
        try:
            if not project_name:
                return {"error": "project_name is required"}
            
            # Load Tier 2 context (always included)
            tier_2_context = self._get_project_context(project_name)
            
            # Check for continuation file
            cont_file = self.base_dir / "data" / "continuation" / f"{project_name}_cont.md"
            
            if cont_file.exists():
                # Load continuation file
                with open(cont_file, 'r', encoding='utf-8') as f:
                    continuation_content = f.read()
                
                # Parse with ContinuationParser if available
                parsed_data = {}
                if HAS_CONTINUATION_PARSER and self.parser:
                    try:
                        parsed_data = self.parser.parse(continuation_content)
                    except Exception as e:
                        print(f"Warning: Could not parse continuation: {e}", file=sys.stderr)
                
                return {
                    "project": project_name,
                    "project_context": tier_2_context,
                    "continuation": {
                        "content": continuation_content,
                        "parsed": parsed_data,
                        "file_path": str(cont_file),
                        "exists": True
                    },
                    "instructions": f"Continuation loaded from {cont_file}. Continue where the last session left off.",
                    "mode": "continuation"
                }
            else:
                # No continuation file - fallback to last session
                last_session = self._get_last_session(project_name)
                
                if not last_session:
                    return {
                        "project": project_name,
                        "project_context": tier_2_context,
                        "continuation": {"exists": False},
                        "instructions": f"No continuation file found at {cont_file}. Starting fresh with project context.",
                        "mode": "fresh_start"
                    }
                
                # Load last session as fallback
                session_content = self._load_session_content(last_session['session_id'])
                
                return {
                    "project": project_name,
                    "project_context": tier_2_context,
                    "last_session": {
                        "session_id": last_session['session_id'],
                        "timestamp": last_session['timestamp'],
                        "summary": session_content[:500] + "..." if len(session_content) > 500 else session_content
                    },
                    "continuation": {"exists": False},
                    "instructions": f"No continuation file. Use 'lo_cont {project_name}' to create one for next time.",
                    "mode": "last_session_fallback"
                }
                
        except Exception as e:
            print(f"Error in lo_start: {e}", file=sys.stderr)
            return {"error": str(e)}
    
    # Helper methods
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def _get_current_session_content(self) -> str:
        """Get current session content - placeholder for real implementation"""
        # In real implementation, this would access Claude's conversation history
        # For now, return empty string
        return ""
    
    def _apply_focus_mode(self, continuation_data: Dict, mode: str) -> Dict:
        """Apply mode-specific focus to continuation data"""
        if mode == "debug":
            # Emphasize errors and problems
            continuation_data['focus'] = "debugging"
        elif mode == "implement":
            # Focus on task and next steps
            continuation_data['focus'] = "implementation"
        elif mode == "refactor":
            # Prioritize files and structure
            continuation_data['focus'] = "refactoring"
        elif mode == "document":
            # Highlight decisions and context
            continuation_data['focus'] = "documentation"
        
        return continuation_data
    
    def _extract_continuation_context(self, project_name: str) -> Dict:
        """Extract continuation context from current session"""
        # Get recent sessions for the project
        recent_sessions = self._get_recent_sessions(project_name, limit=3)
        
        # Initialize context with current work
        context = {
            "task": f"Working on {project_name} enhancements",
            "result": "Implementation and testing in progress",
            "position": "Multiple files edited",
            "next": "Continue development and testing",
            "files": [],
            "commands": [],
            "context": ""
        }
        
        # Analyze recent sessions
        all_files = {}
        task_found = False
        
        for session in recent_sessions:
            session_content = self._load_session_content(session['session_id'])
            
            # Extract Desktop Commander operations
            dc_operations = self.dc_parser.extract_operations(session_content)
            
            for op in dc_operations:
                if op['type'] in ['read_file', 'write_file', 'edit_block']:
                    path = op['path']
                    if self._is_valid_path(path):
                        relevance = "edited" if op['type'] in ['write_file', 'edit_block'] else "viewed"
                        # Prioritize edited files
                        if path not in all_files or relevance == "edited":
                            all_files[path] = {"path": path, "relevance": relevance}
                
                elif op['type'] == 'execute_command':
                    # Extract commands
                    context['commands'].append({
                        "cmd": op['path'][:50],  # Truncate long commands
                        "status": "executed"
                    })
            
            # Extract task from content (only from most recent)
            if not task_found and session == recent_sessions[0]:
                # Look for headers or task descriptions
                task_patterns = [
                    r'# (.+?)(?:\n|$)',  # Markdown headers
                    r'## What was accomplished:\s*\n- (.+?)(?:\n|$)',
                    r'working on\s+(.+?)(?:\.|$)',
                    r'implementing\s+(.+?)(?:\.|$)',
                    r'Task:\s*(.+?)(?:\.|$)'
                ]
                
                for pattern in task_patterns:
                    match = re.search(pattern, session_content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        context['task'] = match.group(1).strip()
                        task_found = True
                        break
                
                # Extract result/status
                result_patterns = [
                    r'Result:\s*(.+?)(?:\.|$)',
                    r'✅\s*(.+?)(?:\.|$)',
                    r'Status:\s*(.+?)(?:\.|$)',
                    r'## Technical implementation:\s*\n- (.+?)(?:\n|$)'
                ]
                
                for pattern in result_patterns:
                    match = re.search(pattern, session_content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        context['result'] = match.group(1).strip()
                        break
                
                # Extract position if possible
                if all_files:
                    # Get the most recently edited file
                    edited_files = [f for f in all_files.values() if f['relevance'] == 'edited']
                    if edited_files:
                        context['position'] = edited_files[0]['path']
                
                # Set knowledge type as context
                if session.get('type'):
                    context['context'] = f"Session type: {session['type']}"
                    
                # Determine next steps based on content
                if "implementation complete" in session_content.lower():
                    context['next'] = "Test the implementation and verify functionality"
                elif "error" in session_content.lower() or "fehler" in session_content.lower():
                    context['next'] = "Debug and fix identified issues"
                elif "test" in session_content.lower():
                    context['next'] = "Run tests and validate implementation"
        
        # Sort files by relevance (edited first)
        sorted_files = sorted(all_files.values(), 
                            key=lambda x: (0 if x['relevance'] == 'edited' else 1, x['path']))
        context['files'] = sorted_files[:10]
        
        # Limit commands to last 5
        context['commands'] = context['commands'][-5:]
        
        return context
    
    def _save_continuation_to_db(self, project_name: str, continuation_data: Dict):
        """Save continuation data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create continuation table if not exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS continuation_data (
                        project_name TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        data TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Save continuation data
                conn.execute("""
                    INSERT OR REPLACE INTO continuation_data 
                    (project_name, timestamp, data)
                    VALUES (?, ?, ?)
                """, (
                    project_name,
                    datetime.now().isoformat(),
                    json.dumps(continuation_data)
                ))
                conn.commit()
        except Exception as e:
            print(f"Error saving continuation data: {e}", file=sys.stderr)
    
    def _load_continuation_from_db(self, project_name: str) -> Optional[Dict]:
        """Load continuation data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT data FROM continuation_data
                    WHERE project_name = ?
                """, (project_name,))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
        except Exception as e:
            print(f"Error loading continuation data: {e}", file=sys.stderr)
        
        return None
    
    def _is_valid_path(self, path: str) -> bool:
        """Check if path exists and is valid"""
        try:
            return Path(path).exists()
        except:
            return False
    
    def _get_recent_sessions(self, project_name: str = None, limit: int = 5) -> List[Dict]:
        """Get recent sessions"""
        sessions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT session_id, project_name, timestamp, knowledge_type, tags FROM session_metadata"
                params = []
                
                if project_name:
                    query += " WHERE project_name = ?"
                    params.append(project_name)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                
                for row in cursor:
                    sessions.append({
                        "session_id": row[0],
                        "project": row[1],
                        "timestamp": row[2],
                        "type": row[3],
                        "tags": json.loads(row[4]) if row[4] else []
                    })
        except Exception as e:
            print(f"Warning: Could not get sessions: {e}", file=sys.stderr)
        
        return sessions
    
    def _get_project_stats(self, project_name: str = None) -> Dict:
        """Get project statistics"""
        stats = {"total_sessions": 0, "knowledge_types": {}}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total sessions
                if project_name:
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM session_metadata WHERE project_name = ?",
                        (project_name,)
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) FROM session_metadata")
                
                stats["total_sessions"] = cursor.fetchone()[0]
        except Exception as e:
            print(f"Warning: Could not get stats: {e}", file=sys.stderr)
        
        return stats
    
    def _detect_project_from_parsed(self, parsed: Dict, operations: List[Dict]) -> Optional[str]:
        """Detect project from parsed data"""
        detector = ProjectDetector()
        
        # Check from operations first
        for op in operations:
            project = detector.detect_project(op['path'])
            if project:
                return project
        
        return None
    
    def _format_load_output(self, result: Dict) -> str:
        """Format lo_load output for display - NEW TWO-MODE FORMAT"""
        output = []
        
        # Check for display instructions
        if result.get("display_instructions"):
            output.append(f"[{result['display_instructions']}]\n")
        
        # Header with project name
        project_name = result.get("project", "Unknown")
        output.append(f"📚 Project Knowledge: {project_name}")
        
        # Project Context (Tier 2) - always present
        if "project_context" in result:
            context = result["project_context"]
            output.append(f"\n🎯 Project Context:")
            
            # NEU: Projekt-Grundinfos prominent anzeigen
            if context.get('project_root'):
                output.append(f"  📁 Root: {context['project_root']}")
            if context.get('repository_url'):
                output.append(f"  🔗 GitHub: {context['repository_url']}")
            
            output.append(f"  • Description: {context.get('description', 'No description')}")
            output.append(f"  • Phase: {context.get('current_phase', 'Unknown')}")
            
            if context.get('key_directories'):
                output.append(f"  📂 Directories: {', '.join(context['key_directories'])}")
            
            if context.get('documentation_files'):
                output.append(f"  📄 Documentation:")
                for idx, doc in enumerate(context['documentation_files'][:8], 1):  # Max 8 docs, start at 1
                    output.append(f"     {idx}. {doc}")
            
            if context.get('tech_stack'):
                output.append(f"  • Tech Stack: {', '.join(context['tech_stack'])}")
            
            output.append(f"  • Total Sessions: {context.get('total_sessions', 0)}")
            if context.get('last_activity'):
                output.append(f"  • Last Activity: {context['last_activity'][:16]}")
        
        # Mode-specific content
        mode = result.get("mode", "unknown")
        
        if mode == "summary":
            # MODUS 1: Summary with recent activity
            if "recent_activity" in result:
                recent = result["recent_activity"]
                output.append(f"\n📑 Recent Activity ({len(recent)} sessions):")
                for session in recent:
                    output.append(f"  • {session['session_id']} ({session.get('knowledge_type', 'unknown')}) - {session.get('timestamp', 'Unknown time')[:16]}")
            
            if "theme_overview" in result:
                themes = result["theme_overview"]
                if themes:
                    output.append(f"\n🏷️ Knowledge Themes:")
                    for theme, count in themes.items():
                        output.append(f"  • {theme}: {count} sessions")
                
                # Suggestions
                output.append(f"\n💡 Try searching:")
                output.append(f"  • lo_load {project_name} \"API documentation\"")
                output.append(f"  • lo_load {project_name} \"implementation\"")
                
        elif mode == "search":
            # MODUS 2: Search results
            query = result.get("query", "")
            output.append(f"\n🔍 Search Results for: \"{query}\"")
            
            if "search_results" in result:
                results = result["search_results"]
                output.append(f"\n📋 Found {len(results)} relevant sessions:")
                
                # Group by knowledge type
                grouped = {}
                for item in results:
                    ktype = item.get('knowledge_type', 'unknown')
                    if ktype not in grouped:
                        grouped[ktype] = []
                    grouped[ktype].append(item)
                
                for ktype, items in grouped.items():
                    output.append(f"\n🏷️ {ktype.title()} ({len(items)} sessions):")
                    for item in items:
                        similarity = item.get('similarity', 0)
                        output.append(f"  • {item['session_id']} - {item.get('timestamp', 'Unknown')[:16]} (similarity: {similarity:.2f})")
        
        return "\n".join(output)
    
    def _format_save_output(self, result: Dict) -> str:
        """Format lo_save output for display"""
        output = []
        
        # Check if this is a summary request
        if result.get("action") == "request_summary":
            output.append("📝 **Session Summary Request**")
            output.append("")
            output.append(result.get("prompt", "Please provide a session summary"))
            output.append("")
            output.append("---")
            output.append("")
            # Der nächste Output sollte die Zusammenfassung sein
            return "\n".join(output)
        
        # Normal save response
        output.append("✅ Knowledge saved successfully!")
        output.append(f"\n📁 Session ID: {result['session_id']}")
        output.append(f"📂 Project: {result.get('project', 'general')}")
        output.append(f"🏷️ Tags: {', '.join(result.get('tags', []))}")
        output.append(f"🧩 Type: {result.get('knowledge_type', 'unknown')} (confidence: {result.get('confidence', 0):.0%})")
        output.append(f"📍 Location: {result.get('filepath', 'N/A')}")
        
        return "\n".join(output)
    
    def _format_tree(self, structure: Dict, prefix: str = "", is_last: bool = True) -> str:
        """Format directory structure as tree"""
        if not structure:
            return ""
            
        lines = []
        
        # Current item
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + structure['name'] + ('/' if structure.get('type') == 'directory' else ''))
        
        # Children
        if 'children' in structure and structure['children']:
            extension = "    " if is_last else "│   "
            children = structure['children']
            
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                child_lines = self._format_tree(child, prefix + extension, is_last_child)
                lines.append(child_lines)
        
        return '\n'.join(lines)
    
    def _format_result(self, tool_name: str, result: Dict) -> str:
        """Format tool results for display"""
        if "error" in result:
            return f"❌ Error: {result['error']}"
            
        if tool_name == "lo_load":
            return self._format_load_output(result)
        elif tool_name == "lo_save":
            return self._format_save_output(result)
        elif tool_name == "lo_cont":
            return self._format_cont_output(result)
        elif tool_name == "lo_start":
            return self._format_start_output(result)
        else:
            # Fallback to JSON for unknown tools
            return json.dumps(result, indent=2)
    
    def _format_cont_output(self, result: Dict) -> str:
        """Format enhanced lo_cont output for display"""
        output = []
        
        if "error" in result:
            return f"❌ Error: {result['error']}"
        
        if result.get("action") == "create_continuation":
            # This is the new format
            output.append("🔍 Analyzing Current Session for Continuation...")
            output.append("")
            output.append(f"📂 Continuation will be saved to: {result.get('continuation_path', 'unknown')}")
            output.append("")
            output.append("Instructions:")
            output.append(result.get("instructions", ""))
            
        elif result.get("action") == "request_analysis":
            # Legacy format (kept for compatibility)
            output.append("🔍 Analyzing Current Session...")
            output.append("")
            output.append(result.get("prompt", ""))
            output.append("")
            output.append("📝 " + result.get("instructions", ""))
            
        elif result.get("success") and "continuation_saved" in result:
            # This is the saved result
            output.append("✅ Continuation Context Saved")
            output.append("")
            
            cont = result["continuation_saved"]
            output.append(f"📋 Project: {result['project']}")
            output.append(f"🎯 Task: {cont.get('task', 'N/A')}")
            output.append(f"📊 Last Result: {cont.get('result', 'N/A')}")
            output.append(f"📍 Position: {cont.get('position', 'N/A')}")
            output.append(f"➡️  Next: {cont.get('next', 'N/A')}")
            
            if cont.get("files"):
                output.append("\n📁 Active Files:")
                for file in cont["files"][:5]:
                    output.append(f"  • {file['path']} ({file['relevance']})")
            
            if cont.get("commands"):
                output.append("\n⚡ Recent Commands:")
                for cmd in cont["commands"][:3]:
                    status_icon = "✅" if cmd['status'] == "success" else "❌"
                    output.append(f"  {status_icon} {cmd['cmd']}")
            
            if cont.get("context"):
                output.append(f"\n💡 Context: {cont['context']}")
            
            output.append("")
            output.append(result.get("message", ""))
        else:
            output.append("❌ " + result.get("error", "Unknown error"))
        
        return "\n".join(output)

    def _format_start_output(self, result: Dict) -> str:
        """Format enhanced lo_start output for display"""
        output = []
        
        if "error" in result:
            return f"❌ Error: {result['error']}"
        
        project_name = result.get("project", "Unknown")
        output.append(f"🚀 {project_name.title()} Session Start")
        output.append("")
        
        # Show mode
        mode = result.get("mode", "unknown")
        
        if mode == "continuation":
            output.append("✨ Continuation file loaded!")
            output.append("")
            
            # Show continuation content
            cont = result.get("continuation", {})
            if cont.get("exists") and cont.get("content"):
                output.append("📋 Continuation Context:")
                output.append("-" * 50)
                # Show first 1000 chars of continuation
                content = cont["content"][:1000]
                if len(cont["content"]) > 1000:
                    content += "\n... (truncated)"
                output.append(content)
                output.append("-" * 50)
                output.append("")
                output.append(f"📂 Loaded from: {cont.get('file_path', 'unknown')}")
            
        elif mode == "last_session_fallback":
            output.append("📝 No continuation file found - showing last session")
            output.append("")
            
            last_session = result.get("last_session", {})
            if last_session:
                output.append(f"Session ID: {last_session.get('session_id', 'unknown')}")
                output.append(f"Timestamp: {last_session.get('timestamp', 'unknown')}")
                output.append("")
                output.append("Summary:")
                output.append(last_session.get('summary', 'No summary available'))
            
            output.append("")
            output.append(result.get("instructions", ""))
            
        elif mode == "fresh_start":
            output.append("🆕 Fresh start - no previous sessions found")
            output.append("")
            output.append(result.get("instructions", ""))
        
        # Always show project context if available
        context = result.get("project_context", {})
        if context:
            output.append("")
            output.append("📚 Project Context:")
            if context.get("description"):
                output.append(f"  • Description: {context['description']}")
            if context.get("current_phase"):
                output.append(f"  • Phase: {context['current_phase']}")
            if context.get("repository_url"):
                output.append(f"  • Repository: {context['repository_url']}")
        
        output.append("")
        output.append("🎯 Ready to continue!")
        
        return "\n".join(output)


    def handle_mcp_request(self, request: Dict) -> Optional[Dict]:
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            # Return proper MCP initialize response
            return {
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "logsec-enhanced",
                        "version": "3.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
            
        elif method == "notifications/initialized":
            # This is a notification, no response needed
            return None
            
        elif method == "tools/list":
            return {
                "result": {
                    "tools": [
                        {
                            "name": "lo_load",
                            "description": "Load project knowledge - two modes: summary or search (Tier 2 always included for Claude)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                                    "query": {"type": "string", "description": "Search query for Tier 3 knowledge base (optional - triggers search mode)"}
                                },
                                "required": ["project_name"]
                            }
                        },
                        {
                            "name": "lo_save",
                            "description": "Save content or current session to project",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                                    "content": {"type": "string", "description": "Content to save (optional - auto-generates if not provided)"},
                                    "session_id": {"type": "string", "description": "Session ID (optional)"}
                                },
                                "required": ["project_name"]
                            }
                        },
                        {
                            "name": "lo_cont",
                            "description": "Auto-extract continuation context from current session",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                                    "mode": {"type": "string", "enum": ["auto", "debug", "implement", "refactor", "document"], "description": "Focus mode (default: auto)"}
                                },
                                "required": ["project_name"]
                            }
                        },
                        {
                            "name": "lo_start",
                            "description": "Quick start - seamless session continuation with workspace context",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Project name (REQUIRED)"}
                                },
                                "required": ["project_name"]
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                if tool_name == "lo_load":
                    result = self.lo_load(**arguments)
                elif tool_name == "lo_save":
                    result = self.lo_save(**arguments)
                elif tool_name == "lo_cont":
                    result = self.lo_cont(**arguments)
                elif tool_name == "lo_start":
                    result = self.lo_start(**arguments)
                else:
                    return {
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                # Return structured data, not formatted strings
                # But include formatted output for display
                return {
                    "result": {
                        "toolResult": result,
                        "content": [
                            {
                                "type": "text",
                                "text": self._format_result(tool_name, result)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution error: {str(e)}"
                    }
                }
            
        else:
            # Check if it's a notification (no response needed)
            if method and method.startswith("notifications/"):
                return None
            
            # For unknown methods, return error
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    # NEW METHODS FOR TWO-MODE SYSTEM
    def _get_project_context(self, project_name: str) -> Dict:
        """Get essential project context (Tier 2) - always included for Claude"""
        try:
            # Get or generate README
            readme = self._get_or_generate_readme(project_name)
            
            # Get project statistics
            stats = self._get_project_stats(project_name)
            
            # Get main directories (if available) - from README or detect
            directories = readme.get('key_directories', []) or self._get_project_directories(project_name)
            
            return {
                "name": project_name,
                "description": readme.get('description', f"{project_name} project"),
                "current_phase": readme.get('phase', 'In development'),
                "project_root": readme.get('project_root', ''),  
                "repository_url": readme.get('repository_url', ''),  
                "tech_stack": readme.get('tech_stack', []),
                "key_components": readme.get('components', []),
                "key_directories": directories[:5],  
                "documentation_files": readme.get('documentation_files', []),  # NEU
                "total_sessions": stats.get('total_sessions', 0),
                "last_activity": self._get_last_activity(project_name)
            }
        except Exception as e:
            print(f"Warning: Could not get project context: {e}", file=sys.stderr)
            return {
                "name": project_name,
                "description": f"{project_name} project",
                "current_phase": "Unknown",
                "tech_stack": [],
                "key_components": [],
                "total_sessions": 0,
                "last_activity": None,
                "main_directories": []
            }

    def _get_or_generate_readme(self, project_name: str) -> Dict:
        """Get README from DB or generate basic one"""
        try:
            # Try to get existing README
            readme_data = self.readme_manager.get_readme(project_name)
            if readme_data and readme_data.get('content'):
                # Parse README content for structured data
                content = readme_data.get('content', '')
                parsed = self._parse_readme_content(content)
                return parsed
        except:
            pass
        
        # Generate basic README from sessions
        return self._generate_basic_readme(project_name)
    
    def _parse_readme_content(self, content: str) -> Dict:
        """Parse README content to extract structured data"""
        parsed = {
            'description': '',
            'phase': 'Active Development', 
            'project_root': '',
            'repository_url': '',
            'tech_stack': [],
            'components': [],
            'key_directories': [],
            'documentation_files': []  # NEU
        }
        
        # Extract from README format
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Project Root
            if 'Project Root' in line and ':' in line:
                parsed['project_root'] = line.split(':', 1)[1].strip().strip('*`')
            
            # GitHub URL
            elif 'GitHub' in line and 'http' in line:
                if ':' in line:
                    url = line.split(':', 1)[1].strip().strip('*`')
                    if 'http' in url:
                        parsed['repository_url'] = 'https:' + url.split('https:')[1] if 'https:' in url else url
            
            # Status/Phase
            elif 'Status' in line and ':' in line:
                parsed['phase'] = line.split(':', 1)[1].strip().strip('*`')
            
            # Description (usually after ## Description)
            elif line.strip() == '## Description' and i + 1 < len(lines):
                parsed['description'] = lines[i + 1].strip()
            
            # Tech Stack
            elif line.strip() == '## Tech Stack' and i + 1 < len(lines):
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('-'):
                    tech = lines[j].strip().lstrip('- ').strip()
                    if tech:
                        parsed['tech_stack'].append(tech)
                    j += 1
        
        # Extract directories from structure section
        in_structure = False
        for line in lines:
            if '## Project Structure' in line:
                in_structure = True
                continue
            elif in_structure and line.strip().startswith('##'):
                break
            elif in_structure and '`' in line and '/' in line:
                # Extract directory name
                import re
                match = re.search(r'`([^`]+)/`', line)
                if match:
                    parsed['key_directories'].append(match.group(1))
        
        # NEU: Extract documentation files
        in_docs = False
        for line in lines:
            if '## Documentation Files' in line:
                in_docs = True
                continue
            elif in_docs and line.strip().startswith('##'):
                break  
            elif in_docs and line.strip().startswith('-'):
                # Extract .md files
                import re
                # Match patterns like `README.md` or `docs/FILE.md`
                matches = re.findall(r'`([^`]+\.md)`', line)
                for match in matches:
                    parsed['documentation_files'].append(match)
        
        return parsed

    def _generate_basic_readme(self, project_name: str) -> Dict:
        """Generate basic README from existing sessions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get knowledge types
                cursor = conn.execute("""
                    SELECT knowledge_type, COUNT(*) as count
                    FROM session_metadata 
                    WHERE project_name = ?
                    GROUP BY knowledge_type
                    ORDER BY count DESC
                """, (project_name,))
                
                knowledge_types = dict(cursor.fetchall())
                
                # Generate description based on content
                description = f"{project_name} project"
                if 'api_doc' in knowledge_types:
                    description += " with API documentation"
                if 'implementation' in knowledge_types:
                    description += " and implementation details"
                
                return {
                    'description': description,
                    'phase': 'Active development',
                    'tech_stack': self._detect_tech_stack(project_name),
                    'components': list(knowledge_types.keys())
                }
        except Exception as e:
            print(f"Warning: Could not generate README: {e}", file=sys.stderr)
            return {
                'description': f"{project_name} project",
                'phase': 'Unknown',
                'tech_stack': [],
                'components': []
            }

    def _detect_tech_stack(self, project_name: str) -> List[str]:
        """Detect tech stack from file extensions and content"""
        tech_stack = set()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT tags FROM session_metadata 
                    WHERE project_name = ? AND tags IS NOT NULL
                """, (project_name,))
                
                for row in cursor:
                    try:
                        tags = json.loads(row[0])
                        for tag in tags:
                            if isinstance(tag, (list, tuple)) and len(tag) >= 1:
                                tag_name = tag[0].lower()
                                if tag_name in ['python', 'javascript', 'html', 'css', 'sql', 'json', 'yaml']:
                                    tech_stack.add(tag_name.title())
                    except:
                        continue
        except:
            pass
        
        return list(tech_stack)

    def _get_project_directories(self, project_name: str) -> List[str]:
        """Get main project directories from session data"""
        directories = set()
        try:
            # Get directories from recent sessions
            sessions = self._get_recent_sessions(project_name, limit=10)
            for session in sessions:
                # Try to extract directories from session files
                session_file = self.base_dir / "data" / "sessions" / f"{session['session_id']}_{project_name}.md"
                if session_file.exists():
                    with open(session_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract directory patterns
                        dir_patterns = re.findall(r'[C-Z]:\\[^"\s]+|\/[^"\s]+', content)
                        for path in dir_patterns[:5]:  # Limit to avoid too many
                            if os.path.sep in path:
                                directories.add(os.path.dirname(path))
        except:
            pass
        
        return list(directories)

    def _get_last_activity(self, project_name: str) -> Optional[str]:
        """Get timestamp of last activity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp FROM session_metadata 
                    WHERE project_name = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (project_name,))
                
                result = cursor.fetchone()
                return result[0] if result else None
        except:
            return None

    def _get_theme_stats(self, project_name: str) -> Dict:
        """Get theme statistics for project overview"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT knowledge_type, COUNT(*) as count
                    FROM session_metadata 
                    WHERE project_name = ?
                    GROUP BY knowledge_type
                    ORDER BY count DESC
                """, (project_name,))
                
                return dict(cursor.fetchall())
        except Exception as e:
            print(f"Warning: Could not get theme stats: {e}", file=sys.stderr)
            return {}

    def _search_knowledge_base(self, project_name: str, query: str) -> List[Dict]:
        """Search Tier 3 - Real Vector search within project boundaries"""
        results = []
        
        try:
            if HAS_VECTOR_SEARCH and self.embedding_engine and self.vector_search:
                # REAL VECTOR SEARCH
                # 1. Generate query embedding
                query_embedding = self.embedding_engine.generate_embedding(query)
                
                # 2. Use stored embeddings for efficient search
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT sm.session_id, sm.knowledge_type, sm.timestamp, sm.tags, sv.embedding
                        FROM session_metadata sm
                        JOIN session_vectors sv ON sm.session_id = sv.session_id
                        WHERE sm.project_name = ?
                        ORDER BY sm.timestamp DESC
                        LIMIT 20
                    """, (project_name,))
                    
                    for row in cursor:
                        session_id, knowledge_type, timestamp, tags, embedding_bytes = row
                        
                        # Convert stored embedding back to numpy array
                        if embedding_bytes:
                            try:
                                session_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                                
                                # Calculate cosine similarity
                                similarity = self._cosine_similarity(query_embedding, session_embedding)
                                
                                # Only include results above threshold
                                if similarity > 0.1:  # Lowered threshold for debugging
                                    results.append({
                                        "session_id": session_id,
                                        "knowledge_type": knowledge_type,
                                        "timestamp": timestamp,
                                        "tags": json.loads(tags) if tags else [],
                                        "similarity": float(similarity)
                                    })
                            except Exception as e:
                                print(f"Warning: Could not process embedding for {session_id}: {e}", file=sys.stderr)
                
                # Sort by similarity (highest first)
                results.sort(key=lambda x: x['similarity'], reverse=True)
                results = results[:10]  # Top 10 results
                
            else:
                # FALLBACK: Simple text search (if vector search not available)
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT session_id, knowledge_type, timestamp, tags
                        FROM session_metadata 
                        WHERE project_name = ?
                        ORDER BY timestamp DESC
                        LIMIT 10
                    """, (project_name,))
                    
                    for row in cursor:
                        results.append({
                            "session_id": row[0],
                            "knowledge_type": row[1],
                            "timestamp": row[2],
                            "tags": json.loads(row[3]) if row[3] else [],
                            "similarity": 0.75  # Placeholder
                        })
        
        except Exception as e:
            print(f"Warning: Could not search knowledge base: {e}", file=sys.stderr)
        
        return results

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Ensure vectors are numpy arrays
            a = np.array(a)
            b = np.array(b)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            return dot_product / (norm_a * norm_b)
        except Exception:
            return 0.0

    def _get_last_session(self, project_name: str) -> Optional[Dict]:
        """Get the most recent session for a project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, timestamp, knowledge_type, tags
                    FROM session_metadata 
                    WHERE project_name = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (project_name,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "session_id": result[0],
                        "timestamp": result[1],
                        "knowledge_type": result[2],
                        "tags": json.loads(result[3]) if result[3] else []
                    }
        except Exception as e:
            print(f"Warning: Could not get last session: {e}", file=sys.stderr)
        return None

    def _load_session_content(self, session_id: str) -> str:
        """Load session content from file"""
        try:
            # Look for session file
            session_files = list(self.base_dir.glob(f"data/sessions/{session_id}_*.md"))
            if session_files:
                with open(session_files[0], 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Warning: Could not load session content: {e}", file=sys.stderr)
        return ""

    def _generate_workspace_context(self, dc_operations: List[Dict], project_name: str) -> Dict:
        """Generate workspace context from Desktop Commander operations"""
        workspace = {
            "active_files": [],
            "working_directories": [],
            "last_commands": [],
            "recent_edits": []
        }
        
        try:
            # Extract unique paths and commands from operations
            files = set()
            directories = set()
            commands = []
            edits = []
            
            for op in dc_operations:
                op_type = op.get('type', '')
                path = op.get('path', '')
                
                if op_type in ['read_file', 'write_file'] and path:
                    files.add(path)
                    if os.path.dirname(path):
                        directories.add(os.path.dirname(path))
                elif op_type == 'edit_block' and path:
                    edits.append(path)
                    files.add(path)
                elif op_type == 'execute_command' and path:
                    commands.append(path)
                elif op_type == 'list_directory' and path:
                    directories.add(path)
            
            workspace = {
                "active_files": list(files)[-8:],  # Last 8 files
                "working_directories": list(directories)[-5:],  # Last 5 dirs
                "last_commands": commands[-5:],  # Last 5 commands
                "recent_edits": edits[-8:]  # Last 8 edits
            }
            
        except Exception as e:
            print(f"Warning: Could not generate workspace context: {e}", file=sys.stderr)
        
        return workspace


def main():
    """MCP Server main loop - FIXED with proper event loop"""
    
    # Initialize core
    try:
        core = LogSecCore()
        print("LogSec Core Enhanced initialized", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing LogSec Core: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    # Setup signal handlers for graceful shutdown (Windows compatible)
    try:
        import signal
        def signal_handler(signum, frame):
            print("\nShutting down gracefully...", file=sys.stderr)
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
    except Exception as e:
        print(f"Warning: Could not setup signal handlers: {e}", file=sys.stderr)
    
    print("MCP Server ready, waiting for messages...", file=sys.stderr)
    
    # CRITICAL FIX: Continuous input loop
    while True:
        try:
            # Read line from stdin
            line = sys.stdin.readline()
            
            # Check for EOF (empty string) - but don't exit immediately
            if not line:
                print("Warning: Empty line received, continuing...", file=sys.stderr)
                # On Windows, sometimes we get empty lines but the connection is still alive
                import time
                time.sleep(0.1)  # Small delay to avoid busy loop
                continue
            
            # Skip empty lines
            line = line.strip()
            if not line:
                continue
            
            # Parse JSON request
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} for line: {line}", file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                continue
            
            # Log request
            print(f"Received: {request.get('method', 'unknown')}", file=sys.stderr)
            
            # Handle request
            response = core.handle_mcp_request(request)
            
            # Send response if not a notification
            if response is not None:
                response["jsonrpc"] = "2.0"
                if "id" in request:
                    response["id"] = request["id"]
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Special handling for notifications
            if request.get("method", "").startswith("notifications/"):
                print(f"Notification received: {request.get('method')}", file=sys.stderr)
        
        except KeyboardInterrupt:
            print("\nKeyboard interrupt, shutting down...", file=sys.stderr)
            break
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            
            # Send error response if we have a request ID
            if 'request' in locals() and 'id' in request:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    print("Server shutdown complete", file=sys.stderr)


if __name__ == "__main__":
    main()
