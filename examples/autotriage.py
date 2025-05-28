#!/usr/bin/env python3

import argparse
import os
import sys
import json
from dotenv import load_dotenv
from finite_state_sdk import get_auth_token, get_findings, get_software_components, update_finding_statuses
import requests
import time

# Valid triage statuses
VALID_STATUSES = {
    'AFFECTED',
    'FIXED',
    'NOT_AFFECTED',
    'UNDER_INVESTIGATION',
    'NOT_STARTED'
}

def get_current_user_id(token, org_context, debug=False):
    """
    Get the current user's ID from the Finite State API.
    """
    try:
        # GraphQL query to get all users
        query = """
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
        """
        
        # Make the API call
        response = requests.post(
            'https://platform.finitestate.io/api/v1/graphql',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'X-Organization-Context': org_context
            },
            json={
                'query': query,
                'variables': {
                    'after': None,
                    'first': 100
                }
            }
        )
        
        # Check for errors
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
            
        # Get the first user (assuming the current user is in the list)
        users = data['data']['allUsers']
        if not users:
            raise Exception("No users found in response")
            
        # For now, we'll use the first user's ID
        # TODO: In the future, we could match by email or other criteria
        user_id = users[0]['id']
        if not user_id:
            raise Exception("No user ID found in response")
            
        if debug:
            print(f"\nDEBUG: Found {len(users)} users")
            print("First user:", users[0])
            
        return user_id
        
    except Exception as e:
        print(f"Error getting current user ID: {str(e)}", file=sys.stderr)
        sys.exit(1)

def load_environment():
    """
    Load environment variables from .env file.
    Returns a tuple of (client_id, client_secret, org_context, user_id)
    """
    # Try to load from .env file
    load_dotenv()
    
    # Get required environment variables
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    org_context = os.getenv('ORGANIZATION_CONTEXT')
    user_id = os.getenv('USER_ID')
    
    # Check if all required variables are present
    missing_vars = []
    if not client_id:
        missing_vars.append('CLIENT_ID')
    if not client_secret:
        missing_vars.append('CLIENT_SECRET')
    if not org_context:
        missing_vars.append('ORGANIZATION_CONTEXT')
    if not user_id:
        missing_vars.append('USER_ID')
    
    if missing_vars:
        print("Error: Missing required environment variables:", file=sys.stderr)
        for var in missing_vars:
            print(f"  - {var}", file=sys.stderr)
        print("\nPlease create a .env file with these variables or set them in your environment.", file=sys.stderr)
        print("You can copy .env.example to .env and fill in your values.", file=sys.stderr)
        sys.exit(1)
    
    return client_id, client_secret, org_context, user_id

