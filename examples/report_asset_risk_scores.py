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
    parser = argparse.ArgumentParser(description='Report on asset risk scores.')
    parser.add_argument('--secrets-file', help='Path to the secrets file (only required if .env not found in working directory)')
    parser.add_argument('--asset-version-id', help='Specific asset version ID to analyze')
    parser.add_argument('--csv', nargs='?', const='asset_risk_scores.csv', help='Export the report to a CSV file (default: asset_risk_scores.csv)')
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

    if args.asset_version_id:
        # Analyze specific asset version
        print(f"\nAnalyzing asset version {args.asset_version_id}...")
        
        try:
            # Get asset version details
            asset_versions = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)
            if not asset_versions:
                print(f"No asset version found with ID {args.asset_version_id}")
                return
                
            asset_version = asset_versions[0]  # Get the first (and should be only) result
            asset = asset_version.get('asset', {})
            group_name = asset.get('group', {}).get('name', 'N/A')
            
            # Extract risk score
            risk_score = asset_version.get('relativeRiskScore', 'N/A')
            
            # Print results
            print("\nAsset Risk Score:")
            print("-" * 50)
            print(f"Asset Name: {asset.get('name', 'N/A')}")
            print(f"Group: {group_name}")
            print(f"Version: {asset_version.get('name', 'N/A')}")
            print(f"Risk Score: {risk_score}")
                
        except Exception as e:
            print(f"Error analyzing asset version: {str(e)}")
            
    else:
        # Get all asset versions
        print("\nFetching asset versions...")
        asset_versions = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT)
        
        print(f"\nFound {len(asset_versions)} asset versions to analyze")
        print("\nAsset Risk Score Analysis:")
        print("-" * 100)
        print(f"{'Asset Name':<30} {'Group':<15} {'Version':<20} {'Risk Score':<10}")
        print("-" * 100)
        
        # Prepare data for CSV export
        csv_data = [['Asset Name', 'Group', 'Version', 'Risk Score']]
        
        for asset_version in asset_versions:
            asset = asset_version.get('asset', {})
            asset_name = asset.get('name', 'N/A')
            group_name = asset.get('group', {}).get('name', 'N/A')
            version_name = asset_version.get('name', 'N/A')
            risk_score = asset_version.get('relativeRiskScore', 'N/A')
            
            # Print results
            print(f"{asset_name or 'N/A':<30} {group_name or 'N/A':<15} {version_name or 'N/A':<20} {risk_score or 'N/A':<10}")
            
            # Add data for CSV
            csv_data.append([asset_name or 'N/A', group_name or 'N/A', version_name or 'N/A', risk_score or 'N/A'])
        
        # Export to CSV if requested
        if args.csv:
            with open(args.csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)
            print(f"\nReport exported to {args.csv}")

if __name__ == '__main__':
    main() 