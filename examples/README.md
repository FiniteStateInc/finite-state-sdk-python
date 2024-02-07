# Finite State Python SDK Examples

In this directory you can find examples for doing common tasks using the SDK.


# compare_versions.py

Compares two asset versions to show Findings that were introduced or remediated, and which software components were added, updated, or removed.

# create_a_new_product.py

How to create a new Product programatically.

# custom_query.py

If you want to run custom GraphQL queries using all the available fields in the API.

# download_reports.py

Shows how to download PDF and CSV reports for an asset version.

# download_sboms.py

For programmatically downloading SBOMs for an asset version.

# generate_products_csv.py

Creates a CSV report of high level information about products.

# get_findings.py

Getting all the Findings for an asset version, with filters by type, such as "CVE".

# get_product_and_asset_information.py

Querying for all the product and asset version using the SDK.

# get sbom_for_an_asset_version.py

Gets the entire list of software components for an asset version, with filters by type, such as "OPERATING SYSTEM".

# paginated_query.py

How to make custom queries using pagination and helper methods in the SDK.

# search_sbom.py

How to use the `search_sbom` function of the SDK to search for components by name and version, and specify whether the search should be case-sensitive or not.

# update_finding_status.py

How to update Finding resolutions using the SDK, which allows you to set the status and specify justifications or vendor responses and provide comments.

# upload_test_results.py

How to programmatically upload test results (e.g. SBOMs or Third Party Scanners). Basically a one-liner you can add to your CI systems.

# uploading_a_binary.py

How to programmatically upload a binary image (e.g. a firmware or system image). Basically a one-liner you can add to your CI systems.