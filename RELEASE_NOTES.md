# Finite State Python SDK RELEASE NOTES

# v0.1.0

Updated minor version due to breaking change.

## New Features
N/A

## Bug Fixes
N/A

## Breaking Changes

* GraphQL queries that fail will now raise an Exception with details about the exception

Your code should include try / except blocks for making calls, instead of relying on the API to return a potentially unexpected JSON document with an `errors` field.


# v0.0.8

## New Features
* Updated TOKEN_URL endpoint
* Added get_asset_versions method
* Updated Asset Versions query to have group information
* Added cve_id filter for Get Findings variables
* Added generate_download_sbom_url and queries and variables to support CycloneDX and SPDX downloads
* Added download_sbom helper function
* Added download_sboms.py example

## Bug Fixes
* N/A

## Breaking Changes
* N/A