import argparse
import json
import os
import semver
from dotenv import load_dotenv

import sys

import finite_state_sdk
from finite_state_sdk.token_cache import TokenCache

"""
Compare Asset Versions to see what changed between them
* Shows Findings Introduced and Remediated
* Shows Software Components Added, Updated, and Removed
"""

"""
You can store your secrets in a file called .secrets in the same directory as this script
that looks like:

CLIENT_ID="your client id"
CLIENT_SECRET="your client secret"
ORGANIZATION_CONTEXT="your organization context"

Pass the path to the .secrets file as an argument to this script (--secrets-file)

DO NOT COMMIT THE SECRET FILE TO YOUR SOURCE CODE REPOSITORY!!!
"""


def compare_cves(version1_findings, version2_findings):
    cve_changes = []

    version1_cve_ids = []
    version2_cve_ids = [finding['cves'][0]['cveId'] for finding in version2_findings]

    version2_skip_list = []

    # double check for findings that were resolved
    for finding in version1_findings:
        cve_id = finding['cves'][0]['cveId']
        skip = False
        if finding['currentStatus'] is not None:
            if finding['currentStatus']['status'] == 'NOT_AFFECTED' or finding['currentStatus']['status'] == 'FIXED':
                skip = True
                version2_skip_list.append(cve_id)

        if not skip:
            version1_cve_ids.append(cve_id)

    # Findings that were introduced
    for finding in version2_findings:
        cve_id = finding['cves'][0]['cveId']
        if cve_id in version2_skip_list:
            continue

        if cve_id not in version1_cve_ids:
            affects = finding['affects'][0]
            cve_changes.append({'action': 'INTRODUCED', 'cve_id': cve_id, 'name': affects['name'], 'version': affects['version'], 'cvssSeverity': finding['cvssSeverity'], 'cvssScore': finding['cvssScore']})

    # Findings that were remediated
    for finding in version1_findings:
        cve_id = finding['cves'][0]['cveId']

        if cve_id not in version2_cve_ids:
            affects = finding['affects'][0]
            cve_changes.append({'action': 'REMEDIATED', 'cve_id': cve_id, 'name': affects['name'], 'version': affects['version'], 'cvssSeverity': finding['cvssSeverity'], 'cvssScore': finding['cvssScore']})

    return cve_changes


def compare_sw_components(sw_components_fw1, sw_components_fw2):
    """
    Compares the software components between two asset versions
    The format of the objects in the list that gets returned:
    {
        "action": "UPDATED",
        "name": "software name",
        "version1": "version 1",
        "version2": "version 2"
    }

    actions = ADDED, UPDATED, REMOVED
    name = name of the software component
    version1 = version from asset version 1
    version2 = version from asset version 2

    Args:
        sw_components_fw1 (list): software components from asset version 1
        sw_components_fw2 (list): software components from asset version 2

    Returns:
        list: list of changes between the two asset versions
    """
    sw_component_changes = []

    # compare lists - lookup table, keys: sw_name, values: array<versions>
    sw1_versions = {}
    sw2_versions = {}

    for sw1 in sw_components_fw1:
        name = sw1['name'].lower()
        version = sw1['version']
        if name not in sw1_versions:
            sw1_versions[name] = []
        sw1_versions[name].append(version)

    for sw2 in sw_components_fw2:
        name = sw2['name'].lower()
        version = sw2['version']
        if name not in sw2_versions:
            sw2_versions[name] = []
        sw2_versions[name].append(version)

    # TODO: add CVE information for software to be able to add additional context like "High Risk Components Added"

    for sw_name in sw1_versions:
        # software not present in version 2
        if sw_name not in sw2_versions:
            for version in sw1_versions[sw_name]:
                sw_component_changes.append({'action': 'REMOVED', 'name': sw_name, 'version1': version})
        else:
            # compare the versions
            for version1 in sw1_versions[sw_name]:
                if version1 in sw2_versions[sw_name]:
                    # no change
                    pass
                else:
                    # check if updated or removed
                    for version2 in sw2_versions[sw_name]:
                        if version1 == '' or version2 == '':
                            pass
                        else:
                            sw_component_changes.append({'action': 'UPDATED', 'name': sw_name, 'version1': version1, 'version2': version2})

    for sw_name in sw2_versions:
        # software present in version 2 but not present in version 1 (ADDED)
        if sw_name not in sw1_versions:
            for version2 in sw2_versions[sw_name]:
                sw_component_changes.append({'action': 'ADDED', 'name': sw_name, 'version2': version2})
        else:
            # compare the versions
            for version2 in sw2_versions[sw_name]:
                if version2 in sw1_versions[sw_name]:
                    # no change
                    continue
                else:
                    # check if updated or removed
                    for version1 in sw1_versions[sw_name]:
                        if version1 == '' or version2 == '':
                            pass
                        else:
                            try:
                                if semver.compare(version1, version2) < 0:
                                    sw_component_changes.append({'action': 'UPDATED', 'name': sw_name, 'version1': version1, 'version2': version2})
                                else:
                                    sw_component_changes.append({'action': 'ADDED', 'name': sw_name, 'version2': version2})
                            except Exception:
                                sw_component_changes.append({'action': 'UPDATED', 'name': sw_name, 'version1': version1, 'version2': version2})

    return sw_component_changes


