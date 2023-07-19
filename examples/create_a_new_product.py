import finite_state_sdk
import json
import os

"""
Creating a new product using the Finite State SDK Methods
To create a Product, you will need:

* Business Unit ID (get this from the API or app, see this example)
* Created By User ID (get this from the API)
* Product Name (you make this up)
* Product Description (you make this up)
* Vendor Name (you can get an existing vendor ID, or you can make this up to create a new Vendor)

To install the SDK, use pip:
pip install finite-state-sdk
"""

"""
You can store your secrets in a file called .env in the same directory as this script
that looks like:

export CLIENT_ID="your client id"
export CLIENT_SECRET="your client secret"
export ORGANIZATION_CONTEXT="your organization context"

Before running the script, run the following command in the terminal:
source .env

DO NOT COMMIT THIS FILE TO YOUR SOURCE CODE REPOSITORY!!!
"""

# get CLIENT_ID and CLIENT_SECRET from env
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ORGANIZATION_CONTEXT = os.environ.get("ORGANIZATION_CONTEXT")


# Get an auth token - this is a bearer token that you will use for all subsequent requests
# The token is valid for 24 hours
token = finite_state_sdk.get_auth_token(CLIENT_ID, CLIENT_SECRET)

# get all business units to get the business_unit_id
business_units = finite_state_sdk.get_all_business_units(token, ORGANIZATION_CONTEXT)
# print(json.dumps(business_units, indent=4))

"""
Example Response:
[
    {
        "_cursor": "{\"id\":\"2581488428\"}",
        "id": "2581488428",
        "name": "Finite State Products"
    }
]
"""

# You can also get this from the app by clicking Account and navigating to the Business Unit
business_unit_id = ""  # CHANGEME: Get the business unit ID of the BU that owns the product

# get all users to get the user id
users = finite_state_sdk.get_all_users(token, ORGANIZATION_CONTEXT)
print(json.dumps(users, indent=4))

"""
Example Response:
[
    {
        "_cursor": "{\"id\":\"1625274673\"}",
        "id": "1625274673",
        "email": "nicholas@finitestate.io"
    }
]
"""
# You can also get this from the app by clicking Account and navigating to the User
created_by_user_id = ""  # CHANGEME: Get the user ID to associate with the creation of the product

product_name = "My New Product"
product_description = "This is a new product created by the SDK"
vendor_name = "My New Vendor"

# create the product
product = finite_state_sdk.create_product(token, ORGANIZATION_CONTEXT, business_unit_id=business_unit_id, created_by_user_id=created_by_user_id, product_name=product_name, product_description=product_description, vendor_name=vendor_name)
print("Created the product:")
print(json.dumps(product, indent=4))

"""
Example Response:
{
    "createProduct": {
        "id": "2620271926",
        "name": "Nicholas Python API Created Product 2023-07-19-1026",
        "vendor": {
            "name": "My New Vendor"
        },
        "group": {
            "id": "2620270956",
            "name": "API Testing Business Unit"
        },
        "createdBy": {
            "id": "1625274673",
            "email": "nicholas@finitestate.io"
        },
        "ctx": {
            "businessUnit": "2620270956"
        }
    }
}
"""