def view_findings(token, org_context, artifact_id, component_name=None, component_version=None, debug=False):
    """
    View all findings and their triage status for a given artifact.
    Optionally filter by component name and version.
    """
    # Get all findings for the artifact
    findings = get_findings(token, org_context, artifact_id)
    
    if not findings:
        print("No findings found for the artifact")
        return
        
    if debug:
        print("\nDEBUG: Raw findings data:")
        print(json.dumps(findings, indent=2))
        print(f"\nTotal findings received: {len(findings)}")
    
    # Filter findings if component name or version is specified
    if component_name or component_version:
        findings = [
            f for f in findings
            if f and isinstance(f, dict) and  # Ensure f is a valid dictionary
               f.get('affects') and len(f.get('affects', [])) > 0 and
               (not component_name or f.get('affects', [{}])[0].get('name') == component_name) and
               (not component_version or f.get('affects', [{}])[0].get('version') == component_version)
        ]
    
    if not findings:
        print("No findings found matching the specified criteria")
        return
    
    # Group findings by component
    component_findings = {}
    for finding in findings:
        if not finding or not isinstance(finding, dict):
            if debug:
                print(f"\nSkipping invalid finding: {finding}")
            continue
            
        affects = finding.get('affects', [])
        if not affects:
            if debug:
                print(f"\nSkipping finding {finding.get('id', 'Unknown')} - no affects data")
            continue
            
        component_name = affects[0].get('name', 'Unknown')
        component_version = affects[0].get('version', 'Unknown')
        key = f"{component_name}:{component_version}"
        
        if key not in component_findings:
            component_findings[key] = []
        component_findings[key].append(finding)
    
    # Print findings grouped by component
    print(f"\nFindings for artifact {artifact_id}:")
    print("=" * 80)
    
    # Track status counts
    status_counts = {status: 0 for status in VALID_STATUSES}
    status_counts['UNKNOWN'] = 0
    
    for component_key, component_findings_list in component_findings.items():
        component_name, component_version = component_key.split(':')
        print(f"\nComponent: {component_name} (v{component_version})")
        print("-" * 80)
        
        for finding in component_findings_list:
            if not finding or not isinstance(finding, dict):
                continue
                
            vuln_id = finding.get('vulnIdFromTool', 'Unknown')
            current_status = finding.get('currentStatus', {})
            if not isinstance(current_status, dict):
                current_status = {}
            status = current_status.get('status', 'NOT_STARTED')
            
            # Count statuses
            if status in VALID_STATUSES:
                status_counts[status] += 1
            else:
                status_counts['UNKNOWN'] += 1
            
            print(f"Vulnerability: {vuln_id}")
            print(f"Status: {status}")
            print(f"Finding ID: {finding.get('id', 'Unknown')}")
            if debug:
                print("Raw finding data:")
                print(json.dumps(finding, indent=2))
            print("-" * 40)
    
    # Print status summary
    print("\nStatus Summary:")
    print("-" * 40)
    for status, count in status_counts.items():
        if count > 0:
            print(f"{status}: {count}")

def get_component_triage_rules(token, org_context, artifact_id, component_name=None, component_version=None, debug=False):
    """
    Get triage rules for specific components or all components from a source artifact.
    Returns a dictionary mapping component names and versions to their triage statuses.
    """
    # Get all findings for the source artifact
    findings = get_findings(token, org_context, artifact_id)
    
    if not findings:
        print("No findings found for the artifact")
        return {}
        
    if debug:
        print("\nDEBUG: Processing findings for triage rules:")
        print(f"Total findings received: {len(findings)}")
    
    # Create a dictionary to store triage rules
    triage_rules = {}
    
    # Process each finding
    for finding in findings:
        if not finding or not isinstance(finding, dict):
            if debug:
                print(f"\nSkipping invalid finding: {finding}")
            continue
            
        current_status = finding.get('currentStatus', {})
        if not isinstance(current_status, dict):
            current_status = {}
        status = current_status.get('status')
        
        affects = finding.get('affects', [])
        if not affects:
            if debug:
                print(f"\nSkipping finding {finding.get('id', 'Unknown')} - no affects data")
            continue
            
        if debug:
            print(f"\nProcessing finding:")
            print(f"ID: {finding.get('id', 'Unknown')}")
            print(f"Status: {status}")
            print(f"Component: {affects[0].get('name', 'Unknown')} v{affects[0].get('version', 'Unknown')}")
            print(f"Vulnerability: {finding.get('vulnIdFromTool', 'Unknown')}")
        
        if status and status in VALID_STATUSES:  # Only process findings that have been triaged with valid status
            current_component_name = affects[0].get('name')
            current_component_version = affects[0].get('version')
            
            # Skip if we're filtering by component and this isn't a match
            if component_name and current_component_name != component_name:
                if debug:
                    print("Skipping - component name doesn't match filter")
                continue
            if component_version and current_component_version != component_version:
                if debug:
                    print("Skipping - component version doesn't match filter")
                continue
                
            if current_component_name and current_component_version:
                key = f"{current_component_name}:{current_component_version}"
                if key not in triage_rules:
                    triage_rules[key] = []
                triage_rules[key].append({
                    'status': status,
                    'finding_id': finding.get('id', 'Unknown'),
                    'vulnerability': finding.get('vulnIdFromTool', 'Unknown'),
                    'title': finding.get('title', 'Unknown'),
                    'description': finding.get('description', '')
                })
                if debug:
                    print(f"Added to triage rules for {key}")
        elif debug:
            print("Skipping - no valid status")
    
    if debug:
        print("\nDEBUG: Final triage rules:")
        print(json.dumps(triage_rules, indent=2))
        print("\nComponent matching summary:")
        for key, rules in triage_rules.items():
            print(f"\n{key}:")
            for rule in rules:
                print(f"  - {rule['vulnerability']}: {rule['status']}")
    
    return triage_rules

