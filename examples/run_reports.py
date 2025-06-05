#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from typing import List

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# List of all available reports
ALL_REPORTS = [
    'report_assets_over_time.py',
    'report_asset_risk_scores.py',
    'report_asset_version_comparison.py',
    'report_uploads_over_time.py',
    'report_vulnerabilities_over_time.py',
    'report_vulnerability_severity_trends.py'
]

# Reports to run by default (excluding vulnerability_severity_trends)
DEFAULT_REPORTS = [r for r in ALL_REPORTS if r != 'report_vulnerability_severity_trends.py']

def parse_args():
    parser = argparse.ArgumentParser(description='Run all or specified Finite State reports.')
    parser.add_argument('--secrets-file', help='Path to the secrets file (only required if .env not found in working directory)')
    parser.add_argument('--include-severity-trends', action='store_true', 
                       help='Include the vulnerability severity trends report (excluded by default due to long runtime)')
    parser.add_argument('--reports', nargs='+', choices=ALL_REPORTS,
                       help='Specific reports to run (if not specified, runs all default reports)')
    parser.add_argument('--no-csv', action='store_true',
                       help='Disable CSV output (enabled by default)')
    parser.add_argument('--output-dir', help='Directory to save CSV output files (default: current directory)')
    return parser.parse_args()

def run_report(report: str, secrets_file: str = None, csv: bool = True, output_dir: str = None) -> bool:
    """Run a single report and return True if successful."""
    print(f"\n{'='*80}")
    print(f"Running {report}...")
    print(f"{'='*80}\n")
    
    # Get absolute path to the report script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, report)
    
    # Build the command
    cmd = [sys.executable, report_path]
    
    # Add secrets file if provided
    if secrets_file:
        # Convert secrets file path to absolute path if it's not already
        if not os.path.isabs(secrets_file):
            secrets_file = os.path.abspath(secrets_file)
        cmd.extend(['--secrets-file', secrets_file])
    
    # Add CSV flag if enabled
    if csv:
        # Get the base name of the report without .py extension
        report_base = os.path.splitext(report)[0]
        csv_filename = f"{report_base}.csv"
        
        # If output directory is specified, create it if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            # Change to the output directory before running the report
            original_dir = os.getcwd()
            os.chdir(output_dir)
            cmd.extend(['--csv', csv_filename])
        else:
            cmd.extend(['--csv', csv_filename])
    
    try:
        # Run the report
        result = subprocess.run(cmd, check=True, text=True)
        print(f"\n{report} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError running {report}:")
        print(e)
        return False
    except Exception as e:
        print(f"\nUnexpected error running {report}:")
        print(e)
        return False
    finally:
        # Change back to original directory if we changed it
        if output_dir and csv:
            os.chdir(original_dir)

def main():
    args = parse_args()
    
    # Determine which reports to run
    reports_to_run = args.reports if args.reports else DEFAULT_REPORTS
    
    # Add severity trends if requested
    if args.include_severity_trends and 'report_vulnerability_severity_trends.py' not in reports_to_run:
        reports_to_run.append('report_vulnerability_severity_trends.py')
    
    # Print summary
    print("\nReports to run:")
    for report in reports_to_run:
        print(f"  - {report}")
    print(f"\nCSV output: {'enabled' if not args.no_csv else 'disabled'}")
    if args.output_dir:
        print(f"Output directory: {args.output_dir}")
    if args.secrets_file:
        print(f"Using secrets file: {args.secrets_file}")
    else:
        # Check for .env in current directory
        if os.path.exists('.env'):
            args.secrets_file = os.path.abspath('.env')
            print(f"Using .env file from current directory: {args.secrets_file}")
    print()
    
    # Run each report
    successful = 0
    failed = 0
    
    for report in reports_to_run:
        if run_report(report, args.secrets_file, not args.no_csv, args.output_dir):
            successful += 1
        else:
            failed += 1
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Report execution summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(reports_to_run)}")
    print(f"{'='*80}\n")
    
    # Exit with error if any reports failed
    if failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main() 