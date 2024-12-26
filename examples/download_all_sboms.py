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

    parser = argparse.ArgumentParser(description='Download all SBOMs for an organization')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 10 hours
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    asset_versions = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT)

    print(f'Found {len(asset_versions)} asset_versions')

    org_name = args.secrets_file.split(".secrets_")[1]

    if not os.path.exists(f'{org_name}'):
        os.makedirs(f'{org_name}')
    output_directory = f'{org_name}'

    for asset_version in asset_versions:
        print(f'** Downloading SBOMs for {asset_version["asset"]["name"]} {asset_version["name"]}')

        output_filename = f"{dt_str}_{asset_version['asset']['name']}_{asset_version['name']}".replace(' ', '_').replace("/", "_").replace(":", "_").replace("=", "_")
        output_filename = os.path.join(output_directory, output_filename)

        altername_filename = f"{asset_version['id']}"
        altername_filename = os.path.join(output_directory, altername_filename)

        if not os.path.exists(f"{output_filename}_sbom_only.json") and not os.path.exists(f"{altername_filename}_sbom_only.json"):
            try:
                finite_state_sdk.download_sbom(token, ORGANIZATION_CONTEXT, sbom_type="CYCLONEDX", sbom_subtype="SBOM_ONLY", asset_version_id=asset_version['id'], output_filename=f"{output_filename}_sbom_only.json")
                print(f"Downloaded SBOM_ONLY for {asset_version['asset']['name']} {asset_version['name']} to {output_filename}_sbom_only.json")
            except Exception as e:
                finite_state_sdk.download_sbom(token, ORGANIZATION_CONTEXT, sbom_type="CYCLONEDX", sbom_subtype="SBOM_ONLY", asset_version_id=asset_version['id'], output_filename=f"{altername_filename}_sbom_only.json")
                print(f"Downloaded SBOM_ONLY for {asset_version['asset']['name']} {asset_version['name']} to {altername_filename}_sbom_only.json")
        else:
            print(f"\tALREADY DOWNLOADED SBOM_ONLY SBOMs for {asset_version['asset']['name']} {asset_version['name']}")

        if not os.path.exists(f"{output_filename}_with_vdr.json") and not os.path.exists(f"{altername_filename}_with_vdr.json"):
            try:
                finite_state_sdk.download_sbom(token, ORGANIZATION_CONTEXT, sbom_type="CYCLONEDX", sbom_subtype="SBOM_WITH_VDR", asset_version_id=asset_version['id'], output_filename=f"{output_filename}_with_vdr.json")
                print(f"Downloaded SBOM_WITH_VDR for {asset_version['asset']['name']} {asset_version['name']} to {output_filename}_with_vdr.json")
            except:
                finite_state_sdk.download_sbom(token, ORGANIZATION_CONTEXT, sbom_type="CYCLONEDX", sbom_subtype="SBOM_WITH_VDR", asset_version_id=asset_version['id'], output_filename=f"{altername_filename}_with_vdr.json")
                print(f"Downloaded SBOM_WITH_VDR for {asset_version['asset']['name']} {asset_version['name']} to {altername_filename}_with_vdr.json")
        else:
            print(f"\t ALREADY DOWNLOADED SBOM WITH VDR SBOMs for {asset_version['asset']['name']} {asset_version['name']}")


if __name__ == "__main__":
    main()
