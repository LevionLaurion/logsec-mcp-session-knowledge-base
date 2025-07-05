"""
Enhanced Session Handoff for LogSec 3.0
Integrates with ContinuationParser for structured handoffs
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Any
import logging

# Import the new continuation parser
from core.continuation_parser import ContinuationParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionHandoffV3:
    """Enhanced handoff system with structured continuation support"""
    
    def __init__(self, base_path: str = r"C:\LogSec"):
        self.base_path = Path(base_path)
        self.handoff_dir = self.base_path / "knowledge" / "handoffs"
        self.handoff_dir.mkdir(parents=True, exist_ok=True)
        self.parser = ContinuationParser()
        
    def save_continuation(self, content: str, project: str) -> Dict[str, Any]:
        """
        Save a continuation session using lo_cont format
        
        Args:
            content: Raw continuation text in structured format
            project: Project name
            
        Returns:
            Parsed continuation data with session ID
        """
        try:
            # Parse the continuation format
            parsed_data = self.parser.parse(content)
            
            # Generate session ID
            session_id = self._generate_session_id(project)
            parsed_data['session_id'] = session_id
            parsed_data['project'] = project
            
            # Save handoff file (project-specific)
            handoff_file = self.handoff_dir / f"{project}_handoff.json"
            with open(handoff_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
            # Also save a backup with timestamp
            backup_file = self.handoff_dir / f"{project}_{session_id}_backup.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Continuation saved for {project}: {session_id}")
            
            # Extract key files for ProjectPathTracker integration
            if parsed_data.get('position', {}).get('file'):
                self._update_project_files(project, parsed_data['position']['file'])
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to save continuation: {e}")
            raise
    
    def load_continuation(self, project: str) -> Optional[Dict[str, Any]]:
        """
        Load the last continuation for a project
        
        Returns:
            Parsed continuation data or None if not found
        """
        try:
            handoff_file = self.handoff_dir / f"{project}_handoff.json"
            
            if not handoff_file.exists():
                logger.info(f"No handoff found for project: {project}")
                return None
            
            with open(handoff_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if handoff is recent (within 7 days)
            timestamp = datetime.fromisoformat(data['timestamp'])
            age = datetime.now() - timestamp
            
            if age > timedelta(days=7):
                logger.warning(f"Handoff for {project} is {age.days} days old")
                data['age_warning'] = f"Note: This continuation is {age.days} days old"
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load continuation: {e}")
            return None
    
    def format_for_start(self, project: str) -> str:
        """
        Format continuation for lo_start display
        
        Returns:
            Formatted string ready for display
        """
        data = self.load_continuation(project)
        
        if not data:
            return f"No active continuation found for project: {project}"
        
        # Use the parser's format method
        formatted = self.parser.format_for_display(data)
        
        # Add age warning if present
        if 'age_warning' in data:
            formatted = f"⚠️  {data['age_warning']}\n\n" + formatted
        
        return formatted
    
    def get_active_files(self, project: str) -> List[str]:
        """Get list of files to open for continuation"""
        data = self.load_continuation(project)
        
        if not data:
            return []
        
        files = []
        
        # Primary file from position
        if data.get('position', {}).get('file'):
            files.append(data['position']['file'])
        
        # Any files mentioned in context or todos
        # (This could be enhanced with better file detection)
        
        return files
    
    def _generate_session_id(self, project: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{project}_{timestamp}"
    
    def _update_project_files(self, project: str, file_path: str):
        """Update project file tracking (for ProjectPathTracker integration)"""
        # This will integrate with the existing project_tracker module
        # For now, just log it
        logger.info(f"Project {project} working on: {file_path}")
    
    def clear_continuation(self, project: str) -> bool:
        """Clear continuation data when work is complete"""
        try:
            handoff_file = self.handoff_dir / f"{project}_handoff.json"
            if handoff_file.exists():
                handoff_file.unlink()
                logger.info(f"Cleared continuation for {project}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to clear continuation: {e}")
            return False
    
    def list_active_continuations(self) -> List[Dict[str, Any]]:
        """List all active continuations across projects"""
        continuations = []
        
        for handoff_file in self.handoff_dir.glob("*_handoff.json"):
            if "_backup" in handoff_file.name:
                continue
                
            try:
                with open(handoff_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                project = handoff_file.stem.replace("_handoff", "")
                continuations.append({
                    'project': project,
                    'status': data.get('status', 'Unknown'),
                    'timestamp': data.get('timestamp', 'Unknown'),
                    'has_problem': bool(data.get('problem'))
                })
            except Exception as e:
                logger.error(f"Error reading {handoff_file}: {e}")
        
        return continuations


# Backward compatibility wrapper
class SessionHandoff(SessionHandoffV3):
    """Maintains compatibility with existing code while using V3 features"""
    
    def save_handoff(self, session_id: str, project: str, context: Dict) -> bool:
        """Legacy method - converts to new format"""
        try:
            # Convert old format to new continuation format
            content_parts = []
            
            if context.get("current_task"):
                content_parts.append(f"STATUS: {context['current_task']}")
            
            if context.get("key_files"):
                if context["key_files"]:
                    content_parts.append(f"POSITION: {context['key_files'][0]}")
            
            if context.get("next_steps"):
                content_parts.append("NEXT:")
                for step in context["next_steps"]:
                    content_parts.append(f"- {step}")
            
            if context.get("notes"):
                content_parts.append(f"CONTEXT: {context['notes']}")
            
            content = "\n".join(content_parts)
            self.save_continuation(content, project)
            return True
            
        except Exception:
            return False