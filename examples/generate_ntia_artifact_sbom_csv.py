import argparse
import csv
import datetime
import json
import os
from dotenv import load_dotenv
from time import sleep

import sys
import finite_state_sdk

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
    short_dt_str = dt.strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(description='Generates a human readable NTIA SBOM report for an artifact version')
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

    if not os.path.exists(f'{org_name}'):
        os.makedirs(f'{org_name}')

    # get the asset version
    asset_version = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)[0]
    asset_version_name = f"{asset_version['asset']['name']}_{asset_version['name']}"

    asset_version_name = asset_version_name.replace(" ", "_")
    asset_version_name = asset_version_name.replace("/", "_")
    asset_version_name = asset_version_name.replace(":", "_")
    asset_version_name = asset_version_name.replace(",", "_")
    asset_version_name = asset_version_name.replace(";", "_")

    # NTIA Required SBOM Fields
    # https://www.cisa.gov/sites/default/files/2024-10/SBOM%20Framing%20Software%20Component%20Transparency%202024.pdf
    #
    # Minimum Elements
    # 1. SBOM Author Name (optionally tool name and version information)
    # 2. Timestamp of SBOM creation in ISO 8601 format (e.g., 2024-10-02T12:00:00Z)
    # 3. SBOM Type (e.g. Source, Build, Deployed, Runtime)
    # 4. SBOM Primary Component (root of dependencies)
    # 5. Component Attributes (for all static, direct dependencies of the primary component)
    #  a. Name
    #  b. Version
    #  c. Supplier Name
    #  d. Unique Identifier (e.g. CPE, PURL, SWID, UUID)
    #  e. Cryptographic Hash + Algorithm (if sufficient info to generate the hash is not available, indicate as unknown) (Minimum: Provide at least one hash of the Primary Component)
    #  f. Relationship (or Primary for the primary component)
    #  g. Relationship Completeness (Unknown, None, Partial, Known)
    #  h. License (minimum: for the primary component)
    #  i. Copyright Notice (minimum: for the primary component)

    sbom_field_names = [
        "id",
        "name",
        "version",
        "supplier",
        "type",
        "softwareIdentifiers",
        "hash",
        "relationship",
        "relationshipCompleteness",
        "licenses",
        "licenseTypes",
    ]

    vulnerability_field_names = [
        "id",
        "vulnIdFromTool",
        "title",
        "affectedComponents",
        "severity",
        "cvssScore",
        "cvssVector",
        "publishedDate",
        "status"
    ]

    output_filename1 = f'{org_name}/{dt_str}-{org_name}_{asset_version_name}_components.csv'

    components_api_results_filename = f'{org_name}/{short_dt_str}-{org_name}_{asset_version_name}_components_api_results.json'

    if os.path.exists(components_api_results_filename):
        with open(components_api_results_filename, 'r') as json_file:
            components = json.load(json_file)
    else:
        # for the artifact version, get all the softare components with files
        components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)

        # save components to a json file so we don't have to query for it again
        with open(components_api_results_filename, 'w') as json_file:
            json.dump(components, json_file)

    def get_sha256_hash(component):
        if "hashes" in component:
            for hash in component["hashes"]:
                if hash["alg"] == "SHA_256":
                    return f'{hash["alg"]}: {hash["content"]}'
        return "Unknown"

    with open(output_filename1, mode='w') as csv_file1:

        writer1 = csv.DictWriter(csv_file1, fieldnames=sbom_field_names)
        writer1.writeheader()

        for component in components:
            if component["name"].endswith(".ko"):
                continue

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

            if component["type"] == "" or component["type"] is None:
                component["type"] = "LIBRARY"

            if component["type"] != "FILE":
                writer1.writerow({
                    "id": component["id"],
                    "name": component["name"],
                    "version": component["version"],
                    "supplier": component["supplier"]["name"],
                    "type": component["type"],
                    "softwareIdentifiers": software_identifiers_str,
                    "hash": get_sha256_hash(component),
                    "relationship": "Included In",
                    "relationshipCompleteness": "Unknown",
                    "licenses": licenses,
                    "licenseTypes": get_license_types(all_licenses)
                })

    print(f'CSV file created: {output_filename1}')

    def get_cvss_vector(finding):
        if len(finding["cves"]) > 0:
            cve = finding["cves"][0]
            if cve["cvssBaseMetricV3"] is not None:
                return cve["cvssBaseMetricV3"]["cvssv3"]["vectorString"]
            elif cve["cvssBaseMetricV2"] is not None:
                return cve["cvssBaseMetricV2"]["cvssv2"]["vectorString"]
            else:
                return ""
        else:
            return ""

    def get_published_date(finding):
        if finding["category"] == "CVE":
            return finding["cves"][0]["published"]
        else:
            return finding["createdAt"]

if __name__ == "__main__":
    main()

