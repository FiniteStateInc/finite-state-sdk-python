#!/usr/bin/env python3

import argparse
import json
import os
import sys
import tempfile
import time
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import finite_state_sdk

def parse_args():
    parser = argparse.ArgumentParser(description='Report on security features detected in asset versions.')
    parser.add_argument('--secrets-file', required=True, help='Path to the secrets file')
    parser.add_argument('--asset-version-id', help='Specific asset version ID to analyze')
    parser.add_argument('--csv', nargs='?', const='security_features.csv', help='Export the report to a CSV file')
    parser.add_argument('--sbom-type', default='CYCLONEDX', help='SBOM type to retrieve (default: CYCLONEDX)')
    parser.add_argument('--sbom-subtype', default='BOM', help='SBOM subtype to retrieve (default: BOM)')
    parser.add_argument('--debug', action='store_true', help='Print debug information about the SBOM data')
    return parser.parse_args()

def get_security_features(software_components):
    """Extract security features from software components data."""
    security_features = {
        'stackguard': False,
        'dep': False,
        'relro-full': False,
        'pic': False,
        'aslr': False
    }
    
    for component in software_components:
        # Example: Check if the component has security features
        # This is a placeholder - adjust based on actual data structure
        if 'securityFeatures' in component:
            features = component['securityFeatures']
            security_features['stackguard'] = features.get('stackguard', False)
            security_features['dep'] = features.get('dep', False)
            security_features['relro-full'] = features.get('relro-full', False)
            security_features['pic'] = features.get('pic', False)
            security_features['aslr'] = features.get('aslr', False)
    
    return security_features

def download_sbom_for_asset_version(token, org_ctx, asset_version_id, sbom_type, sbom_subtype=None, debug=False):
    """Download SBOM data for a specific asset version, trying multiple subtypes if needed."""
    subtypes_to_try = [sbom_subtype] if sbom_subtype else ['BOM', 'VEX', '']
    errors = []
    for subtype in subtypes_to_try:
        try:
            url = finite_state_sdk.generate_sbom_download_url(
                token,
                org_ctx,
                asset_version_id=asset_version_id,
                sbom_type=sbom_type,
                sbom_subtype=subtype if subtype else None
            )
            if debug:
                print(f"\n[DEBUG] SBOM download URL generated: {url}")
            # Wait for SBOM generation to complete (polling)
            max_attempts = 30  # 5 minutes (10 seconds * 30)
            for attempt in range(max_attempts):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
                        finite_state_sdk.download_sbom(
                            token,
                            org_ctx,
                            asset_version_id,
                            temp_file.name,
                            sbom_type=sbom_type,
                            sbom_subtype=subtype if subtype else None
                        )
                        with open(temp_file.name, 'r') as f:
                            if debug:
                                print(f"\n[DEBUG] Successfully downloaded SBOM with subtype: {subtype or 'None'}")
                            return json.load(f)
                except Exception as e:
                    if "SBOM not ready" in str(e):
                        if debug:
                            print(f"\n[DEBUG] SBOM not ready, waiting... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(10)  # Wait 10 seconds before retrying
                    else:
                        raise
            raise Exception("SBOM generation timed out after 5 minutes")
        except Exception as e:
            errors.append(f"Subtype '{subtype or 'None'}': {str(e)}")
    raise Exception(f"All SBOM subtype attempts failed. Errors: {'; '.join(errors)}")

def main():
    args = parse_args()
    load_dotenv(args.secrets_file)
    token = finite_state_sdk.get_auth_token(
        os.getenv('CLIENT_ID'),
        os.getenv('CLIENT_SECRET')
    )
    org_ctx = os.getenv('ORGANIZATION_CONTEXT')

    if args.asset_version_id:
        # Analyze specific asset version
        print(f"\nAnalyzing asset version {args.asset_version_id}...")
        
        try:
            # Get software components
            software_components = finite_state_sdk.get_software_components(token, org_ctx, asset_version_id=args.asset_version_id)
            
            # Extract security features
            security_features = get_security_features(software_components)
            
            # Print results
            print("\nSecurity Features:")
            print("-" * 50)
            for feature, enabled in security_features.items():
                status = "Enabled" if enabled else "Disabled"
                print(f"{feature:<15}: {status}")
                
        except Exception as e:
            print(f"Error analyzing asset version: {str(e)}")
            
    else:
        # Get all asset versions
        print("\nFetching asset versions...")
        asset_versions = finite_state_sdk.get_all_asset_versions(token, org_ctx)
        
        print(f"\nFound {len(asset_versions)} asset versions to analyze")
        print("\nSecurity Features Analysis:")
        print("-" * 80)
        print(f"{'Asset Name':<30} {'Version':<20} {'StackGuard':<10} {'DEP':<10} {'RELRO':<10} {'PIC':<10} {'ASLR':<10}")
        print("-" * 80)
        
        for asset_version in asset_versions:
            asset = asset_version.get('asset', {})
            asset_name = asset.get('name', 'N/A')
            version_name = asset_version.get('name', 'N/A')
            
            # Get software components
            try:
                software_components = finite_state_sdk.get_software_components(token, org_ctx, asset_version_id=asset_version.get('id'))
                
                # Extract security features
                security_features = get_security_features(software_components)
                
                # Print results
                print(f"{asset_name:<30} {version_name:<20} "
                      f"{'Yes' if security_features['stackguard'] else 'No':<10} "
                      f"{'Yes' if security_features['dep'] else 'No':<10} "
                      f"{'Yes' if security_features['relro-full'] else 'No':<10} "
                      f"{'Yes' if security_features['pic'] else 'No':<10} "
                      f"{'Yes' if security_features['aslr'] else 'No':<10}")
                
            except Exception as e:
                print(f"{asset_name:<30} {version_name:<20} Error: {str(e)}")

if __name__ == '__main__':
    main() 