import argparse
import csv
import datetime
import json
import os
from dotenv import load_dotenv
from time import sleep

import sys
import finite_state_sdk


# create a .secrets file with the API credentials
# to get the API credentials, request them from Finite State directly by emailing support@finitestate.io
'''
export CLIENT_ID=YOUR_CLIENT_ID (secret provided by Finite State, looks like: 12asf3asdf6789012)
export CLIENT_SECRET=YOUR_CLIENT_SECRET
export ORGANIZATION_CONTEXT=YOUR_ORG_CONTEXT
'''

# to call the script
'''
# python3 pip install finite-state-sdk
$ python get_all_eol_components.py --secrets-file .secrets
$ python get_all_eol_components.py --secrets-file .secrets --asset-version-id YOUR_ASSET_VERSION_ID
'''

# Finite State SDK Extensions

def get_eol_components(token, organization_context, asset_version_id=None):
    """Returns the EOL components for the given asset version."""

    query = """
query GetSoftwareComponents (
    $filter: SoftwareComponentInstanceFilter,
    $after: String,
    $first: Int,
    $orderBy: [SoftwareComponentInstanceOrderBy!]
) {
    allSoftwareComponentInstances(filter: $filter,
                                  after: $after,
                                  first: $first,
                                  orderBy: $orderBy
    ) {
        _cursor
        _findingsMeta {
            count
        }
        id
        name
        type
        version
        supportEol
        assetVersion {
            id
            name
            asset {
                id
                name
                group {
                    name
                }
            }
            products {
                name
            }
        }
        hashes {
            alg
            content
        }
        author
        softwareIdentifiers {
            cpes
            purl
            __typename
        }
        absoluteRiskScore
        softwareComponent {
            id
            name
            version
            type
            url
            supportEndOfLife
            licenses {
                id
                name
                copyLeft
                isFsfLibre
                isOsiApproved
                url
                __typename
            }
            softwareIdentifiers {
                cpes
                purl
                __typename
            }
            __typename
        }
        supplier {
            name
        }
        releaseDate
        summaryDescription
        updatedAt
        currentStatus {
            id
            status
            comment
            createdBy {
                email
            }
            __typename
        }
        __typename
    }
}
"""

    variables = {
        "filter": {
            "mergedComponentRefId": None,
            "deletedAt": None,
            "AND": [
                {
                    "AND": [
                        {
                            "supportEol_lte": f"{datetime.datetime.now().isoformat(sep='T', timespec='seconds')}Z"
                        },
                        {
                            "softwareComponent": {
                                "supportEndOfLife_lte": f"{datetime.datetime.now().isoformat(sep='T', timespec='seconds')}Z"
                            }
                        },
                        {
                            "OR": [
                                {
                                    "supportEol_not": None
                                },
                                {
                                    "softwareComponent": {
                                        "supportEndOfLife_not": None
                                    }
                                }
                            ]
                        }
                    ]
                },
            ]
        },
        "after": None,
        "first": finite_state_sdk.queries.DEFAULT_PAGE_SIZE,
        "orderBy": ["absoluteRiskScore_DESC"],

    }

    if asset_version_id is not None:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    eol_components = finite_state_sdk.get_all_paginated_results(token, organization_context, query, variables, 'allSoftwareComponentInstances')

    if len(eol_components) > 0:
        print(f'** Found {len(eol_components)} EOL components')
    else:
        print(f'No EOL components found')

    return eol_components

# /Finite State SDK Extensions

def get_eol(component):
        if component['supportEol'] is not None:
            return component['supportEol']
        elif component['softwareComponent']['supportEndOfLife'] is not None:
            return component['softwareComponent']['supportEndOfLife']
        else:
            return None

