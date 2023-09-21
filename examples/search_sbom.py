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

print('Searching for busybox with no version, case insensitive')
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', name='busybox')
print(f'Found {len(sbom)} SBOM entries')
print(f'SBOM: {json.dumps(sbom, indent=2)}')


print('Searching for busybox with no version, case sensitive')
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', name='busybox', case_sensitive=True)

print('Searching for busybox with version 1.26.2, case insensitive')
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', name='busybox', version='1.26.2')


print('Searching for busybox with version 1.32.0, case insensitive')
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', name='busybox', version='1.32.0')

print('Searching for BusyBox with version 1.26.2, case sensitive')
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, asset_version_id='123456789', name='BusyBox', version='1.26.2', case_sensitive=True)

print("Searching for busybox for the whole org, case insensitive")
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, name='busybox')

print("Searching for busybox for the whole org, case sensitive")
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, name='busybox', case_sensitive=True)

print("Searching for busybox for the whole org, case sensitive, with version 1.26.2")
sbom = finite_state_sdk.search_sbom(token, ORGANIZATION_CONTEXT, name='busybox', case_sensitive=True, version='1.26.2')

