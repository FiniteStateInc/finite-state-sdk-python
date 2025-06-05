#!/usr/bin/env python3

import argparse
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import finite_state_sdk

def parse_args():
    parser = argparse.ArgumentParser(description='Report on vulnerabilities per asset version.')
    parser.add_argument('--secrets-file', help='Path to the secrets file (only required if .env not found in working directory)')
    parser.add_argument('--csv', nargs='?', const='vulnerabilities_over_time.csv', help='Export the report to a CSV file (default: vulnerabilities_over_time.csv)')
    parser.add_argument('--debug', action='store_true', help='Print debug information about the API response')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Try to load .env from working directory first
    if not args.secrets_file and os.path.exists('.env'):
        load_dotenv('.env')
    elif args.secrets_file:
        load_dotenv(args.secrets_file)
    else:
        print("Error: No .env file found in working directory and no --secrets-file specified")
        sys.exit(1)

    # Get environment variables
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    if not all([CLIENT_ID, CLIENT_SECRET, ORGANIZATION_CONTEXT]):
        print("Error: Missing required environment variables (CLIENT_ID, CLIENT_SECRET, ORGANIZATION_CONTEXT)")
        sys.exit(1)

    # Get an auth token
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)
    org_ctx = ORGANIZATION_CONTEXT

    # Get all asset versions using get_all_asset_versions
    asset_versions = finite_state_sdk.get_asset_versions(token, org_ctx)
    
    # Debug output
    if args.debug and asset_versions:
        print("\nDebug: First 3 asset versions raw data:")
        for i, asset_version in enumerate(asset_versions[:3]):
            print(f"\nAsset Version {i + 1}:")
            print(json.dumps(asset_version, indent=2))
    
    # Prepare data for CSV export
    csv_data = []
    total_vulnerabilities = 0
    
    print("\nVulnerabilities per asset version:")
    print("-" * 120)
    print(f"{'Asset Name':<30} {'Group':<10} {'Version':<30} {'Vulnerabilities':<15}")
    print("-" * 120)
    
    for asset_version in asset_versions:
        # Get asset information
        asset = asset_version.get('asset', {})
        asset_name = asset.get('name', 'N/A')
        group_name = asset.get('group', {}).get('name', 'N/A')
        version_name = asset_version.get('name', 'N/A')
        
        asset_version_id = asset_version.get('id')
        
        # Get vulnerability count for this asset version
        findings = finite_state_sdk.get_findings(
            token, 
            org_ctx,
            asset_version_id=asset_version_id,
            count=True
        )
        count = findings['count'] if isinstance(findings, dict) and 'count' in findings else findings
        
        # Print to console
        print(f"{asset_name:<30} {group_name:<10} {version_name:<30} {count:<15}")
        
        # Store for CSV
        csv_data.append({
            'Asset Name': asset_name,
            'Group': group_name,
            'Version': version_name,
            'Vulnerabilities': count
        })
        
        total_vulnerabilities += count
    
    print("-" * 120)
    print(f"\nTotal number of vulnerabilities across all assets: {total_vulnerabilities}")
    
    # Export to CSV if requested
    if args.csv:
        with open(args.csv, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['Asset Name', 'Group', 'Version', 'Vulnerabilities'])
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"\nReport exported to {args.csv}")

if __name__ == '__main__':
    main() 