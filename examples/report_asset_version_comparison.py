#!/usr/bin/env python3

import argparse
import os
import sys
from dotenv import load_dotenv
import csv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import finite_state_sdk

def parse_args():
    parser = argparse.ArgumentParser(description='Compare different versions of the same asset to identify improvements or regressions in security features and vulnerabilities.')
    parser.add_argument('--secrets-file', help='Path to the secrets file (only required if .env not found in working directory)')
    parser.add_argument('--csv', nargs='?', const='asset_version_comparison.csv', help='Export the report to a CSV file (default: asset_version_comparison.csv)')
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

    # Get all asset versions
    print("\nFetching asset versions...")
    asset_versions = finite_state_sdk.get_asset_versions(token, org_ctx)
    
    # Group asset versions by asset name
    asset_groups = {}
    for av in asset_versions:
        asset_name = av.get('asset', {}).get('name')
        if asset_name:
            if asset_name not in asset_groups:
                asset_groups[asset_name] = []
            asset_groups[asset_name].append(av)
    
    # Prepare data for CSV export (all assets)
    csv_data = [['Asset Name', 'Group', 'Version', 'Risk Score', 'Vulnerabilities']]

    # Compare versions for each asset
    for asset_name, versions in asset_groups.items():
        print(f"\nAnalyzing asset: {asset_name}")
        group_name = versions[0].get('asset', {}).get('group', {}).get('name', 'N/A')
        print(f"Group: {group_name}")
        
        for asset_version in versions:
            version_name = asset_version.get('name', 'N/A')
            risk_score = asset_version.get('relativeRiskScore', 'N/A')
            
            # Fetch vulnerabilities for this version
            try:
                findings = finite_state_sdk.get_findings(token, org_ctx, asset_version_id=asset_version.get('id'), count=True)
                vulnerability_count = findings['count'] if isinstance(findings, dict) and 'count' in findings else findings
            except Exception as e:
                print(f"Error fetching vulnerabilities for {asset_name} version {version_name}: {str(e)}")
                vulnerability_count = 0
            
            # Print results
            if version_name is not None and risk_score is not None and vulnerability_count is not None:
                print(f"{version_name:<20} {risk_score:<10} {vulnerability_count:<15}")
            else:
                print(f"Missing data for {asset_name} version {version_name}")
            
            # Add data for CSV (all assets)
            csv_data.append([asset_name, group_name, version_name, risk_score, vulnerability_count])
    
    # Export to CSV if requested (once, after all assets)
    if args.csv:
        with open(args.csv, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)
        print(f"\nReport exported to {args.csv}")

if __name__ == '__main__':
    main() 