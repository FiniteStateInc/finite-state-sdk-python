"""
get_all_components_metadata.py

This script retrieves and exports software component metadata for a specific artifact version from the Finite State platform.

Features:
- Uses a custom GraphQL query to fetch all software components for a given asset version.
- Supports CSV and JSON output, with custom column ordering and property handling.
- Filters out components with certain statuses/types and supports additional filtering by type and risk score.
- Handles authentication via a secrets file.
- Robust error handling and logging.
- Output filenames include asset and version names by default.

Usage:
    python examples/get_all_components_metadata.py --secrets-file <path_to_secrets> --version-id <asset_version_id> [options]

Options:
    --artifact-id <artifact_id>         Optional. Artifact ID to query (not always required).
    --output-format <csv|json|both>    Output format. Default is csv.
    --output-file <filename>           Custom output filename. If not provided, uses asset/version names.
    --component-type <type>            Filter by component type.
    --min-risk-score <float>           Filter by minimum risk score.
    --verbose                         Enable verbose output.

Run this script from the 'finite-state-sdk-examples' directory, e.g.:
    cd finite-state-sdk-python
    python examples/get_all_components_metadata.py --secrets-file .secrets --version-id <asset_version_id>

The secrets file (.env) should define CLIENT_ID, CLIENT_SECRET, and ORGANIZATION_CONTEXT.
"""
import argparse
import datetime
import json
import os
import sys
# Add SDK path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from time import sleep
import csv
import collections.abc
import time
import logging
import finite_state_sdk
from finite_state_sdk.token_cache import TokenCache
from finite_state_sdk import send_graphql_query


# Logging setup
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def setup_logging(log_file=None, verbose=False):
    """Configure logging to file and/or console."""
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(fh)


class ComponentsMetadataError(Exception):
    """Custom exception for components metadata retrieval errors."""
    pass


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Retrieve all software components and their metadata for a specific artifact and version. Components with status 'REVIEWED_FALSE_POSITIVE' or 'EXCLUDED', or type 'file', are always filtered out."
    )
    parser.add_argument('--secrets-file', required=True, help='Path to secrets file (required)')
    parser.add_argument('--artifact-id', required=False, help='Artifact ID to query (optional)')
    parser.add_argument('--version-id', required=True, help='Artifact version ID to query (required)')
    parser.add_argument('--output-format', choices=['csv', 'json', 'both'], default='csv', help="Output format: 'csv', 'json', or 'both' (default: 'csv')")
    parser.add_argument('--output-file', help='Custom output filename (optional)')
    parser.add_argument('--component-type', help='Filter by component type (optional)')
    parser.add_argument('--min-risk-score', type=float, help='Filter by minimum risk score (optional)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output (optional)')
    return parser.parse_args()


def authenticate(secrets_file):
    """Authenticate using secrets file and return API token and org context."""
    if not os.path.exists(secrets_file):
        raise FileNotFoundError(f"Secrets file not found: {secrets_file}")
    load_dotenv(secrets_file)
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    organization_context = os.getenv('ORGANIZATION_CONTEXT')
    if not client_id or not client_secret or not organization_context:
        raise ValueError("Missing CLIENT_ID, CLIENT_SECRET, or ORGANIZATION_CONTEXT in secrets file.")
    token_cache = TokenCache(organization_context)
    token = token_cache.get_token(client_id, client_secret)
    if not token:
        raise RuntimeError("Failed to obtain authentication token.")
    return token, organization_context


# Embedded GraphQL query for component metadata
ALL_COMPONENTS_METADATA_QUERY = """
query GetFullComponentDetailsByAsset(
  $filter: SoftwareComponentInstanceFilter,
  $orderBy: [SoftwareComponentInstanceOrderBy!],
  $after: String,
  $skip: Int,
  $first: Int
) {
  allSoftwareComponentInstances(
    filter: $filter,
    orderBy: $orderBy,
    after: $after,
    skip: $skip,
    first: $first
  ) {
    id
    name
    version
    origin
    originalComponentsSources {
      id
      name
    }
    createdBy {
      email
    }
    assetVersion {
      id
      name
      asset {
        id
        name
      }
    }
    summaryDescription
    detailedDescription
    scope
    author
    buildDate
    group
    supportEol
    fileName
    publisher
    originator
    supplier {
      name
      url
    }
    properties {
      id
      key
      value
    }
    softwareIdentifiers {
      cpes
      generic
      purl
      softwareHeritageIds
      swidTags
      udis
      upcs
    }
    externalReferences {
      category
      comment
      value
      extRefType
      hashes {
        content
        alg
        id
      }
    }
  }
}
"""


