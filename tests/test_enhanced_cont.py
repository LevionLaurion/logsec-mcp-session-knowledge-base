"""
Test for enhanced lo_cont functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logsec_core_v3 import LogSecCore
from pathlib import Path
import tempfile
import shutil

def test_enhanced_lo_cont():
    """Test the enhanced lo_cont function"""
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_logsec.db"
        
        # Initialize LogSec
        logsec = LogSecCore()
        logsec.db_path = db_path
        logsec._ensure_database()
        
        print("Testing enhanced lo_cont functionality...")
        print("=" * 50)
        
        # Test 1: Basic lo_cont
        print("\n1. Testing basic lo_cont:")
        result = logsec.lo_cont("test_project")
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', '')}")
        
        # Test 2: lo_cont with mode
        print("\n2. Testing lo_cont with debug mode:")
        result = logsec.lo_cont("test_project", "debug")
        print(f"Mode: {result.get('mode')}")
        print(f"Saved data: {result.get('continuation_saved', {})}")
        
        # Test 3: lo_start after lo_cont
        print("\n3. Testing lo_start after lo_cont:")
        start_result = logsec.lo_start("test_project")
        print(f"Source: {start_result.get('source', 'unknown')}")
        
        # Test 4: Error handling
        print("\n4. Testing error handling:")
        error_result = logsec.lo_cont("")
        print(f"Error: {error_result.get('error', 'No error')}")
        
        print("\n" + "=" * 50)
        print("✅ Enhanced lo_cont tests completed!")
        
        # Test formatting
        print("\n5. Testing output formatting:")
        formatted = logsec._format_cont_output(result)
        print(formatted)


if __name__ == "__main__":
    test_enhanced_lo_cont()