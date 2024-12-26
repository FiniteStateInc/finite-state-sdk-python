import argparse
import csv
import datetime
import json
import os
from dotenv import load_dotenv
from time import sleep

import sys
import finite_state_sdk


# Finite State SDK Extensions

def get_os_components(token, organization_context, asset_version_id=None):
    """Returns the OS components for the given asset version."""

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
            "currentStatus": {
                "AND": [
                    {
                        "status_not_in": ["REVIEWED_FALSE_POSITIVE"]
                    }
                ]
            },
            "type_in": ["OPERATING_SYSTEM"]
        },
        "after": None,
        "first": finite_state_sdk.queries.DEFAULT_PAGE_SIZE,
        "orderBy": ["absoluteRiskScore_DESC"],
    }

    if asset_version_id is not None:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    os_components = finite_state_sdk.get_all_paginated_results(token, organization_context, query, variables, 'allSoftwareComponentInstances')

    if len(os_components) > 0:
        print(f'** Found {len(os_components)} OS components')
    else:
        print(f'No OS components found')

    return os_components

# /Finite State SDK Extensions

def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Generates a report of all Operating System components for an organization or asset version')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--asset-version-id', type=str, help='Asset Version ID', required=False)

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

    HISTORY_FILES_DIRECTORY = 'fs_os_history_files'

    # if history_files directory doesn't exist, create it
    if not os.path.exists(HISTORY_FILES_DIRECTORY):
        os.makedirs(HISTORY_FILES_DIRECTORY)

    # keep track of the history of asset ids and asset versions ids queried in a file
    # so we can pick up where we left off it if crashes

    OS_QUERY_ASSET_IDS_QUERIED_HISTORY_FILENAME = f'{HISTORY_FILES_DIRECTORY}/{org_name}_os_query_asset_ids_queried.json'
    asset_ids_queried = []
    if os.path.exists(OS_QUERY_ASSET_IDS_QUERIED_HISTORY_FILENAME):
        with open(OS_QUERY_ASSET_IDS_QUERIED_HISTORY_FILENAME, 'r') as f:
            asset_ids_queried = json.load(f)

    OS_QUERY_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME = f'{HISTORY_FILES_DIRECTORY}/{org_name}_os_query_asset_version_ids_queried.json'

    asset_version_ids_queried = []
    if os.path.exists(OS_QUERY_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME):
        with open(OS_QUERY_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME, 'r') as f:
            asset_version_ids_queried = json.load(f)

    ALL_OS_COMPONENTS_HISTORY_FILENAME = f'{HISTORY_FILES_DIRECTORY}/{org_name}_os_components.json'

    all_os_components = []
    if os.path.exists(ALL_OS_COMPONENTS_HISTORY_FILENAME):
        with open(ALL_OS_COMPONENTS_HISTORY_FILENAME, 'r') as f:
            all_os_components = json.load(f)

    def get_product_names(products):
        if products is None or len(products) == 0:
            return None
        return ';'.join([product['name'] for product in products])

    OS_COMPONENTS_OUTPUT_FILENAME = f'{dt_str}-{org_name}-os_components.csv'

    # generate a CSV of all components with name, version
    with open(OS_COMPONENTS_OUTPUT_FILENAME, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['URL', 'BU', 'Products', 'Asset Name', 'Asset Version', 'Component Name', 'Component Version', 'Component URL'])

        for component in all_os_components:
            asset_version_url = f"https://platform.finitestate.io/artifacts/{component['assetVersion']['asset']['id']}/versions/{component['assetVersion']['id']}"
            component_url = f"https://platform.finitestate.io/artifacts/{component['assetVersion']['asset']['id']}/versions/{component['assetVersion']['id']}/bill-of-materials/{component['id']}/about"
            csvwriter.writerow([asset_version_url, component['assetVersion']['asset']['group']['name'], get_product_names(component['assetVersion']['products']), component['assetVersion']['asset']['name'], component['assetVersion']['name'], component['name'], component['version'], component_url])

        print(f"Wrote OS components to {OS_COMPONENTS_OUTPUT_FILENAME}")

    if args.asset_version_id is not None:
        os_components = get_os_components(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)

        for component in os_components:
            print(f'\OS Component: {component["name"]} {component["version"]}')

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

                os_components = get_os_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id)

                for component in os_components:
                    print(f'\tOS Component: {component["name"]} {component["version"]}')
                    all_os_components.append(component)

                asset_version_ids_queried.append(asset_version_id)

                print("-" * 20)

            # save the asset version ids queried
            with open(OS_QUERY_ASSET_VERSION_IDS_QUERIED_HISTORY_FILENAME, 'w+') as f:
                json.dump(asset_version_ids_queried, f)

            # save the components
            with open(ALL_OS_COMPONENTS_HISTORY_FILENAME, 'w+') as f:
                json.dump(all_os_components, f)

            asset_ids_queried.append(asset['id'])

            # save the asset version ids queried
            with open(OS_QUERY_ASSET_IDS_QUERIED_HISTORY_FILENAME, 'w+') as f:
                json.dump(asset_ids_queried, f)

        print("=" * 80)


if __name__ == '__main__':
    main()