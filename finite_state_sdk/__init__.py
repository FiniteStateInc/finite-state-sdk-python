import json
from enum import Enum

import requests
import time
from warnings import warn
import finite_state_sdk.queries as queries

API_URL = 'https://platform.finitestate.io/api/v1/graphql'
AUDIENCE = "https://platform.finitestate.io/api/v1/graphql"
TOKEN_URL = "https://platform.finitestate.io/api/v1/auth/token"

"""
DEFAULT CHUNK SIZE: 1000 MiB
"""
DEFAULT_CHUNK_SIZE = 1024**2 * 1000
"""
MAX CHUNK SIZE: 2 GiB
"""
MAX_CHUNK_SIZE = 1024**2 * 2000
"""
MIN CHUNK SIZE: 5 MiB
"""
MIN_CHUNK_SIZE = 1024**2 * 5


class UploadMethod(Enum):
    """
    Enumeration class representing different upload methods.

    Attributes:
        WEB_APP_UI: Upload method via web application UI.
        API: Upload method via API.
        GITHUB_INTEGRATION: Upload method via GitHub integration.
        AZURE_DEVOPS_INTEGRATION: Upload method via Azure DevOps integration.

    To use any value from this enumeration, use UploadMethod.<attribute> i.e. finite_state_sdk.UploadMethod.WEB_APP_UI
    """
    WEB_APP_UI = "WEB_APP_UI"
    API = "API"
    GITHUB_INTEGRATION = "GITHUB_INTEGRATION"
    AZURE_DEVOPS_INTEGRATION = "AZURE_DEVOPS_INTEGRATION"


def create_artifact(
    token,
    organization_context,
    business_unit_id=None,
    created_by_user_id=None,
    asset_version_id=None,
    artifact_name=None,
    product_id=None,
):
    """
    Create a new Artifact.
    This is an advanced method - you are probably looking for create_new_asset_version_and_upload_test_results or create_new_asset_version_and_upload_binary.
    Please see the examples in the Github repository for more information:
    - https://github.com/FiniteStateInc/finite-state-sdk-python/blob/main/examples/upload_test_results.py
    - https://github.com/FiniteStateInc/finite-state-sdk-python/blob/main/examples/uploading_a_binary.py

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the artifact with.
        created_by_user_id (str, required):
            User ID of the user creating the artifact.
        asset_version_id (str, required):
            Asset Version ID to associate the artifact with.
        artifact_name (str, required):
            The name of the Artifact being created.
        product_id (str, optional):
            Product ID to associate the artifact with. If not specified, the artifact will not be associated with a product.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_version_id, or artifact_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createArtifact Object
    """
    if not business_unit_id:
        raise ValueError("Business unit ID is required")
    if not created_by_user_id:
        raise ValueError("Created by user ID is required")
    if not asset_version_id:
        raise ValueError("Asset version ID is required")
    if not artifact_name:
        raise ValueError("Artifact name is required")

    graphql_query = """
    mutation CreateArtifactMutation_SDK($input: CreateArtifactInput!) {
        createArtifact(input: $input) {
            id
            name
            assetVersion {
                id
                name
                asset {
                    id
                    name
                }
            }
            createdBy {
                id
                email
            }
            ctx {
                asset
                products
                businessUnits
            }
        }
    }
    """

    # Asset name, business unit context, and creating user are required
    variables = {
        "input": {
            "name": artifact_name,
            "createdBy": created_by_user_id,
            "assetVersion": asset_version_id,
            "ctx": {
                "asset": asset_version_id,
                "businessUnits": [business_unit_id]
            }
        }
    }

    if product_id is not None:
        variables["input"]["ctx"]["products"] = product_id

    response = send_graphql_query(token, organization_context, graphql_query, variables)
    return response['data']


def create_asset(token, organization_context, business_unit_id=None, created_by_user_id=None, asset_name=None, product_id=None):
    """
    Create a new Asset.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the asset with.
        created_by_user_id (str, required):
            User ID of the user creating the asset.
        asset_name (str, required):
            The name of the Asset being created.
        product_id (str, optional):
            Product ID to associate the asset with. If not specified, the asset will not be associated with a product.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, or asset_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createAsset Object
    """
    if not business_unit_id:
        raise ValueError("Business unit ID is required")
    if not created_by_user_id:
        raise ValueError("Created by user ID is required")
    if not asset_name:
        raise ValueError("Asset name is required")

    graphql_query = """
    mutation CreateAssetMutation_SDK($input: CreateAssetInput!) {
        createAsset(input: $input) {
            id
            name
            dependentProducts {
                id
                name
            }
            group {
                id
                name
            }
            createdBy {
                id
                email
            }
            ctx {
                asset
                products
                businessUnits
            }
        }
    }
    """

    # Asset name, business unit context, and creating user are required
    variables = {
        "input": {
            "name": asset_name,
            "group": business_unit_id,
            "createdBy": created_by_user_id,
            "ctx": {
                "businessUnits": [business_unit_id]
            }
        }
    }

    if product_id is not None:
        variables["input"]["ctx"]["products"] = product_id

    response = send_graphql_query(token, organization_context, graphql_query, variables)
    return response['data']


def create_asset_version(
    token,
    organization_context,
    business_unit_id=None,
    created_by_user_id=None,
    asset_id=None,
    asset_version_name=None,
    product_id=None,
):
    """
    Create a new Asset Version.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the asset version with.
        created_by_user_id (str, required):
            User ID of the user creating the asset version.
        asset_id (str, required):
            Asset ID to associate the asset version with.
        asset_version_name (str, required):
            The name of the Asset Version being created.
        product_id (str, optional):
            Product ID to associate the asset version with. If not specified, the asset version will not be associated with a product.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_id, or asset_version_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createAssetVersion Object

    deprecated:: 0.1.7. Use create_asset_version_on_asset instead.
    """
    warn('`create_asset_version` is deprecated. Use: `create_asset_version_on_asset instead`', DeprecationWarning, stacklevel=2)
    if not business_unit_id:
        raise ValueError("Business unit ID is required")
    if not created_by_user_id:
        raise ValueError("Created by user ID is required")
    if not asset_id:
        raise ValueError("Asset ID is required")
    if not asset_version_name:
        raise ValueError("Asset version name is required")

    graphql_query = """
    mutation CreateAssetVersionMutation_SDK($input: CreateAssetVersionInput!) {
        createAssetVersion(input: $input) {
            id
            name
            asset {
                id
                name
            }
            createdBy {
                id
                email
            }
            ctx {
                asset
                products
                businessUnits
            }
        }
    }
    """

    # Asset name, business unit context, and creating user are required
    variables = {
        "input": {
            "name": asset_version_name,
            "createdBy": created_by_user_id,
            "asset": asset_id,
            "ctx": {
                "asset": asset_id,
                "businessUnits": [business_unit_id]
            }
        }
    }

    if product_id is not None:
        variables["input"]["ctx"]["products"] = product_id

    response = send_graphql_query(token, organization_context, graphql_query, variables)
    return response['data']


def create_asset_version_on_asset(
    token,
    organization_context,
    created_by_user_id=None,
    asset_id=None,
    asset_version_name=None,
    product_id=None,
):
    """
    Create a new Asset Version.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        created_by_user_id (str, optional):
            User ID of the user creating the asset version.
        asset_id (str, required):
            Asset ID to associate the asset version with.
        asset_version_name (str, required):
            The name of the Asset Version being created.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_id, or asset_version_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createAssetVersion Object
    """
    if not asset_id:
        raise ValueError("Asset ID is required")
    if not asset_version_name:
        raise ValueError("Asset version name is required")

    graphql_query = """
        mutation BapiCreateAssetVersion_SDK($assetVersionName: String!, $assetId: ID!, $createdByUserId: ID!, $productId: ID) {
            createNewAssetVersionOnAsset(assetVersionName: $assetVersionName, assetId: $assetId, createdByUserId: $createdByUserId, productId: $productId) {
                id
                assetVersion {
                    id
                }
            }
        }
    """

    # Asset name, business unit context, and creating user are required
    variables = {"assetVersionName": asset_version_name, "assetId": asset_id}

    if created_by_user_id:
        variables["createdByUserId"] = created_by_user_id

    if product_id:
        variables["productId"] = product_id

    response = send_graphql_query(token, organization_context, graphql_query, variables)
    return response['data']


