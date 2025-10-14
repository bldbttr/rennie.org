#!/usr/bin/env python3
"""
Performance Log Analyzer

Downloads and analyzes performance logs from rennie.org to identify
timing patterns, bottlenecks, and UX issues.

Usage:
    python scripts/analyze_logs.py                    # Analyze today's logs
    python scripts/analyze_logs.py --date 2025-10-13  # Analyze specific date
    python scripts/analyze_logs.py --all              # Analyze all available logs
"""

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import statistics


class LogAnalyzer:
    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(exist_ok=True)

    def download_logs(self, date: str = None):
        """Download logs from server using rsync or scp."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        log_filename = f"perf_{date}.jsonl"

        # DreamHost connection details (matching deploy.yml)
        ssh_key = Path.home() / '.ssh' / 'id_ed25519_dreamhost'
        remote_host = 'rennie@iad1-shared-e1-05.dreamhost.com'
        remote_path = f'{remote_host}:~/rennie.org/logs/{log_filename}'
        local_path = self.logs_dir / log_filename

        print(f"📥 Downloading logs for {date}...")

        try:
            # Check if SSH key exists
            if not ssh_key.exists():
                print(f"❌ SSH key not found: {ssh_key}")
                print("   Please configure SSH access to DreamHost")
                return None

            # Try using scp with SSH key
            result = subprocess.run(
                ['scp', '-i', str(ssh_key), remote_path, str(local_path)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"✅ Downloaded to {local_path}")
                return local_path
            else:
                print(f"❌ Failed to download: {result.stderr}")
                return None

        except FileNotFoundError:
            print("❌ scp not found. Please install SSH tools.")
            print("   You can also manually download logs:")
            print(f"   scp -i {ssh_key} {remote_path} {local_path}")
            return None

    def load_logs(self, log_file: Path) -> List[Dict[str, Any]]:
        """Load JSONL log file."""
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return []

        logs = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        return logs

    def group_by_session(self, logs: List[Dict]) -> Dict[str, List[Dict]]:
        """Group logs by session ID."""
        sessions = defaultdict(list)
        for log in logs:
            session_id = log.get('sessionId', 'unknown')
            sessions[session_id].append(log)

        # Sort each session by relativeTime
        for session_id in sessions:
            sessions[session_id].sort(key=lambda x: x.get('relativeTime', 0))

        return sessions

    def analyze_session(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze a single session."""
        if not logs:
            return {}

        # Extract key metrics
        app_init = next((l for l in logs if l['event'] == 'app_init_start'), None)
        app_complete = next((l for l in logs if l['event'] == 'app_init_complete'), None)

        # Image load times
        image_loads = [l for l in logs if l['event'] in ['carousel_initial_image_loaded', 'single_image_loaded']]
        image_durations = [l.get('duration', 0) for l in image_loads if 'duration' in l]

        # Carousel transitions
        transitions = [l for l in logs if l['event'] == 'carousel_transition_complete']

        # Quote transitions
        quote_transitions = [l for l in logs if l['event'] == 'quote_transition_start']

        # Cache status
        cache_status = logs[0].get('cacheStatus', 'unknown')

        return {
            'sessionId': logs[0].get('sessionId', 'unknown'),
            'cacheStatus': cache_status,
            'totalEvents': len(logs),
            'duration': logs[-1].get('relativeTime', 0) if logs else 0,
            'appInitTime': app_complete['relativeTime'] - app_init['relativeTime'] if app_init and app_complete else None,
            'imageLoads': {
                'count': len(image_loads),
                'durations': image_durations,
                'avgDuration': statistics.mean(image_durations) if image_durations else 0,
                'maxDuration': max(image_durations) if image_durations else 0,
                'minDuration': min(image_durations) if image_durations else 0,
            },
            'transitions': {
                'carousel': len(transitions),
                'quotes': len(quote_transitions),
            }
        }

    def print_summary(self, sessions: Dict[str, List[Dict]]):
        """Print analysis summary."""
        print(f"\n{'='*80}")
        print(f"📊 PERFORMANCE LOG ANALYSIS")
        print(f"{'='*80}\n")

        print(f"Total Sessions: {len(sessions)}")

        # Analyze each session
        all_stats = []
        for session_id, logs in sessions.items():
            stats = self.analyze_session(logs)
            if stats:
                all_stats.append(stats)

        if not all_stats:
            print("No valid sessions found.")
            return

        # Group by cache status
        cached_sessions = [s for s in all_stats if s['cacheStatus'] == 'cached']
        network_sessions = [s for s in all_stats if s['cacheStatus'] == 'network']

        print(f"\n🔵 NETWORK LOADS (First-time visitors)")
        print(f"   Sessions: {len(network_sessions)}")
        if network_sessions:
            avg_init = statistics.mean([s['appInitTime'] for s in network_sessions if s['appInitTime']])
            avg_img = statistics.mean([s['imageLoads']['avgDuration'] for s in network_sessions if s['imageLoads']['avgDuration'] > 0])
            print(f"   Avg App Init: {avg_init:.0f}ms")
            print(f"   Avg Image Load: {avg_img:.0f}ms")

        print(f"\n🟢 CACHED LOADS (Returning visitors)")
        print(f"   Sessions: {len(cached_sessions)}")
        if cached_sessions:
            avg_init = statistics.mean([s['appInitTime'] for s in cached_sessions if s['appInitTime']])
            avg_img = statistics.mean([s['imageLoads']['avgDuration'] for s in cached_sessions if s['imageLoads']['avgDuration'] > 0])
            print(f"   Avg App Init: {avg_init:.0f}ms")
            print(f"   Avg Image Load: {avg_img:.0f}ms")

        # Detailed session breakdown
        print(f"\n{'─'*80}")
        print(f"📋 SESSION DETAILS\n")

        for i, stats in enumerate(all_stats, 1):
            cache_emoji = "🟢" if stats['cacheStatus'] == 'cached' else "🔵"
            print(f"{cache_emoji} Session {i}: {stats['sessionId'][:20]}...")
            print(f"   Status: {stats['cacheStatus']}")
            print(f"   Duration: {stats['duration']:.0f}ms")
            if stats['appInitTime']:
                print(f"   App Init: {stats['appInitTime']:.0f}ms")
            print(f"   Images Loaded: {stats['imageLoads']['count']}")
            if stats['imageLoads']['count'] > 0:
                print(f"   Image Load Times: avg={stats['imageLoads']['avgDuration']:.0f}ms, "
                      f"max={stats['imageLoads']['maxDuration']:.0f}ms, "
                      f"min={stats['imageLoads']['minDuration']:.0f}ms")
            print(f"   Transitions: {stats['transitions']['carousel']} carousel, {stats['transitions']['quotes']} quotes")
            print()

        # Find slow sessions
        slow_sessions = [s for s in all_stats if s['imageLoads']['maxDuration'] > 500]
        if slow_sessions:
            print(f"\n⚠️  SLOW IMAGE LOADS (>500ms)")
            for s in slow_sessions:
                print(f"   Session {s['sessionId'][:20]}... - Max load: {s['imageLoads']['maxDuration']:.0f}ms ({s['cacheStatus']})")

        print(f"\n{'='*80}\n")

    def run(self, date: str = None, download: bool = True):
        """Run the analysis."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        log_file = self.logs_dir / f"perf_{date}.jsonl"

        # Download if requested
        if download:
            downloaded = self.download_logs(date)
            if downloaded:
                log_file = downloaded
            else:
                print(f"ℹ️  Analyzing local logs only...")

        # Load and analyze
        logs = self.load_logs(log_file)
        if not logs:
            print(f"No logs found for {date}")
            return

        sessions = self.group_by_session(logs)
        self.print_summary(sessions)


def main():
    parser = argparse.ArgumentParser(description='Analyze performance logs')
    parser.add_argument('--date', help='Date to analyze (YYYY-MM-DD)', default=None)
    parser.add_argument('--local-only', action='store_true', help='Skip download, analyze local logs only')
    args = parser.parse_args()

    # Set up paths
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / 'logs'

    # Run analysis
    analyzer = LogAnalyzer(logs_dir)
    analyzer.run(date=args.date, download=not args.local_only)


if __name__ == '__main__':
    main()
