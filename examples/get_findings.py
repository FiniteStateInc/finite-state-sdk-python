import argparse
import json
import os
from dotenv import load_dotenv

import finite_state_sdk


def main():
    """
    Get all Findings for a specific asset version
    """
    parser = argparse.ArgumentParser(description='Compare two asset versions')
    parser.add_argument('--secrets-file', type=str, help='Path to the secrets file', required=True)
    parser.add_argument('--asset-version', type=str, help='Asset Version ID', required=True)

    args = parser.parse_args()

    load_dotenv(args.secrets_file, override=True)

    # get CLIENT_ID and CLIENT_SECRET from env
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

    # Get an auth token - this is a bearer token that you will use for all subsequent requests
    # The token is valid for 24 hours
    token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

    # Get all CVE findings for a specific asset version
    # For more info see: https://docs.finitestate.io/types/finding-category
    findings = finite_state_sdk.get_findings(token, ORGANIZATION_CONTEXT, asset_version_id=args.asset_version, category="CRYPTO_MATERIAL")

    print(f'Found {len(findings)} findings')

    for finding in findings:
        if finding["vulnIdFromTool"] and "FS-" in finding["vulnIdFromTool"]:
            print(f'Finding: {json.dumps(finding, indent=2)}')


if __name__ == "__main__":
    main()


"""
Example response for a single finding:

{
  "_cursor": "{\"id\":\"123456789\"}",
  "id": "123456789",
  "title": "CVE-2020-21583 - util-linux:2.20.1",
  "date": "2023-09-18T22:31:56.123837Z",
  "createdAt": "2023-09-18T22:32:54.976807Z",
  "updatedAt": "2023-09-26T10:53:41.606205Z",
  "vulnIdFromTool": "CVE-2020-21583",
  "description": "## Description\n\nThe vulnerability known as CVE-2020-21583 affects the software component util-linux:2.20.1.\n\nThis vulnerability was matched by the Finite State platform with a confidence of 1.0 based on the following software identifier associated with util-linux:2.20.1:\n\n  - `cpe:2.3:a:kernel:util-linux:2.20.1:*:*:*:*:*:*:*`\n",
  "severity": "LOW",
  "riskScore": 0.5,
  "affects": [
    {
      "name": "util-linux",
      "version": "2.20.1"
    }
  ],
  "sourceTypes": [
    "STATIC"
  ],
  "category": "CVE",
  "subcategory": null,
  "regression": null,
  "currentStatus": null,
  "cwes": [
    {
      "id": "123456789",
      "cweId": "200",
      "name": "Exposure of Sensitive Information to an Unauthorized Actor",
      "__typename": "Cwe"
    }
  ],
  "cves": [
    {
      "id": "123456789",
      "cveId": "CVE-2020-21583",
      "exploitsInfo": {
        "exploitProofOfConcept": true,
        "reportedInTheWild": false,
        "weaponized": false,
        "exploitedByNamedThreatActors": false,
        "exploitedByBotnets": false,
        "exploitedByRansomware": false,
        "exploits": [
          {
            "id": "ae992b5c-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "__typename": "Exploit"
          },
          {
            "id": "b99f6a89-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "__typename": "Exploit"
          }
        ],
        "__typename": "ExploitInfo"
      },
      "__typename": "Cve"
    }
  ],
  "origin": "FS_MONITORING",
  "originalFindingsSources": [],
  "test": null
}
"""
