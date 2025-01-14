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

def get_software_components_with_files(token, organization_context, asset_version_id):
    """Returns the software components with files for the given asset version."""

    query = """
query GetSoftwareComponentsForAnAssetVersion (
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
        hashes {
            alg
            content
        }
        author
        licenses {
            id
            name
            copyLeft
            isFsfLibre
            isOsiApproved
            url
            __typename
        }
        copyrights {
            name
            text
            url
        }
        softwareIdentifiers {
            cpes
            purl
            __typename
        }
        absoluteRiskScore
        files {
            path
        }
        originalComponents {
            files {
                path
            }
        }
        softwareComponent {
            id
            name
            version
            type
            url
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
        originalComponents {
            name
            version
            files {
                path
                name
            }
        }
        currentStatus {
            id
            status
            comment
            createdBy {
                email
            }
            __typename
        }
        test {
            name
            tools {
                name
            }
        }
        files {
            path
            name
            hashes {
                alg
                content
            }
        }
        origin
        __typename
    }
}
"""
    components = finite_state_sdk.get_all_paginated_results(token, organization_context, query, finite_state_sdk.queries.GET_SOFTWARE_COMPONENTS['variables'](asset_version_id=asset_version_id), 'allSoftwareComponentInstances')

    return components

# /Finite State SDK Extensions


def get_license_types(licenses) -> str:
    try:
        """Returns the license types of the software component instance as a CSV-ready string."""
        if licenses:
            return ";".join(
                [f"Copyleft: {license['copyLeft']}" if license['copyLeft'] else "Permissive" for license in licenses]
            )
        return "Unknown"
    except Exception as e:
        print(f"Error: {e}")
        print(f"{json.dumps(licenses, indent=2)}")
        exit(1)


def main():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%Y-%m-%d-%H%M")

    parser = argparse.ArgumentParser(description='Gets an artifact version software components with file paths')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--asset-version-id', type=str, help='Asset Version ID', required=True)

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

    # get the asset version
    asset_version = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)[0]
    asset_version_name = f"{asset_version['asset']['name']}_{asset_version['name']}"

    asset_version_name = asset_version_name.replace(" ", "_")
    asset_version_name = asset_version_name.replace("/", "_")
    asset_version_name = asset_version_name.replace(":", "_")
    asset_version_name = asset_version_name.replace(",", "_")
    asset_version_name = asset_version_name.replace(";", "_")

    # for the artifact version, get all the softare components with files
    components = get_software_components_with_files(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)

    field_names = [
        "id",
        "name",
        "version",
        "type",
        "softwareIdentifiers",
        "findingsCount",
        "licenses",
        "licenseTypes",
        "filePaths"
    ]

    output_filename1 = f'{dt_str}-{org_name}_{asset_version_name}_components.csv'

    with open(output_filename1, mode='w') as csv_file1:

        writer1 = csv.DictWriter(csv_file1, fieldnames=field_names)
        writer1.writeheader()

        for component in components:
            software_identifiers = component["softwareIdentifiers"]["cpes"]
            software_identifiers.append(component["softwareIdentifiers"]["purl"])
            software_identifiers_str = ";".join(software_identifiers)

            all_licenses = []
            for license in component["licenses"]:
                all_licenses.append(license)

            for license in component["softwareComponent"]["licenses"]:
                # only add if another license with the same name is not already in the list
                if not any(x["name"] == license["name"] for x in all_licenses):
                    all_licenses.append(license)

            licenses = "; ".join(x["name"] for x in all_licenses)

            # get locations from related file evidence
            file_paths = []

            for filepath in component['files']:
                file_paths.append(filepath['path'])

            if len(component['originalComponents']) > 0:
                for affected_original_component in component['originalComponents']:
                    for filepath in affected_original_component['files']:
                        file_paths.append(filepath['path'])

            if component["type"] != "FILE":
                writer1.writerow({
                    "id": component["id"],
                    "name": component["name"],
                    "version": component["version"],
                    "type": component["type"],
                    "softwareIdentifiers": software_identifiers_str,
                    "findingsCount": component["_findingsMeta"]["count"],
                    "licenses": licenses,
                    "licenseTypes": get_license_types(all_licenses),
                    "filePaths": file_paths
                })

        print(f'CSV file created: {output_filename1}')


if __name__ == "__main__":
    main()

