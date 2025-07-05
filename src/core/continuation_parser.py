"""
Continuation Format Parser for LogSec 3.0
Handles structured lo_cont format for seamless session continuation
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class ContinuationParser:
    """Parse and structure lo_cont format for perfect work continuation"""
    
    # Multi-language support for section headers
    SECTION_MAPPINGS = {
        'STATUS': ['STATUS', 'WAS', 'AUFGABE', 'TASK'],
        'POSITION': ['POSITION', 'WO', 'WHERE', 'STELLE'],
        'PROBLEM': ['PROBLEM', 'BLOCKER', 'ISSUE', 'FEHLER'],
        'TRIED': ['TRIED', 'VERSUCHT', 'ATTEMPTED', 'PROBIERT'],
        'NEXT': ['NEXT', 'NÄCHSTE', 'WEITER'],
        'TODO': ['TODO', 'TODOS', 'AUFGABEN', 'TASKS'],
        'CONTEXT': ['CONTEXT', 'KONTEXT', 'INFO', 'ZUSATZ']
    }
    
    def __init__(self):
        self.section_pattern = self._build_section_pattern()
        
    def _build_section_pattern(self) -> re.Pattern:
        """Build regex pattern for all possible section headers"""
        all_keywords = []
        for section_variants in self.SECTION_MAPPINGS.values():
            all_keywords.extend(section_variants)
        
        # Pattern: KEYWORD: at start of line (case insensitive)
        pattern = r'^(' + '|'.join(all_keywords) + r'):\s*(.*)$'
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse continuation format into structured data
        
        Returns:
            {
                'status': 'Current task description',
                'position': {'file': 'example.py', 'line': 123, 'function': 'method_name'},
                'problem': 'What is blocking',
                'tried': ['attempt 1', 'attempt 2'],
                'next': ['next step 1', 'next step 2'],
                'todo': ['todo item 1', 'todo item 2'],
                'context': 'Additional context',
                'raw_sections': {...},  # Original text for each section
                'timestamp': '2025-01-07T10:30:00',
                'has_git': false  # Placeholder for git integration
            }
        """
        
        # Extract sections
        sections = self._extract_sections(content)
        
        # Parse specific fields
        result = {
            'timestamp': datetime.now().isoformat(),
            'raw_sections': sections,
            'has_git': False  # Will be enhanced in Phase 2
        }
        
        # Process each section
        result['status'] = self._get_section(sections, 'STATUS')
        result['position'] = self._parse_position(self._get_section(sections, 'POSITION'))
        result['problem'] = self._get_section(sections, 'PROBLEM')
        result['tried'] = self._parse_list(self._get_section(sections, 'TRIED'))
        result['next'] = self._parse_list(self._get_section(sections, 'NEXT'))
        result['todo'] = self._parse_list(self._get_section(sections, 'TODO'))
        result['context'] = self._get_section(sections, 'CONTEXT')
        
        # Validate minimum required fields
        if not result['status']:
            result['status'] = self._extract_first_line(content) or "Continuation session"
            
        return result
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract all sections from content"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            match = self.section_pattern.match(line.strip())
            
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                keyword = match.group(1).upper()
                current_section = self._normalize_section(keyword)
                current_content = [match.group(2).strip()] if match.group(2).strip() else []
            else:
                # Continue current section
                if current_section:
                    current_content.append(line.strip())
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections
    
    def _normalize_section(self, keyword: str) -> str:
        """Normalize keyword to standard section name"""
        keyword_upper = keyword.upper()
        for standard, variants in self.SECTION_MAPPINGS.items():
            if keyword_upper in [v.upper() for v in variants]:
                return standard
        return keyword_upper
    
    def _get_section(self, sections: Dict[str, str], section: str) -> str:
        """Get section content with fallback to empty string"""
        return sections.get(section, '')
    
    def _parse_position(self, position_text: str) -> Dict[str, Any]:
        """
        Parse position information
        Examples:
        - "main.py:123 - function_name()"
        - "src/module.py:45"
        - "config.json"
        """
        if not position_text:
            return {}
            
        result = {'raw': position_text}
        
        # Try to extract file:line pattern
        file_pattern = r'([^:]+?):(\d+)'
        match = re.search(file_pattern, position_text)
        
        if match:
            result['file'] = match.group(1).strip()
            result['line'] = int(match.group(2))
            
            # Try to extract function/method name
            func_pattern = r'-\s*(\w+)\s*\('
            func_match = re.search(func_pattern, position_text)
            if func_match:
                result['function'] = func_match.group(1)
        else:
            # Just a file path
            result['file'] = position_text.strip()
            
        return result
    
    def _parse_list(self, text: str) -> List[str]:
        """Parse text into list items (bullet points, numbered, or line-separated)"""
        if not text:
            return []
            
        items = []
        
        # Split by common list indicators
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove bullet points, numbers, etc.
            cleaned = re.sub(r'^[\s\-\*\•\·\→\>]+', '', line)
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', cleaned)
            
            if cleaned.strip():
                items.append(cleaned.strip())
                
        return items
    
    def _extract_first_line(self, content: str) -> str:
        """Extract first non-empty line as fallback"""
        for line in content.split('\n'):
            if line.strip() and not self.section_pattern.match(line.strip()):
                return line.strip()
        return ""
    
    def format_for_display(self, parsed_data: Dict[str, Any]) -> str:
        """Format parsed data for lo_start display"""
        lines = []
        
        # Header
        lines.append("═" * 60)
        lines.append("📍 CONTINUATION SESSION")
        lines.append("═" * 60)
        
        # Status
        if parsed_data.get('status'):
            lines.append(f"\n🎯 CURRENT TASK:")
            lines.append(f"   {parsed_data['status']}")
        
        # Position
        if parsed_data.get('position'):
            pos = parsed_data['position']
            lines.append(f"\n📂 POSITION:")
            if 'file' in pos:
                location = f"   {pos['file']}"
                if 'line' in pos:
                    location += f":{pos['line']}"
                if 'function' in pos:
                    location += f" - {pos['function']}()"
                lines.append(location)
        
        # Problem
        if parsed_data.get('problem'):
            lines.append(f"\n⚠️  BLOCKED BY:")
            lines.append(f"   {parsed_data['problem']}")
        
        # Tried
        if parsed_data.get('tried'):
            lines.append(f"\n🔄 ALREADY TRIED:")
            for item in parsed_data['tried']:
                lines.append(f"   ❌ {item}")
        
        # Next steps
        if parsed_data.get('next'):
            lines.append(f"\n➡️  NEXT STEPS:")
            for item in parsed_data['next']:
                lines.append(f"   → {item}")
        
        # TODOs
        if parsed_data.get('todo'):
            lines.append(f"\n📋 TODO LIST:")
            for item in parsed_data['todo']:
                lines.append(f"   ☐ {item}")
        
        # Context
        if parsed_data.get('context'):
            lines.append(f"\n💡 CONTEXT:")
            lines.append(f"   {parsed_data['context']}")
        
        lines.append("\n" + "═" * 60)
        
        return '\n'.join(lines)


# Example usage and testing