def create_new_asset_version_artifact_and_test_for_upload(
    token,
    organization_context,
    business_unit_id=None,
    created_by_user_id=None,
    asset_id=None,
    version=None,
    product_id=None,
    test_type=None,
    artifact_description=None,
    upload_method: UploadMethod = UploadMethod.API,
):
    """
    Creates the entities needed for uploading a file for Binary Analysis or test results from a third party scanner to an existing Asset. This will create a new Asset Version, Artifact, and Test.
    This method is used by the upload_file_for_binary_analysis and upload_test_results_file methods, which are generally easier to use for basic use cases.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, optional):
            Business Unit ID to create the asset version for. If not provided, the default Business Unit will be used.
        created_by_user_id (str, optional):
            User ID that will be the creator of the asset version. If not specified, the creator of the related Asset will be used.
        asset_id (str, required):
            Asset ID to create the asset version for. If not provided, the default asset will be used.
        version (str, required):
            Version to create the asset version for.
        product_id (str, optional):
            Product ID to create the entities for. If not provided, the default product will be used.
        test_type (str, required):
            Test type to create the test for. Must be one of "finite_state_binary_analysis" or of the list of supported third party test types. For the full list, see the API documenation.
        artifact_description (str, optional):
            Description to use for the artifact. Examples inlcude "Firmware", "Source Code Repository". This will be appended to the default Artifact description. If none is provided, the default Artifact description will be used.
        upload_method (UploadMethod, optional):
            The method of uploading the test results. Default is UploadMethod.API.


    Raises:
        ValueError: Raised if asset_id or version are not provided.
        Exception: Raised if the query fails.

    Returns:
        str: The Test ID of the newly created test that is used for uploading the file.
    """
    if not asset_id:
        raise ValueError("Asset ID is required")
    if not version:
        raise ValueError("Version is required")

    assets = get_all_assets(token, organization_context, asset_id=asset_id)
    if not assets:
        raise ValueError("No assets found with the provided asset ID")
    asset = assets[0]

    # get the asset name
    asset_name = asset['name']

    # get the existing asset product IDs
    asset_product_ids = asset['ctx']['products']

    # get the asset product ID
    if product_id and product_id not in asset_product_ids:
        asset_product_ids.append(product_id)

    # if business_unit_id or created_by_user_id are not provided, get the existing asset
    if not business_unit_id or not created_by_user_id:
        if not business_unit_id:
            business_unit_id = asset['group']['id']
        if not created_by_user_id:
            created_by_user_id = asset['createdBy']['id']

        if not business_unit_id:
            raise ValueError("Business Unit ID is required and could not be retrieved from the existing asset")
        if not created_by_user_id:
            raise ValueError("Created By User ID is required and could not be retrieved from the existing asset")

    # create the asset version
    response = create_asset_version_on_asset(
        token, organization_context, created_by_user_id=created_by_user_id, asset_id=asset_id, asset_version_name=version, product_id=product_id
    )
    # get the asset version ID
    asset_version_id = response['createNewAssetVersionOnAsset']['assetVersion']['id']

    # create the test
    if test_type == "finite_state_binary_analysis":
        # create the artifact
        if not artifact_description:
            artifact_description = "Binary"
        binary_artifact_name = f"{asset_name} {version} - {artifact_description}"
        response = create_artifact(token, organization_context, business_unit_id=business_unit_id,
                                   created_by_user_id=created_by_user_id, asset_version_id=asset_version_id,
                                   artifact_name=binary_artifact_name, product_id=asset_product_ids)

        # get the artifact ID
        binary_artifact_id = response['createArtifact']['id']

        # create the test
        test_name = f"{asset_name} {version} - Finite State Binary Analysis"
        response = create_test_as_binary_analysis(token, organization_context, business_unit_id=business_unit_id,
                                                  created_by_user_id=created_by_user_id, asset_id=asset_id,
                                                  artifact_id=binary_artifact_id, product_id=asset_product_ids,
                                                  test_name=test_name, upload_method=upload_method)
        test_id = response['createTest']['id']
        return test_id

    else:
        # create the artifact
        if not artifact_description:
            artifact_description = "Unspecified Artifact"
        artifact_name = f"{asset_name} {version} - {artifact_description}"
        response = create_artifact(token, organization_context, business_unit_id=business_unit_id,
                                   created_by_user_id=created_by_user_id, asset_version_id=asset_version_id,
                                   artifact_name=artifact_name, product_id=asset_product_ids)

        # get the artifact ID
        binary_artifact_id = response['createArtifact']['id']

        # create the test
        test_name = f"{asset_name} {version} - {test_type}"
        response = create_test_as_third_party_scanner(token, organization_context, business_unit_id=business_unit_id,
                                                      created_by_user_id=created_by_user_id, asset_id=asset_id,
                                                      artifact_id=binary_artifact_id, product_id=asset_product_ids,
                                                      test_name=test_name, test_type=test_type,
                                                      upload_method=upload_method)
        test_id = response['createTest']['id']
        return test_id


def create_new_asset_version_and_upload_binary(
    token,
    organization_context,
    business_unit_id=None,
    created_by_user_id=None,
    asset_id=None,
    version=None,
    file_path=None,
    product_id=None,
    artifact_description=None,
    quick_scan=False,
    upload_method: UploadMethod = UploadMethod.API,
):
    """
    Creates a new Asset Version for an existing asset, and uploads a binary file for Finite State Binary Analysis.
    By default, this uses the existing Business Unit and Created By User for the Asset. If you need to change these, you can provide the IDs for them.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, optional):
            Business Unit ID to create the asset version for. If not provided, the existing Business Unit for the Asset will be used.
        created_by_user_id (str, optional):
            Created By User ID to create the asset version for. If not provided, the existing Created By User for the Asset will be used.
        asset_id (str, required):
            Asset ID to create the asset version for.
        version (str, required):
            Version to create the asset version for.
        file_path (str, required):
            Local path to the file to upload.
        product_id (str, optional):
            Product ID to create the asset version for. If not provided, the existing Product for the Asset will be used, if it exists.
        artifact_description (str, optional):
            Description of the artifact. If not provided, the default is "Firmware Binary".
        quick_scan (bool, optional):
            If True, will upload the file for quick scan. Defaults to False (Full Scan). For details about Quick Scan vs Full Scan, please see the API documentation.
        upload_method (UploadMethod, optional):
            The method of uploading the test results. Default is UploadMethod.API.

    Raises:
        ValueError: Raised if asset_id, version, or file_path are not provided.
        Exception: Raised if any of the queries fail.

    Returns:
        dict: The response from the GraphQL query, a createAssetVersion Object.
    """
    if not asset_id:
        raise ValueError("Asset ID is required")
    if not version:
        raise ValueError("Version is required")
    if not file_path:
        raise ValueError("File path is required")

    # create the asset version and binary test
    if not artifact_description:
        artifact_description = "Firmware Binary"
    binary_test_id = create_new_asset_version_artifact_and_test_for_upload(
        token,
        organization_context,
        business_unit_id=business_unit_id,
        created_by_user_id=created_by_user_id,
        asset_id=asset_id,
        version=version,
        product_id=product_id,
        test_type="finite_state_binary_analysis",
        artifact_description=artifact_description,
        upload_method=upload_method,
    )

    # upload file for binary test
    response = upload_file_for_binary_analysis(token, organization_context, test_id=binary_test_id, file_path=file_path,
                                               quick_scan=quick_scan)
    return response


