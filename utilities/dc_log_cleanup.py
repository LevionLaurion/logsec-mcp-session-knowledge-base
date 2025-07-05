"""
Desktop Commander Log Cleanup Tool
Helps manage privacy by cleaning Desktop Commander logs

Author: LogSec Team
License: Same as LogSec (Proprietary)
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# Log directory location
LOG_DIR = Path.home() / ".claude-server-commander-logs"

def get_log_stats():
    """Get statistics about log files"""
    if not LOG_DIR.exists():
        return None
    
    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        return None
    
    total_size = sum(f.stat().st_size for f in log_files)
    oldest = min(f.stat().st_mtime for f in log_files)
    newest = max(f.stat().st_mtime for f in log_files)
    
    return {
        "count": len(log_files),
        "total_size_mb": total_size / (1024 * 1024),
        "oldest": datetime.fromtimestamp(oldest),
        "newest": datetime.fromtimestamp(newest)
    }

def clean_logs(days_to_keep=7, dry_run=True):
    """Clean logs older than specified days"""
    if not LOG_DIR.exists():
        print("No log directory found.")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    log_files = list(LOG_DIR.glob("*.log"))
    
    files_to_delete = []
    size_to_free = 0
    
    for log_file in log_files:
        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        if file_time < cutoff_date:
            files_to_delete.append(log_file)
            size_to_free += log_file.stat().st_size
    
    if dry_run:
        print(f"\n[DRY RUN] Would delete {len(files_to_delete)} files")
        print(f"Would free up {size_to_free / (1024*1024):.2f} MB")
        if files_to_delete:
            print("\nFiles to delete:")
            for f in files_to_delete[:10]:  # Show first 10
                print(f"  - {f.name}")
            if len(files_to_delete) > 10:
                print(f"  ... and {len(files_to_delete) - 10} more")
    else:
        print(f"\nDeleting {len(files_to_delete)} files...")
        for f in files_to_delete:
            try:
                f.unlink()
            except Exception as e:
                print(f"Error deleting {f.name}: {e}")
        print(f"Freed up {size_to_free / (1024*1024):.2f} MB")

def archive_logs(output_dir="dc_logs_archive"):
    """Archive all logs to a specified directory"""
    if not LOG_DIR.exists():
        print("No log directory found.")
        return
    
    archive_path = Path(output_dir)
    archive_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_subdir = archive_path / f"logs_{timestamp}"
    
    print(f"Archiving logs to {archive_subdir}")
    shutil.copytree(LOG_DIR, archive_subdir)
    print("Archive complete!")

def main():
    parser = argparse.ArgumentParser(
        description="Desktop Commander Log Cleanup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dc_log_cleanup.py --stats           # Show log statistics
  python dc_log_cleanup.py --clean           # Dry run (show what would be deleted)
  python dc_log_cleanup.py --clean --execute # Actually delete old logs
  python dc_log_cleanup.py --archive         # Archive all logs
  python dc_log_cleanup.py --clean --days 30 # Keep only last 30 days
        """
    )
    
    parser.add_argument("--stats", action="store_true", 
                        help="Show log statistics")
    parser.add_argument("--clean", action="store_true",
                        help="Clean old log files")
    parser.add_argument("--archive", action="store_true",
                        help="Archive all logs before cleaning")
    parser.add_argument("--days", type=int, default=7,
                        help="Days of logs to keep (default: 7)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually perform deletions (default is dry run)")
    
    args = parser.parse_args()
    
    print("Desktop Commander Log Cleanup Tool")
    print("=" * 40)
    print(f"Log directory: {LOG_DIR}")
    
    # Always show stats first
    stats = get_log_stats()
    if stats:
        print(f"\nCurrent status:")
        print(f"  Files: {stats['count']}")
        print(f"  Size: {stats['total_size_mb']:.2f} MB")
        print(f"  Oldest: {stats['oldest'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Newest: {stats['newest'].strftime('%Y-%m-%d %H:%M')}")
    else:
        print("\nNo log files found.")
        return
    
    # Perform requested actions
    if args.archive:
        archive_logs()
    
    if args.clean:
        clean_logs(days_to_keep=args.days, dry_run=not args.execute)
    
    if not (args.stats or args.clean or args.archive):
        print("\nUse --help to see available options")

if __name__ == "__main__":
    main()
