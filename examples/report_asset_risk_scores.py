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
    parser.add_argument('--secrets-file', required=True, help='Path to the secrets file')
    parser.add_argument('--asset-version-id', help='Specific asset version ID to analyze')
    parser.add_argument('--csv', nargs='?', const='asset_risk_scores.csv', help='Export the report to a CSV file')
    return parser.parse_args()

def main():
    args = parse_args()
    load_dotenv(args.secrets_file)
    token = finite_state_sdk.get_auth_token(
        os.getenv('CLIENT_ID'),
        os.getenv('CLIENT_SECRET')
    )
    org_ctx = os.getenv('ORGANIZATION_CONTEXT')

    if args.asset_version_id:
        # Analyze specific asset version
        print(f"\nAnalyzing asset version {args.asset_version_id}...")
        
        try:
            # Get asset version details
            asset_version = finite_state_sdk.get_asset_version(token, org_ctx, args.asset_version_id)
            
            # Extract risk score
            risk_score = asset_version.get('relativeRiskScore', 'N/A')
            
            # Print results
            print("\nAsset Risk Score:")
            print("-" * 50)
            print(f"Risk Score: {risk_score}")
                
        except Exception as e:
            print(f"Error analyzing asset version: {str(e)}")
            
    else:
        # Get all asset versions
        print("\nFetching asset versions...")
        asset_versions = finite_state_sdk.get_all_asset_versions(token, org_ctx)
        
        print(f"\nFound {len(asset_versions)} asset versions to analyze")
        print("\nAsset Risk Score Analysis:")
        print("-" * 80)
        print(f"{'Asset Name':<30} {'Version':<20} {'Risk Score':<10}")
        print("-" * 80)
        
        # Prepare data for CSV export
        csv_data = [['Asset Name', 'Version', 'Risk Score']]
        
        for asset_version in asset_versions:
            asset = asset_version.get('asset', {})
            asset_name = asset.get('name', 'N/A')
            version_name = asset_version.get('name', 'N/A')
            risk_score = asset_version.get('relativeRiskScore', 'N/A')
            
            # Print results
            print(f"{asset_name or 'N/A':<30} {version_name or 'N/A':<20} {risk_score or 'N/A':<10}")
            
            # Add data for CSV
            csv_data.append([asset_name or 'N/A', version_name or 'N/A', risk_score or 'N/A'])
        
        # Export to CSV if requested
        if args.csv:
            csv_file = args.csv
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)
            print(f"\nReport exported to {csv_file}")

if __name__ == '__main__':
    main() 