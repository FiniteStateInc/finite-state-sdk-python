
import finite_state_sdk
import json

TOKEN = 'YOUR_TOKEN'
ORGANIZATION_CONTEXT = 'YOUR_ORG_CONTEXT'

# Get all CVE findings for a specific asset version
# For more info see: https://docs.finitestate.io/types/finding-category
findings = finite_state_sdk.get_findings(TOKEN, ORGANIZATION_CONTEXT, asset_version_id='123456789', category="CVE")

print(f'Found {len(findings)} findings')

i = 0
for finding in findings:
    print(f'Finding: {json.dumps(finding, indent=2)}')
    i += 1
    if i > 10:
        break


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
