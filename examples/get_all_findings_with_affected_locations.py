import argparse
import datetime
import json
import os
from dotenv import load_dotenv

import sys
sys.path.append('..')
import finite_state_sdk


def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Get all CVE findings for a specific asset version, with the file locations associated with the affected components')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--asset-version-id', type=str, help='The asset version id', required=True)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # get the name from the secrets file
    # and use that to create a csv file
    org_name = args.secrets_file.split('.secrets_')[1]
    print(f'Org name: {org_name}')

    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    # Get all CVE findings for a specific asset version
    # For more info see: https://docs.finitestate.io/types/finding-category
    findings = finite_state_sdk.get_findings(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id, category='CVE')

    print(f'Found {len(findings)} findings')

    # get the asset version
    asset_version = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)[0]
    asset_version_name = f"{asset_version['asset']['name']}_{asset_version['name']}".replace(' ', '_').replace("/", "_").replace(":", "_").replace("=", "_")

    print(f'Asset version: {asset_version_name}')

    output_filename = f'{dt_str}_{org_name}-{asset_version_name}-findings_with_paths.csv'

    with open(output_filename, 'w') as f:
        f.write("Finite State Finding ID,CVE ID,Title,Category,Severity,File Paths\n")
        for finding in findings:
            file_paths = []

            affects = finding['affects']

            if len(affects) > 0:
                for affected_component in affects:
                    try:
                        for filepath in affected_component['files']:
                            file_paths.append(filepath['path'])

                        if len(affected_component['originalComponents']) > 0:
                            for affected_original_component in affected_component['originalComponents']:
                                for filepath in affected_original_component['files']:
                                    file_paths.append(filepath['path'])
                    except:
                        print(f'Error processing affected component: {json.dumps(affected_component, indent=2)}')
                        exit(1)

            clean_title = finding['title'].replace(',', ' ').replace('\n', ' ')

            file_path_to_output = ";".join(file_paths[0:10])

            f.write(f'{finding["id"]},{finding["cves"][0]["cveId"]},{clean_title},{finding["category"]},{finding["severity"]},{file_path_to_output}\n')

        f.write('\n')
        f.write('\n')

    print(f'Wrote findings to {output_filename}')

if __name__ == "__main__":
    main()
