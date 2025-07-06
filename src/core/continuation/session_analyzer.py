"""
Enhanced Continuation Extractor for LogSec 3.0
Automatically extracts continuation context from session
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class SessionAnalyzer:
    """Analyzes session content to extract continuation context"""
    
    def __init__(self):
        self.dc_patterns = {
            'read_file': r'desktop-commander:read_file.*?"path":\s*"([^"]+)"',
            'write_file': r'desktop-commander:write_file.*?"path":\s*"([^"]+)"',
            'edit_block': r'desktop-commander:edit_block.*?"file_path":\s*"([^"]+)".*?"old_str":\s*"([^"]*)".*?"new_str":\s*"([^"]*)"',
            'execute_command': r'desktop-commander:execute_command.*?"command":\s*"([^"]+)"',
            'list_directory': r'desktop-commander:list_directory.*?"path":\s*"([^"]+)"'
        }
        
    def extract_from_session(self, session_content: str, last_n: int = 5) -> Dict[str, Any]:
        """
        Extract continuation context from session
        
        Args:
            session_content: Full session content
            last_n: Number of last interactions to analyze
            
        Returns:
            Structured continuation data
        """
        # Split into interactions (simplified - in real implementation would be more sophisticated)
        interactions = self._split_interactions(session_content)
        recent_interactions = interactions[-last_n:] if len(interactions) > last_n else interactions
        
        # Extract components
        task = self._extract_task(recent_interactions)
        result = self._extract_last_result(recent_interactions)
        position = self._extract_current_position(recent_interactions)
        next_step = self._infer_next_step(recent_interactions, result)
        files = self._extract_files(session_content)
        commands = self._extract_commands(recent_interactions)
        context = self._extract_essential_context(recent_interactions)        
        return {
            "task": task,
            "result": result,
            "position": position,
            "next": next_step,
            "files": files,
            "commands": commands,
            "context": context
        }
    
    def _split_interactions(self, content: str) -> List[str]:
        """Split session into individual interactions"""
        # This is a simplified version - real implementation would be more sophisticated
        # Could use Claude message boundaries, timestamp patterns, etc.
        parts = re.split(r'(?=Human:|Assistant:)', content)
        return [p.strip() for p in parts if p.strip()]
    
    def _extract_task(self, interactions: List[str]) -> str:
        """Extract what was being worked on"""
        # Look for task indicators in recent interactions
        task_patterns = [
            r'working on\s+(.+?)(?:\.|$)',
            r'implementing\s+(.+?)(?:\.|$)',
            r'fixing\s+(.+?)(?:\.|$)',
            r'creating\s+(.+?)(?:\.|$)',
            r'task:\s*(.+?)(?:\.|$)'
        ]
        
        for interaction in reversed(interactions):
            for pattern in task_patterns:
                match = re.search(pattern, interaction, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Fallback: extract from first significant line
        return "Session work"
    
    def _extract_last_result(self, interactions: List[str]) -> str:
        """Extract the result of last actions"""
        if not interactions:
            return "No recent results"
            
        last_interaction = interactions[-1]
        
        # Look for result indicators
        result_patterns = [
            r'(?:successfully|completed|finished|done)\s+(.+?)(?:\.|$)',
            r'(?:error|failed|problem)\s+(.+?)(?:\.|$)',
            r'result:\s*(.+?)(?:\.|$)',
            r'output:\s*(.+?)(?:\.|$)'
        ]        
        for pattern in result_patterns:
            match = re.search(pattern, last_interaction, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Extract last significant statement
        sentences = re.split(r'[.!?]+', last_interaction)
        return sentences[-2].strip() if len(sentences) > 1 else "Work in progress"
    
    def _extract_current_position(self, interactions: List[str]) -> str:
        """Extract where exactly work stopped"""
        # Look for file positions in recent interactions
        position_patterns = [
            r'(?:at|in|editing)\s+([^\s]+\.py):(\d+)',
            r'line\s+(\d+)\s+(?:of|in)\s+([^\s]+)',
            r'function\s+(\w+)\s+in\s+([^\s]+)',
            r'([^\s]+\.(?:py|js|java|cpp|c|h|md|txt|json|yaml|yml)):(\d+)'
        ]
        
        for interaction in reversed(interactions):
            for pattern in position_patterns:
                match = re.search(pattern, interaction)
                if match:
                    if match.lastindex == 2:
                        return f"{match.group(1)}:{match.group(2)}"
                    else:
                        return match.group(0)
        
        return "Unknown position"
    
    def _infer_next_step(self, interactions: List[str], last_result: str) -> str:
        """Infer the logical next step based on context"""
        # Check if last result indicates a problem
        if any(word in last_result.lower() for word in ['error', 'failed', 'problem']):
            return f"Debug and fix: {last_result}"
        
        # Look for TODO or next step mentions
        next_patterns = [
            r'(?:next|then|todo|need to)\s+(.+?)(?:\.|$)',
            r'(?:should|must|have to)\s+(.+?)(?:\.|$)',
            r'(?:remaining|pending):\s*(.+?)(?:\.|$)'
        ]
        
        for interaction in reversed(interactions):
            for pattern in next_patterns:
                match = re.search(pattern, interaction, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return "Continue implementation"    
    def _extract_files(self, content: str) -> List[Dict[str, str]]:
        """Extract files that were worked on"""
        files = {}
        
        # Extract read operations
        for match in re.finditer(self.dc_patterns['read_file'], content):
            path = match.group(1)
            if self._is_valid_path(path):
                files[path] = {"path": path, "relevance": "viewed"}
        
        # Extract write operations (higher relevance)
        for match in re.finditer(self.dc_patterns['write_file'], content):
            path = match.group(1)
            if self._is_valid_path(path):
                files[path] = {"path": path, "relevance": "edited"}
        
        # Extract edit operations (highest relevance)
        for match in re.finditer(self.dc_patterns['edit_block'], content):
            path = match.group(1)
            if self._is_valid_path(path):
                files[path] = {"path": path, "relevance": "edited"}
        
        return list(files.values())
    
    def _extract_commands(self, interactions: List[str]) -> List[Dict[str, str]]:
        """Extract executed commands with status"""
        commands = []
        
        for interaction in interactions:
            for match in re.finditer(self.dc_patterns['execute_command'], interaction):
                cmd = match.group(1)
                # Try to determine status from surrounding context
                status = self._determine_command_status(interaction, match.start())
                commands.append({"cmd": cmd, "status": status})
        
        return commands[-5:]  # Last 5 commands
    
    def _determine_command_status(self, content: str, cmd_position: int) -> str:
        """Determine if command succeeded or failed based on context"""
        # Look ahead in content for success/failure indicators
        context = content[cmd_position:cmd_position + 500]
        
        if any(word in context.lower() for word in ['success', 'passed', 'complete', '✓', '✅']):
            return "success"
        elif any(word in context.lower() for word in ['error', 'failed', 'exception', '✗', '❌']):
            return "failed"
        
        return "unknown"    
    def _extract_essential_context(self, interactions: List[str]) -> str:
        """Extract essential context for continuation"""
        # Look for context clues
        context_patterns = [
            r'(?:because|due to|since)\s+(.+?)(?:\.|$)',
            r'(?:using|with|via)\s+(.+?)(?:\.|$)',
            r'(?:note:|important:|remember:)\s*(.+?)(?:\.|$)'
        ]
        
        contexts = []
        for interaction in interactions:
            for pattern in context_patterns:
                matches = re.findall(pattern, interaction, re.IGNORECASE)
                contexts.extend([m.strip() for m in matches])
        
        # Return most recent relevant context
        return contexts[-1] if contexts else ""
    
    def _is_valid_path(self, path: str) -> bool:
        """Check if path exists and is valid"""
        try:
            return Path(path).exists()
        except:
            return False


class ContinuationManager:
    """Manages continuation data storage and retrieval"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure continuation_data table exists"""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS continuation_data (
                    project_name TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    task TEXT,
                    result TEXT,
                    position TEXT,
                    next_step TEXT,
                    files TEXT,
                    commands TEXT,
                    context TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()    
    def save_continuation(self, project_name: str, continuation_data: Dict[str, Any]):
        """Save continuation data for project"""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            # Convert lists to JSON
            files_json = json.dumps(continuation_data.get('files', []))
            commands_json = json.dumps(continuation_data.get('commands', []))
            
            conn.execute("""
                INSERT OR REPLACE INTO continuation_data 
                (project_name, timestamp, task, result, position, next_step, files, commands, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_name,
                datetime.now().isoformat(),
                continuation_data.get('task', ''),
                continuation_data.get('result', ''),
                continuation_data.get('position', ''),
                continuation_data.get('next', ''),
                files_json,
                commands_json,
                continuation_data.get('context', '')
            ))
            conn.commit()
    
    def get_continuation(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve continuation data for project"""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, task, result, position, next_step, files, commands, context
                FROM continuation_data
                WHERE project_name = ?
            """, (project_name,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'timestamp': row[0],
                    'task': row[1],
                    'result': row[2],
                    'position': row[3],
                    'next': row[4],
                    'files': json.loads(row[5]) if row[5] else [],
                    'commands': json.loads(row[6]) if row[6] else [],
                    'context': row[7]
                }
        
        return None