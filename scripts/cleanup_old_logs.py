#!/usr/bin/env python3
"""
Clean up old performance logs from DreamHost server

Usage:
    python scripts/cleanup_old_logs.py           # Delete logs older than 90 days
    python scripts/cleanup_old_logs.py --days 30 # Delete logs older than 30 days
    python scripts/cleanup_old_logs.py --dry-run # Preview what would be deleted
"""

import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Clean up old performance logs')
    parser.add_argument('--days', type=int, default=90, help='Delete logs older than N days (default: 90)')
    parser.add_argument('--dry-run', action='store_true', help='Preview deletions without executing')
    args = parser.parse_args()

    # SSH connection details
    ssh_key = Path.home() / '.ssh' / 'id_ed25519_dreamhost'
    remote_host = 'rennie@iad1-shared-e1-05.dreamhost.com'
    remote_logs_dir = '~/rennie.org/logs'

    if not ssh_key.exists():
        print(f"❌ SSH key not found: {ssh_key}")
        return

    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=args.days)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')

    print(f"🧹 Cleaning up logs older than {args.days} days (before {cutoff_str})...")
    if args.dry_run:
        print("   (DRY RUN - no files will be deleted)")

    # List all log files on server
    cmd = ['ssh', '-i', str(ssh_key), remote_host, f'ls -1 {remote_logs_dir}/perf_*.jsonl 2>/dev/null || true']
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Failed to list files: {result.stderr}")
        return

    files = result.stdout.strip().split('\n')
    files = [f for f in files if f]  # Remove empty lines

    if not files:
        print("✅ No log files found on server")
        return

    # Filter files older than cutoff
    old_files = []
    for file in files:
        # Extract date from filename: perf_YYYY-MM-DD.jsonl
        try:
            filename = file.split('/')[-1]
            date_str = filename.replace('perf_', '').replace('.jsonl', '')
            file_date = datetime.strptime(date_str, '%Y-%m-%d')

            if file_date < cutoff_date:
                old_files.append(file)
        except ValueError:
            continue

    if not old_files:
        print(f"✅ No logs older than {args.days} days found")
        return

    print(f"\n📋 Found {len(old_files)} old log files:")
    for file in old_files:
        print(f"   - {file.split('/')[-1]}")

    if args.dry_run:
        print(f"\n✅ Dry run complete - would delete {len(old_files)} files")
        return

    # Delete old files
    print(f"\n🗑️  Deleting {len(old_files)} files...")
    for file in old_files:
        cmd = ['ssh', '-i', str(ssh_key), remote_host, f'rm {file}']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"   ✓ Deleted {file.split('/')[-1]}")
        else:
            print(f"   ✗ Failed to delete {file.split('/')[-1]}: {result.stderr}")

    print(f"\n✅ Cleanup complete - deleted {len(old_files)} old log files")


if __name__ == '__main__':
    main()
