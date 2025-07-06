#!/usr/bin/env python3
"""
LogSec Core v3 Clean - Direct implementation without external dependencies
All functionality in one clean file
"""
import os
import sys
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import numpy as np

# Simple vector search implementation
class SimpleVectorSearch:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def search(self, project_name: str, query: str, limit: int = 10) -> List[Dict]:
        """Simple keyword search as fallback"""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT session_id, content_text, knowledge_type, timestamp
                    FROM session_metadata 
                    WHERE project_name = ? AND content_text LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (project_name, f"%{query}%", limit))
                
                for row in cursor.fetchall():
                    results.append({
                        'session_id': row[0],
                        'content': row[1][:200] + "..." if len(row[1]) > 200 else row[1],
                        'knowledge_type': row[2],
                        'timestamp': row[3]
                    })
        except Exception as e:
            print(f"Search error: {e}", file=sys.stderr)
        return results
    
    def update_index(self, project_name: str):
        """Placeholder for index update"""
        pass


class LogSecCore:
    """Clean implementation - All in one file!"""
    
    def __init__(self):
        self.config = self._load_config()
        self.templates = self._load_templates()
        self.db_path = self.config['db_path']
        
        # Skip DB init - we use existing phase3.db
        # self._init_db()
        
        # Simple search engine
        self.search = SimpleVectorSearch(self.db_path)
        
        # Paths - now organized!
        self.projects_dir = Path(self.config['projects_dir'])
        self.templates_dir = Path(self.config['templates_dir'])
    
    def _init_db(self):
        """Initialize database with proper schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Main session table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS session_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        project_name TEXT NOT NULL,
                        knowledge_type TEXT,
                        content TEXT,
                        tags TEXT,
                        embeddings TEXT,
                        location TEXT,
                        participants TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Indices
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_project_name 
                    ON session_metadata(project_name)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON session_metadata(timestamp)
                """)
                
                conn.commit()
        except Exception as e:
            print(f"DB init error: {e}", file=sys.stderr)    
    def _load_config(self) -> Dict:
        """Load config from JSON"""
        config_path = "C:\\LogSec\\src\\config\\config.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            # Default config
            return {
                "db_path": "C:\\LogSec\\data\\database\\logsec_phase3.db",
                "projects_dir": "C:\\LogSec\\data\\projects",
                "templates_dir": "C:\\LogSec\\data\\templates"
            }
    
    def _load_templates(self) -> Dict:
        """Load templates"""
        template_path = os.path.join(
            self.config.get('templates_dir', 'C:\\LogSec\\data\\templates'),
            'command_templates.json'
        )
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except:
            return {"commands": {}, "formatting": {"divider": "-" * 50}}
    
    def _normalize_project_name(self, name: str) -> str:
        """Simple lowercase normalization"""
        return name.lower() if name else ""
    
    # === DATABASE OPERATIONS ===
    
    def save_session(self, project_name: str, content: str = None, 
                    session_id: str = None, knowledge_type: str = "manual",
                    metadata: Dict = None) -> Dict:
        """Save session to database"""
        try:
            if not session_id:
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Auto-generate content if needed
            if not content:
                content = "Auto-generated session content"
            
            # Simple tag extraction
            words = re.findall(r'\b\w+\b', content.lower())
            tags = [w for w in words if len(w) > 4][:5]
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO session_metadata 
                    (session_id, project_name, knowledge_type, content_text, tags, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    project_name,
                    knowledge_type,
                    content,
                    json.dumps(tags),
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            return {
                "success": True,
                "session_id": session_id,
                "project_name": project_name,
                "tags": tags,
                "knowledge_type": knowledge_type
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_project_stats(self, project_name: str) -> Dict:
        """Get project statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
                    FROM session_metadata
                    WHERE project_name = ?
                """, (project_name,))
                
                count, first, last = cursor.fetchone()
                
                return {
                    "total_sessions": count or 0,
                    "first_activity": first,
                    "last_activity": last
                }
        except Exception as e:
            print(f"Stats error: {e}", file=sys.stderr)
            return {"total_sessions": 0}    
    # === CORE COMMANDS ===
    
    def lo_save(self, project_name: str, content: str = None, session_id: str = None) -> Dict:
        """Save session to Tier 3"""
        if not project_name:
            return {"error": "project_name is required"}
        
        project_name = self._normalize_project_name(project_name)
        
        result = self.save_session(
            project_name=project_name,
            content=content,
            session_id=session_id,
            knowledge_type="manual",
            metadata={}
        )
        
        if result.get('success'):
            self.search.update_index(project_name)
            
            # Use template for response
            template = self.templates.get('commands', {}).get('lo_save', {}).get('success_template', [
                "✅ Knowledge saved successfully!",
                "",
                "📁 Session ID: {session_id}",
                "📂 Project: {project_name}"
            ])
            
            response_lines = []
            for line in template:
                response_lines.append(line.format(
                    session_id=result.get('session_id', 'unknown'),
                    project_name=project_name,
                    tags=', '.join(result.get('tags', [])),
                    knowledge_type=result.get('knowledge_type', 'manual'),
                    location='N/A'
                ))
            
            return {"response": "\n".join(response_lines)}
        
        return result
    
    def lo_load(self, project_name: str, query: str = None) -> Dict:
        """Load from Tier 2 + optional Tier 3 search"""
        if not project_name:
            return {"error": "project_name is required"}
        
        project_name = self._normalize_project_name(project_name)
        response_lines = [f"📚 Project Knowledge: {project_name}", ""]
        
        # Check Tier 2 (README)
        project_dir = self.projects_dir / project_name
        readme_path = project_dir / "readme.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            divider = self.templates.get('formatting', {}).get('divider', '-' * 50)
            response_lines.extend([
                f"📄 Project README loaded from: {readme_path}",
                divider,
                readme_content,
                divider
            ])
        
        # Add stats
        stats = self.get_project_stats(project_name)
        response_lines.extend([
            f"  • Total Sessions: {stats.get('total_sessions', 0)}",
            ""
        ])
        
        # Tier 3 search if query
        if query:
            results = self.search.search(project_name, query, limit=10)
            if results:
                response_lines.extend([
                    f"🔍 Search Results for: \"{query}\"",
                    f"📋 Found {len(results)} relevant sessions:",
                    ""
                ])
                for r in results[:5]:
                    response_lines.append(f"  • {r['session_id']} - {r.get('timestamp', '')[:16]}")
        
        return {"response": "\n".join(response_lines)}    
    def lo_update(self, project_name: str, mode: str = "normal", project_path: str = None) -> Dict:
        """Update - read from JSON templates"""
        try:
            # Smart parameter detection
            if mode and (mode.startswith('C:\\') or mode.startswith('/') or '\\' in mode or '/' in mode):
                project_path = mode
                mode = "normal"
            
            # Read JSON commands
            with open("C:\\LogSec\\data\\templates\\update_commands.json", 'r', encoding='utf-8') as f:
                commands = json.load(f)
            
            # Get the right template
            template = commands.get('lo_update', {}).get(mode, commands.get('lo_update', {}).get('default', 'Hello Claude!'))
            
            return {"response": template}
            
        except Exception as e:
            return {"response": f"Error: {str(e)}"}
    
    def lo_start(self, project_name: str) -> Dict:
        """Start with continuation"""
        if not project_name:
            return {"error": "project_name is required"}
        
        project_name = self._normalize_project_name(project_name)
        project_dir = self.projects_dir / project_name
        cont_file = project_dir / "continuation.md"
        
        response_lines = [f"🚀 {project_name.title()} Session Start", ""]
        
        # Load continuation if exists
        if cont_file.exists():
            with open(cont_file, 'r', encoding='utf-8') as f:
                cont_content = f.read()
            
            divider = self.templates.get('formatting', {}).get('divider', '-' * 50)
            response_lines.extend([
                "✨ Continuation file loaded!",
                "",
                "📋 Continuation Context:",
                divider,
                cont_content,
                divider,
                "",
                f"📂 Loaded from: {cont_file}"
            ])
        
        # Add project context
        load_result = self.lo_load(project_name)
        response_lines.extend([
            "",
            load_result.get("response", ""),
            "",
            "🎯 Ready to continue!"
        ])
        
        return {"response": "\n".join(response_lines)}
    
    def lo_cont(self, project_name: str, mode: str = "auto") -> Dict:
        """Create continuation"""
        if not project_name:
            return {"error": "project_name is required"}
        
        project_name = self._normalize_project_name(project_name)
        project_dir = self.projects_dir / project_name
        cont_file = project_dir / "continuation.md"
        
        # Ensure project directory exists
        project_dir.mkdir(parents=True, exist_ok=True)
        
        template = self.templates.get('commands', {}).get('lo_cont', {}).get('response_template', [
            "🔍 Analyzing Current Session for Continuation...",
            "",
            f"📂 Continuation will be saved to: {cont_file}",
            "",
            "Instructions:",
            f"Claude will create continuation file at: {cont_file}"
        ])
        
        response_lines = []
        for line in template:
            response_lines.append(line.format(cont_file=cont_file))
        
        return {"response": "\n".join(response_lines)}    
    # === MCP PROTOCOL ===
    
    def handle_mcp_request(self, request: Dict) -> Optional[Dict]:
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return {
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "logsec",
                        "version": "3.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
            
        elif method == "notifications/initialized":
            return None
            
        elif method == "tools/list":
            # Tool definitions
            tools = [
                {
                    "name": "lo_load",
                    "description": "Load project knowledge - two modes: summary or search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                            "query": {"type": "string", "description": "Search query (optional)"}
                        },
                        "required": ["project_name"]
                    }
                },
                {
                    "name": "lo_save",
                    "description": "Save content to project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                            "content": {"type": "string", "description": "Content to save (optional)"},
                            "session_id": {"type": "string", "description": "Session ID (optional)"}
                        },
                        "required": ["project_name"]
                    }
                },
                {
                    "name": "lo_update",
                    "description": "Update project README",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                            "mode": {"type": "string", "enum": ["normal", "deep"]},
                            "project_path": {"type": "string", "description": "Optional project path"}
                        },
                        "required": ["project_name"]
                    }
                },
                {
                    "name": "lo_start",
                    "description": "Start session with continuation",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Project name (REQUIRED)"}
                        },
                        "required": ["project_name"]
                    }
                },
                {
                    "name": "lo_cont",
                    "description": "Create continuation file",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Project name (REQUIRED)"},
                            "mode": {"type": "string", "enum": ["auto", "debug", "implement"]}
                        },
                        "required": ["project_name"]
                    }
                }
            ]
            
            return {"result": {"tools": tools}}
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                # Route to appropriate method
                if tool_name == "lo_load":
                    result = self.lo_load(**arguments)
                elif tool_name == "lo_save":
                    result = self.lo_save(**arguments)
                elif tool_name == "lo_update":
                    result = self.lo_update(**arguments)
                elif tool_name == "lo_start":
                    result = self.lo_start(**arguments)
                elif tool_name == "lo_cont":
                    result = self.lo_cont(**arguments)
                else:
                    return {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
                
                # Format response
                if "error" in result:
                    return {"error": {"code": -32000, "message": result["error"]}}
                else:
                    return {
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": result.get("response", json.dumps(result, indent=2))
                            }]
                        }
                    }
                    
            except Exception as e:
                import traceback
                traceback.print_exc(file=sys.stderr)
                return {"error": {"code": -32000, "message": str(e)}}
        
        else:
            return {"error": {"code": -32601, "message": f"Method not found: {method}"}}


def main():
    """MCP Server main loop"""
    try:
        core = LogSecCore()
        print("LogSec Core v3 Simple initialized", file=sys.stderr)
    except Exception as e:
        print(f"Error initializing: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("MCP Server ready", file=sys.stderr)
    
    # Main loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                import time
                time.sleep(0.1)
                continue
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error", "data": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                continue
            
            response = core.handle_mcp_request(request)
            
            if response is not None:
                response["jsonrpc"] = "2.0"
                if "id" in request:
                    response["id"] = request["id"]
                print(json.dumps(response))
                sys.stdout.flush()
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if 'request' in locals() and 'id' in request:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request["id"],
                    "error": {"code": -32603, "message": "Internal error", "data": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


if __name__ == "__main__":
    main()