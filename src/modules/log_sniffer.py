import json
import re
from datetime import datetime
from pathlib import Path

class LogSniffer:
    """Reads Desktop Commander log file and extracts operations"""
    
    def __init__(self):
        self.log_path = Path(r"C:\Users\FB\AppData\Roaming\Claude\logs\mcp-server-desktop-commander.log")
        self.last_position = 0
        
    def extract_new_operations(self, project_name: str = None):
        """Extract new DC operations from log file"""
        operations = []
        
        if not self.log_path.exists():
            print(f"Log file not found: {self.log_path}", file=sys.stderr)
            return operations
            
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                # Skip to last read position
                f.seek(self.last_position)
                
                for line in f:
                    if '"method":"tools/call"' in line and 'desktop-commander' in line:
                        try:
                            # Extract JSON from log line
                            json_match = re.search(r'\{.*\}$', line)
                            if json_match:
                                data = json.loads(json_match.group())
                                
                                # Extract operation details
                                if 'params' in data and 'name' in data['params']:
                                    op_type = data['params']['name']
                                    arguments = data['params'].get('arguments', {})
                                    
                                    # Extract path based on operation type
                                    path = None
                                    if op_type in ['read_file', 'write_file', 'list_directory', 
                                                 'create_directory', 'get_file_info']:
                                        path = arguments.get('path')
                                    elif op_type == 'edit_block':
                                        path = arguments.get('file_path')
                                    elif op_type == 'move_file':
                                        path = arguments.get('source')  # or destination
                                    elif op_type in ['search_files', 'search_code']:
                                        path = arguments.get('path')
                                    elif op_type == 'execute_command':
                                        path = arguments.get('command')
                                        
                                    if path:
                                        operations.append({
                                            'type': op_type,
                                            'path': path,
                                            'timestamp': self._extract_timestamp(line),
                                            'project': project_name or self._guess_project(path)
                                        })
                                        
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"Error parsing log line: {e}", file=sys.stderr)
                            
                # Remember position for next read
                self.last_position = f.tell()
                
        except Exception as e:
            print(f"Error reading log file: {e}", file=sys.stderr)
            
        return operations
        
    def _extract_timestamp(self, line):
        """Extract timestamp from log line"""
        match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', line)
        if match:
            return match.group(1)
        return datetime.now().isoformat()
        
    def _guess_project(self, path):
        """Guess project from path"""
        if not path:
            return "unknown"
            
        path_lower = path.lower()
        if 'logsec' in path_lower or r'c:\logsec' in path_lower:
            return 'logsec'
        elif 'lynnvest' in path_lower:
            return 'lynnvest'
        elif 'github' in path_lower:
            return 'github'
        # Add more project patterns as needed
        
        return "unknown"
