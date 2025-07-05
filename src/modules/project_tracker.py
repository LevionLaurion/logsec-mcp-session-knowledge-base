"""
📁 Project Path Tracker for LogSec 2.0
Automatically tracks visited directories and files per project
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectPathTracker:
    """Tracks visited paths and files for each project"""
    
    def __init__(self, base_path: str = r"C:\LogSec"):
        self.base_path = Path(base_path)
        self.tracker_file = self.base_path / "knowledge" / "system" / "project_paths.json"
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load existing tracking data"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                logger.warning("Failed to load tracker data, starting fresh")
        
        # Default structure
        return {
            "projects": {
                "laurion": {
                    "base_paths": ["C:\\LogSec", "C:\\Laurion"],
                    "visited_dirs": [],
                    "worked_files": [],
                    "common_patterns": [],
                    "last_active": None
                },
                "lynnvest": {
                    "base_paths": ["C:\\Lynnvest"],
                    "visited_dirs": [],
                    "worked_files": [],
                    "common_patterns": [],
                    "last_active": None
                },
                "tsw": {
                    "base_paths": ["C:\\TSW", "C:\\TOPSOLID"],
                    "visited_dirs": [],
                    "worked_files": [],
                    "common_patterns": [],
                    "last_active": None
                },
                "general": {
                    "base_paths": [],
                    "visited_dirs": [],
                    "worked_files": [],
                    "common_patterns": [],
                    "last_active": None
                }
            },
            "stats": {
                "total_tracked": 0,
                "last_update": None
            }
        }
    
    def _save_data(self):
        """Save tracking data"""
        try:
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved tracking data: {self.data['stats']['total_tracked']} paths")
        except Exception as e:
            logger.error(f"Failed to save tracker data: {e}")
    
    def detect_project_from_path(self, path: str) -> str:
        """Detect project from path"""
        path_lower = path.lower()
        
        # Check base paths
        for project, info in self.data["projects"].items():
            for base_path in info["base_paths"]:
                if base_path.lower() in path_lower:
                    return project
        
        # Check if path contains project name
        for project in self.data["projects"]:
            if project in path_lower:
                return project
                
        return "general"
    
    def track_directory(self, path: str, project: str = None) -> str:
        """Track a visited directory"""
        if not project:
            project = self.detect_project_from_path(path)
        
        # Normalize path
        path = str(Path(path).resolve())
        
        # Add to visited dirs (no duplicates)
        visited = self.data["projects"][project]["visited_dirs"]
        if path not in visited:
            visited.append(path)
            self.data["stats"]["total_tracked"] += 1
            
            # Extract common patterns (e.g., "knowledge", "embeddings")
            parts = Path(path).parts
            for part in parts:
                if part.lower() not in ['c:', 'users', 'fb', project]:
                    patterns = self.data["projects"][project]["common_patterns"]
                    if part not in patterns:
                        patterns.append(part)
        
        # Update timestamps
        self.data["projects"][project]["last_active"] = datetime.now().isoformat()
        self.data["stats"]["last_update"] = datetime.now().isoformat()
        
        self._save_data()
        return project
    
    def track_file(self, filepath: str, project: str = None) -> str:
        """Track a worked-on file"""
        if not project:
            project = self.detect_project_from_path(filepath)
        
        # Track the directory too
        directory = str(Path(filepath).parent)
        self.track_directory(directory, project)
        
        # Track the file
        filename = Path(filepath).name
        worked_files = self.data["projects"][project]["worked_files"]
        if filename not in worked_files:
            worked_files.append(filename)
        
        self._save_data()
        return project
    
    def get_project_info(self, project: str) -> Dict:
        """Get all tracked info for a project"""
        if project not in self.data["projects"]:
            return {"error": f"Unknown project: {project}"}
        
        info = self.data["projects"][project]
        return {
            "project": project,
            "base_paths": info["base_paths"],
            "visited_count": len(info["visited_dirs"]),
            "files_count": len(info["worked_files"]),
            "recent_dirs": info["visited_dirs"][-5:],
            "recent_files": info["worked_files"][-10:],
            "common_patterns": info["common_patterns"][:10],
            "last_active": info["last_active"]
        }
    
    def get_quick_access(self, project: str) -> Dict:
        """Get quick access paths for a project"""
        if project not in self.data["projects"]:
            return {}
        
        info = self.data["projects"][project]
        quick_access = {}
        
        # Most recent directories
        for i, path in enumerate(info["visited_dirs"][-5:]):
            key = Path(path).name or f"path_{i}"
            quick_access[key] = path
        
        return quick_access
    
    def generate_project_report(self) -> str:
        """Generate a report of all tracked projects"""
        report = "# Project Path Tracking Report\n\n"
        
        for project, info in self.data["projects"].items():
            if info["visited_dirs"] or info["worked_files"]:
                report += f"## {project.upper()}\n"
                report += f"- Base: {', '.join(info['base_paths'])}\n"
                report += f"- Visited: {len(info['visited_dirs'])} directories\n"
                report += f"- Worked on: {len(info['worked_files'])} files\n"
                
                if info["common_patterns"]:
                    report += f"- Patterns: {', '.join(info['common_patterns'][:5])}\n"
                
                if info["last_active"]:
                    report += f"- Last active: {info['last_active'][:10]}\n"
                
                report += "\n"
        
        report += f"**Total tracked paths**: {self.data['stats']['total_tracked']}\n"
        return report


# Integration function for logsec_core.py
def track_logsec_activity(path: str, is_file: bool = False) -> str:
    """Track activity for LogSec - to be called from logsec_core"""
    tracker = ProjectPathTracker()
    
    if is_file:
        return tracker.track_file(path)
    else:
        return tracker.track_directory(path)