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
            __typename
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
            __typename
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
            __typename
        }
    }
    """,
    "variables": {
        "after": None,
        "first": 100
    }
}


def _create_GET_ASSET_VERSION_VARIABLES(asset_version_id=None, asset_id=None, business_unit_id=None):
    variables = {
        "filter": {},
        "after": None,
        "first": 1000
    }

    if asset_version_id is not None:
        variables["filter"]["id"] = asset_version_id

    if asset_id is not None:
        variables["filter"]["asset"] = {
            "id": asset_id
        }

    if business_unit_id is not None:
        variables["filter"]["group"] = {
            "id": business_unit_id
        }

    return variables


ALL_ASSET_VERSIONS = {
    "query": """
    query GetAllAssetVersions(
        $filter: AssetVersionFilter!,
        $after: String,
        $first: Int
    ) {
        allAssetVersions(
            filter: $filter,
            after: $after,
            first: $first
        ) {
            _cursor
            id
            createdAt
            createdBy {
                id
                email
                __typename
            }
            name
            relativeRiskScore
            uniqueTestTypes {
                id
                name
                __typename
            }
            testStatuses
            asset {
                id
                name
                group {
                    id
                    name
                    __typename
                }
            }
            __typename
        }
    }
    """,
    "variables": lambda asset_version_id=None, asset_id=None, business_unit_id=None: _create_GET_ASSET_VERSION_VARIABLES(asset_version_id=asset_version_id, asset_id=asset_id, business_unit_id=business_unit_id)
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
                    createdBy {
                        id
                        email
                        __typename
                    }
                    group {
                        id
                        name
                    }
                    ctx {
                        asset
                        businessUnits
                        products
                    }
                    versions {
                        id
                        name
                        relativeRiskScore
                        testStatuses
                        __typename
                    }
                    __typename
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
                    __typename
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
                    __typename
                }
            }
        """,
    "variables": {
        "filter": {},
        "after": None,
        "first": 100
    }
}

GENERATE_EXPORT_DOWNLOAD_PRESIGNED_URL = {
    "query": """
query GenerateExportDownloadPresignedUrl($exportId: ID!) {
  generateExportDownloadPresignedUrl(exportId: $exportId) {
    downloadLink
    status
  }
}
""",
    "variables": lambda export_id: { "exportId": export_id }
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
        __typename
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


def _create_GET_FINDINGS_VARIABLES(asset_version_id=None, category=None, cve_id=None):
    variables = {
        "filter": {
            "assetVersionRefId": asset_version_id,
            "mergedFindingRefId": None
        },
        "after": None,
        "first": 1000,
        "orderBy": "title_ASC"
    }

    if asset_version_id is not None:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    if category is not None:
        variables["filter"]["AND"] = [
            {
                "OR": [
                    {
                        "category_in": [
                            category
                        ]
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

    if cve_id is not None:
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

    return variables


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
        date
        createdAt
        updatedAt
        vulnIdFromTool
        description
        severity
        riskScore
        affects {
            id
            name
            version
            __typename
        }
        sourceTypes
        category
        subcategory
        regression
        currentStatus {
            comment
            createdAt
            createdBy {
                id
                email
                __typename
            }
            id
            justification
            status
            updatedAt
            __typename
        }
        cwes {
            id
            cweId
            name
            __typename
        }
        cves {
            id
            cveId
            epss {
                epssPercentile
                epssScore
            }
            exploitsInfo {
                exploitProofOfConcept
                reportedInTheWild
                weaponized
                exploitedByNamedThreatActors
                exploitedByBotnets
                exploitedByRansomware
                exploits {
                    id
                    __typename
                }
                __typename
            }
            __typename
        }
        origin
        originalFindingsSources {
            id
            name
            __typename
        }
        test {
            id
            tools {
                id
                name
                __typename
            }
            __typename
        }
        __typename
    }
}""",
    "variables": lambda asset_version_id=None, category=None, cve_id=None: _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, cve_id=cve_id)
}


def _create_GET_SOFTWARE_COMPONENTS_VARIABLES(asset_version_id=None, type=None):
    variables = {
        "filter": {
            "mergedComponentRefId": None,
            "deletedAt": None
        },
        "after": None,
        "first": 100,
        "orderBy": ["absoluteRiskScore_DESC"]
    }

    if asset_version_id is not None:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    if type is not None:
        variables["filter"]["type_in"] = [type]

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
        type
        version
        hashes {
            alg
            content
        }
        licenses {
            id
            name
            copyLeft
            isFsfLibre
            isOsiApproved
            url
            __typename
        }
        softwareIdentifiers {
            cpes
            purl
            __typename
        }
        absoluteRiskScore
        softwareComponent {
            id
            name
            version
            type
            url
            licenses {
                id
                name
                copyLeft
                isFsfLibre
                isOsiApproved
                url
                __typename
            }
            softwareIdentifiers {
                cpes
                purl
                __typename
            }
            __typename
        }
        currentStatus {
            id
            status
            comment
            createdBy {
                email
            }
            __typename
        }
        __typename
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
                    createdBy {
                        id
                        email
                        __typename
                    }
                    __typename
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


def _create_LAUNCH_CYCLONEDX_EXPORT_VARIABLES(cdx_subtype, asset_version_id):
    variables = {
        "cdxSubtype": cdx_subtype,
        "assetVersionId": asset_version_id
    }

    return variables


LAUNCH_CYCLONEDX_EXPORT = {
    "mutation": """
mutation LaunchCycloneDxExport($cdxSubtype: CycloneDxExportSubtype!, $assetVersionId: ID!) {
  launchCycloneDxExport(cdxSubtype: $cdxSubtype, assetVersionId: $assetVersionId) {
    exportJobId
  }
}
""",
    "variables": lambda cdx_subtype, asset_version_id: _create_LAUNCH_CYCLONEDX_EXPORT_VARIABLES(cdx_subtype, asset_version_id)
}


def _create_LAUNCH_SPDX_EXPORT_VARIABLES(spdx_subtype, asset_version_id):
    variables = {
        "spdxSubtype": spdx_subtype,
        "assetVersionId": asset_version_id
    }

    return variables


LAUNCH_SPDX_EXPORT = {
    "mutation": """
mutation LaunchSpdxExport($spdxSubtype: SpdxExportSubtype!, $assetVersionId: ID!) {
  launchSpdxExport(spdxSubtype: $spdxSubtype, assetVersionId: $assetVersionId) {
    exportJobId
  }
}
""",
    "variables": lambda spdx_subtype, asset_version_id: _create_LAUNCH_SPDX_EXPORT_VARIABLES(spdx_subtype, asset_version_id)
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