def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Generates a report of all EOL components for an organization or asset version')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--asset-version-id', type=str, help='Asset Version ID', required=False)
    parser.add_argument('--clear-history', action='store_true', help='Clear the history files for a new run', default=False)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 10 hours
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    # get the name from the secrets file
    # and use that to create a csv file
    org_name = args.secrets_file.split('.secrets_')[1]
    print(f'Org name: {org_name}')

    EOL_HISTORY_FILES_DIRECTORY = 'fs_eol_script_history_files'

    if args.clear_history:
        # ask the user to confirm that they want to delete the history files
        response = input("Are you sure you want to delete the history files? (y/n): ")
        if response.lower() != 'y':
            print("Exiting")
            sys.exit(1)

        # delete the history files directory
        if os.path.exists(EOL_HISTORY_FILES_DIRECTORY):
            os.system(f'rm -rf {EOL_HISTORY_FILES_DIRECTORY}')
            print(f"Deleted history files")

    # if history_files directory doesn't exist, create it
    if not os.path.exists(EOL_HISTORY_FILES_DIRECTORY):
        os.makedirs(EOL_HISTORY_FILES_DIRECTORY)

    # keep track of the history of asset ids and asset versions ids queried in a file
    # so we can pick up where we left off it if crashes

    EOL_ASSET_IDS_QUERIED_HISTORY_FILENAME = f'{EOL_HISTORY_FILES_DIRECTORY}/{org_name}_eol_asset_ids_queried.json'
    asset_ids_queried = []
    if os.path.exists(EOL_ASSET_IDS_QUERIED_HISTORY_FILENAME):
        with open(EOL_ASSET_IDS_QUERIED_HISTORY_FILENAME, 'r') as f:
            asset_ids_queried = json.load(f)

    EOL_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME = f'{EOL_HISTORY_FILES_DIRECTORY}/{org_name}_eol_asset_version_ids_queried.json'

    asset_version_ids_queried = []
    if os.path.exists(EOL_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME):
        with open(EOL_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME, 'r') as f:
            asset_version_ids_queried = json.load(f)

    ALL_EOL_COMPONENTS_HISTORY_FILENAME = f'{EOL_HISTORY_FILES_DIRECTORY}/{org_name}_eol_components.json'

    all_eol_components = []
    if os.path.exists(ALL_EOL_COMPONENTS_HISTORY_FILENAME):
        with open(ALL_EOL_COMPONENTS_HISTORY_FILENAME, 'r') as f:
            all_eol_components = json.load(f)

    def get_product_names(products):
        if products is None or len(products) == 0:
            return None
        return ';'.join([product['name'] for product in products])

    if args.asset_version_id is not None:
        eol_components = get_eol_components(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)

        for component in eol_components:
            print(f'\tEOL Component: {component["name"]} {component["version"]} {get_eol(component)}')

    else:
        # get all artifacts
        asset_version_id = None
        assets = finite_state_sdk.get_assets(token, ORGANIZATION_CONTEXT)

        for asset in assets:
            print("=" * 80)
            print(f"Artifact: {asset['name']}")
            print("-" * 40)

            if asset['id'] in asset_ids_queried:
                print(f"Skipping {asset['id']}")
                continue

            asset_versions = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_id=asset['id'])
            for asset_version in asset_versions:
                print(f"Asset Version: {asset_version['name']}")
                asset_version_id = asset_version['id']

                if asset_version_id in asset_version_ids_queried:
                    print(f"Skipping {asset_version_id}")
                    continue

                eol_components = get_eol_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id)

                for component in eol_components:
                    print(f'\tEOL Component: {component["name"]} {component["version"]} {get_eol(component)}')
                    all_eol_components.append(component)

                asset_version_ids_queried.append(asset_version_id)

                print("-" * 20)

            # save the asset version ids queried
            with open(EOL_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME, 'w+') as f:
                json.dump(asset_version_ids_queried, f)

            # save the eol components
            with open(ALL_EOL_COMPONENTS_HISTORY_FILENAME, 'w+') as f:
                json.dump(all_eol_components, f)

            asset_ids_queried.append(asset['id'])

            # save the asset version ids queried
            with open(EOL_ASSET_IDS_QUERIED_HISTORY_FILENAME, 'w+') as f:
                json.dump(asset_ids_queried, f)

        print("=" * 80)

    EOL_COMPONENTS_OUTPUT_FILENAME = f'{dt_str}-{org_name}-eol_components.csv'

    # generate a CSV of all EOL components with name, version, and EOL date
    # note, this writes whatever is in the history file in case there is an interruption
    # to the service in the script, so if you want to get the latest data, delete the history files
    with open(EOL_COMPONENTS_OUTPUT_FILENAME, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['URL', 'BU', 'Products', 'Asset Name', 'Asset Version', 'Component Name', 'Component Version', 'Component EOL Date', 'Component URL'])

        for component in all_eol_components:
            asset_version_url = f"https://platform.finitestate.io/artifacts/{component['assetVersion']['asset']['id']}/versions/{component['assetVersion']['id']}"
            component_url = f"https://platform.finitestate.io/artifacts/{component['assetVersion']['asset']['id']}/versions/{component['assetVersion']['id']}/bill-of-materials/{component['id']}/about"
            csvwriter.writerow([asset_version_url, component['assetVersion']['asset']['group']['name'], get_product_names(component['assetVersion']['products']), component['assetVersion']['asset']['name'], component['assetVersion']['name'], component['name'], component['version'], get_eol(component), component_url])

        print(f"Wrote EOL components to {EOL_COMPONENTS_OUTPUT_FILENAME}")



if __name__ == '__main__':
    main()