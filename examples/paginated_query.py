import finite_state_sdk
import json
import os

from finite_state_sdk.token_cache import TokenCache

"""
This is an example of how to make custom queries
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

# To make a paginated query, make sure to include the _cursor field in the query, and
# the $after and $first variables in the variables object
# To use the get_all_paginated_results function, you must specify the response_key, which
# corresponds to the query field that contains the paginated results,
# in this case `allSoftwareComponentInstances`
query = '''
query GetSoftwareComponentsForAnAssetVersion (
    $filter: SoftwareComponentInstanceFilter,
    $after: String,
    $first: Int
) {
    allSoftwareComponentInstances(filter: $filter,
                                  after: $after,
                                  first: $first
    ) {
        _cursor
        id
        name
        version
        hashes {
            alg
            content
        }
        licenses {
            name
            copyLeft
            isFsfLibre
            isOsiApproved
        }
        type
    }
}
'''

# Define the variable as an object
variables = {
    "filter": {
        "assetVersionRefId": '123456789',
        "mergedComponentRefId": None
    },
    "after": None,
    "first": 100
}

software_components = finite_state_sdk.get_all_paginated_results(token, ORGANIZATION_CONTEXT, query, variables=variables, response_key="allSoftwareComponentInstances")

for software_component in software_components:
    print(f'Software component: {json.dumps(software_component, indent=2)}')