def main():
    parser = argparse.ArgumentParser(description='Compare two asset versions')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--asset-version-1', type=str, help='Asset Version ID 1', required=True)
    parser.add_argument('--asset-version-2', type=str, help='Asset Version ID 2', required=True)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 24 hours
    token_cache = TokenCache(ORGANIZATION_CONTEXT)
    token = token_cache.get_token(CLIENT_ID, CLIENT_SECRET)

    asset_version_id_1 = args.asset_version_1
    asset_version_id_2 = args.asset_version_2

    print(f'\033[0mComparing asset version {asset_version_id_1} to asset version {asset_version_id_2}')

    asset_version_1 = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id_1)
    print(f'Asset version 1: {asset_version_1[0]["asset"]["name"]} {asset_version_1[0]["name"]}')
    asset_version_2 = finite_state_sdk.get_asset_versions(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id_2)
    print(f'Asset version 2: {asset_version_2[0]["asset"]["name"]} {asset_version_2[0]["name"]}')

    print("*" * 80)
    print('CVE Analysis')

    print("*" * 80)
    version1_findings = finite_state_sdk.get_findings(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id_1, category="CVE")
    version2_findings = finite_state_sdk.get_findings(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id_2, category="CVE")

    cve_changes = compare_cves(version1_findings, version2_findings)

    # for grouping together
    introduced_messages = []
    remediated_messages = []

    cve_changes_filename = f'{asset_version_1[0]["asset"]["name"]}-{asset_version_1[0]["name"]}-to-{asset_version_2[0]["name"]}-cve_changes.csv'
    # replace filename spaces with underscores
    cve_changes_filename = cve_changes_filename.replace(' ', '_')
    with open(cve_changes_filename, 'w') as f:
        # write header
        f.write('action,cve_id,name,version,cvssSeverity,cvssScore\n')

        for cve_change in cve_changes:
            # write to csv
            f.write(f"{cve_change['action']},{cve_change['cve_id']},{cve_change['name']},{cve_change['version']},{cve_change['cvssSeverity']},{cve_change['cvssScore']}\n")
            if 'action' in cve_change:
                if cve_change['action'] == 'INTRODUCED':
                    # print in green
                    introduced_messages.append(f"\033[91m{cve_change['cve_id']} was introduced for {cve_change['name']} {cve_change['version']} - [{cve_change['cvssSeverity']}] ({cve_change['cvssScore']})\033[0m")

                elif cve_change['action'] == 'REMEDIATED':
                    # print in red
                    remediated_messages.append(f"\033[92m{cve_change['cve_id']} was remediated for {cve_change['name']} {cve_change['version']} - [{cve_change['cvssSeverity']}] ({cve_change['cvssScore']})\033[0m")

        print(f'Wrote CVE changes to {cve_changes_filename}')

    print("*" * 80)
    print('CVEs INTRODUCED')
    for message in introduced_messages:
        print(message)

    print("*" * 80)
    print('CVEs REMEDIATED')
    for message in remediated_messages:
        print(message)

    version1_software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id_1)
    version2_software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id=asset_version_id_2)

    # run compare
    sw_changes = compare_sw_components(version1_software_components, version2_software_components)

    # for grouping together
    added_messages = []
    updated_messages = []
    removed_messages = []

    sw_changes_filename = f'{asset_version_1[0]["asset"]["name"]}-{asset_version_1[0]["name"]}-to-{asset_version_2[0]["name"]}-sw_component_changes.csv'
    # replace filename spaces with underscores
    sw_changes_filename = sw_changes_filename.replace(' ', '_')
    with open(sw_changes_filename, 'w') as f:
        # write header
        f.write('action,name,version1,version2\n')

        for sw_change in sw_changes:
            # write to csv
            f.write(f"{sw_change['action']},{sw_change['name']}")
            if "version1" in sw_change:
                f.write(f",{sw_change['version1']}")
            else:
                f.write(",")
            if "version2" in sw_change:
                f.write(f",{sw_change['version2']}\n")
            else:
                f.write(",\n")

            if 'action' in sw_change:
                if sw_change['action'] == 'UPDATED':
                    # print in yellow
                    updated_messages.append(f"\033[93m{sw_change['name']} was updated from {sw_change['version1']} to {sw_change['version2']}\033[0m")
                elif sw_change['action'] == 'ADDED':
                    # print in green
                    added_messages.append(f"\033[92m{sw_change['name']} was added with version {sw_change['version2']}\033[0m")
                elif sw_change['action'] == 'REMOVED':
                    # print in red
                    removed_messages.append(f"\033[91m{sw_change['name']} was removed with version {sw_change['version1']}\033[0m")

        print(f'Wrote Software Component changes to {sw_changes_filename}')

    print("*" * 80)
    print('Software Component Changes')
    print("*" * 80)
    print('Software Components ADDED')
    for message in added_messages:
        print(message)

    print("*" * 80)
    print('Software Components UPDATED')
    for message in updated_messages:
        print(message)

    print("*" * 80)
    print('Software Components REMOVED')
    for message in removed_messages:
        print(message)


if __name__ == "__main__":
    main()

