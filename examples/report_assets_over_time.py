#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import finite_state_sdk

def parse_args():
    parser = argparse.ArgumentParser(description='Report on the number of assets under management over time.')
    parser.add_argument('--secrets-file', required=True, help='Path to the secrets file')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information about each asset')
    parser.add_argument('--csv', nargs='?', const='assets_report.csv', help='Export the report to a CSV file (default: assets_report.csv)')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load secrets from the .env file
    load_dotenv(args.secrets_file)
    
    # Get the token
    token = finite_state_sdk.get_auth_token(
        os.getenv('CLIENT_ID'),
        os.getenv('CLIENT_SECRET')
    )
    
    # Get all assets
    assets = finite_state_sdk.get_all_assets(token, os.getenv('ORGANIZATION_CONTEXT'))
    
    # Create a dictionary to store the number of assets per date
    assets_by_date = {}
    asset_details = {}
    
    # Process each asset
    for asset in assets:
        # Get the creation date from the asset
        created_at = asset.get('createdAt')
        if created_at:
            # Convert the timestamp to a date string
            date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            
            # Increment the count for this date
            assets_by_date[date] = assets_by_date.get(date, 0) + 1
            
            # Store the asset details if verbose mode is enabled
            if args.verbose:
                if date not in asset_details:
                    asset_details[date] = []
                asset_details[date].append({
                    'id': asset.get('id'),
                    'name': asset.get('name'),
                    'created_at': created_at
                })
    
    # Sort the dates
    sorted_dates = sorted(assets_by_date.keys())
    
    # Print the report
    print("Number of assets under management over time:")
    for date in sorted_dates:
        print(f"{date}: {assets_by_date[date]} assets")
        
        # Print detailed information if verbose mode is enabled
        if args.verbose and date in asset_details:
            print("  Asset details:")
            for asset in asset_details[date]:
                print(f"    - {asset['name']} (ID: {asset['id']})")
    
    # Export to CSV if requested
    if args.csv:
        with open(args.csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'Number of Assets'])
            for date in sorted_dates:
                writer.writerow([date, assets_by_date[date]])
        print(f"\nReport exported to {args.csv}")

if __name__ == '__main__':
    main() 