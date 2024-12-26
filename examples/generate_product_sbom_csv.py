import argparse
import csv
import datetime
import json
import os
import sys

import finite_state_sdk

product_field_names = [
    "id",
    "product_name",
    "asset_name",
    "supplier",
    "name",
    "version",
    "type",
    "softwareIdentifiers",
    "licenses",
    "licenseTypes",
    "description",
]


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

    parser = argparse.ArgumentParser(description='Generates a Product SBOM CSV file for all artifacts associated to the product')
    parser.add_argument('--org-name', type=str, help='Organization name', required=False)
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=False)
    parser.add_argument('--verbose', action='store_true', help='Print verbose output', default=False)
    parser.add_argument('--product-id', type=str, help='Product ID', required=True)

    args = parser.parse_args()

    if args.secrets_file:
        from dotenv import load_dotenv
        load_dotenv(args.secrets_file, override=True)

    org_name = None
    if args.org_name:
        org_name = args.org_name
    else:
        # get the name from the secrets file
        # and use that to create a csv file
        org_name = args.secrets_file.split('.secrets_')[1]

    if not org_name:
        print(f"Organization name not provided")
        exit(1)

    print(f'Org name: {org_name}')

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 10 hours by default
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    product = finite_state_sdk.get_products(token, ORGANIZATION_CONTEXT, product_id=args.product_id)[0]

    product_name = product["name"].replace(" ", "_")
    product_name = product_name.replace("/", "_")
    product_name = product_name.replace(":", "_")
    product_name = product_name.replace(",", "_")
    product_name = product_name.replace(";", "_")

    if args.verbose:
        print(f"For product: {product_name}")

    product_output_filename = f'{dt_str}-{org_name}_{product_name}_sbom.csv'

    # get all artifact versions associated with the product
    artifact_versions = finite_state_sdk.get_all_asset_versions_for_product(token, ORGANIZATION_CONTEXT, args.product_id)[0]['assets']

    with open(product_output_filename, mode='w', newline='') as product_csv_file:

        product_writer = csv.DictWriter(product_csv_file, fieldnames=product_field_names)
        product_writer.writeheader()

        for artifact_version in artifact_versions:
            asset_version_id = artifact_version["id"]

            # get the asset version
            asset_version = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id)[0]

            asset_version_name = f"{asset_version['asset']['name']}_{asset_version['name']}"

            asset_version_name = asset_version_name.replace(" ", "_")
            asset_version_name = asset_version_name.replace("/", "_")
            asset_version_name = asset_version_name.replace(":", "_")
            asset_version_name = asset_version_name.replace(",", "_")
            asset_version_name = asset_version_name.replace(";", "_")

            if args.verbose:
                print(f"Handling asset version: {asset_version_name}")

            # for the artifact version, get all the software components
            components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id)

            product_writer = csv.DictWriter(product_csv_file, fieldnames=product_field_names)

            for component in components:
                software_identifiers = component["softwareIdentifiers"]["cpes"]
                software_identifiers.append(component["softwareIdentifiers"]["purl"])

                # replace any comma in software identifiers
                for i in range(len(software_identifiers)):
                    software_identifiers[i] = software_identifiers[i].replace(",", "_")

                software_identifiers_str = ";".join(software_identifiers)

                all_licenses = []
                for license in component["licenses"]:
                    all_licenses.append(license)

                for license in component["softwareComponent"]["licenses"]:
                    # only add if another license with the same name is not already in the list
                    if not any(x["name"] == license["name"] for x in all_licenses):
                        all_licenses.append(license)

                licenses = "; ".join(x["name"] for x in all_licenses)
                license_types = get_license_types(all_licenses)

                safe_supplier_name = ""
                if component["supplier"] and "name" in component["supplier"] and component["supplier"]["name"]:
                    safe_supplier_name = component["supplier"]["name"]

                safe_component_name = ""
                if component["name"]:
                    safe_component_name = component["name"]

                safe_version = ""
                if component["version"]:
                    safe_version = component["version"]

                safe_description = ""
                if "summaryDescription" in component and component["summaryDescription"]:
                    safe_description = component["summaryDescription"]
                    safe_description = safe_description.replace(",", " ")
                else:
                    if args.verbose:
                        print(f"No description for component: {json.dumps(component, indent=2)}")

                product_row = {
                    "id": component["id"],
                    "product_name": product_name,
                    "asset_name": asset_version_name,
                    "supplier": safe_supplier_name,
                    "name": safe_component_name,
                    "version": safe_version,
                    "type": component["type"],
                    "softwareIdentifiers": software_identifiers_str,
                    "licenses": licenses,
                    "licenseTypes": license_types,
                    "description": safe_description,
                }

                if component["type"] != "FILE":
                    product_writer.writerow(product_row)

    print(f'CSV file created: {product_output_filename}')


if __name__ == "__main__":
    main()

