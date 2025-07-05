#!/usr/bin/env python
"""
LogSec MCP Server Entry Point
This ensures proper initialization when started by Claude
"""

import sys
import os
from pathlib import Path

# Add LogSec to path
sys.path.insert(0, str(Path(__file__).parent))

# Change to LogSec directory
os.chdir(Path(__file__).parent)

# Import and run
if __name__ == "__main__":
    try:
        # This will trigger database initialization
        from logsec_core import main
        import asyncio
        
        print("[LogSec] Starting MCP Server...")
        print("[LogSec] Base directory:", os.getcwd())
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n[LogSec] Shutdown requested")
    except Exception as e:
        print(f"[LogSec] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