def create_new_asset_version_and_upload_test_results(token, organization_context, business_unit_id=None,
                                                     created_by_user_id=None, asset_id=None, version=None,
                                                     file_path=None, product_id=None, test_type=None,
                                                     artifact_description="", upload_method: UploadMethod = UploadMethod.API):
    """
    Creates a new Asset Version for an existing asset, and uploads test results for that asset version.
    By default, this uses the existing Business Unit and Created By User for the Asset. If you need to change these, you can provide the IDs for them.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, optional):
            Business Unit ID to create the asset version for. If not provided, the existing Business Unit for the Asset will be used.
        created_by_user_id (str, optional):
            Created By User ID to create the asset version for. If not provided, the existing Created By User for the Asset will be used.
        asset_id (str, required):
            Asset ID to create the asset version for.
        version (str, required):
            Version to create the asset version for.
        file_path (str, required):
            Path to the test results file to upload.
        product_id (str, optional):
            Product ID to create the asset version for. If not provided, the existing Product for the Asset will be used.
        test_type (str, required):
            Test type. This must be one of the list of supported third party scanner types. For the full list of supported third party scanner types, see the Finite State API documentation.
        artifact_description (str, optional):
            Description of the artifact being scanned (e.g. "Source Code Repository", "Container Image"). If not provided, the default artifact description will be used.
        upload_method (UploadMethod, optional):
            The method of uploading the test results. Default is UploadMethod.API.

    Raises:
        ValueError: If the asset_id, version, or file_path are not provided.
        Exception: If the test_type is not a supported third party scanner type, or if the query fails.

    Returns:
        dict: The response from the GraphQL query, a createAssetVersion Object.
    """
    if not asset_id:
        raise ValueError("Asset ID is required")
    if not version:
        raise ValueError("Version is required")
    if not file_path:
        raise ValueError("File path is required")
    if not test_type:
        raise ValueError("Test type is required")

    # create the asset version and test
    test_id = create_new_asset_version_artifact_and_test_for_upload(token, organization_context,
                                                                    business_unit_id=business_unit_id,
                                                                    created_by_user_id=created_by_user_id,
                                                                    asset_id=asset_id, version=version,
                                                                    product_id=product_id, test_type=test_type,
                                                                    artifact_description=artifact_description,
                                                                    upload_method=upload_method)

    # upload test results file
    response = upload_test_results_file(token, organization_context, test_id=test_id, file_path=file_path)
    return response


def create_product(token, organization_context, business_unit_id=None, created_by_user_id=None, product_name=None,
                   product_description=None, vendor_id=None, vendor_name=None):
    """
    Create a new Product.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the product with.
        created_by_user_id (str, required):
            User ID of the user creating the product.
        product_name (str, required):
            The name of the Product being created.
        product_description (str, optional):
            The description of the Product being created.
        vendor_id (str, optional):
            Vendor ID to associate the product with. If not specified, vendor_name must be provided.
        vendor_name (str, optional):
            Vendor name to associate the product with. This is used to create the Vendor if the vendor does not currently exist.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, or product_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createProduct Object
    """

    if not business_unit_id:
        raise ValueError("Business unit ID is required")
    if not created_by_user_id:
        raise ValueError("Created by user ID is required")
    if not product_name:
        raise ValueError("Product name is required")

    graphql_query = """
    mutation CreateProductMutation_SDK($input: CreateProductInput!) {
        createProduct(input: $input) {
            id
            name
            vendor {
                name
            }
            group {
                id
                name
            }
            createdBy {
                id
                email
            }
            ctx {
                businessUnit
            }
        }
    }
    """

    # Product name, business unit context, and creating user are required
    variables = {
        "input": {
            "name": product_name,
            "group": business_unit_id,
            "createdBy": created_by_user_id,
            "ctx": {
                "businessUnit": business_unit_id
            }
        }
    }

    if product_description is not None:
        variables["input"]["description"] = product_description

    # If the vendor ID is specified, this will link the new product to the existing vendor
    if vendor_id is not None:
        variables["input"]["vendor"] = {
            "id": vendor_id
        }

    # If the vendor name is specified, this will create a new vendor and link it to the new product
    if vendor_name is not None:
        variables["input"]["createVendor"] = {
            "name": vendor_name
        }

    response = send_graphql_query(token, organization_context, graphql_query, variables)

    return response['data']


def create_test(
    token,
    organization_context,
    business_unit_id=None,
    created_by_user_id=None,
    asset_id=None,
    artifact_id=None,
    test_name=None,
    product_id=None,
    test_type=None,
    tools=[],
    upload_method: UploadMethod = UploadMethod.API,
):
    """
    Create a new Test object for uploading files.
    This is an advanced method - you are probably looking for create_new_asset_version_and_upload_test_results or create_new_asset_version_and_upload_binary.
    Please see the examples in the Github repository for more information:
    - https://github.com/FiniteStateInc/finite-state-sdk-python/blob/main/examples/upload_test_results.py
    - https://github.com/FiniteStateInc/finite-state-sdk-python/blob/main/examples/uploading_a_binary.py

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the Test with.
        created_by_user_id (str, required):
            User ID of the user creating the Test.
        asset_id (str, required):
            Asset ID to associate the Test with.
        artifact_id (str, required):
            Artifact ID to associate the Test with.
        test_name (str, required):
            The name of the Test being created.
        product_id (str, optional):
            Product ID to associate the Test with. If not specified, the Test will not be associated with a product.
        test_type (str, required):
            The type of test being created. Valid values are "cyclonedx" and "finite_state_binary_analysis".
        tools (list, optional):
            List of Tool objects used to perform the test. Each Tool object is a dict that should have a "name" and "description" field. This is used to describe the actual scanner that was used to perform the test.
        upload_method (UploadMethod, required):
            The method of uploading the test results.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_id, artifact_id, test_name, or test_type are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createTest Object
    """
    if not business_unit_id:
        raise ValueError("Business unit ID is required")
    if not created_by_user_id:
        raise ValueError("Created by user ID is required")
    if not asset_id:
        raise ValueError("Asset ID is required")
    if not artifact_id:
        raise ValueError("Artifact ID is required")
    if not test_name:
        raise ValueError("Test name is required")
    if not test_type:
        raise ValueError("Test type is required")

    graphql_query = """
    mutation CreateTestMutation_SDK($input: CreateTestInput!) {
        createTest(input: $input) {
            id
            name
            artifactUnderTest {
                id
                name
                assetVersion {
                    id
                    name
                    asset {
                        id
                        name
                        dependentProducts {
                            id
                            name
                        }
                    }
                }
            }
            createdBy {
                id
                email
            }
            ctx {
                asset
                products
                businessUnits
            }
            uploadMethod
        }
    }
    """

    # Asset name, business unit context, and creating user are required
    variables = {
        "input": {
            "name": test_name,
            "createdBy": created_by_user_id,
            "artifactUnderTest": artifact_id,
            "testResultFileFormat": test_type,
            "ctx": {
                "asset": asset_id,
                "businessUnits": [business_unit_id]
            },
            "tools": tools,
            "uploadMethod": upload_method.value
        }
    }

    if product_id is not None:
        variables["input"]["ctx"]["products"] = product_id

    response = send_graphql_query(token, organization_context, graphql_query, variables)
    return response['data']


def create_test_as_binary_analysis(token, organization_context, business_unit_id=None, created_by_user_id=None,
                                   asset_id=None, artifact_id=None, test_name=None, product_id=None,
                                   upload_method: UploadMethod = UploadMethod.API):
    """
    Create a new Test object for uploading files for Finite State Binary Analysis.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the Test with.
        created_by_user_id (str, required):
            User ID of the user creating the Test.
        asset_id (str, required):
            Asset ID to associate the Test with.
        artifact_id (str, required):
            Artifact ID to associate the Test with.
        test_name (str, required):
            The name of the Test being created.
        product_id (str, optional):
            Product ID to associate the Test with. If not specified, the Test will not be associated with a product.
        upload_method (UploadMethod, optional):
            The method of uploading the test results. Default is UploadMethod.API.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_id, artifact_id, or test_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createTest Object
    """
    tools = [
        {
            "description": "SBOM and Vulnerability Analysis from Finite State Binary SCA and Binary SAST.",
            "name": "Finite State Binary Analysis"
        }
    ]
    return create_test(token, organization_context, business_unit_id=business_unit_id,
                       created_by_user_id=created_by_user_id, asset_id=asset_id, artifact_id=artifact_id,
                       test_name=test_name, product_id=product_id, test_type="finite_state_binary_analysis",
                       tools=tools, upload_method=upload_method)


