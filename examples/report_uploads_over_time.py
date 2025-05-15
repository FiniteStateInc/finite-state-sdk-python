import argparse
import os
from dotenv import load_dotenv
import finite_state_sdk
import csv

def main():
    parser = argparse.ArgumentParser(description='Generate a report on the number of uploads over time')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--verbose', action='store_true', help='Show detailed information about each upload')
    parser.add_argument('--csv', type=str, help='Output CSV file (optional)', required=False)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    # Get all asset versions using get_all_asset_versions
    asset_versions = finite_state_sdk.get_all_asset_versions(token, ORGANIZATION_CONTEXT)

    # Process asset versions to count uploads over time and collect details if verbose or csv
    uploads_over_time = {}  # Dictionary to store uploads by date
    details_by_date = {}    # Dictionary to store asset version details by date
    all_details = []        # List to store all asset version details for CSV
    for asset_version in asset_versions:
        created_at = asset_version.get('createdAt')
        if created_at:
            date = created_at.split('T')[0]  # Extract the date part
            uploads_over_time[date] = uploads_over_time.get(date, 0) + 1
            detail = {
                'date': date,
                'id': asset_version.get('id'),
                'name': asset_version.get('name'),
                'createdAt': created_at
            }
            if args.verbose:
                details_by_date.setdefault(date, []).append(detail)
            if args.csv:
                all_details.append(detail)

    # Output the report
    print("Number of uploads over time:")
    for date, count in sorted(uploads_over_time.items()):
        print(f"{date}: {count} uploads")
        if args.verbose and date in details_by_date:
            for detail in details_by_date[date]:
                print(f"  - ID: {detail['id']}, Name: {detail['name']}, Created At: {detail['createdAt']}")

    # Output to CSV if requested
    if args.csv:
        with open(args.csv, 'w', newline='') as csvfile:
            fieldnames = ['date', 'id', 'name', 'createdAt']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for detail in all_details:
                writer.writerow(detail)
        print(f"\nDetailed upload data exported to {args.csv}")

if __name__ == "__main__":
    main() 