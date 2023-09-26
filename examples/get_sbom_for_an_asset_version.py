import finite_state_sdk
import json
import os

from finite_state_sdk.token_cache import TokenCache

"""
This is an example of making a query
"""

"""
You can store your secrets in a file called .env in the same directory as this script
that looks like:

export CLIENT_ID="your client id"
export CLIENT_SECRET="your client secret"
export ORGANIZATION_CONTEXT="your organization context"

Before running the script, run the following command in the terminal:
source .env

DO NOT COMMIT THE SECRET FILE TO YOUR SOURCE CODE REPOSITORY!!!
"""

# get CLIENT_ID and CLIENT_SECRET from env
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")

# Get an auth token - this is a bearer token that you will use for all subsequent requests
# The token is valid for 24 hours
token_cache = TokenCache(ORGANIZATION_CONTEXT)
token = token_cache.get_token(CLIENT_ID, CLIENT_SECRET)

print(f'Getting software components for asset version id 123456789')
software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id='123456789')
print(f'Found {len(software_components)} software components')
print(f'Software components: {json.dumps(software_components, indent=2)}')

print(f'Getting software components of type "APPLICATION" for asset version id 123456789')
software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', type='APPLICATION')

print(f'Getting software components of type "OPERATING_SYSTEM" for asset version id 123456789')
software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', type='OPERATING_SYSTEM')

print(f'Getting software components of type "LIBRARY" for asset version id 123456789')
software_components = finite_state_sdk.get_software_components(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', type='LIBRARY')

"""
Example response for a single software component:
{
  "_cursor": "{\"id\":\"123456789\"}",
  "id": "123456789",
  "name": "Linux Kernel",
  "type": "OPERATING_SYSTEM",
  "version": "3.10.14",
  "hashes": [],
  "licenses": [
    {
      "id": "123456789",
      "name": "0BSD",
      "copyLeft": null,
      "isFsfLibre": null,
      "isOsiApproved": true,
      "url": null,
      "__typename": "License"
    },
    {
      "id": "123456789",
      "name": "GPL-1.0-only",
      "copyLeft": "STRONG",
      "isFsfLibre": null,
      "isOsiApproved": false,
      "url": null,
      "__typename": "License"
    }
  ],
  "softwareIdentifiers": {
    "cpes": [
      "cpe:2.3:o:linux:linux_kernel:3.10.14:*:*:*:*:*:*:*"
    ],
    "purl": "pkg:generic/linux%2Bkernel@3.10.14",
    "__typename": "SoftwareIdentifiers"
  },
  "absoluteRiskScore": 2085.600000000005,
  "softwareComponent": {
    "id": "123456789",
    "name": "Linux Kernel",
    "version": "3.10.14",
    "type": "OPERATING_SYSTEM",
    "url": null,
    "licenses": [
      {
        "id": "123456789",
        "name": "GPL-1.0-only",
        "copyLeft": "STRONG",
        "isFsfLibre": null,
        "isOsiApproved": false,
        "url": null,
        "__typename": "License"
      }
    ],
    "softwareIdentifiers": {
      "cpes": [
        "cpe:2.3:o:linux:linux_kernel:3.10.14:*:*:*:*:*:*:*"
      ],
      "purl": "pkg:generic/linux%2Bkernel@3.10.14",
      "__typename": "SoftwareIdentifiers"
    },
    "__typename": "SoftwareComponent"
  },
  "currentStatus": {
    "id": "123456789",
    "status": "CONFIRMED",
    "comment": "Confirmed this is present",
    "createdBy": {
      "email": "user@company.com"
    },
    "__typename": "SoftwareComponentStatus"
  },
  "__typename": "SoftwareComponentInstance"
}
"""