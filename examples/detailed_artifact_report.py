import argparse
import datetime
import json
import os
from dotenv import load_dotenv
from time import sleep

import sys
sys.path.append('..')
import finite_state_sdk


def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Creates a detailed artifact report that includes OS, software component count, and finding counts')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 24 hours
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    # get the name from the secrets file
    # and use that to create a csv file
    org_name = args.secrets_file.split('.secrets_')[1]
    print(f'Org name: {org_name}')

    specific_scans = []

    # GET:
    # latest version scan of each artifact since December 1 2023
    # with number of software components and findings for each
    # and test id

    scans = finite_state_sdk.get_scans(token, ORGANIZATION_CONTEXT, date_filter="2023-01-01T00:00:00.000Z")
    print(f'Found {len(scans)} scans')
    #print(f'Scans: {json.dumps(scans, indent=2)}')

    for specific_scan in specific_scans:
        scan = finite_state_sdk.get_scans(token, ORGANIZATION_CONTEXT, scan_id=specific_scan)
        print(f'Specific scan: {json.dumps(scan, indent=2)}')
        scans.extend(scan)

    # create csv file
    output_filename = f'{dt_str}-detailed_artifact_report-{org_name}.csv'
    print(f"Writing to {output_filename}")

    with open(output_filename, "w") as f:
        f.write("app_link,scan_id,artifact_id,artifact_version_id,artifact_name,artifact_version,business_unit,created_at,software_components_count,findings_count,status,uploaded_by,oses,YEAR_MONTH\n")

        for scan in scans:
            #print(f'Scan: {json.dumps(scan, indent=2)}')
            # get the software component instances and findings counts
            asset_version = scan['artifactUnderTest']['assetVersion']

            if asset_version is None:
                print(f'No asset version for scan: {json.dumps(scan, indent=2)}')
                continue

            asset_version_id = asset_version['id']

            got_data = False
            while not got_data:
                try:
                    finding_count = finite_state_sdk.get_findings(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id, count=True)
                    software_component_count = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id, count=True)
                    scan["software_component_count"] = software_component_count
                    scan["finding_count"] = finding_count

                    os_software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id, type="OPERATING_SYSTEM")

                    scan["OS"] = ""
                    oses = []
                    if len(os_software_components) > 0:
                        #print(f'Operating system software components: {json.dumps(os_software_components, indent=2)}')
                        for os_software_component in os_software_components:
                            os_name_version = f"{os_software_component['name']} {os_software_component['version']}"
                            oses.append(os_name_version)

                        scan["OS"] = "; ".join(oses)

                    print(f'Artifact: {asset_version["asset"]["name"]} {asset_version["name"]}')
                    print(f'Finding count: {finding_count}')
                    print(f'Software component count: {software_component_count}')
                    print(f'OS: {scan["OS"]}')
                    print("--" * 10)
                    got_data = True
                except:
                    print(f"Error retrieving results, sleeping then trying again")
                    sleep(2)

                id = scan['id']
                asset_version = scan['artifactUnderTest']['assetVersion']
                if asset_version is None:
                    print(f'No asset version for scan: {json.dumps(scan, indent=2)}')
                    continue
                artifact_id = asset_version['asset']['id']
                artifact_version_id = asset_version['id']
                artifact_name = asset_version['asset']['name'].replace(',', '')

                business_unit = asset_version['asset']['group']['name']
                artifact_version = asset_version['name'].replace(',', '')
                link = f'https://platform.finitestate.io/artifacts/{artifact_id}/versions/{asset_version["id"]}'
                created_at = scan['createdAt']

                status = scan['state']['status']
                try:
                    uploaded_by = scan['createdBy']['email']
                except:
                    uploaded_by = "NOT_SPECIFIED"
                try:
                    findings_count = scan['finding_count']['count']
                    software_components_count = scan['software_component_count']['count']
                except:
                    findings_count = -1
                    software_components_count = -1
                f.write(f"{link},{id},{artifact_id},{artifact_version_id},{artifact_name},{artifact_version},{business_unit},{created_at},{software_components_count},{findings_count},{status},{uploaded_by},{scan['OS']},{created_at[0:7]}\n")

    print(f'Wrote {output_filename}')


if __name__ == "__main__":
    main()

