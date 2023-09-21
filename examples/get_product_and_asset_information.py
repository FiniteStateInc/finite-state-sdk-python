import finite_state_sdk
import json
import os

from finite_state_sdk.token_cache import TokenCache

"""
This is an example of getting product and asset information
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

business_units = finite_state_sdk.get_business_units(token, ORGANIZATION_CONTEXT)

business_unit = business_units[0]


print(f'Getting products for BU id {business_unit["id"]}')
products = finite_state_sdk.get_products(token, ORGANIZATION_CONTEXT, business_unit_id='2310647013')
print(f'Found {len(products)} products')

for product in products:
    product_id = product['id']
    print(f'Getting product asset versions for product {product_id}')
    product_asset_versions = finite_state_sdk.get_product_asset_versions(token, ORGANIZATION_CONTEXT, product_id=product_id)

    print(f'Found {len(product_asset_versions)} product asset versions')
    print(f'Product asset versions: {json.dumps(product_asset_versions, indent=2)}')