def create_test_as_cyclone_dx(
    token,
    organization_context,
    business_unit_id=None,
    created_by_user_id=None,
    asset_id=None,
    artifact_id=None,
    test_name=None,
    product_id=None,
    upload_method: UploadMethod = UploadMethod.API,
):
    """
    Create a new Test object for uploading CycloneDX files.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the Test with.
        created_by_user_id (str, required):
            User ID of the user creating the Test.
        asset_id (str, required):
            Asset ID to associate the Test with.
        artifact_id (str, required):
            Artifact ID to associate the Test with.
        test_name (str, required):
            The name of the Test being created.
        product_id (str, optional):
            Product ID to associate the Test with. If not specified, the Test will not be associated with a product.
        upload_method (UploadMethod, optional):
            The method of uploading the test results. Default is UploadMethod.API.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_id, artifact_id, or test_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createTest Object
    """
    return create_test(token, organization_context, business_unit_id=business_unit_id,
                       created_by_user_id=created_by_user_id, asset_id=asset_id, artifact_id=artifact_id,
                       test_name=test_name, product_id=product_id, test_type="cyclonedx", upload_method=upload_method)


def create_test_as_third_party_scanner(token, organization_context, business_unit_id=None, created_by_user_id=None,
                                       asset_id=None, artifact_id=None, test_name=None, product_id=None, test_type=None,
                                       upload_method: UploadMethod = UploadMethod.API):
    """
    Create a new Test object for uploading Third Party Scanner files.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        business_unit_id (str, required):
            Business Unit ID to associate the Test with.
        created_by_user_id (str, required):
            User ID of the user creating the Test.
        asset_id (str, required):
            Asset ID to associate the Test with.
        artifact_id (str, required):
            Artifact ID to associate the Test with.
        test_name (str, required):
            The name of the Test being created.
        product_id (str, optional):
            Product ID to associate the Test with. If not specified, the Test will not be associated with a product.
        test_type (str, required):
            Test type of the scanner which indicates the output file format from the scanner. Valid values are "cyclonedx" and others. For the full list see the API documentation.
        upload_method (UploadMethod, optional):
            The method of uploading the test results. Default is UploadMethod.API.

    Raises:
        ValueError: Raised if business_unit_id, created_by_user_id, asset_id, artifact_id, or test_name are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: createTest Object
    """
    return create_test(token, organization_context, business_unit_id=business_unit_id,
                       created_by_user_id=created_by_user_id, asset_id=asset_id, artifact_id=artifact_id,
                       test_name=test_name, product_id=product_id, test_type=test_type, upload_method=upload_method)


def download_asset_version_report(token, organization_context, asset_version_id=None, report_type=None,
                                  report_subtype=None, output_filename=None, verbose=False):
    """
    Download a report for a specific asset version and save it to a local file. This is a blocking call, and can sometimes take minutes to return if the report is very large.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_version_id (str, required):
            The Asset Version ID to download the report for.
        report_type (str, required):
            The file type of the report to download. Valid values are "CSV" and "PDF".
        report_subtype (str, required):
            The type of report to download. Based on available reports for the `report_type` specified
            Valid values for CSV are "ALL_FINDINGS", "ALL_COMPONENTS", "EXPLOIT_INTELLIGENCE".
            Valid values for PDF are "RISK_SUMMARY".
        output_filename (str, optional):
            The local filename to save the report to. If not provided, the report will be saved to a file named "report.csv" or "report.pdf" in the current directory based on the report type.
        verbose (bool, optional):
            If True, will print additional information to the console. Defaults to False.

    Raises:
        ValueError: Raised if required parameters are not provided.
        Exception: Raised if the query fails.

    Returns:
        None
    """
    url = generate_report_download_url(token, organization_context, asset_version_id=asset_version_id,
                                       report_type=report_type, report_subtype=report_subtype, verbose=verbose)

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open a local file in binary write mode and write the content to it
        if verbose:
            print("File downloaded successfully.")
        with open(output_filename, 'wb') as file:
            file.write(response.content)
            if verbose:
                print(f'Wrote file to {output_filename}')
    else:
        raise Exception(f"Failed to download the file. Status code: {response.status_code}")


def download_product_report(token, organization_context, product_id=None, report_type=None, report_subtype=None,
                            output_filename=None, verbose=False):
    """
    Download a report for a specific product and save it to a local file. This is a blocking call, and can sometimes take minutes to return if the report is very large.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        product_id (str, required):
            The Product ID to download the report for.
        report_type (str, required):
            The file type of the report to download. Valid values are "CSV".
        report_subtype (str, required):
            The type of report to download. Based on available reports for the `report_type` specified
            Valid values for CSV are "ALL_FINDINGS".
        output_filename (str, optional):
            The local filename to save the report to. If not provided, the report will be saved to a file named "report.csv" or "report.pdf" in the current directory based on the report type.
        verbose (bool, optional):
            If True, will print additional information to the console. Defaults to False.
    """
    url = generate_report_download_url(token, organization_context, product_id=product_id, report_type=report_type,
                                       report_subtype=report_subtype, verbose=verbose)

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open a local file in binary write mode and write the content to it
        if verbose:
            print("File downloaded successfully.")
        with open(output_filename, 'wb') as file:
            file.write(response.content)
            if verbose:
                print(f'Wrote file to {output_filename}')
    else:
        raise Exception(f"Failed to download the file. Status code: {response.status_code}")


def download_sbom(token, organization_context, sbom_type="CYCLONEDX", sbom_subtype="SBOM_ONLY", asset_version_id=None,
                  output_filename="sbom.json", verbose=False):
    """
    Download an SBOM for an Asset Version and save it to a local file. This is a blocking call, and can sometimes take minutes to return if the SBOM is very large.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        sbom_type (str, required):
            The type of SBOM to download. Valid values are "CYCLONEDX" and "SPDX". Defaults to "CYCLONEDX".
        sbom_subtype (str, required):
            The subtype of SBOM to download. Valid values for CycloneDX are "SBOM_ONLY", "SBOM_WITH_VDR", "VDR_ONLY. For SPDX valid values are "SBOM_ONLY". Defaults to "SBOM_ONLY".
        asset_version_id (str, required):
            The Asset Version ID to download the SBOM for.
        output_filename (str, required):
            The local filename to save the SBOM to. If not provided, the SBOM will be saved to a file named "sbom.json" in the current directory.
        verbose (bool, optional):
            If True, will print additional information to the console. Defaults to False.

    Raises:
        ValueError: Raised if required parameters are not provided.
        Exception: Raised if the query fails.

    Returns:
        None
    """
    url = generate_sbom_download_url(token, organization_context, sbom_type=sbom_type, sbom_subtype=sbom_subtype,
                                     asset_version_id=asset_version_id, verbose=verbose)

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open a local file in binary write mode and write the content to it
        if verbose:
            print("File downloaded successfully.")
        with open(output_filename, 'wb') as file:
            file.write(response.content)
            if verbose:
                print(f'Wrote file to {output_filename}')
    else:
        raise Exception(f"Failed to download the file. Status code: {response.status_code}")


def file_chunks(file_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Helper method to read a file in chunks.

    Args:
        file_path (str):
            Local path to the file to read.
        chunk_size (int, optional):
            The size of the chunks to read. Defaults to DEFAULT_CHUNK_SIZE.

    Yields:
        bytes: The next chunk of the file.

    Raises:
        FileIO Exceptions: Raised if the file cannot be opened or read correctly.
    """
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if chunk:
                yield chunk
            else:
                break


def get_all_artifacts(token, organization_context, artifact_id=None, business_unit_id=None):
    """
    Get all artifacts in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        artifact_id (str, optional):
            An optional Artifact ID if this is used to get a single artifact, by default None
        business_unit_id (str, optional):
            An optional Business Unit ID if this is used to get artifacts for a single business unit, by default None

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of Artifact Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_ARTIFACTS['query'],
                                     queries.ALL_ARTIFACTS['variables'](artifact_id, business_unit_id), 'allAssets')


def get_all_assets(token, organization_context, asset_id=None, business_unit_id=None):
    """
    Gets all assets in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_id (str, optional):
            Asset ID to get, by default None. If None specified, will get all Assets. If specified, will get only the Asset with that ID.
        business_unit_id (str, optional):
            Business Unit ID to filter by, by default None. If None specified, will get all Assets. If specified, will get only the Assets in the specified Business Unit.

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of Asset Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_ASSETS['query'],
                                     queries.ALL_ASSETS['variables'](asset_id, business_unit_id), 'allAssets')


def get_all_asset_versions(token, organization_context):
    """
    Get all asset versions in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of AssetVersion Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_ASSET_VERSIONS['query'],
                                     queries.ALL_ASSET_VERSIONS['variables'], 'allAssetVersions')


