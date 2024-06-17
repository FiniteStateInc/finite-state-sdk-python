"""
GraphQL queries for the Finite State Platform
"""
DEFAULT_PAGE_SIZE = 100

ALL_BUSINESS_UNITS = {
    "query": """
    query GetBusinessUnits_SDK(
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
    "variables": {"after": None, "first": DEFAULT_PAGE_SIZE},
}

ALL_USERS = {
    "query": """
    query GetUsers_SDK(
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
    "variables": {"after": None, "first": DEFAULT_PAGE_SIZE},
}

ALL_ORGANIZATIONS = {
    "query": """
    query GetOrganizations_SDK(
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
    "variables": {"after": None, "first": DEFAULT_PAGE_SIZE},
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
    query GetAllAssetVersions_SDK(
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
    variables = {"filter": {}, "after": None, "first": DEFAULT_PAGE_SIZE}

    if asset_id is not None:
        variables["filter"]["id"] = asset_id

    if business_unit_id is not None:
        variables["filter"]["group"] = {
            "id": business_unit_id
        }

    return variables


ALL_ASSETS = {
    "query": """
        query GetAllAssets_SDK(
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
                    defaultVersion {
                        id
                        name
                        relativeRiskScore
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
    variables = {"filter": {}, "after": None, "first": DEFAULT_PAGE_SIZE, "orderBy": ["name_ASC"]}

    if artifact_id is not None:
        variables["filter"]["id"] = artifact_id

    if business_unit_id is not None:
        variables["filter"]["group"] = {
            "id": business_unit_id
        }

    return variables


ALL_ARTIFACTS = {
    "query": """
        query GetAllArtifacts_SDK(
            $filter: AssetFilter!,
            $after: String,
            $first: Int,
            $orderBy: [AssetOrderBy!]
            ) {
                allAssets(
                    filter: $filter,
                    after: $after,
                    first: $first,
                    orderBy: $orderBy
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
                    deletedAt
                    ctx {
                        asset
                        businessUnits
                        products
                    }
                    defaultVersion {
                        name
                        createdAt
                        __typename
                    }
                    _versionsMeta {
                        count
                    }
                    __typename
                }
            }
        """,
    "variables": artifact_variables
}

ALL_PRODUCTS = {
    "query": """
        query GetAllProducts_SDK(
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
                    relativeRiskScore
                    group {
                        id
                        name
                    }
                    assets {
                        id
                        name
                        _findingsMeta {
                            count
                        }
                        __typename
                    }
                    __typename
                }
            }
        """,
    "variables": {"filter": {}, "after": None, "first": DEFAULT_PAGE_SIZE},
}

GENERATE_EXPORT_DOWNLOAD_PRESIGNED_URL = {
    "query": """
query GenerateExportDownloadPresignedUrl_SDK($exportId: ID!) {
  generateExportDownloadPresignedUrl(exportId: $exportId) {
    downloadLink
    status
  }
}
""",
    "variables": lambda export_id: {"exportId": export_id}
}


GET_PRODUCT_ASSET_VERSIONS = {
    "query": """
query GetProductAssetVersions_SDK(
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
    "variables": lambda product_id: {"filter": {"id": product_id}, "after": None, "first": DEFAULT_PAGE_SIZE},
}


def _create_GET_FINDINGS_VARIABLES(asset_version_id=None, category=None, cve_id=None, finding_id=None, status=None, severity=None, limit=1000, count=False):
    variables = {
        "filter": {
            "mergedFindingRefId": None,
            "deletedAt": None
        }
    }

    # if not counting, set the pagination and ordering
    if not count:
        variables["after"] = None
        variables["first"] = limit if limit else DEFAULT_PAGE_SIZE
        variables["orderBy"] = ["title_ASC"]

    if finding_id is not None:
        # if finding_id is a list, use the "in" operator
        if isinstance(finding_id, list):
            variables["filter"]["id_in"] = finding_id
        else:
            variables["filter"]["id"] = str(finding_id)

    if asset_version_id is not None:
        # if asset_version_id is a list, use the "in" operator
        if isinstance(asset_version_id, list):
            variables["filter"]["assetVersionRefId_in"] = asset_version_id
        else:
            variables["filter"]["assetVersionRefId"] = str(asset_version_id)

    # if category is a string, make it a list
    if isinstance(category, str):
        category = [category]

    if category is not None:
        variables["filter"]["AND"] = [
            {
                "OR": [
                    {
                        "category_in": category
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

    if severity is not None:
        variables["filter"]["severity"] = severity

    if cve_id is not None:
        if "AND" not in variables["filter"]:
            variables["filter"]["AND"] = []

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

    if status is not None:
        variables["filter"]["currentStatus"] = {
            "status_in": [
                status
            ]
        }

    return variables


GET_FINDINGS_COUNT = {
    "query": """
query GetFindingsCount_SDK($filter: FindingFilter)
{
    _allFindingsMeta(filter: $filter) {
        count
    }
}
""",
    "variables": lambda asset_version_id=None, category=None, cve_id=None, finding_id=None, status=None, severity=None, limit=None: _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, cve_id=cve_id, finding_id=finding_id, status=status, severity=severity, limit=limit, count=True)
}

GET_FINDINGS = {
    "query": """
query GetFindingsForAnAssetVersion_SDK (
    $filter: FindingFilter,
    $after: String,
    $first: Int,
    $orderBy: [FindingOrderBy!]
) {
    allFindings(filter: $filter,
                after: $after,
                first: $first,
                orderBy: $orderBy
    ) {
        _cursor
        id
        title
        date
        createdAt
        updatedAt
        deletedAt
        cvssScore
        cvssSeverity
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
            responses
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
            cvssScore
            cvssBaseMetricV3 {
                cvssv3 {
                    baseScore
                    vectorString
                }
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
        originalFindings {
            id
            vulnIdFromTool
            origin
            cvssScore
            cvssSeverity
            __typename
        }
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
    "variables": lambda asset_version_id=None, category=None, cve_id=None, finding_id=None, status=None, severity=None, limit=None: _create_GET_FINDINGS_VARIABLES(asset_version_id=asset_version_id, category=category, cve_id=cve_id, finding_id=finding_id, severity=severity, status=status, limit=limit)
}


def _create_GET_SOFTWARE_COMPONENTS_VARIABLES(asset_version_id=None, type=None):
    variables = {
        "filter": {
            "mergedComponentRefId": None,
            "deletedAt": None
        },
        "after": None,
        "first": DEFAULT_PAGE_SIZE,
        "orderBy": ["absoluteRiskScore_DESC"]
    }

    if asset_version_id is not None:
        variables["filter"]["assetVersionRefId"] = asset_version_id

    if type is not None:
        variables["filter"]["type_in"] = [type]

    return variables


GET_SOFTWARE_COMPONENTS = {
    "query": """
query GetSoftwareComponentsForAnAssetVersion_SDK (
    $filter: SoftwareComponentInstanceFilter,
    $after: String,
    $first: Int,
    $orderBy: [SoftwareComponentInstanceOrderBy!]
) {
    allSoftwareComponentInstances(filter: $filter,
                                  after: $after,
                                  first: $first,
                                  orderBy: $orderBy
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
        author
        licenses {
            id
            name
            copyLeft
            isFsfLibre
            isOsiApproved
            url
            __typename
        }
        copyrights {
            name
            text
            url
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
        supplier {
            name
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
        test {
            name
            tools {
                name
            }
        }
        origin
        __typename
    }
}
""",
    "variables": lambda asset_version_id=None, type=None: _create_GET_SOFTWARE_COMPONENTS_VARIABLES(asset_version_id=asset_version_id, type=type)
}


def _create_GET_PRODUCTS_VARIABLES(product_id=None, business_unit_id=None):
    variables = {"filter": {}, "after": None, "first": DEFAULT_PAGE_SIZE}

    if product_id:
        variables["filter"]["id"] = product_id

    if business_unit_id:
        variables["filter"]["group"] = {
            "id": business_unit_id
        }

    return variables


GET_PRODUCTS = {
    "query": """
        query GetAllProducts_SDK(
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
                    group {
                        id
                        name
                    }
                    __typename
                }
            }
        """,
    "variables": lambda product_id=None, business_unit_id=None: _create_GET_PRODUCTS_VARIABLES(product_id=product_id, business_unit_id=business_unit_id)
}


GET_PRODUCTS_BUSINESS_UNIT = {
    "query": """
        query GetAllProducts_SDK(
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
        "first": DEFAULT_PAGE_SIZE,
    },
}


def _create_LAUNCH_CYCLONEDX_EXPORT_VARIABLES(cdx_subtype, asset_version_id):
    variables = {
        "cdxSubtype": cdx_subtype,
        "assetVersionId": asset_version_id
    }

    return variables


LAUNCH_CYCLONEDX_EXPORT = {
    "mutation": """
mutation LaunchCycloneDxExport_SDK($cdxSubtype: CycloneDxExportSubtype!, $assetVersionId: ID!) {
  launchCycloneDxExport(cdxSubtype: $cdxSubtype, assetVersionId: $assetVersionId) {
    exportJobId
  }
}
""",
    "variables": lambda cdx_subtype, asset_version_id: _create_LAUNCH_CYCLONEDX_EXPORT_VARIABLES(cdx_subtype, asset_version_id)
}


def _create_LAUNCH_REPORT_EXPORT_MUTATION(asset_version_id=None, product_id=None, report_type=None, report_subtype=None):
    if not asset_version_id and not product_id:
        raise Exception("Must specify either asset_version_id or product_id")

    if asset_version_id and product_id:
        raise Exception("Cannot specify both asset_version_id and product_id")

    if asset_version_id:
        if report_type == "CSV":
            mutation = """
mutation LaunchArtifactCSVExport_SDK($artifactCsvSubtype: ArtifactCSVExportSubtype!, $assetVersionId: ID!) {
    launchArtifactCSVExport(artifactCsvSubtype: $artifactCsvSubtype, assetVersionId: $assetVersionId) {
        exportJobId
    }
}
"""
        elif report_type == "PDF":
            mutation = """
mutation LaunchArtifactPDFExport_SDK($artifactPdfSubtype: ArtifactPdfExportSubtype!, $assetVersionId: ID!) {
    launchArtifactPdfExport(artifactPdfSubtype: $artifactPdfSubtype, assetVersionId: $assetVersionId) {
        exportJobId
    }
}
"""

    if product_id:
        if report_type == "CSV":
            mutation = """
mutation LaunchProductCSVExport_SDK($productCsvSubtype: ProductCSVExportSubtype!, $productId: ID!) {
    launchProductCSVExport(productCsvSubtype: $productCsvSubtype, productId: $productId) {
        exportJobId
    }
}
"""

    return mutation


def _create_LAUNCH_REPORT_EXPORT_VARIABLES(asset_version_id=None, product_id=None, report_type=None, report_subtype=None):
    variables = {}

    if not asset_version_id and not product_id:
        raise Exception("Must specify either asset_version_id or product_id")

    if asset_version_id and product_id:
        raise Exception(f"Cannot specify both asset_version_id and product_id: specified {asset_version_id} and {product_id}")

    if asset_version_id:
        if report_type == "CSV":
            variables = {
                "artifactCsvSubtype": report_subtype,
                "assetVersionId": asset_version_id
            }
        elif report_type == "PDF":
            variables = {
                "artifactPdfSubtype": report_subtype,
                "assetVersionId": asset_version_id
            }

    if product_id:
        if report_type == "CSV":
            variables = {
                "productCsvSubtype": report_subtype,
                "productId": product_id
            }

    return variables


LAUNCH_REPORT_EXPORT = {
    "mutation": lambda asset_version_id, product_id, report_type, report_subtype: _create_LAUNCH_REPORT_EXPORT_MUTATION(asset_version_id=asset_version_id, product_id=product_id, report_type=report_type, report_subtype=report_subtype),
    "variables": lambda asset_version_id, product_id, report_type, report_subtype: _create_LAUNCH_REPORT_EXPORT_VARIABLES(asset_version_id=asset_version_id, product_id=product_id, report_type=report_type, report_subtype=report_subtype)
}


def _create_LAUNCH_SPDX_EXPORT_VARIABLES(spdx_subtype, asset_version_id):
    variables = {
        "spdxSubtype": spdx_subtype,
        "assetVersionId": asset_version_id
    }

    return variables


LAUNCH_SPDX_EXPORT = {
    "mutation": """
mutation LaunchSpdxExport_SDK($spdxSubtype: SpdxExportSubtype!, $assetVersionId: ID!) {
  launchSpdxExport(spdxSubtype: $spdxSubtype, assetVersionId: $assetVersionId) {
    exportJobId
  }
}
""",
    "variables": lambda spdx_subtype, asset_version_id: _create_LAUNCH_SPDX_EXPORT_VARIABLES(spdx_subtype, asset_version_id)
}


ONE_PRODUCT_ALL_ASSET_VERSIONS = {
    "query": """
        query GetProductAssetVersions_SDK(
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
    "variables": lambda product_id: {"filter": {"id": product_id}, "after": None, "first": DEFAULT_PAGE_SIZE},
}


def __create_UPDATE_FINDING_STATUSES_VARIABLES(user_id=None, finding_ids=None, status=None, justification=None, response=None, comment=None):
    if not isinstance(finding_ids, list):
        finding_ids = [finding_ids]

    if status == "AFFECTED":
        if justification is not None:
            raise Exception("justification pertains to status NOT AFFECTED. Specify response instead.")
    elif status == "NOT_AFFECTED":
        if response is not None:
            raise Exception("response pertains to status AFFECTED. Specify justification instead.")

    return {
        "ids": finding_ids,
        "updateStatusInput": {
            "comment": comment,
            "status": status,
            "justification": justification,
            "responses": response
        },
        "userId": user_id
    }


UPDATE_FINDING_STATUSES = {
    "mutation": """
mutation UpdateFindingsStatuses_SDK($ids: [ID!]!, $updateStatusInput: UpdateFindingStatusesInput!, $userId: ID!) {
    updateFindingsStatuses(ids: $ids, updateStatusInput: $updateStatusInput, userId: $userId) {
        ids
    }
}
    """,
    "variables": lambda user_id=None, finding_ids=None, status=None, justification=None, response=None, comment=None: __create_UPDATE_FINDING_STATUSES_VARIABLES(user_id=user_id, finding_ids=finding_ids, status=status, justification=justification, response=response, comment=comment)
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
