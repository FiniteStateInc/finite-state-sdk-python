import argparse
import os
from dotenv import load_dotenv

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
$ python get_artifact_finding_severity.py --secrets-file .secrets --asset-version-id YOUR_ASSET_VERSION_ID
'''

# Finite State SDK Extensions

DEFAULT_PAGE_SIZE = 100


def _create_GET_FINDINGS_VARIABLES(asset_version_id=None, category=None, cve_id=None, finding_id=None, status=None, severity=None, severity_type="CVSS", limit=100, count=False):
    variables = {
        "filter": {
            "mergedFindingRefId": None,
            "deletedAt": None
        }
    }

    # if not counting, set the pagination and ordering
    if not count:
        variables["after"] = None
        variables["first"] = limit if limit else DEFAULT_PAGE_SIZE
        variables["orderBy"] = ["title_ASC"]

    if finding_id is not None:
        # if finding_id is a list, use the "in" operator
        if isinstance(finding_id, list):
            variables["filter"]["id_in"] = finding_id
        else:
            variables["filter"]["id"] = str(finding_id)

    if asset_version_id is not None:
        # if asset_version_id is a list, use the "in" operator
        if isinstance(asset_version_id, list):
            variables["filter"]["assetVersionRefId_in"] = asset_version_id
        else:
            variables["filter"]["assetVersionRefId"] = str(asset_version_id)

    # if category is a string, make it a list
    if isinstance(category, str):
        category = [category]

    if category is not None:
        variables["filter"]["AND"] = [
            {
                "OR": [
                    {
                        "category_in": category
                    }
                ]
            },
            {
                "OR": [
                    {
                        "title_like": "%%"
                    },
                    {
                        "description_like": "%%"
                    }
                ]
            }
        ]

    if severity is not None:
        if severity_type == "CVSS":
            variables["filter"]["cvssSeverity"] = severity
        elif severity_type == "FSRS":
            variables["filter"]["severity"] = severity
        else:
            raise ValueError(f"Invalid severity type: {severity_type}")

    if cve_id is not None:
        if "AND" not in variables["filter"]:
            variables["filter"]["AND"] = []

        variables["filter"]["AND"].append(
            {
                "OR": [
                    {
                        "cves_every": {
                            "cveId": cve_id
                        }
                    }
                ]
            }
        )

    if status is not None:
        variables["filter"]["currentStatus"] = {
            "status_in": [
                status
            ]
        }

    return variables


def get_all_severities_by_category(token, organization_context, asset_version_id=None, category=None, severity_type="CVSS"):
    query = """
query GetFindingsCount_SDK($filter: FindingFilter)
{
    _allFindingsMeta(filter: $filter) {
        count
    }
}
"""

    critical_count = finite_state_sdk.send_graphql_query(token, organization_context, query, _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, severity="CRITICAL", severity_type=severity_type, count=True))["data"]["_allFindingsMeta"]["count"]
    high_count = finite_state_sdk.send_graphql_query(token, organization_context, query, _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, severity="HIGH", severity_type=severity_type, count=True))["data"]["_allFindingsMeta"]["count"]
    medium_count = finite_state_sdk.send_graphql_query(token, organization_context, query, _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, severity="MEDIUM", severity_type=severity_type, count=True))["data"]["_allFindingsMeta"]["count"]
    low_count = finite_state_sdk.send_graphql_query(token, organization_context, query, _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, severity="LOW", severity_type=severity_type, count=True))["data"]["_allFindingsMeta"]["count"]

    return critical_count, high_count, medium_count, low_count


def get_finding_severity_counts(token, organization_context, asset_version_id=None):
    """
    Returns the finding CVSS severity counts (CRITICAL, HIGH, MEDIUM, LOW) for the artifact version.
    Note - this does NOT use the Finite State Risk Score severity.
    """

    if asset_version_id is None:
        raise ValueError("asset_version_id is required")

    # get the finding severity counts for the artifact version
    critical_cve_count, high_cve_count, medium_cve_count, low_cve_count = get_all_severities_by_category(token, organization_context, asset_version_id=asset_version_id, category="CVE", severity_type="CVSS")

    print(f"Critical CVE Findings: {critical_cve_count}")
    print(f"High CVE Findings: {high_cve_count}")
    print(f"Medium CVE Findings: {medium_cve_count}")
    print(f"Low CVE Findings: {low_cve_count}")

    total_cve_count = critical_cve_count + high_cve_count + medium_cve_count + low_cve_count
    print(f"Total CVEs: {total_cve_count}")
    print("*" * 80)

    # get other types of vulnerabilities, which have a Finite State Risk Score (because they are not CVEs they don't have CVSS score)
    config_issues_critical_count, config_issues_high_count, config_issues_medium_count, config_issues_low_count = get_all_severities_by_category(token, organization_context, asset_version_id=asset_version_id, category="CONFIG_ISSUES", severity_type="FSRS")
    print(f"Config Issues Critical: {config_issues_critical_count}")
    print(f"Config Issues High: {config_issues_high_count}")
    print(f"Config Issues Medium: {config_issues_medium_count}")
    print(f"Config Issues Low: {config_issues_low_count}")
    total_config_issues_count = config_issues_critical_count + config_issues_high_count + config_issues_medium_count + config_issues_low_count
    print(f"Total Config Issues: {total_config_issues_count}")
    print("*" * 80)

    credentials_issues_critical_count, credentials_issues_high_count, credentials_issues_medium_count, credentials_issues_low_count = get_all_severities_by_category(token, organization_context, asset_version_id=asset_version_id, category="CREDENTIALS", severity_type="FSRS")
    print(f"Credentials Issues Critical: {credentials_issues_critical_count}")
    print(f"Credentials Issues High: {credentials_issues_high_count}")
    print(f"Credentials Issues Medium: {credentials_issues_medium_count}")
    print(f"Credentials Issues Low: {credentials_issues_low_count}")
    total_credentials_issues_count = credentials_issues_critical_count + credentials_issues_high_count + credentials_issues_medium_count + credentials_issues_low_count
    print(f"Total Credentials Issues: {total_credentials_issues_count}")
    print("*" * 80)

    crypto_materials_issues_critical_count, crypto_materials_issues_high_count, crypto_materials_issues_medium_count, crypto_materials_issues_low_count = get_all_severities_by_category(token, organization_context, asset_version_id=asset_version_id, category="CRYPTO_MATERIAL", severity_type="FSRS")
    print(f"Crypto Materials Issues Critical: {crypto_materials_issues_critical_count}")
    print(f"Crypto Materials Issues High: {crypto_materials_issues_high_count}")
    print(f"Crypto Materials Issues Medium: {crypto_materials_issues_medium_count}")
    print(f"Crypto Materials Issues Low: {crypto_materials_issues_low_count}")
    total_crypto_materials_issues_count = crypto_materials_issues_critical_count + crypto_materials_issues_high_count + crypto_materials_issues_medium_count + crypto_materials_issues_low_count
    print(f"Total Crypto Materials Issues: {total_crypto_materials_issues_count}")
    print("*" * 80)

    sast_analysis_issues_critical_count, sast_analysis_issues_high_count, sast_analysis_issues_medium_count, sast_analysis_issues_low_count = get_all_severities_by_category(token, organization_context, asset_version_id=asset_version_id, category="SAST_ANALYSIS", severity_type="FSRS")
    print(f"SAST Analysis Issues Critical: {sast_analysis_issues_critical_count}")
    print(f"SAST Analysis Issues High: {sast_analysis_issues_high_count}")
    print(f"SAST Analysis Issues Medium: {sast_analysis_issues_medium_count}")
    print(f"SAST Analysis Issues Low: {sast_analysis_issues_low_count}")
    total_sast_analysis_issues_count = sast_analysis_issues_critical_count + sast_analysis_issues_high_count + sast_analysis_issues_medium_count + sast_analysis_issues_low_count
    print(f"Total SAST Analysis Issues: {total_sast_analysis_issues_count}")
    print("*" * 80)


# /Finite State SDK Extensions

def main():
    parser = argparse.ArgumentParser(description='Generates a report of all EOL components for an organization or asset version')
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

    # get the finding severity counts for the artifact version
    get_finding_severity_counts(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version_id)


if __name__ == '__main__':
    main()