def get_all_asset_versions_for_product(token, organization_context, product_id):
    """
    Get all asset versions for a product. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        product_id (str):
            The Product ID to get asset versions for

    Returns:
        list: List of AssetVersion Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ONE_PRODUCT_ALL_ASSET_VERSIONS['query'],
                                     queries.ONE_PRODUCT_ALL_ASSET_VERSIONS['variables'](product_id), 'allProducts')


def get_all_business_units(token, organization_context):
    """
    Get all business units in the organization. NOTE: The return type here is Group. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of Group Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_BUSINESS_UNITS['query'],
                                     queries.ALL_BUSINESS_UNITS['variables'], 'allGroups')


def get_all_organizations(token, organization_context):
    """
    Get all organizations available to the user. For most users there is only one organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of Organization Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_ORGANIZATIONS['query'],
                                     queries.ALL_ORGANIZATIONS['variables'], 'allOrganizations')


def get_all_paginated_results(token, organization_context, query, variables=None, field=None, limit=None):
    """
    Get all results from a paginated GraphQL query

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        query (str):
            The GraphQL query string
        variables (dict, optional):
            Variables to be used in the GraphQL query, by default None
        field (str, required):
            The field in the response JSON that contains the results
        limit (int, Optional):
            The maximum number of results to return. By default, None to return all results. Limit cannot be greater than 1000.

    Raises:
        Exception: If the response status code is not 200, or if the field is not in the response JSON

    Returns:
        list: List of results
    """

    if not field:
        raise Exception("Error: field is required")
    if limit and limit > 1000:
        raise Exception("Error: limit cannot be greater than 1000")
    if limit and limit < 1:
        raise Exception("Error: limit cannot be less than 1")
    if not variables["first"]:
        raise Exception("Error: first is required")
    if variables["first"] < 1:
        raise Exception("Error: first cannot be less than 1")
    if variables["first"] > 1000:
        raise Exception("Error: limit cannot be greater than 1000")

    # query the API for the first page of results
    response_data = send_graphql_query(token, organization_context, query, variables)

    # if there are no results, return an empty list
    if not response_data:
        return []

    # create a list to store the results
    results = []

    # add the first page of results to the list
    if field in response_data['data']:
        results.extend(response_data['data'][field])
    else:
        raise Exception(f"Error: {field} not in response JSON")

    if len(response_data['data'][field]) > 0:
        # get the cursor from the last entry in the list
        cursor = response_data['data'][field][len(response_data['data'][field]) - 1]['_cursor']

        while cursor:
            if limit and len(results) == limit:
                break

            variables['after'] = cursor

            # add the next page of results to the list
            response_data = send_graphql_query(token, organization_context, query, variables)
            results.extend(response_data['data'][field])

            try:
                cursor = response_data['data'][field][len(response_data['data'][field]) - 1]['_cursor']
            except IndexError:
                # when there is no additional cursor, stop getting more pages
                cursor = None

    return results


def get_all_products(token, organization_context):
    """
    Get all products in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of Product Objects

    .. deprecated:: 0.1.4. Use get_products instead.
    """
    warn('`get_all_products` is deprecated. Use: `get_products instead`', DeprecationWarning, stacklevel=2)
    return get_all_paginated_results(token, organization_context, queries.ALL_PRODUCTS['query'],
                                     queries.ALL_PRODUCTS['variables'], 'allProducts')


def get_all_users(token, organization_context):
    """
    Get all users in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of User Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_USERS['query'],
                                     queries.ALL_USERS['variables'], 'allUsers')


def get_artifact_context(token, organization_context, artifact_id):
    """
    Get the context for a single artifact. This is typically used for querying for existing context, which is used for role based access control. This is not used for creating new artifacts.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".

    Raises:
        Exception: Raised if the query fails.

    Returns:
        dict: Artifact Context Object
    """
    artifact = get_all_paginated_results(token, organization_context, queries.ALL_ARTIFACTS['query'],
                                         queries.ALL_ARTIFACTS['variables'](artifact_id, None), 'allAssets')

    return artifact[0]['ctx']


