"""
Tier 2 README Manager for LogSec 3.0
Handles persistent project documentation that changes rarely
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tier2Manager:
    """Manages persistent README-style documentation for projects"""
    
    def __init__(self, base_path: str = r"C:\LogSec"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "knowledge" / "tier2_readme.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize Tier 2 database with README table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_readme (
                project TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                version TEXT DEFAULT '1.0',
                update_count INTEGER DEFAULT 0,
                created_at TIMESTAMP NOT NULL
            )
        """)
        
        # Also create a history table for tracking changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readme_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT NOT NULL,
                content TEXT NOT NULL,
                version TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                update_reason TEXT,
                FOREIGN KEY (project) REFERENCES project_readme(project)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Tier 2 database initialized")
    
    def get_readme(self, project: str) -> Optional[Dict[str, Any]]:
        """Get the current README for a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content, last_updated, version, update_count, created_at
            FROM project_readme
            WHERE project = ?
        """, (project,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
            
        return {
            'project': project,
            'content': result[0],
            'last_updated': result[1],
            'version': result[2],
            'update_count': result[3],
            'created_at': result[4]
        }
    
    def create_readme(self, project: str, content: str, template: Optional[str] = None) -> bool:
        """Create a new README for a project"""
        if template:
            content = self._apply_template(project, template, content)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO project_readme (project, content, last_updated, created_at)
                VALUES (?, ?, ?, ?)
            """, (project, content, now, now))
            
            # Add to history
            cursor.execute("""
                INSERT INTO readme_history (project, content, version, updated_at, update_reason)
                VALUES (?, ?, '1.0', ?, 'Initial creation')
            """, (project, content, now))
            
            conn.commit()
            logger.info(f"Created README for project: {project}")
            return True
            
        except sqlite3.IntegrityError:
            logger.error(f"README already exists for project: {project}")
            return False
        finally:
            conn.close()
    
    def update_readme(self, project: str, content: str, reason: str = "Manual update") -> bool:
        """Update existing README - this should be rare!"""
        current = self.get_readme(project)
        if not current:
            logger.error(f"No README found for project: {project}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Increment version
            major, minor = current['version'].split('.')
            new_version = f"{major}.{int(minor) + 1}"
            now = datetime.now().isoformat()
            
            # Update main table
            cursor.execute("""
                UPDATE project_readme
                SET content = ?, last_updated = ?, version = ?, update_count = update_count + 1
                WHERE project = ?
            """, (content, now, new_version, project))
            
            # Add to history
            cursor.execute("""
                INSERT INTO readme_history (project, content, version, updated_at, update_reason)
                VALUES (?, ?, ?, ?, ?)
            """, (project, content, new_version, now, reason))
            
            conn.commit()
            logger.info(f"Updated README for project: {project} to version {new_version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update README: {e}")
            return False
        finally:
            conn.close()
    
    def get_readme_history(self, project: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get update history for a project README"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version, updated_at, update_reason, content
            FROM readme_history
            WHERE project = ?
            ORDER BY updated_at DESC
            LIMIT ?
        """, (project, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'version': row[0],
                'updated_at': row[1],
                'reason': row[2],
                'content_preview': row[3][:200] + '...' if len(row[3]) > 200 else row[3]
            })
            
        conn.close()
        return history
    
    def format_readme_display(self, project: str) -> str:
        """Format README for display in lo_load"""
        readme = self.get_readme(project)
        
        if not readme:
            return f"No README found for project: {project}\nUse 'lo_readme create {project}' to create one."
            
        lines = []
        lines.append("=" * 70)
        lines.append(f"📚 PROJECT README: {project.upper()}")
        lines.append("=" * 70)
        lines.append(f"Version: {readme['version']} | Updated: {readme['last_updated'][:10]}")
        lines.append(f"Update Count: {readme['update_count']} | Created: {readme['created_at'][:10]}")
        lines.append("-" * 70)
        lines.append("")
        lines.append(readme['content'])
        lines.append("")
        lines.append("=" * 70)
        lines.append("📝 To update: lo_readme update [project] [content]")
        
        return '\n'.join(lines)
    
    def _apply_template(self, project: str, template: str, custom_content: str) -> str:
        """Apply a template to create consistent READMEs"""
        templates = {
            'software': """# {project}

## Overview
{custom_content}

## Architecture
- **Language**: [Primary language]
- **Framework**: [Main framework]
- **Database**: [Database system]
- **Key Dependencies**: [List main deps]

## Project Structure
```
{project}/
├── src/          # Source code
├── tests/        # Test files
├── docs/         # Documentation
└── config/       # Configuration
```

## Current Status
- **Version**: [Current version]
- **Stage**: [Development/Beta/Production]
- **Last Major Update**: [Date]

## Key Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Development Notes
[Any important notes for continuation]
""",
            'minimal': """# {project}

## Description
{custom_content}

## Status
- Active development
- Current focus: [What you're working on]

## Quick Start
[How to resume work]

## Notes
[Important information]
"""
        }
        
        template_content = templates.get(template, templates['minimal'])
        return template_content.format(project=project.upper(), custom_content=custom_content)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with READMEs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT project, version, last_updated, update_count
            FROM project_readme
            ORDER BY last_updated DESC
        """)
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                'project': row[0],
                'version': row[1],
                'last_updated': row[2],
                'update_count': row[3]
            })
            
        conn.close()
        return projects


# Example usage for testing