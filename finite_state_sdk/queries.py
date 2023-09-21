"""
GraphQL queries for the Finite State Platform
"""

ALL_BUSINESS_UNITS = {
    "query": """
    query GetBusinessUnits(
        $after: String,
        $first: Int
    ) {
        allGroups(
            after: $after,
            first: $first
        ) {
            _cursor
            id
            name
        }
    }
    """,
    "variables": {
        "after": None,
        "first": 100
    }
}

ALL_USERS = {
    "query": """
    query GetUsers(
        $after: String,
        $first: Int
    ) {
        allUsers(
            after: $after,
            first: $first
        ) {
            _cursor
            id
            email
        }
    }
    """,
    "variables": {
        "after": None,
        "first": 100
    }
}

ALL_ORGANIZATIONS = {
    "query": """
    query GetOrganizations(
        $after: String,
        $first: Int
    ) {
        allOrganizations(
            after: $after,
            first: $first
        ) {
            _cursor
            id
            name
        }
    }
    """,
    "variables": {
        "after": None,
        "first": 100
    }
}

ALL_ASSET_VERSIONS = {
    "query": """
    query GetAllAssetVersions(
        $after: String,
        $first: Int
    ) {
        allAssetVersions(
            after: $after,
            first: $first
        ) {
            _cursor
            id
            name
            asset {
                id
                name
            }
        }
    }
    """,
    "variables": {
        "after": None,
        "first": 100
    }
}


def asset_variables(asset_id=None, business_unit_id=None):
    variables = {
        "filter": {},
        "after": None,
        "first": 100
    }

    if asset_id is not None:
        variables["filter"]["id"] = asset_id

    if business_unit_id is not None:
        variables["filter"]["group"] = {
            "id": business_unit_id
        }

    return variables


ALL_ASSETS = {
    "query": """
        query GetAllAssets(
            $filter: AssetFilter!,
            $after: String,
            $first: Int
            ) {
                allAssets(
                    filter: $filter,
                    after: $after,
                    first: $first
                ) {
                    _cursor
                    id
                    name
                    createdAt
                    ctx {
                        asset
                        businessUnits
                        products
                    }
                }
            }
        """,
    "variables": asset_variables
}


def artifact_variables(artifact_id=None, business_unit_id=None):
    variables = {
        "filter": {},
        "after": None,
        "first": 100
    }

    if artifact_id is not None:
        variables["filter"]["id"] = artifact_id

    if business_unit_id is not None:
        variables["filter"]["group"] = {
            "id": business_unit_id
        }

    return variables


ALL_ARTIFACTS = {
    "query": """
        query GetAllArtifacts(
            $filter: AssetFilter!,
            $after: String,
            $first: Int
            ) {
                allAssets(
                    filter: $filter,
                    after: $after,
                    first: $first
                ) {
                    _cursor
                    id
                    name
                    createdAt
                    ctx {
                        asset
                        businessUnits
                        products
                    }
                }
            }
        """,
    "variables": artifact_variables
}

ALL_PRODUCTS = {
    "query": """
        query GetAllProducts(
            $filter: ProductFilter!,
            $after: String,
            $first: Int
            ) {
                allProducts(
                    filter: $filter,
                    after: $after,
                    first: $first
                ) {
                    _cursor
                    id
                    name
                    createdAt
                }
            }
        """,
    "variables": {
        "filter": {},
        "after": None,
        "first": 100
    }
}

GET_PRODUCT_ASSET_VERSIONS = {
    "query": """
query GetProductAssetVersions(
    $filter: ProductFilter!,
    $after: String,
    $first: Int
    ) {
    allProducts(
        filter: $filter,
        after: $after,
        first: $first
    ) {
        _cursor
        id
        name
        createdAt
        assets {
            id
            name
            relativeRiskScore
            asset {
                id
                name
            }
        }
    }
}""",
    "variables": lambda product_id: {
        "filter": {
            "id": product_id
        },
        "after": None,
        "first": 100
    }
}


def _create_GET_FINDINGS_VARIABLES(asset_version_id=None):
    if asset_version_id is not None:
        return {
            "filter": {
                "assetVersionRefId": asset_version_id,
                "mergedFindingRefId": None
            },
            "after": None,
            "first": 1000
        }


GET_FINDINGS = {
    "query": """
query GetFindingsForAnAssetVersion (
    $filter: FindingFilter,
    $after: String,
    $first: Int
) {
    allFindings(filter: $filter,
                after: $after,
                first: $first
    ) {
        _cursor
        id
        title
        vulnIdFromTool
        description
        severity
        riskScore
        affects {
            name
            version
        }
    }
}""",
    "variables": lambda asset_version_id=None: _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id)
}


def _create_GET_SOFTWARE_COMPONENTS_VARIABLES(asset_version_id=None, type=None):
    variables = {
        "filter": {
            "mergedComponentRefId": None
        },
        "after": None,
        "first": 100
    }

    if asset_version_id is not None:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    if type is not None:
        variables["filter"]["type"] = type

    return variables


GET_SOFTWARE_COMPONENTS = {
    "query": """
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
""",
    "variables": lambda asset_version_id=None, type=None: _create_GET_SOFTWARE_COMPONENTS_VARIABLES(asset_version_id=asset_version_id, type=type)
}


GET_PRODUCTS_BUSINESS_UNIT = {
    "query": """
        query GetAllProducts(
            $filter: ProductFilter!,
            $after: String,
            $first: Int
            ) {
                allProducts(
                    filter: $filter,
                    after: $after,
                    first: $first
                ) {
                    _cursor
                    id
                    name
                    createdAt
                }
            }
        """,
    "variables": lambda business_unit_id: {
        "filter": {
            "group": {
                "id": business_unit_id
            }
        },
        "after": None,
        "first": 100
    }
}

ONE_PRODUCT_ALL_ASSET_VERSIONS = {
    "query": """
        query GetProductAssetVersions(
            $filter: ProductFilter!,
            $after: String,
            $first: Int
            ) {
                allProducts(
                    filter: $filter,
                    after: $after,
                    first: $first
                ) {
                    _cursor
                    id
                    name
                    createdAt
                    assets {
                        id
                        name
                        relativeRiskScore
                        asset {
                            id
                            name
                        }
                    }
                }
            }
        """,
    "variables": lambda product_id: {
        "filter": {
            "id": product_id
        },
        "after": None,
        "first": 100
    }
}

__all__ = [
    "ALL_BUSINESS_UNITS",
    "ALL_USERS",
    "ALL_ORGANIZATIONS",
    "ALL_ASSET_VERSIONS",
    "ALL_ARTIFACTS",
    "ALL_PRODUCTS",
    "ONE_PRODUCT_ALL_ASSET_VERSIONS"
]