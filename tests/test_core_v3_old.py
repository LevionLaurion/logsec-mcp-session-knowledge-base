import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
from logsec_core_v3 import LogSecCore

def test_lo_save():
    """Test saving with auto-tagging and classification"""
    print("\n=== Testing lo_save ===")
    
    core = LogSecCore()
    
    # Test content with clear knowledge type
    test_content = """
# API Documentation for UserService

## Endpoints

### GET /api/users/{id}
Returns user details by ID.

**Parameters:**
- id (integer): User ID

**Response:**
```json
{
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
}
```

### POST /api/users
Creates a new user.

**Request Body:**
```json
{
    "name": "string",
    "email": "string"
}
```
"""
    
    result = core.lo_save(
        content=test_content,
        project_name="test_project",
        session_id="test_api_doc_001"
    )
    
    print(f"Status: {result['status']}")
    print(f"Session ID: {result['session_id']}")
    print(f"Knowledge Type: {result['knowledge_type']} (confidence: {result['confidence']:.2f})")
    print(f"Tags: {', '.join(result['tags'])}")
    print(f"Saved to: {result.get('filepath', 'N/A')}")
    
    return result['status'] == 'success'


def test_lo_load():
    """Test loading project knowledge"""
    print("\n=== Testing lo_load ===")
    
    core = LogSecCore()
    
    # Load without project (general)
    result = core.lo_load()
    
    print(f"Status: {result['status']}")
    print(f"Recent sessions: {len(result['recent_sessions'])}")
    
    if result['recent_sessions']:
        print("\nLatest sessions:")
        for session in result['recent_sessions'][:3]:
            print(f"  - {session['session_id']} ({session['knowledge_type']}) - {session['project']}")
    
    print(f"\nStats: {json.dumps(result['stats'], indent=2)}")
    
    # Load specific project
    print("\n--- Loading test_project ---")
    result = core.lo_load("test_project")
    
    print(f"Project: {result['project']}")
    print(f"Sessions found: {len(result['recent_sessions'])}")
    
    return result['status'] == 'success'


def test_lo_cont():
    """Test continuation parsing"""
    print("\n=== Testing lo_cont ===")
    
    core = LogSecCore()
    
    # Test German continuation
    test_query = """
STATUS: API Documentation fertig
POSITION: UserService dokumentiert
NEXT: ProductService API dokumentieren
TODO:
- Endpoints definieren
- Response schemas erstellen
- Beispiele hinzufügen
CONTEXT: Microservices API Dokumentation
"""
    
    result = core.lo_cont(test_query, "de")
    
    print(f"Status: {result['status']}")
    print(f"Parsed elements:")
    for key, value in result['parsed'].items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    
    print(f"\nRelevant sessions found: {len(result['context']['relevant_sessions'])}")
    print(f"\nContinuation prompt:")
    print(result['prompt'])
    
    return result['status'] == 'success'


def test_mcp_protocol():
    """Test MCP protocol handling"""
    print("\n=== Testing MCP Protocol ===")
    
    core = LogSecCore()
    
    # Test tools/list
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    response = core.handle_mcp_request(request)
    print(f"Available tools: {len(response.get('tools', []))}")
    for tool in response.get('tools', []):
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test tools/call
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "lo_save",
            "arguments": {
                "content": "Test content for MCP",
                "project_name": "mcp_test"
            }
        },
        "id": 2
    }
    
    response = core.handle_mcp_request(request)
    print(f"\nMCP call result: {response.get('result', {}).get('status', 'error')}")
    
    return 'error' not in response


def main():
    """Run all tests"""
    print("[TEST] LogSec Core v3 Test Suite")
    print("=" * 50)
    
    tests = [
        ("Save with auto-tagging", test_lo_save),
        ("Load project knowledge", test_lo_load),
        ("Parse continuation", test_lo_cont),
        ("MCP protocol", test_mcp_protocol)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                print(f"\n[OK] {name}: PASSED")
                passed += 1
            else:
                print(f"\n[FAIL] {name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"\n[ERROR] {name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"[STATS] Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed! LogSec Core v3 is ready!")
    else:
        print("\n[WARNING] Some tests failed. Please check the output above.")


if __name__ == "__main__":
    main()