def get_assets(token, organization_context, asset_id=None, business_unit_id=None):
    """
    Gets assets in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_id (str, optional):
            Asset ID to get, by default None. If None specified, will get all Assets. If specified, will get only the Asset with that ID.
        business_unit_id (str, optional):
            Business Unit ID to filter by, by default None. If None specified, will get all Assets. If specified, will get only the Assets in the specified Business Unit.

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of Asset Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_ASSETS['query'],
                                     queries.ALL_ASSETS['variables'](asset_id, business_unit_id), 'allAssets')


def get_asset_versions(token, organization_context, asset_version_id=None, asset_id=None, business_unit_id=None):
    """
    Gets asset versions in the organization. Uses pagination to get all results.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_version_id (str, optional):
            Asset Version ID to get, by default None. If None specified, will get all Asset Versions. If specified, will get only the Asset Version with that ID.
        asset_id (str, optional):
            Asset ID to filter by, by default None. If None specified, will get all Asset Versions. If specified, will get only the Asset Versions for the specified Asset.
        business_unit_id (str, optional):
            Business Unit ID to filter by, by default None. If None specified, will get all Asset Versions. If specified, will get only the Asset Versions in the specified Business Unit.

    Raises:
        Exception: Raised if the query fails.

    Returns:
        list: List of AssetVersion Objects
    """
    return get_all_paginated_results(token, organization_context, queries.ALL_ASSET_VERSIONS['query'],
                                     queries.ALL_ASSET_VERSIONS['variables'](asset_version_id=asset_version_id,
                                                                             asset_id=asset_id,
                                                                             business_unit_id=business_unit_id),
                                     'allAssetVersions')


def get_auth_token(client_id, client_secret, token_url=TOKEN_URL, audience=AUDIENCE):
    """
    Get an auth token for use with the API using CLIENT_ID and CLIENT_SECRET

    Args:
        client_id (str):
            CLIENT_ID as specified in the API documentation
        client_secret (str):
            CLIENT_SECRET as specified in the API documentation
        token_url (str, optional):
            Token URL, by default TOKEN_URL
        audience (str, optional):
            Audience, by default AUDIENCE

    Raises:
        Exception: If the response status code is not 200

    Returns:
        str: Auth token. Use this token as the Authorization header in subsequent API calls.
    """
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": AUDIENCE,
        "grant_type": "client_credentials"
    }

    headers = {
        'content-type': "application/json"
    }

    response = requests.post(TOKEN_URL, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        auth_token = response.json()['access_token']
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

    return auth_token


def get_findings(
    token,
    organization_context,
    asset_version_id=None,
    finding_id=None,
    category=None,
    status=None,
    severity=None,
    count=False,
    limit=None,
):
    """
    Gets all the Findings for an Asset Version. Uses pagination to get all results.
    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_version_id (str, optional):
            Asset Version ID to get findings for. If not provided, will get all findings in the organization.
        finding_id (str, optional):
            The ID of a specific finding to get. If specified, will return only the finding with that ID.
        category (str, optional):
            The category of Findings to return. Valid values are "CONFIG_ISSUES", "CREDENTIALS", "CRYPTO_MATERIAL", "CVE", "SAST_ANALYSIS". If not specified, will return all findings. See https://docs.finitestate.io/types/finding-category.
            This can be a single string, or an array of values.
        status (str, optional):
            The status of Findings to return.
        severity (str, optional):
            The severity of Findings to return. Valid values are "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", and "UNKNOWN". If not specified, will return all findings.
        count (bool, optional):
            If True, will return the count of findings instead of the findings themselves. Defaults to False.
        limit (int, optional):
            The maximum number of findings to return. By default, this is None. Limit must be between 1 and 1000.

    Raises:
        Exception: Raised if the query fails, required parameters are not specified, or parameters are incompatible.

    Returns:
        list: List of Finding Objects
    """

    if limit and limit > 1000:
        raise Exception("Error: limit must be less than 1000")
    if limit and limit < 1:
        raise Exception("Error: limit must be greater than 0")

    if count:
        return send_graphql_query(token, organization_context, queries.GET_FINDINGS_COUNT['query'],
                                  queries.GET_FINDINGS_COUNT['variables'](asset_version_id=asset_version_id,
                                                                          finding_id=finding_id, category=category,
                                                                          status=status, severity=severity,
                                                                          limit=limit))["data"]["_allFindingsMeta"]
    else:
        return get_all_paginated_results(token, organization_context, queries.GET_FINDINGS['query'],
                                         queries.GET_FINDINGS['variables'](asset_version_id=asset_version_id,
                                                                           finding_id=finding_id, category=category,
                                                                           status=status, severity=severity,
                                                                           limit=limit), 'allFindings', limit=limit)


def get_product_asset_versions(token, organization_context, product_id=None):
    """
    Gets all the asset versions for a product.
    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        product_id (str, optional):
            Product ID to get asset versions for. If not provided, will get all asset versions in the organization.
    Raises:
        Exception: Raised if the query fails, required parameters are not specified, or parameters are incompatible.
    Returns:
        list: List of AssetVersion Objects
    """
    if not product_id:
        raise Exception("Product ID is required")

    return get_all_paginated_results(token, organization_context, queries.GET_PRODUCT_ASSET_VERSIONS['query'],
                                     queries.GET_PRODUCT_ASSET_VERSIONS['variables'](product_id), 'allProducts')


def get_products(token, organization_context, product_id=None, business_unit_id=None) -> list:
    """
    Gets all the products for the specified business unit.
    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        product_id (str, optional):
            Product ID to get. If not provided, will get all products in the organization.
        business_unit_id (str, optional):
            Business Unit ID to get products for. If not provided, will get all products in the organization.
    Raises:
        Exception: Raised if the query fails, required parameters are not specified, or parameters are incompatible.
    Returns:
        list: List of Product Objects
    """

    return get_all_paginated_results(token, organization_context, queries.GET_PRODUCTS['query'],
                                     queries.GET_PRODUCTS['variables'](product_id=product_id,
                                                                       business_unit_id=business_unit_id),
                                     'allProducts')


def generate_report_download_url(token, organization_context, asset_version_id=None, product_id=None, report_type=None,
                                 report_subtype=None, verbose=False) -> str:
    """
    Blocking call: Initiates generation of a report, and returns a pre-signed URL for downloading the report.
    This may take several minutes to complete, depending on the size of the report.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_version_id (str, optional):
            Asset Version ID to download the report for. Either `asset_version_id` or `product_id` are required.
        product_id (str, optional):
            Product ID to download the report for. Either `asset_version_id` or `product_id` are required.
        report_type (str, required):
            The file type of the report to download. Valid values are "CSV" and "PDF".
        report_subtype (str, required):
            The type of report to download. Based on available reports for the `report_type` specified
            Valid values for CSV are "ALL_FINDINGS", "ALL_COMPONENTS", "EXPLOIT_INTELLIGENCE".
            Valid values for PDF are "RISK_SUMMARY".
        verbose (bool, optional):
            If True, print additional information to the console. Defaults to False.
    """
    if not report_type:
        raise ValueError("Report Type is required")
    if not report_subtype:
        raise ValueError("Report Subtype is required")
    if not asset_version_id and not product_id:
        raise ValueError("Asset Version ID or Product ID is required")

    if asset_version_id and product_id:
        raise ValueError("Asset Version ID and Product ID are mutually exclusive")

    if report_type not in ["CSV", "PDF"]:
        raise Exception(f"Report Type {report_type} not supported")

    if report_type == "CSV":
        if report_subtype not in ["ALL_FINDINGS", "ALL_COMPONENTS", "EXPLOIT_INTELLIGENCE"]:
            raise Exception(f"Report Subtype {report_subtype} not supported")

        mutation = queries.LAUNCH_REPORT_EXPORT['mutation'](asset_version_id=asset_version_id, product_id=product_id,
                                                            report_type=report_type, report_subtype=report_subtype)
        variables = queries.LAUNCH_REPORT_EXPORT['variables'](asset_version_id=asset_version_id, product_id=product_id,
                                                              report_type=report_type, report_subtype=report_subtype)

        response_data = send_graphql_query(token, organization_context, mutation, variables)
        if verbose:
            print(f'Response Data: {json.dumps(response_data, indent=4)}')

        # get exportJobId from the result
        if asset_version_id:
            export_job_id = response_data['data']['launchArtifactCSVExport']['exportJobId']
        elif product_id:
            export_job_id = response_data['data']['launchProductCSVExport']['exportJobId']
        else:
            raise Exception(
                "Error: Export Job ID not found - this should not happen, please contact your Finite State representative")

        if verbose:
            print(f'Export Job ID: {export_job_id}')

    if report_type == "PDF":
        if report_subtype not in ["RISK_SUMMARY"]:
            raise Exception(f"Report Subtype {report_subtype} not supported")

        mutation = queries.LAUNCH_REPORT_EXPORT['mutation'](asset_version_id=asset_version_id, product_id=product_id,
                                                            report_type=report_type, report_subtype=report_subtype)
        variables = queries.LAUNCH_REPORT_EXPORT['variables'](asset_version_id=asset_version_id, product_id=product_id,
                                                              report_type=report_type, report_subtype=report_subtype)

        response_data = send_graphql_query(token, organization_context, mutation, variables)
        if verbose:
            print(f'Response Data: {json.dumps(response_data, indent=4)}')

        # get exportJobId from the result
        if asset_version_id:
            export_job_id = response_data['data']['launchArtifactPdfExport']['exportJobId']
        elif product_id:
            export_job_id = response_data['data']['launchProductPdfExport']['exportJobId']
        else:
            raise Exception(
                "Error: Export Job ID not found - this should not happen, please contact your Finite State representative")

        if verbose:
            print(f'Export Job ID: {export_job_id}')

    if not export_job_id:
        raise Exception(
            "Error: Export Job ID not found - this should not happen, please contact your Finite State representative")

    # poll the API until the export job is complete
    sleep_time = 10
    total_time = 0
    if verbose:
        print(f'Polling every {sleep_time} seconds for export job to complete')

    while True:
        time.sleep(sleep_time)
        total_time += sleep_time
        if verbose:
            print(f'Total time elapsed: {total_time} seconds')

        query = queries.GENERATE_EXPORT_DOWNLOAD_PRESIGNED_URL['query']
        variables = queries.GENERATE_EXPORT_DOWNLOAD_PRESIGNED_URL['variables'](export_job_id)

        response_data = send_graphql_query(token, organization_context, query, variables)

        if verbose:
            print(f'Response Data: {json.dumps(response_data, indent=4)}')

        if response_data['data']['generateExportDownloadPresignedUrl']['status'] == 'COMPLETED':
            if response_data['data']['generateExportDownloadPresignedUrl']['downloadLink']:
                if verbose:
                    print(
                        f'Export Job Complete. Download URL: {response_data["data"]["generateExportDownloadPresignedUrl"]["downloadLink"]}')
                return response_data['data']['generateExportDownloadPresignedUrl']['downloadLink']


def generate_sbom_download_url(token, organization_context, sbom_type=None, sbom_subtype=None, asset_version_id=None,
                               verbose=False) -> str:
    """
    Blocking call: Initiates generation of an SBOM for the asset_version_id, and return a pre-signed URL for downloading the SBOM.
    This may take several minutes to complete, depending on the size of SBOM.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        sbom_type (str, required):
            The type of SBOM to download. Valid values are "CYCLONEDX" or "SPDX".
        sbom_subtype (str, required):
            The subtype of SBOM to download. Valid values for CycloneDX are "SBOM_ONLY", "SBOM_WITH_VDR", "VDR_ONLY"; valid values for SPDX are "SBOM_ONLY".
        asset_version_id (str, required):
            Asset Version ID to download the SBOM for.
        verbose (bool, optional):
            If True, print additional information to the console. Defaults to False.

    Raises:
        ValueError: Raised if sbom_type, sbom_subtype, or asset_version_id are not provided.
        Exception: Raised if the query fails.

    Returns:
        str: URL to download the SBOM from.
    """

    if not sbom_type:
        raise ValueError("SBOM Type is required")
    if not sbom_subtype:
        raise ValueError("SBOM Subtype is required")
    if not asset_version_id:
        raise ValueError("Asset Version ID is required")

    if sbom_type not in ["CYCLONEDX", "SPDX"]:
        raise Exception(f"SBOM Type {sbom_type} not supported")

    if sbom_type == "CYCLONEDX":
        if sbom_subtype not in ["SBOM_ONLY", "SBOM_WITH_VDR", "VDR_ONLY"]:
            raise Exception(f"SBOM Subtype {sbom_subtype} not supported")

        mutation = queries.LAUNCH_CYCLONEDX_EXPORT['mutation']
        variables = queries.LAUNCH_CYCLONEDX_EXPORT['variables'](sbom_subtype, asset_version_id)

        response_data = send_graphql_query(token, organization_context, mutation, variables)
        if verbose:
            print(f'Response Data: {json.dumps(response_data, indent=4)}')

        # get exportJobId from the result
        export_job_id = response_data['data']['launchCycloneDxExport']['exportJobId']
        if verbose:
            print(f'Export Job ID: {export_job_id}')

    if sbom_type == "SPDX":
        if sbom_subtype not in ["SBOM_ONLY"]:
            raise Exception(f"SBOM Subtype {sbom_subtype} not supported")

        mutation = queries.LAUNCH_SPDX_EXPORT['mutation']
        variables = queries.LAUNCH_SPDX_EXPORT['variables'](sbom_subtype, asset_version_id)

        response_data = send_graphql_query(token, organization_context, mutation, variables)
        if verbose:
            print(f'Response Data: {json.dumps(response_data, indent=4)}')

        # get exportJobId from the result
        export_job_id = response_data['data']['launchSpdxExport']['exportJobId']
        if verbose:
            print(f'Export Job ID: {export_job_id}')

    if not export_job_id:
        raise Exception(
            "Error: Export Job ID not found - this should not happen, please contact your Finite State representative")

    # poll the API until the export job is complete
    sleep_time = 10
    total_time = 0
    if verbose:
        print(f'Polling every {sleep_time} seconds for export job to complete')
    while True:
        time.sleep(sleep_time)
        total_time += sleep_time
        if verbose:
            print(f'Total time elapsed: {total_time} seconds')

        query = queries.GENERATE_EXPORT_DOWNLOAD_PRESIGNED_URL['query']
        variables = queries.GENERATE_EXPORT_DOWNLOAD_PRESIGNED_URL['variables'](export_job_id)

        response_data = send_graphql_query(token, organization_context, query, variables)

        if verbose:
            print(f'Response Data: {json.dumps(response_data, indent=4)}')

        if response_data['data']['generateExportDownloadPresignedUrl']['status'] == "COMPLETED":
            if response_data['data']['generateExportDownloadPresignedUrl']['downloadLink']:
                if verbose:
                    print(
                        f'Export Job Complete. Download URL: {response_data["data"]["generateExportDownloadPresignedUrl"]["downloadLink"]}')
                return response_data['data']['generateExportDownloadPresignedUrl']['downloadLink']


def get_software_components(token, organization_context, asset_version_id=None, type=None) -> list:
    """
    Gets all the Software Components for an Asset Version. Uses pagination to get all results.
    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        asset_version_id (str, optional):
            Asset Version ID to get software components for.
        type (str, optional):
            The type of software component to return. Valid values are "APPLICATION", "ARCHIVE", "CONTAINER", "DEVICE", "FILE", "FIRMWARE", "FRAMEWORK", "INSTALL", "LIBRARY", "OPERATING_SYSTEM", "OTHER", "SERVICE", "SOURCE". If not specified, will return all software components. See https://docs.finitestate.io/types/software-component-type
    Raises:
        Exception: Raised if the query fails, required parameters are not specified, or parameters are incompatible.
    Returns:
        list: List of Software Component Objects
    """
    if not asset_version_id:
        raise Exception("Asset Version ID is required")

    return get_all_paginated_results(token, organization_context, queries.GET_SOFTWARE_COMPONENTS['query'],
                                     queries.GET_SOFTWARE_COMPONENTS['variables'](asset_version_id=asset_version_id,
                                                                                  type=type),
                                     'allSoftwareComponentInstances')


def search_sbom(token, organization_context, name=None, version=None, asset_version_id=None, search_method='EXACT',
                case_sensitive=False) -> list:
    """
    Searches the SBOM of a specific asset version or the entire organization for matching software components.
    Search Methods: EXACT or CONTAINS
    An exact match will return only the software component whose name matches the name exactly.
    A contains match will return all software components whose name contains the search string.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        name (str, required):
            Name of the software component to search for.
        version (str, optional):
            Version of the software component to search for. If not specified, will search for all versions of the software component.
        asset_version_id (str, optional):
            Asset Version ID to search for software components in. If not specified, will search the entire organization.
        search_method (str, optional):
            Search method to use. Valid values are "EXACT" and "CONTAINS". Defaults to "EXACT".
        case_sensitive (bool, optional):
            Whether or not to perform a case sensitive search. Defaults to False.
    Raises:
        ValueError: Raised if name is not provided.
        Exception: Raised if the query fails.
    Returns:
        list: List of SoftwareComponentInstance Objects
    """
    if asset_version_id:
        query = """
