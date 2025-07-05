"""
Test suite for continuation parser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.continuation_parser import ContinuationParser
import json

def test_basic_parsing():
    """Test basic continuation format parsing"""
    parser = ContinuationParser()
    
    # Test 1: Standard format
    content1 = """
    STATUS: WebSocket reconnection implementation
    POSITION: channel_manager.py:245 - reconnect()
    PROBLEM: Connection drops after 30s timeout
    TRIED: 
    - Simple setTimeout retry
    - Increasing timeout to 60s
    NEXT:
    - Implement exponential backoff
    - Add connection state tracking
    TODO:
    - Add error handling for network failures
    - Write unit tests for reconnection logic
    CONTEXT: This is part of the real-time data feature for LynnVest
    """
    
    result = parser.parse(content1)
    
    print("TEST 1: Standard Format")
    print("-" * 50)
    assert result['status'] == "WebSocket reconnection implementation"
    assert result['position']['file'] == "channel_manager.py"
    assert result['position']['line'] == 245
    assert result['position']['function'] == "reconnect"
    assert len(result['tried']) == 2
    assert len(result['next']) == 2  # "Implement exponential backoff" and "Add connection state tracking"
    assert len(result['todo']) == 2  # "Add error handling..." and "Write unit tests..."
    print("[PASS] All assertions passed")
    
    # Test 2: German keywords
    content2 = """
    WAS: Datenbank Schema Update
    WO: migration_v2.sql:15
    PROBLEM: Foreign Key Constraint fehlt
    VERSUCHT: Manual ALTER TABLE
    NÄCHSTE: Constraint mit CASCADE hinzufügen
    """
    
    result2 = parser.parse(content2)
    
    print("\nTEST 2: German Keywords")
    print("-" * 50)
    assert result2['status'] == "Datenbank Schema Update"
    assert result2['position']['file'] == "migration_v2.sql"
    assert result2['position']['line'] == 15
    assert result2['problem'] == "Foreign Key Constraint fehlt"
    print("[PASS] German keywords work correctly")
    
    # Test 3: Minimal format
    content3 = """
    Working on API endpoints
    POSITION: api/routes.py
    TODO: Add authentication
    """
    
    result3 = parser.parse(content3)
    
    print("\nTEST 3: Minimal Format")
    print("-" * 50)
    assert result3['status'] == "Working on API endpoints"
    assert result3['position']['file'] == "api/routes.py"
    assert 'line' not in result3['position']
    assert result3['todo'] == ["Add authentication"]
    print("[PASS] Minimal format handled correctly")
    
    # Test 4: Display format (without unicode)
    print("\nTEST 4: Display Format")
    print("-" * 50)
    display = parser.format_for_display(result)
    print(display.encode('ascii', 'replace').decode('ascii'))
    print("[PASS] Display format generated")
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    test_basic_parsing()