def get_components_for_artifact_version(token, organization_context, artifact_id, version_id, component_type=None, min_risk_score=None, verbose=False, max_retries=3):
    """Query all software components for a given asset version, with retries and filtering."""
    query = ALL_COMPONENTS_METADATA_QUERY
    variables = {
        "filter": {
            "mergedComponentRefId": None,
            "deletedAt": None,
            "currentStatus": {
                "status_not_in": [
                    "REVIEWED_FALSE_POSITIVE",
                    "EXCLUDED"
                ]
            },
            "type_not_in": [
                "FILE"
            ],
            "assetVersionRefId": version_id
        },
        "orderBy": [
            "absoluteRiskScore_DESC"
        ]
    }
    retries = 0
    while retries < max_retries:
        try:
            response = send_graphql_query(token, organization_context, query, variables)
            components = response['data']['allSoftwareComponentInstances']
            break
        except Exception as e:
            retries += 1
            logger.error(f"Error retrieving components (attempt {retries}): {e}")
            if retries >= max_retries:
                logger.critical(f"Failed after {max_retries} attempts: {e}")
                raise ComponentsMetadataError(f"Failed after {max_retries} attempts: {e}")
            time.sleep(2 ** retries)
    else:
        return []

    filtered = []
    for comp in components:
        status = (comp.get('currentStatus') or {}).get('status', None)
        comp_type = comp.get('type', None)
        risk_score = comp.get('absoluteRiskScore', None)
        # Additional filtering by type and risk score if specified
        if component_type and comp_type != component_type:
            continue
        if min_risk_score is not None and risk_score is not None:
            try:
                if float(risk_score) < float(min_risk_score):
                    continue
            except Exception:
                logger.warning(f"Could not parse risk score for component {comp.get('id')}")
        filtered.append(comp)
    logger.info(f"Retrieved {len(filtered)} components after filtering.")
    return filtered


def collect_components_data(token, organization_context, artifact_id, version_id, filters, verbose=False):
    """Collect all components and summary info for export."""
    component_type = filters.get('component_type')
    min_risk_score = filters.get('min_risk_score')
    components = get_components_for_artifact_version(
        token,
        organization_context,
        artifact_id,
        version_id,
        component_type=component_type,
        min_risk_score=min_risk_score,
        verbose=verbose
    )
    summary = {
        'total_components': len(components),
        'component_type': component_type,
        'min_risk_score': min_risk_score,
    }
    if verbose:
        print(f"Summary: {summary}")
    return components, summary


def apply_filters(components, filters, verbose=False):
    """Apply additional filters to the list of components."""
    component_type = filters.get('component_type')
    min_risk_score = filters.get('min_risk_score')
    filtered = []
    for comp in components:
        status = (comp.get('currentStatus') or {}).get('status', None)
        comp_type = comp.get('type', None)
        risk_score = comp.get('absoluteRiskScore', None)
        if status in ('REVIEWED_FALSE_POSITIVE', 'EXCLUDED'):
            continue
        if comp_type == 'file':
            continue
        if component_type and comp_type != component_type:
            continue
        if min_risk_score is not None and risk_score is not None:
            try:
                if float(risk_score) < float(min_risk_score):
                    continue
            except Exception:
                if verbose:
                    print(f"Warning: Could not parse risk score for component {comp.get('id')}")
        filtered.append(comp)
    if not filtered and verbose:
        print("No components matched the filters.")
    return filtered


def validate_component_data(component, verbose=False):
    """Validate component data types (optional, not strict)."""
    warnings = []
    if 'absoluteRiskScore' in component:
        try:
            float(component['absoluteRiskScore'])
        except (ValueError, TypeError):
            warnings.append("absoluteRiskScore is not a valid float")
    # Add more type checks as needed
    # No print or warning for missing fields
    return warnings


def flatten_dict(d, parent_key='', sep='.'): 
    """Recursively flatten nested dictionaries and lists for CSV export."""
    items = []
    for k, v in (d or {}).items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            if v and all(isinstance(i, dict) for i in v):
                for idx, item in enumerate(v):
                    items.extend(flatten_dict(item, f"{new_key}[{idx}]", sep=sep).items())
            else:
                items.append((new_key, ';'.join(map(str, v or []))))
        else:
            items.append((new_key, v if v is not None else ''))
    return dict(items)