query GetSoftwareComponentInstances_SDK(
    $filter: SoftwareComponentInstanceFilter
    $after: String
    $first: Int
) {
    allSoftwareComponentInstances(
        filter: $filter
        after: $after
        first: $first
    ) {
        _cursor
        id
        name
        version
        originalComponents {
            id
            name
            version
        }
    }
}
"""
    else:
        # gets the asset version info that contains the software component
        query = """
query GetSoftwareComponentInstances_SDK(
    $filter: SoftwareComponentInstanceFilter
    $after: String
    $first: Int
) {
    allSoftwareComponentInstances(
        filter: $filter
        after: $after
        first: $first
    ) {
        _cursor
        id
        name
        version
        assetVersion {
            id
            name
            asset {
                id
                name
            }
        }
    }
}
"""

    variables = {
        "filter": {
            "mergedComponentRefId": None
        },
        "after": None,
        "first": 100
    }

    if asset_version_id:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    if search_method == 'EXACT':
        if case_sensitive:
            variables["filter"]["name"] = name
        else:
            variables["filter"]["name_like"] = name
    elif search_method == 'CONTAINS':
        variables["filter"]["name_contains"] = name

    if version:
        if search_method == 'EXACT':
            variables["filter"]["version"] = version
        elif search_method == 'CONTAINS':
            variables["filter"]["version_contains"] = version

    records = get_all_paginated_results(token, organization_context, query, variables=variables,
                                        field="allSoftwareComponentInstances")

    return records


def send_graphql_query(token, organization_context, query, variables=None):
    """
    Send a GraphQL query to the API

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        query (str):
            The GraphQL query string
        variables (dict, optional):
            Variables to be used in the GraphQL query, by default None

    Raises:
        Exception: If the response status code is not 200

    Returns:
        dict: Response JSON
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'Organization-Context': organization_context
    }
    data = {
        'query': query,
        'variables': variables
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        thejson = response.json()

        if "errors" in thejson:
            raise Exception(f"Error: {thejson['errors']}")

        return thejson
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def update_finding_statuses(token, organization_context, user_id=None, finding_ids=None, status=None,
                            justification=None, response=None, comment=None):
    """
    Updates the status of a findings or multiple findings. This is a blocking call.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        user_id (str, required):
            User ID to update the finding status for.
        finding_ids (str, required):
            Finding ID to update the status for.
        status (str, required):
            Status to update the finding to. Valid values are "AFFECTED", "FIXED", "NOT_AFFECTED", and "UNDER_INVESTIGATION". For more details, see https://docs.finitestate.io/types/finding-status-option
        justification (str, optional):
            Optional justification that applies to status of "NOT AFFECTED". Valid values are "COMPONENT_NOT_PRESENT", "INLINE_MITIGATIONS_ALREADY_EXIST", "VULNERABLE_CODE_CANNOT_BE_CONTROLLED_BY_ADVERSARY", "VULNERABLE_CODE_NOT_IN_EXECUTE_PATH", "VULNERABLE_CODE_NOT_PRESENT". For more details see https://docs.finitestate.io/types/finding-status-justification-enum
        response (str, optional):
            Optional "Vendor Responses" that applies to status of "AFFECTED". Valid values are "CANNOT_FIX", "ROLLBACK_REQUIRED", "UPDATE_REQUIRED", "WILL_NOT_FIX", and "WORKAROUND_AVAILABLE". For more details, see  https://docs.finitestate.io/types/finding-status-response-enum
        comment (str, optional):
            Optional comment to add to the finding status update.

    Raises:
        ValueError: Raised if required parameters are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: Response JSON from the GraphQL query of type UpdateFindingsStatusesResponse. For details see https://docs.finitestate.io/types/update-findings-statuses-response
    """
    if not user_id:
        raise ValueError("User Id is required")
    if not finding_ids:
        raise ValueError("Finding Ids is required")
    if not status:
        raise ValueError("Status is required")

    mutation = queries.UPDATE_FINDING_STATUSES['mutation']
    variables = queries.UPDATE_FINDING_STATUSES['variables'](user_id=user_id, finding_ids=finding_ids, status=status,
                                                             justification=justification, response=response,
                                                             comment=comment)

    return send_graphql_query(token, organization_context, mutation, variables)


def upload_file_for_binary_analysis(
    token, organization_context, test_id=None, file_path=None, chunk_size=DEFAULT_CHUNK_SIZE, quick_scan=False
):
    """
    Upload a file for Binary Analysis. Will automatically chunk the file into chunks and upload each chunk.
    NOTE: This is NOT for uploading third party scanner results. Use upload_test_results_file for that.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        test_id (str, required):
            Test ID to upload the file for.
        file_path (str, required):
            Local path to the file to upload.
        chunk_size (int, optional):
            The size of the chunks to read. 1000 MiB by default. Min 5MiB and max 2GiB.
        quick_scan (bool, optional):
            If True, will perform a quick scan of the Binary. Defaults to False (Full Scan). For details, please see the API documentation.

    Raises:
        ValueError: Raised if test_id or file_path are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: The response from the GraphQL query, a completeMultipartUpload Object.
    """
    # To upload a file for Binary Analysis, you must use the generateMultiplePartUploadUrl mutation
    if not test_id:
        raise ValueError("Test Id is required")
    if not file_path:
        raise ValueError("File Path is required")
    if chunk_size < MIN_CHUNK_SIZE:
        raise ValueError(f"Chunk size must be greater than {MIN_CHUNK_SIZE} bytes")
    if chunk_size >= MAX_CHUNK_SIZE:
        raise ValueError(f"Chunk size must be less than {MAX_CHUNK_SIZE} bytes")

    # Start Multi-part Upload
    graphql_query = """
    mutation Start_SDK($testId: ID!) {
        startMultipartUploadV2(testId: $testId) {
            uploadId
            key
        }
    }
    """

    variables = {
        "testId": test_id
    }

    response = send_graphql_query(token, organization_context, graphql_query, variables)

    upload_id = response['data']['startMultipartUploadV2']['uploadId']
    upload_key = response['data']['startMultipartUploadV2']['key']

    # if the file is greater than max chunk size (or 5 GB), split the file in chunks,
    # call generateUploadPartUrlV2 for each chunk of the file (even if it is a single part)
    # and upload the file to the returned upload URL
    i = 0
    part_data = []
    for chunk in file_chunks(file_path, chunk_size):
        i = i + 1
        graphql_query = """
        mutation GenerateUploadPartUrl_SDK($partNumber: Int!, $uploadId: ID!, $uploadKey: String!) {
            generateUploadPartUrlV2(partNumber: $partNumber, uploadId: $uploadId, uploadKey: $uploadKey) {
                key
                uploadUrl
            }
        }
        """

        variables = {
            "partNumber": i,
            "uploadId": upload_id,
            "uploadKey": upload_key
        }

        response = send_graphql_query(token, organization_context, graphql_query, variables)

        chunk_upload_url = response['data']['generateUploadPartUrlV2']['uploadUrl']

        # upload the chunk to the upload URL
        response = upload_bytes_to_url(chunk_upload_url, chunk)

        part_data.append({
            "ETag": response.headers['ETag'],
            "PartNumber": i
        })

    # call completeMultipartUploadV2
    graphql_query = """
    mutation CompleteMultipartUpload_SDK($partData: [PartInput!]!, $uploadId: ID!, $uploadKey: String!) {
        completeMultipartUploadV2(partData: $partData, uploadId: $uploadId, uploadKey: $uploadKey) {
            key
        }
    }
    """

    variables = {
        "partData": part_data,
        "uploadId": upload_id,
        "uploadKey": upload_key
    }

    response = send_graphql_query(token, organization_context, graphql_query, variables)

    # get key from the result
    key = response['data']['completeMultipartUploadV2']['key']

    variables = {
        "key": key,
        "testId": test_id
    }

    # call launchBinaryUploadProcessing
    if quick_scan:
        graphql_query = """
        mutation LaunchBinaryUploadProcessing_SDK($key: String!, $testId: ID!, $configurationOptions: [BinaryAnalysisConfigurationOption]) {
            launchBinaryUploadProcessing(key: $key, testId: $testId, configurationOptions: $configurationOptions) {
                key
            }
        }
        """
        variables["configurationOptions"] = ["QUICK_SCAN"]
    else:
        graphql_query = """
        mutation LaunchBinaryUploadProcessing_SDK($key: String!, $testId: ID!) {
            launchBinaryUploadProcessing(key: $key, testId: $testId) {
                key
            }
        }
        """

    response = send_graphql_query(token, organization_context, graphql_query, variables)

    return response['data']


def upload_test_results_file(token, organization_context, test_id=None, file_path=None):
    """
    Uploads a test results file to the test specified by test_id. NOTE: This is not for Binary Analysis. Use upload_file_for_binary_analysis for that.

    Args:
        token (str):
            Auth token. This is the token returned by get_auth_token(). Just the token, do not include "Bearer" in this string, that is handled inside the method.
        organization_context (str):
            Organization context. This is provided by the Finite State API management. It looks like "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx".
        test_id (str, required):
            Test ID to upload the file for.
        file_path (str, required):
            Local path to the file to upload.

    Raises:
        ValueError: Raised if test_id or file_path are not provided.
        Exception: Raised if the query fails.

    Returns:
        dict: The response from the GraphQL query, a completeTestResultUpload Object.
    """
    if not test_id:
        raise ValueError("Test Id is required")
    if not file_path:
        raise ValueError("File Path is required")

    # Gerneate Test Result Upload URL
    graphql_query = """
    mutation GenerateTestResultUploadUrl_SDK($testId: ID!) {
        generateSinglePartUploadUrl(testId: $testId) {
            uploadUrl
            key
        }
    }
    """

    variables = {
        "testId": test_id
    }

    response = send_graphql_query(token, organization_context, graphql_query, variables)

    # get the upload URL and key
    upload_url = response['data']['generateSinglePartUploadUrl']['uploadUrl']
    key = response['data']['generateSinglePartUploadUrl']['key']

    # upload the file
    upload_file_to_url(upload_url, file_path)

    # complete the upload
    graphql_query = """
    mutation CompleteTestResultUpload_SDK($key: String!, $testId: ID!) {
        launchTestResultProcessing(key: $key, testId: $testId) {
            key
        }
    }
    """

    variables = {
        "testId": test_id,
        "key": key
    }

    response = send_graphql_query(token, organization_context, graphql_query, variables)
    return response['data']


def upload_bytes_to_url(url, bytes):
    """
    Used for uploading a file to a pre-signed S3 URL

    Args:
        url (str):
            (Pre-signed S3) URL
        bytes (bytes):
            Bytes to upload

    Raises:
        Exception: If the response status code is not 200

    Returns:
        requests.Response: Response object
    """
    response = requests.put(url, data=bytes)

    if response.status_code == 200:
        return response
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")


def upload_file_to_url(url, file_path):
    """
    Used for uploading a file to a pre-signed S3 URL

    Args:
        url (str):
            (Pre-signed S3) URL
        file_path (str):
            Local path to file to upload

    Raises:
        Exception: If the response status code is not 200

    Returns:
        requests.Response: Response object
    """
    with open(file_path, 'rb') as file:
        response = requests.put(url, data=file)

    if response.status_code == 200:
        return response
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")
