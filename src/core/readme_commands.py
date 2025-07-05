"""
README Command Interface for LogSec 3.0
Provides lo_readme functionality
"""

from core.tier2_manager import Tier2Manager
from typing import Optional

class ReadmeCommands:
    """Handle README-related commands"""
    
    def __init__(self, tier2_manager: Optional[Tier2Manager] = None):
        self.tier2 = tier2_manager or Tier2Manager()
    
    def handle_command(self, args: list) -> str:
        """
        Handle lo_readme commands
        
        Commands:
        - lo_readme <project> - View README
        - lo_readme create <project> <content> [template] - Create README
        - lo_readme update <project> <content> [reason] - Update README
        - lo_readme history <project> - View update history
        - lo_readme list - List all projects with READMEs
        """
        
        if not args:
            return self._show_help()
        
        # View README (default action)
        if len(args) == 1:
            return self.tier2.format_readme_display(args[0])
        
        command = args[0].lower()
        
        if command == "create":
            return self._handle_create(args[1:])
        elif command == "update":
            return self._handle_update(args[1:])
        elif command == "history":
            return self._handle_history(args[1:])
        elif command == "list":
            return self._handle_list()
        else:
            # Assume first arg is project name for viewing
            return self.tier2.format_readme_display(command)
    
    def _handle_create(self, args: list) -> str:
        """Handle README creation"""
        if len(args) < 2:
            return "Usage: lo_readme create <project> <content> [template]\n" \
                   "Templates: software, minimal"
        
        project = args[0]
        content = args[1]
        template = args[2] if len(args) > 2 else None
        
        if self.tier2.create_readme(project, content, template):
            return f"✅ README created for project: {project}\n" \
                   f"Use 'lo_readme {project}' to view it."
        else:
            return f"❌ Failed to create README. It may already exist.\n" \
                   f"Use 'lo_readme update {project}' to modify existing README."
    
    def _handle_update(self, args: list) -> str:
        """Handle README updates"""
        if len(args) < 2:
            return "Usage: lo_readme update <project> <content> [reason]"
        
        project = args[0]
        content = args[1]
        reason = args[2] if len(args) > 2 else "Manual update"
        
        if self.tier2.update_readme(project, content, reason):
            readme = self.tier2.get_readme(project)
            return f"✅ README updated for project: {project}\n" \
                   f"New version: {readme['version']}\n" \
                   f"Reason: {reason}"
        else:
            return f"❌ Failed to update README. Does the project exist?"
    
    def _handle_history(self, args: list) -> str:
        """Show README update history"""
        if not args:
            return "Usage: lo_readme history <project>"
        
        project = args[0]
        history = self.tier2.get_readme_history(project)
        
        if not history:
            return f"No history found for project: {project}"
        
        lines = [f"📜 README History for {project.upper()}:", ""]
        
        for entry in history:
            lines.append(f"Version {entry['version']} - {entry['updated_at'][:16]}")
            lines.append(f"  Reason: {entry['reason']}")
            lines.append(f"  Preview: {entry['content_preview'][:80]}...")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _handle_list(self) -> str:
        """List all projects with READMEs"""
        projects = self.tier2.list_projects()
        
        if not projects:
            return "No project READMEs found.\n" \
                   "Use 'lo_readme create <project>' to create one."
        
        lines = ["📚 Projects with READMEs:", ""]
        
        for proj in projects:
            lines.append(f"• {proj['project']} (v{proj['version']})")
            lines.append(f"  Last updated: {proj['last_updated'][:10]}")
            lines.append(f"  Updates: {proj['update_count']}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _show_help(self) -> str:
        """Show help for lo_readme commands"""
        return """📚 lo_readme - Manage Tier 2 Project Documentation

Commands:
  lo_readme <project>                          View project README
  lo_readme create <project> <content> [template]   Create new README
  lo_readme update <project> <content> [reason]     Update existing README
  lo_readme history <project>                  View update history
  lo_readme list                               List all projects

Templates:
  software - Full software project template
  minimal  - Simple template (default)

Examples:
  lo_readme lynnvest                          View LynnVest README
  lo_readme create myproject "Description" software
  lo_readme update myproject "New content" "Added features"
"""


# Integration helper for lo_load
def get_tier2_content(project: str) -> Optional[str]:
    """Get Tier 2 content for lo_load integration"""
    tier2 = Tier2Manager()
    readme = tier2.get_readme(project)
    
    if not readme:
        return None
    
    # Return just the content part for lo_load
    return f"[README v{readme['version']}]\n{readme['content']}"