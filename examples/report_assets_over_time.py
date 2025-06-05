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
    parser = argparse.ArgumentParser(description='Report on the number of assets over time.')
    parser.add_argument('--secrets-file', help='Path to the secrets file (only required if .env not found in working directory)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information about each asset')
    parser.add_argument('--csv', nargs='?', const='assets_over_time.csv', help='Export the report to a CSV file (default: assets_over_time.csv)')
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
    
    # Get all assets
    assets = finite_state_sdk.get_all_assets(token, ORGANIZATION_CONTEXT)
    
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
            
            # Store the asset details
            if date not in asset_details:
                asset_details[date] = []
            asset_details[date].append({
                'id': asset.get('id'),
                'name': asset.get('name'),
                'group': asset.get('group', {}).get('name', 'N/A'),
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
                print(f"    - {asset['name']} (ID: {asset['id']}, Group: {asset['group']})")
    
    # Export to CSV if requested
    if args.csv:
        with open(args.csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write summary section
            writer.writerow(['Date', 'Number of Assets'])
            for date in sorted_dates:
                writer.writerow([date, assets_by_date[date]])
            
            # Write detailed section
            writer.writerow([])  # Add a blank line
            writer.writerow(['Date', 'Asset Name', 'Asset ID', 'Group', 'Created At'])
            for date in sorted_dates:
                if date in asset_details:
                    for asset in asset_details[date]:
                        writer.writerow([
                            date,
                            asset['name'],
                            asset['id'],
                            asset['group'],
                            asset['created_at']
                        ])
        print(f"\nReport exported to {args.csv}")

if __name__ == '__main__':
    main() 