def apply_triage_rules(token, org_context, target_artifact_id, triage_rules, user_id, source_artifact_id, dry_run=False, debug=False):
    """
    Apply triage rules to findings in the target artifact.
    If dry_run is True, only print what would be changed without making changes.
    """
    # Get all findings for the target artifact
    target_findings = get_findings(token, org_context, target_artifact_id)
    
    if not target_findings:
        print("No findings found for the target artifact")
        return
        
    if debug:
        print("\nDEBUG: Processing target findings:")
        print(f"Total target findings: {len(target_findings)}")
    
    # Track which findings we've updated
    updated_findings = []
    unmatched_findings = []
    
    # Process each finding in the target artifact
    for finding in target_findings:
        if not finding or not isinstance(finding, dict):
            if debug:
                print(f"\nSkipping invalid finding: {finding}")
            continue
            
        affects = finding.get('affects', [])
        if not affects:
            if debug:
                print(f"\nSkipping finding {finding.get('id', 'Unknown')} - no affects data")
            continue
            
        component_name = affects[0].get('name')
        component_version = affects[0].get('version')
        vulnerability_name = finding.get('vulnIdFromTool', 'Unknown')
        
        if debug:
            print(f"\nProcessing target finding:")
            print(f"ID: {finding.get('id', 'Unknown')}")
            print(f"Component: {component_name} v{component_version}")
            print(f"Vulnerability: {vulnerability_name}")
        
        if component_name and component_version:
            key = f"{component_name}:{component_version}"
            
            # If we have a matching rule, apply it
            if key in triage_rules:
                if debug:
                    print(f"Found matching component: {key}")
                    print("Available rules:")
                    for rule in triage_rules[key]:
                        print(f"  - {rule['vulnerability']}: {rule['status']}")
                
                # Find the matching vulnerability in the rules
                matching_rule = None
                for rule in triage_rules[key]:
                    if rule['vulnerability'] == vulnerability_name:
                        matching_rule = rule
                        if debug:
                            print(f"Found matching vulnerability: {vulnerability_name}")
                        break
                
                if not matching_rule and debug:
                    print(f"No matching vulnerability found for {vulnerability_name}")
                    unmatched_findings.append({
                        'component': component_name,
                        'version': component_version,
                        'vulnerability': vulnerability_name
                    })
                
                current_status = finding.get('currentStatus', {})
                if not isinstance(current_status, dict):
                    current_status = {}
                    
                if matching_rule and current_status.get('status') != matching_rule['status']:
                    finding_id = finding.get('id')
                    if not finding_id:
                        if debug:
                            print(f"\nSkipping finding - no valid ID")
                        continue
                        
                    update = {
                        'id': finding_id,
                        'status': matching_rule['status'],
                        'component': component_name,
                        'version': component_version,
                        'vulnerability': vulnerability_name
                    }
                    updated_findings.append(update)
                    if debug:
                        print(f"\nWould update finding:")
                        print(f"ID: {finding_id}")
                        print(f"Component: {component_name} v{component_version}")
                        print(f"Vulnerability: {vulnerability_name}")
                        print(f"Current status: {current_status.get('status')}")
                        print(f"New status: {matching_rule['status']}")
            elif debug:
                print(f"No matching component found for {key}")
                unmatched_findings.append({
                    'component': component_name,
                    'version': component_version,
                    'vulnerability': vulnerability_name
                })
    
    # Print what would be changed
    if updated_findings:
        print("\nThe following changes would be made:")
        for update in updated_findings:
            print(f"Component: {update['component']} (v{update['version']})")
            print(f"Vulnerability: {update['vulnerability']}")
            print(f"Status: {update['status']}")
            print("---")
        
        if not dry_run:
            if debug:
                print(f"\nDEBUG: Using user ID: {user_id}")
            
            # Process updates in batches
            failed_updates = []
            for update in updated_findings:
                if update['id'] and update['status']:
                    if debug:
                        print(f"\nDEBUG: Updating finding {update['id']}:")
                        print(f"Status: {update['status']}")
                        print(f"User ID: {user_id}")
                    
                    # Try to apply the update with retries
                    max_retries = 3
                    retry_delay = 2  # seconds
                    success = False
                    
                    for attempt in range(max_retries):
                        try:
                            # Apply the update
                            update_finding_statuses(
                                token=token,
                                organization_context=org_context,
                                user_id=user_id,
                                finding_ids=[update['id']],
                                status=update['status'],
                                justification='COMPONENT_NOT_PRESENT' if update['status'] == 'NOT_AFFECTED' else None,
                                comment=f'Replicated from source artifact {source_artifact_id}'
                            )
                            success = True
                            break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                if debug:
                                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                                    print(f"Retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                            else:
                                print(f"Failed to update finding {update['id']} after {max_retries} attempts: {str(e)}", file=sys.stderr)
                                failed_updates.append(update)
                    
                    if success and debug:
                        print(f"Successfully updated finding {update['id']}")
            
            # Print summary
            successful_updates = len(updated_findings) - len(failed_updates)
            print(f"\nUpdated {successful_updates} findings in target artifact")
            
            if failed_updates:
                print("\nFailed to update the following findings:")
                for update in failed_updates:
                    print(f"Finding ID: {update['id']}")
                    print(f"Component: {update['component']} (v{update['version']})")
                    print(f"Vulnerability: {update['vulnerability']}")
                    print(f"Status: {update['status']}")
                    print("---")
        else:
            print(f"\nDry run: Would update {len(updated_findings)} findings in target artifact")
    else:
        print("No findings needed to be updated")
    
    # Print summary of unmatched findings
    if unmatched_findings and debug:
        print("\nUnmatched findings:")
        print("=" * 80)
        for finding in unmatched_findings:
            print(f"Component: {finding['component']} (v{finding['version']})")
            print(f"Vulnerability: {finding['vulnerability']}")
            print("---")

def main():
    parser = argparse.ArgumentParser(description='Replicate triage decisions from one artifact to another')
    parser.add_argument('source_artifact', nargs='?', help='ID of the source artifact')
    parser.add_argument('target_artifact', nargs='?', help='ID of the target artifact')
    parser.add_argument('--view', action='store_true', help='View findings for an artifact instead of replicating triage')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--component', help='Specific component name to replicate triage for')
    parser.add_argument('--version', help='Specific component version to replicate triage for')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    try:
        # Load environment variables
        client_id, client_secret, org_context, user_id = load_environment()
        
        # Get authentication token
        token = get_auth_token(client_id, client_secret)
        
        if args.view:
            if not args.source_artifact:
                print("Error: Artifact ID is required when using --view", file=sys.stderr)
                sys.exit(1)
            view_findings(token, org_context, args.source_artifact, args.component, args.version, args.debug)
        else:
            if not args.source_artifact or not args.target_artifact:
                print("Error: Both source and target artifact IDs are required for triage replication", file=sys.stderr)
                sys.exit(1)
                
            # Get triage rules from source artifact
            print(f"Getting triage rules from source artifact {args.source_artifact}...")
            triage_rules = get_component_triage_rules(
                token, 
                org_context, 
                args.source_artifact,
                args.component,
                args.version,
                args.debug
            )
            
            if not triage_rules:
                print("No triage rules found matching the specified criteria")
                sys.exit(0)
                
            # Apply triage rules to target artifact
            print(f"Applying triage rules to target artifact {args.target_artifact}...")
            apply_triage_rules(token, org_context, args.target_artifact, triage_rules, user_id, args.source_artifact, args.dry_run, args.debug)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 