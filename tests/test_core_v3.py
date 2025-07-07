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
    
    # Fixed: Check for 'response' key instead of 'status'
    if 'response' in result:
        print("Save successful!")
        print(f"Response: {result['response']}")
        return True
    elif 'error' in result:
        print(f"Error: {result['error']}")
        return False
    else:
        print(f"Unexpected result: {result}")
        return False


def test_lo_load():
    """Test loading project knowledge"""
    print("\n=== Testing lo_load ===")
    
    core = LogSecCore()
    
    # Fixed: lo_load requires project_name parameter
    result = core.lo_load(project_name="test_project")
    
    if 'response' in result:
        print("Load successful!")
        print(f"Response: {result['response']}")
        return True
    elif 'error' in result:
        print(f"Error: {result['error']}")
        return False
    else:
        print(f"Unexpected result: {result}")
        return False

def test_lo_cont():
    """Test continuation parsing"""
    print("\n=== Testing lo_cont ===")
    
    core = LogSecCore()
    
    # Fixed: lo_cont expects project_name and mode parameters
    result = core.lo_cont(
        project_name="test_project",
        mode="auto"
    )
    
    if 'response' in result:
        print("Continuation created successfully!")
        print(f"Response: {result['response']}")
        return True
    elif 'error' in result:
        print(f"Error: {result['error']}")
        return False
    else:
        print(f"Unexpected result: {result}")
        return False


def test_mcp_protocol():
    """Test MCP protocol handling"""
    print("\n=== Testing MCP Protocol ===")
    
    # This test should work as is, but let's make it more robust
    core = LogSecCore()
    
    # Test initialize
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test_client",
                "version": "1.0.0"
            }
        },
        "id": 0
    }
    
    init_response = core.handle_request(init_request)
    print(f"Initialize response: {init_response}")
    
    # Test tools/list
    list_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    list_response = core.handle_request(list_request)
    print(f"Available tools: {len(list_response.get('result', {}).get('tools', []))}")
    
    # Test tools/call
    call_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "logsec:lo_save",
            "arguments": {
                "content": "Test content for MCP",
                "project_name": "mcp_test"
            }
        },
        "id": 2
    }
    
    call_response = core.handle_request(call_request)
    print(f"MCP call response: {call_response}")
    
    # Check if we got a valid response
    if 'result' in call_response:
        return True
    else:
        return False


if __name__ == "__main__":
    # Run individual tests
    tests = [
        ("Save functionality", test_lo_save),
        ("Load functionality", test_lo_load),
        ("Continuation functionality", test_lo_cont),
        ("MCP protocol", test_mcp_protocol)
    ]
    
    print("[TEST] LogSec Core v3 Test Suite")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                print(f"\n[PASS] {name}: PASSED")
                passed += 1
            else:
                print(f"\n[FAIL] {name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"\n[ERROR] {name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    # Exit with proper code for CI/CD
    sys.exit(0 if failed == 0 else 1)