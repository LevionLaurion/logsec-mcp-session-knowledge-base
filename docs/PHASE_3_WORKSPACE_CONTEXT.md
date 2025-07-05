# 📋 Phase 3 Feature: Dynamic Workspace Context

## Feature Overview

**Name**: Dynamic Workspace Context Extraction  
**Target**: `lo_cont` command  
**Priority**: High  
**Complexity**: Medium  

## 🎯 Motivation

When continuing work on a project, it's crucial to know:
- What files were worked on in the previous session
- Which of those files still exist
- What the current project structure looks like
- What commands were executed

Currently, this context is lost between sessions. This feature extracts it dynamically from Desktop Commander logs.

## 📐 Design

### Core Concept
- Extract Desktop Commander operations from session content
- Generate workspace context ON-THE-FLY (not stored in DB)
- Show only CURRENTLY EXISTING files and structures
- Group by project automatically

### Why Dynamic?
1. **Always Current**: Shows actual current state, not outdated info
2. **No DB Pollution**: Doesn't store paths that might be deleted/moved
3. **Context-Aware**: Only shows relevant project information

## 🔧 Technical Implementation

### 1. Desktop Commander Parser
```python
class DesktopCommanderParser:
    """Extract DC operations from session content"""
    
    DC_PATTERNS = {
        'read_file': r'<parameter name="path">(.*?)',
        'write_file': r'<parameter name="path">(.*?)</parameter>',
        'list_directory': r'<parameter name="path">(.*?)</parameter>',
        'execute_command': r'<parameter name="command">(.*?)</parameter>',
        'edit_block': r'<parameter name="file_path">(.*?)</parameter>',
        'move_file': r'<parameter name="(?:source|destination)">(.*?)</parameter>'
    }
    
    def extract_operations(self, content):
        operations = []
        for op_type, pattern in self.DC_PATTERNS.items():
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                operations.append({
                    'type': op_type,
                    'path': match.strip(),
                    'timestamp': self._extract_timestamp(match)
                })
        return operations
```

### 2. Project Detection
```python
class ProjectDetector:
    """Detect project from paths"""
    
    PROJECT_PATTERNS = {
        'logsec': [r'C:\\LogSec', r'/LogSec/', r'logsec_'],
        'lynnvest': [r'C:\\Lynnvest', r'/Lynnvest/', r'lynnvest_'],
        'laurion': [r'C:\\Laurion', r'/Laurion/', r'laurion_'],
        # Add more projects as needed
    }
    
    def detect_project(self, path):
        path_lower = path.lower()
        for project, patterns in self.PROJECT_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in path_lower:
                    return project
        return None
```

### 3. Live Context Generator
```python
class WorkspaceContextGenerator:
    """Generate current workspace context"""
    
    def generate_context(self, operations, target_project=None):
        context = {}
        
        # Group operations by project
        for op in operations:
            project = self.project_detector.detect_project(op['path'])
            if not project or (target_project and project != target_project):
                continue
                
            if project not in context:
                context[project] = {
                    'files': set(),
                    'directories': set(),
                    'commands': [],
                    'last_structure': None
                }
            
            # Add to appropriate category
            if op['type'] in ['read_file', 'write_file', 'edit_block']:
                if os.path.exists(op['path']):  # Only if still exists!
                    context[project]['files'].add(op['path'])
            elif op['type'] == 'list_directory':
                context[project]['directories'].add(op['path'])
                # Get current structure (not from log, but NOW)
                if os.path.exists(op['path']):
                    context[project]['last_structure'] = self._get_current_structure(op['path'])
            
        return context
```

### 4. Integration with lo_cont
```python
def lo_cont(self, query, language="en"):
    # Existing parsing
    parsed = self.parser.parse(query)
    result["parsed"] = parsed
    
    # NEW: Extract workspace context
    dc_parser = DesktopCommanderParser()
    operations = dc_parser.extract_operations(query)
    
    workspace_gen = WorkspaceContextGenerator()
    workspace_context = workspace_gen.generate_context(
        operations,
        target_project=self._detect_project_from_parsed(parsed)
    )
    
    # Add to result
    result["workspace_context"] = workspace_context
    
    # Format for display
    if workspace_context:
        result["prompt"] += self._format_workspace_context(workspace_context)
```

## 📊 Example Output

```markdown
### 🗂️ Workspace Context (Live Snapshot)

**Project: logsec**
📍 Root: C:\LogSec

**Recently Modified Files** (still exist):
- ✅ src/logsec_core_v3.py
- ✅ tests/test_core_v3.py  
- ❌ ~~debug_old.py~~ (no longer exists)

**Current Structure**:
```
C:\LogSec\
├── src/
│   ├── logsec_core_v3.py
│   └── modules/
├── tests/
├── docs/
└── data/
```

**Recent Commands**:
- `python test_core_v3.py` ✅ (successful)
- `git push origin main` ✅ (successful)
```

## 🎨 UI/UX Considerations

1. **Visual Indicators**
   - ✅ for existing files
   - ❌ for deleted files  
   - 📁 for directories
   - 🔧 for commands

2. **Filtering Options**
   - Show only existing files (default)
   - Show all historical files
   - Group by operation type

3. **Performance**
   - Cache file existence checks
   - Limit to last N operations
   - Async file system checks

## ⚡ Performance Optimization

```python
# Cache file existence checks
@lru_cache(maxsize=1000)
def file_exists_cached(path, cache_time=60):
    # Cache for 60 seconds
    return os.path.exists(path)

# Batch operations
def check_files_batch(paths):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(os.path.exists, paths)
    return dict(zip(paths, results))
```

## 🧪 Testing Strategy

1. **Unit Tests**
   - DC pattern extraction
   - Project detection accuracy
   - Path deduplication

2. **Integration Tests**
   - Full lo_cont flow with workspace context
   - Multi-project sessions
   - Non-existent file handling

3. **Performance Tests**
   - Large session parsing
   - Many file existence checks
   - Cache effectiveness

## 🚀 Implementation Steps

1. **Phase 3.1**: Basic Implementation
   - [ ] Create DesktopCommanderParser
   - [ ] Implement ProjectDetector
   - [ ] Basic context generation

2. **Phase 3.2**: Integration
   - [ ] Integrate with lo_cont
   - [ ] Add formatting
   - [ ] Test with real sessions

3. **Phase 3.3**: Optimization
   - [ ] Add caching
   - [ ] Performance tuning
   - [ ] Enhanced formatting

## 📈 Success Metrics

- **Accuracy**: 95%+ correct project detection
- **Performance**: <100ms for average session
- **Usefulness**: Reduces "where was I?" time by 80%

## 🔮 Future Enhancements

1. **Git Integration**
   - Show git status of files
   - Include branch information
   - Show uncommitted changes

2. **Intelligent Grouping**
   - Group by feature/task
   - Time-based clustering
   - Related file detection

3. **Export Options**
   - Export workspace snapshot
   - Generate project documentation
   - Create setup scripts

---

**Status**: 📋 Planned for Phase 3  
**Priority**: High  
**Estimated Effort**: 2-3 days  
**Dependencies**: None (can be built independently)
