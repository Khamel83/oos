#!/usr/bin/env python3
"""
agent-os-health.py - Health monitoring for Agent-OS integration

This script checks the health of all Agent-OS components and provides
detailed status information for monitoring and alerting.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class HealthChecker:
    """Main health checking class."""

    def __init__(self, project_dir: str = None, verbose: bool = False):
        self.project_dir = Path(project_dir or os.getcwd())
        self.verbose = verbose
        self.results = []

    def log(self, level: str, message: str, details: str = None) -> None:
        """Log a health check result."""
        result = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'details': details
        }
        self.results.append(result)

        if self.verbose or level in ['ERROR', 'WARNING']:
            prefix = {
                'INFO': '✓',
                'WARNING': '⚠',
                'ERROR': '✗'
            }.get(level, '?')
            print(f"{prefix} {message}")
            if details and self.verbose:
                print(f"  {details}")

    def check_directory_structure(self) -> bool:
        """Check if required directories exist."""
        success = True
        required_dirs = [
            '.agent-os',
            'data',
            'data/backups',
            'bin'
        ]

        for dir_path in required_dirs:
            full_path = self.project_dir / dir_path
            if full_path.exists():
                self.log('INFO', f"Directory exists: {dir_path}")
            else:
                self.log('WARNING', f"Missing directory: {dir_path}")
                success = False

        return success

    def check_configuration_files(self) -> bool:
        """Check if required configuration files exist."""
        success = True
        required_files = [
            '.agent-os/AGENT.md',
            '.agent-os/PREFERRED_STACK.md',
            '.agent-os/MIRROR_CONTRACT.md',
            '.agent-os/RUNBOOK.md'
        ]

        optional_files = [
            '.env',
            '.env.template'
        ]

        for file_path in required_files:
            full_path = self.project_dir / file_path
            if full_path.exists():
                self.log('INFO', f"Configuration file exists: {file_path}")
            else:
                self.log('ERROR', f"Missing required file: {file_path}")
                success = False

        for file_path in optional_files:
            full_path = self.project_dir / file_path
            if full_path.exists():
                self.log('INFO', f"Optional file exists: {file_path}")
            else:
                self.log('WARNING', f"Optional file missing: {file_path}")

        return success

    def check_database(self) -> bool:
        """Check SQLite database health."""
        db_path = self.get_db_path()
        if not db_path:
            self.log('ERROR', "Database path not found")
            return False

        if not db_path.exists():
            self.log('WARNING', f"Database not initialized: {db_path}")
            return False

        try:
            # Test basic connectivity
            with sqlite3.connect(str(db_path), timeout=10) as conn:
                cursor = conn.cursor()

                # Check WAL mode
                cursor.execute("PRAGMA journal_mode;")
                journal_mode = cursor.fetchone()[0]
                if journal_mode.upper() == 'WAL':
                    self.log('INFO', "Database in WAL mode")
                else:
                    self.log('WARNING', f"Database not in WAL mode: {journal_mode}")

                # Check integrity
                cursor.execute("PRAGMA integrity_check;")
                integrity = cursor.fetchone()[0]
                if integrity == 'ok':
                    self.log('INFO', "Database integrity check passed")
                else:
                    self.log('ERROR', f"Database integrity issues: {integrity}")
                    return False

                # Check tables exist
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name IN ('projects', 'tasks', 'approvals', 'runs')
                """)
                tables = [row[0] for row in cursor.fetchall()]
                expected_tables = ['projects', 'tasks', 'approvals', 'runs']

                for table in expected_tables:
                    if table in tables:
                        self.log('INFO', f"Table exists: {table}")
                    else:
                        self.log('ERROR', f"Missing table: {table}")
                        return False

                # Check recent activity
                cursor.execute("SELECT COUNT(*) FROM tasks WHERE created_at > datetime('now', '-7 days')")
                recent_tasks = cursor.fetchone()[0]
                self.log('INFO', f"Tasks created in last 7 days: {recent_tasks}")

                return True

        except sqlite3.Error as e:
            self.log('ERROR', f"Database connection failed: {e}")
            return False

    def check_backups(self) -> bool:
        """Check backup status and health."""
        backup_dir = self.project_dir / 'data' / 'backups'
        if not backup_dir.exists():
            self.log('WARNING', "Backup directory does not exist")
            return False

        # Find backup files
        backup_files = list(backup_dir.glob('atlas_*.db'))
        if not backup_files:
            self.log('WARNING', "No backup files found")
            return False

        # Check most recent backup
        latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
        backup_age = datetime.now() - datetime.fromtimestamp(latest_backup.stat().st_mtime)

        if backup_age < timedelta(days=1):
            self.log('INFO', f"Recent backup found: {latest_backup.name}")
        elif backup_age < timedelta(days=7):
            self.log('WARNING', f"Backup is {backup_age.days} days old: {latest_backup.name}")
        else:
            self.log('ERROR', f"No recent backups found. Latest: {latest_backup.name}")
            return False

        # Check backup file integrity
        try:
            with sqlite3.connect(str(latest_backup), timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                integrity = cursor.fetchone()[0]
                if integrity == 'ok':
                    self.log('INFO', "Latest backup integrity verified")
                else:
                    self.log('ERROR', f"Backup integrity issues: {integrity}")
                    return False
        except sqlite3.Error as e:
            self.log('ERROR', f"Cannot verify backup integrity: {e}")
            return False

        return True

    def check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            data_dir = self.project_dir / 'data'
            if data_dir.exists():
                total, used, free = shutil.disk_usage(str(data_dir))
                free_gb = free / (1024**3)
                free_percent = (free / total) * 100

                if free_percent > 20:
                    self.log('INFO', f"Disk space OK: {free_gb:.1f}GB free ({free_percent:.1f}%)")
                elif free_percent > 10:
                    self.log('WARNING', f"Disk space low: {free_gb:.1f}GB free ({free_percent:.1f}%)")
                else:
                    self.log('ERROR', f"Disk space critical: {free_gb:.1f}GB free ({free_percent:.1f}%)")
                    return False
            return True
        except Exception as e:
            self.log('WARNING', f"Could not check disk space: {e}")
            return True

    def check_environment(self) -> bool:
        """Check environment configuration."""
        env_file = self.project_dir / '.env'
        if not env_file.exists():
            self.log('WARNING', "No .env file found")
            return False

        # Load environment variables
        env_vars = {}
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            self.log('ERROR', f"Could not read .env file: {e}")
            return False

        # Check required variables
        required_vars = [
            'ATLAS_DB_PATH',
            'ARCHON_URL',
            'ARCHON_PROJECT_ID'
        ]

        success = True
        for var in required_vars:
            if var in env_vars and env_vars[var] not in ['', 'your_value_here']:
                self.log('INFO', f"Environment variable set: {var}")
            else:
                self.log('WARNING', f"Environment variable not set: {var}")
                success = False

        return success

    def check_archon_connectivity(self) -> bool:
        """Check connectivity to Archon MCP server."""
        try:
            import requests

            # Get Archon URL from environment
            env_file = self.project_dir / '.env'
            archon_url = None

            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.startswith('ARCHON_URL='):
                            archon_url = line.split('=', 1)[1].strip()
                            break

            if not archon_url or archon_url == 'your_archon_url_here':
                self.log('WARNING', "Archon URL not configured")
                return False

            # Test connectivity
            response = requests.get(f"{archon_url}/health", timeout=10)
            if response.status_code == 200:
                self.log('INFO', f"Archon server accessible: {archon_url}")
                return True
            else:
                self.log('WARNING', f"Archon server returned {response.status_code}: {archon_url}")
                return False

        except ImportError:
            self.log('WARNING', "requests library not available, skipping Archon connectivity check")
            return True
        except Exception as e:
            self.log('WARNING', f"Could not check Archon connectivity: {e}")
            return False

    def get_db_path(self) -> Optional[Path]:
        """Get database path from environment or default."""
        env_file = self.project_dir / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith('ATLAS_DB_PATH='):
                        path = line.split('=', 1)[1].strip()
                        if not os.path.isabs(path):
                            path = self.project_dir / path
                        return Path(path)

        # Default path
        return self.project_dir / 'data' / 'atlas.db'

    def run_all_checks(self) -> bool:
        """Run all health checks and return overall status."""
        checks = [
            ('Directory Structure', self.check_directory_structure),
            ('Configuration Files', self.check_configuration_files),
            ('Database Health', self.check_database),
            ('Backup Status', self.check_backups),
            ('Disk Space', self.check_disk_space),
            ('Environment Config', self.check_environment),
            ('Archon Connectivity', self.check_archon_connectivity),
        ]

        overall_success = True
        for check_name, check_func in checks:
            if self.verbose:
                print(f"\n--- {check_name} ---")

            try:
                success = check_func()
                if not success:
                    overall_success = False
            except Exception as e:
                self.log('ERROR', f"Check failed: {check_name}", str(e))
                overall_success = False

        return overall_success

    def get_summary(self) -> Dict:
        """Get summary of health check results."""
        error_count = sum(1 for r in self.results if r['level'] == 'ERROR')
        warning_count = sum(1 for r in self.results if r['level'] == 'WARNING')
        info_count = sum(1 for r in self.results if r['level'] == 'INFO')

        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if error_count == 0 else 'unhealthy',
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'total_checks': len(self.results),
            'results': self.results
        }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Check health of Agent-OS integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Check current directory
  %(prog)s --verbose          # Verbose output
  %(prog)s --json             # JSON output
  %(prog)s /path/to/project   # Check specific project
        """
    )

    parser.add_argument(
        'project_dir',
        nargs='?',
        help='Project directory to check (default: current directory)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Run health checks
    checker = HealthChecker(args.project_dir, args.verbose)
    success = checker.run_all_checks()
    summary = checker.get_summary()

    # Output results
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"\n--- Health Check Summary ---")
        print(f"Overall Status: {'✓ HEALTHY' if success else '✗ UNHEALTHY'}")
        print(f"Errors: {summary['error_count']}")
        print(f"Warnings: {summary['warning_count']}")
        print(f"Info: {summary['info_count']}")

        if not success:
            print("\nErrors found. Review the output above for details.")
            print("Run with --verbose for more information.")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()