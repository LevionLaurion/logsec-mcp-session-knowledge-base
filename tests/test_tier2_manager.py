"""
Test suite for Tier 2 README Manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tier2_manager import Tier2Manager
import tempfile
import shutil

def test_tier2_functionality():
    """Test Tier 2 README management"""
    
    # Create temporary directory for test database
    test_dir = tempfile.mkdtemp()
    
    try:
        tier2 = Tier2Manager(base_path=test_dir)
        
        print("TEST 1: Create README")
        print("-" * 50)
        
        # Test content
        content = """LynnVest is a 3D financial visualization system.

## Features
- Real-time market data
- 3D portfolio view
- WebSocket streaming"""
        
        # Create README
        success = tier2.create_readme("lynnvest", content)
        assert success == True
        print("[PASS] README created")
        
        # Try to create again (should fail)
        success = tier2.create_readme("lynnvest", "duplicate")
        assert success == False
        print("[PASS] Duplicate prevention works")
        
        print("\nTEST 2: Read README")
        print("-" * 50)
        
        readme = tier2.get_readme("lynnvest")
        assert readme is not None
        assert readme['project'] == 'lynnvest'
        assert readme['version'] == '1.0'
        assert readme['update_count'] == 0
        assert '3D financial visualization' in readme['content']
        print("[PASS] README retrieved correctly")
        
        print("\nTEST 3: Update README")
        print("-" * 50)
        
        updated_content = content + "\n\n## Updates\n- Fixed WebSocket timeout"
        success = tier2.update_readme("lynnvest", updated_content, "Added timeout fix")
        assert success == True
        
        readme = tier2.get_readme("lynnvest")
        assert readme['version'] == '1.1'
        assert readme['update_count'] == 1
        assert 'Fixed WebSocket timeout' in readme['content']
        print("[PASS] README updated to version 1.1")
        
        print("\nTEST 4: README History")
        print("-" * 50)
        
        history = tier2.get_readme_history("lynnvest")
        assert len(history) == 2  # Initial + update
        assert history[0]['version'] == '1.1'
        assert history[0]['reason'] == 'Added timeout fix'
        assert history[1]['version'] == '1.0'
        assert history[1]['reason'] == 'Initial creation'
        print("[PASS] History tracking works")
        
        print("\nTEST 5: List Projects")
        print("-" * 50)
        
        # Add another project
        tier2.create_readme("logsec", "Knowledge management system")
        
        projects = tier2.list_projects()
        assert len(projects) == 2
        project_names = [p['project'] for p in projects]
        assert 'lynnvest' in project_names
        assert 'logsec' in project_names
        print("[PASS] Project listing works")
        
        print("\nTEST 6: Template Application")
        print("-" * 50)
        
        tier2.create_readme("testproject", "A test project", template="minimal")
        readme = tier2.get_readme("testproject")
        assert '# TESTPROJECT' in readme['content']
        assert 'Description' in readme['content']
        assert 'A test project' in readme['content']
        print("[PASS] Template application works")
        
        print("\nTEST 7: Display Format")
        print("-" * 50)
        
        display = tier2.format_readme_display("lynnvest")
        # Remove unicode for testing
        display_ascii = display.encode('ascii', 'replace').decode('ascii')
        assert 'PROJECT README: LYNNVEST' in display_ascii
        assert 'Version: 1.1' in display_ascii
        assert 'Update Count: 1' in display_ascii
        print("[PASS] Display format works")
        print("\nSample output:")
        print(display_ascii[:300] + "...")
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_tier2_functionality()