def export_to_csv(components, output_file, verbose=False):
    """Export components to a CSV file with custom column ordering and property handling."""
    # Flatten all components and collect all unique keys
    flat_components = [flatten_dict(comp) for comp in components]
    all_keys = set()
    for comp in flat_components:
        all_keys.update(comp.keys())
    # Specify preferred order for the first columns
    preferred_order = [
        'Artifact ID',  # maps to assetVersion.asset.id
        'Artifact Name',  # maps to assetVersion.asset.name
        'Version ID',  # maps to assetVersion.id
        'Version Name',  # maps to assetVersion.name
        'name',
        'version',
        'summaryDescription',
        'detailedDescription',
        'supportEol',
    ]
    # Fields to exclude from output
    exclude_fields = {'author', 'buildDate', 'createdBy', 'id', 'licenses[0].id', 'origin'}
    # Property keys to extract as their own columns
    special_property_keys = [
        'finitestate:sbom:component_id',
        'finitestate:sbom:component_type',
        'finitestate:sbom:confidence',
        'finitestate:sbom:sbom_entry_id',
    ]
    property_columns = [f'property:{key}' for key in special_property_keys]
    # All other keys, sorted, that are not in preferred or excluded
    rest = [k for k in sorted(all_keys) if k not in preferred_order and k not in exclude_fields and not k.startswith('properties[') and not k.startswith('property:')]
    columns = preferred_order + property_columns + ['custom_properties'] + rest

    def get_property_map(comp):
        """Extract special and custom properties for CSV columns."""
        prop_map = {}
        custom_props = []
        for prop in comp.get('properties', []):
            if 'key' in prop and 'value' in prop:
                if prop['key'] in special_property_keys:
                    prop_map[f'property:{prop["key"]}'] = prop['value']
                else:
                    custom_props.append(f"{prop['key']}={prop['value']}")
        prop_map['custom_properties'] = ';'.join(custom_props) if custom_props else ''
        return prop_map

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for comp, flat in zip(components, flat_components):
                row = {k: flat.get(k, '') for k in columns}
                # Map 'Artifact ID' column to 'assetVersion.asset.id' value
                row['Artifact ID'] = flat.get('assetVersion.asset.id', '')
                # Map 'Artifact Name' column to 'assetVersion.asset.name' value
                row['Artifact Name'] = flat.get('assetVersion.asset.name', '')
                # Map 'Version ID' column to 'assetVersion.id' value
                row['Version ID'] = flat.get('assetVersion.id', '')
                # Map 'Version Name' column to 'assetVersion.name' value
                row['Version Name'] = flat.get('assetVersion.name', '')
                row.update(get_property_map(comp))
                writer.writerow(row)
        logger.info(f"Exported {len(components)} components to {output_file} with {len(columns)} columns.")
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")


def export_to_json(components, output_file, summary=None, verbose=False):
    """Export components and summary to a JSON file."""
    export_data = {
        'metadata': {
            'export_timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'component_count': len(components),
        },
        'components': components
    }
    if summary:
        export_data['metadata'].update(summary)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported {len(components)} components to {output_file} (JSON)")
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")


def get_unique_output_filename(base_filename):
    """Return a unique filename by appending a counter if needed."""
    if not os.path.exists(base_filename):
        return base_filename
    name, ext = os.path.splitext(base_filename)
    counter = 1
    while True:
        new_filename = f"{name}({counter}){ext}"
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1


if __name__ == "__main__":
    args = parse_args()
    setup_logging(verbose=args.verbose)
    try:
        token, organization_context = authenticate(args.secrets_file)
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)

    filters = {
        'component_type': args.component_type,
        'min_risk_score': args.min_risk_score,
    }
    components, summary = collect_components_data(
        token, organization_context, args.artifact_id, args.version_id, filters, verbose=args.verbose
    )

    # Validate data (optional, not strict)
    for comp in components:
        validate_component_data(comp, verbose=args.verbose)

    # Export logic: build output filename if not provided, using asset/version names
    def sanitize_filename_part(s):
        return str(s).replace(' ', '_').replace('/', '_') if s else 'unknown'

    def build_default_filename(components, ext):
        if components and isinstance(components, list) and len(components) > 0:
            first = components[0]
            asset = first.get('assetVersion', {}).get('asset', {})
            asset_name = sanitize_filename_part(asset.get('name', 'asset'))
            version_name = sanitize_filename_part(first.get('assetVersion', {}).get('name', 'version'))
            return f"{asset_name}_{version_name}_components.{ext}"
        return f"components.{ext}"

    if args.output_format in ("csv", "both"):
        if args.output_file:
            output_file = args.output_file
        else:
            output_file = build_default_filename(components, 'csv')
        output_file = get_unique_output_filename(output_file)
        export_to_csv(components, output_file, verbose=args.verbose)
    if args.output_format in ("json", "both"):
        if args.output_file:
            output_file = args.output_file
        else:
            output_file = build_default_filename(components, 'json')
        output_file = get_unique_output_filename(output_file)
        export_to_json(components, output_file, summary=summary, verbose=args.verbose)
