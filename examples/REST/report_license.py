#!/usr/bin/env python3
"""
Finite State License Report Generator

A CLI tool that pulls license data from the Finite State REST API and emits
CSV, JSON, and searchable HTML reports.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

import pandas as pd
import requests
from jinja2 import Template
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Configuration
TOKEN = os.getenv("FINITE_STATE_AUTH_TOKEN")
DOMAIN = os.getenv("FINITE_STATE_DOMAIN")
if not DOMAIN:
    console.print("[red]Error: FINITE_STATE_DOMAIN environment variable is required[/red]")
    console.print("Set it with: export FINITE_STATE_DOMAIN='your_domain.finitestate.io'")
    sys.exit(1)
HEADERS = {"X-Authorization": TOKEN}
BASE_URL = f"https://{DOMAIN}/api/public/v0"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Report - {{ project_name }}</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/2/datables.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --fs-primary: #0f172a;
            --fs-secondary: #475569;
            --fs-accent: #3b82f6;
            --fs-accent-hover: #2563eb;
            --fs-success: #10b981;
            --fs-warning: #f59e0b;
            --fs-error: #ef4444;
            --fs-bg-primary: #ffffff;
            --fs-bg-secondary: #f8fafc;
            --fs-bg-tertiary: #f1f5f9;
            --fs-border: #e2e8f0;
            --fs-border-light: #f1f5f9;
            --fs-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            --fs-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--fs-bg-secondary);
            color: var(--fs-primary);
            line-height: 1.6;
            font-size: 14px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            background: var(--fs-bg-primary);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--fs-shadow);
            border: 1px solid var(--fs-border);
        }

        .header h1 {
            color: var(--fs-primary);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }

        .header .project-info {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }

        .header .project-name {
            color: var(--fs-primary);
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }

        .header .version-info {
            color: var(--fs-secondary);
            font-size: 1rem;
            font-weight: 400;
        }

        .summary {
            background: var(--fs-bg-primary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--fs-shadow);
            border: 1px solid var(--fs-border);
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }

        .summary-item {
            text-align: center;
        }

        .summary-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--fs-accent);
            display: block;
            margin-bottom: 0.25rem;
        }

        .summary-label {
            font-size: 0.875rem;
            color: var(--fs-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .table-container {
            background: var(--fs-bg-primary);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--fs-shadow);
            border: 1px solid var(--fs-border);
            overflow: hidden;
        }

        /* DataTables Customization */
        .dataTables_wrapper {
            font-family: 'Inter', sans-serif;
        }

        .dataTables_wrapper .dataTables_length,
        .dataTables_wrapper .dataTables_filter,
        .dataTables_wrapper .dataTables_info,
        .dataTables_wrapper .dataTables_paginate {
            margin: 1rem 0;
        }

        .dataTables_wrapper .dataTables_filter input {
            border: 1px solid var(--fs-border);
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
            background: var(--fs-bg-primary);
            color: var(--fs-primary);
        }

        .dataTables_wrapper .dataTables_filter input:focus {
            outline: none;
            border-color: var(--fs-accent);
            box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
        }

        .dataTables_wrapper .dataTables_length select {
            border: 1px solid var(--fs-border);
            border-radius: 6px;
            padding: 0.25rem 0.5rem;
            background: var(--fs-bg-primary);
            color: var(--fs-primary);
        }

        .dataTables_wrapper .dataTables_paginate .paginate_button {
            border: 1px solid var(--fs-border);
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            margin: 0 0.125rem;
            background: var(--fs-bg-primary);
            color: var(--fs-secondary) !important;
            font-weight: 500;
        }

        .dataTables_wrapper .dataTables_paginate .paginate_button:hover {
            background: var(--fs-bg-tertiary);
            border-color: var(--fs-accent);
            color: var(--fs-accent) !important;
        }

        .dataTables_wrapper .dataTables_paginate .paginate_button.current {
            background: var(--fs-accent);
            border-color: var(--fs-accent);
            color: white !important;
        }

        .dataTables_wrapper .dataTables_paginate .paginate_button.current:hover {
            background: var(--fs-accent-hover);
            border-color: var(--fs-accent-hover);
        }

        table.dataTable {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }

        table.dataTable thead th {
            background: var(--fs-bg-tertiary);
            color: var(--fs-primary);
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 1rem;
            border-bottom: 2px solid var(--fs-border);
            text-align: left;
        }

        table.dataTable tbody td {
            padding: 1rem;
            border-bottom: 1px solid var(--fs-border-light);
            color: var(--fs-primary);
            font-size: 0.875rem;
        }

        table.dataTable tbody tr:hover {
            background: var(--fs-bg-tertiary);
        }

        .license-badge {
            display: inline-block;
            background: var(--fs-bg-tertiary);
            color: var(--fs-secondary);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            border: 1px solid var(--fs-border);
        }

        .license-unknown {
            background: #fef3c7;
            color: #92400e;
            border-color: #fbbf24;
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .header {
                padding: 1.5rem;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .table-container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>License Report</h1>
            <div class="project-info">
                <div class="project-name">{{ project_name }}</div>
                {% if version_id %}
                <div class="version-info">Version: {{ version_id }}</div>
                {% endif %}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="summary-number">{{ total_components }}</span>
                    <span class="summary-label">Total Components</span>
                </div>
                <div class="summary-item">
                    <span class="summary-number">{{ unique_licenses }}</span>
                    <span class="summary-label">Unique Licenses</span>
                </div>
                <div class="summary-item">
                    <span class="summary-number">{{ generated_at }}</span>
                    <span class="summary-label">Generated</span>
                </div>
            </div>
        </div>
        
        <div class="table-container">
            <table id="licenseTable" class="display">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Version</th>
                        <th>License</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        <td><strong>{{ row['component'] }}</strong></td>
                        <td><code>{{ row['version'] }}</code></td>
                        <td>
                            {% if row['license'] == 'UNKNOWN' %}
                                <span class="license-badge license-unknown">Unknown</span>
                            {% else %}
                                {% for license in row['license'].split(' | ') %}
                                    <span class="license-badge">{{ license }}</span>
                                {% endfor %}
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script src="https://cdn.datatables.net/2/datables.js"></script>
    <script>
        new DataTable('#licenseTable', {
            pageLength: 25,
            order: [[0, 'asc'], [1, 'asc']],
            responsive: true,
            language: {
                search: "Search components:",
                lengthMenu: "Show _MENU_ components per page",
                info: "Showing _START_ to _END_ of _TOTAL_ components",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    </script>
</body>
</html>
"""

def validate_environment() -> None:
    """Validate required environment variables."""
    if not TOKEN:
        console.print("[red]Error: FINITE_STATE_AUTH_TOKEN environment variable is required[/red]")
        sys.exit(1)

def fetch_all_projects() -> List[Dict]:
    url = f"{BASE_URL}/projects"
    projects = []
    page = 0
    while True:
        resp = requests.get(url, headers=HEADERS, params={"page": page, "size": 100})
        if resp.status_code != 200:
            console.print(f"[red]Failed to fetch projects: {resp.status_code}[/red]")
            sys.exit(1)
        data = resp.json()
        if not data or not isinstance(data, list):
            break
        projects.extend(data)
        if len(data) < 100:
            break
        page += 1
    return projects

def get_project_and_latest_version_id_by_name(project_name: str):
    projects = fetch_all_projects()
    for project in projects:
        if project.get("name") == project_name:
            project_id = project.get("id")
            version_id = (
                project.get("defaultBranch", {})
                .get("latestVersion", {})
                .get("id")
            )
            return project_id, version_id
    return None, None

def get_latest_version_id_by_project_id(project_id: str):
    projects = fetch_all_projects()
    version_id = None
    for project in projects:
        if project.get("id") == project_id:
            version_id = (
                project.get("defaultBranch", {})
                .get("latestVersion", {})
                .get("id")
            )
            break
    return version_id

def get_latest_version_id(project_id: str) -> Optional[str]:
    url = f"{BASE_URL}/projects/{project_id}/versions"
    resp = requests.get(url, headers=HEADERS, params={"page": 0, "size": 1})
    if resp.status_code != 200:
        console.print(f"[red]Failed to fetch versions: {resp.status_code}[/red]")
        sys.exit(1)
    data = resp.json()
    if isinstance(data, list) and data:
        return data[0].get("id")
    return None

def fetch_components(version_id: str) -> List[Dict]:
    url = f"{BASE_URL}/versions/{version_id}/components"
    components = []
    page = 0
    while True:
        resp = requests.get(url, headers=HEADERS, params={"page": page, "size": 100})
        if resp.status_code != 200:
            console.print(f"[red]Failed to fetch components: {resp.status_code}[/red]")
            sys.exit(1)
        data = resp.json()
        if not data or not isinstance(data, list):
            break
        components.extend(data)
        if len(data) < 100:
            break
        page += 1
    return components

def filter_components_by_project(components: List[Dict[str, Any]], project_id: str) -> List[Dict[str, Any]]:
    """Filter components by project ID."""
    filtered = []
    for component in components:
        if component.get("project", {}).get("id") == project_id:
            filtered.append(component)
    return filtered

def filter_components_by_version(components: List[Dict[str, Any]], version_id: str) -> List[Dict[str, Any]]:
    """Filter components by version ID."""
    filtered = []
    for component in components:
        if component.get("projectVersion", {}).get("id") == version_id:
            filtered.append(component)
    return filtered

def find_project_by_name(components, project_name):
    """Find project ID by name from components data"""
    for component in components:
        if component.get('name') == project_name:
            return component.get('projectId')
    return None

def get_project_name_from_components(components: List[Dict[str, Any]], version_id: str) -> Optional[str]:
    """Get project name from components for a specific version."""
    if not components:
        return None
    for component in components:
        if component.get("project", {}).get("name"):
            return component.get("project", {}).get("name")
        if component.get("projectVersion", {}).get("project", {}).get("name"):
            return component.get("projectVersion", {}).get("project", {}).get("name")
    potential_project_names = []
    for component in components:
        component_name = component.get("name")
        if component_name and component_name != "UNKNOWN":
            if (not "/" in component_name and 
                not "." in component_name and 
                not component_name.startswith("org.") and
                not component_name.startswith("com.") and
                not component_name.startswith("io.") and
                not component_name.startswith("net.") and
                len(component_name) > 2):
                potential_project_names.append(component_name)
    if potential_project_names:
        project_name = max(potential_project_names, key=len)
        return project_name
    return None

def extract_components_from_sbom(sbom_data: Dict) -> List[Dict]:
    """Extract components from SBOM (CycloneDX or SPDX format)."""
    components = []
    
    # Handle CycloneDX format
    if "components" in sbom_data:
        for component in sbom_data["components"]:
            components.append({
                "name": component.get("name", "UNKNOWN"),
                "version": component.get("version", "UNKNOWN"),
                "licenses": component.get("licenses", []),
                "purl": component.get("purl", "")
            })
    
    # Handle SPDX format
    elif "packages" in sbom_data:
        for package in sbom_data["packages"]:
            licenses = []
            if "licenseInfoFromFiles" in package:
                licenses.extend(package["licenseInfoFromFiles"])
            if "licenseConcluded" in package:
                licenses.append(package["licenseConcluded"])
            
            components.append({
                "name": package.get("name", "UNKNOWN"),
                "version": package.get("versionInfo", "UNKNOWN"),
                "licenses": licenses,
                "purl": package.get("externalRefs", [{}])[0].get("referenceLocator", "") if package.get("externalRefs") else ""
            })
    
    return components

def has_license_data(sbom_data: Dict) -> bool:
    """Check if SBOM contains license information."""
    # Check CycloneDX format
    if "components" in sbom_data:
        for component in sbom_data["components"]:
            licenses = component.get("licenses", [])
            if licenses:
                # Check if any license has actual data
                for license_info in licenses:
                    if isinstance(license_info, dict):
                        if (license_info.get("license") or 
                            license_info.get("spdxId") or 
                            license_info.get("name") or
                            license_info.get("url")):
                            return True
                    elif isinstance(license_info, str) and license_info.strip():
                        return True
                return True
    
    # Check SPDX format
    elif "packages" in sbom_data:
        for package in sbom_data["packages"]:
            # Check various SPDX license fields
            if (package.get("licenseInfoFromFiles") or 
                package.get("licenseConcluded") or
                package.get("licenseDeclared") or
                package.get("licenseInfoInFiles")):
                return True
    
    # Check if there are any components at all (even without licenses)
    # This might be useful for debugging
    if "components" in sbom_data and sbom_data["components"]:
        return True
    elif "packages" in sbom_data and sbom_data["packages"]:
        return True
    
    return False

def fetch_sbom_json(version_id: str) -> Dict:
    """Fetch SBOM for a version in CycloneDX JSON format."""
    # Try SPDX first then fall back to CycloneDX
    for sbom_format in ["spdx", "cyclonedx"]:
        try:
            response = requests.get(f"{BASE_URL}/sboms/{sbom_format}/{version_id}", 
                                  headers=HEADERS, 
                                  timeout=30)
            if response.status_code == 200:
                console.print(f"[blue]✓ Successfully fetched {sbom_format.upper()} SBOM[/blue]")
                return response.json()
            elif response.status_code == 404:
                console.print(f"[yellow]⚠ {sbom_format.upper()} SBOM not available, trying next format...[/yellow]")
                continue
            else:
                console.print(f"[yellow]⚠ {sbom_format.upper()} SBOM returned {response.status_code}, trying next format...[/yellow]")
                continue
        except Exception as e:
            console.print(f"[yellow]⚠ {sbom_format.upper()} SBOM fetch failed: {e}, trying next format...[/yellow]")
            continue
    
    raise Exception("Both SPDX and CycloneDX SBOM formats failed")

def test_available_endpoints() -> None:
    """Test which endpoints are available for debugging."""
    console.print("[blue]Testing available endpoints...[/blue]")
    
    test_endpoints = [
        f"{BASE_URL}/components",
        f"{BASE_URL}/projects",
        f"{BASE_URL}/sboms/cyclonedx/test",
        f"{BASE_URL}/sboms/spdx/test",
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(endpoint, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                console.print(f"[green]✓ {endpoint} - OK[/green]")
            else:
                console.print(f"[yellow]⚠ {endpoint} - {response.status_code}[/yellow]")
        except Exception as e:
            console.print(f"[red]✗ {endpoint} - {e}[/red]")

def fetch_components_api(version_id: str) -> List[Dict]:
    """Fetch components for a specific version."""
    # Try different possible endpoints for components
    possible_endpoints = [
        f"{BASE_URL}/components?versionId={version_id}",
        f"{BASE_URL}/components?projectVersionId={version_id}",
        f"{BASE_URL}/components?version={version_id}"
    ]
    
    for endpoint in possible_endpoints:
        try:
            console.print(f"[blue]Trying component endpoint: {endpoint}[/blue]")
            response = requests.get(endpoint, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    console.print(f"[green]✓ Found components via: {endpoint}[/green]")
                    return data
                elif isinstance(data, dict) and "data" in data:
                    console.print(f"[green]✓ Found components via: {endpoint}[/green]")
                    return data["data"]
                else:
                    console.print(f"[yellow]⚠ Unexpected response format from {endpoint}[/yellow]")
                    continue
            elif response.status_code == 404:
                console.print(f"[yellow]⚠ Endpoint not found: {endpoint}[/yellow]")
                continue
            else:
                console.print(f"[yellow]⚠ Endpoint returned {response.status_code}: {endpoint}[/yellow]")
                continue
        except Exception as e:
            console.print(f"[yellow]⚠ Endpoint failed: {endpoint} - {e}[/yellow]")
            continue
    
    raise Exception("All component API endpoints failed")

def transform_to_dataframe(components: List[Dict], delimiter: str = " | ", project_name: str = None) -> pd.DataFrame:
    """Transform components to pandas DataFrame."""
    rows = []
    seen_components = set()
    
    for component in components:
        component_key = f"{component.get('name', '')}-{component.get('version', '')}"
        
        # Keep first occurrence of duplicate components
        if component_key in seen_components:
            continue
        seen_components.add(component_key)
        
        # Skip project-level components (component name matches project name)
        if project_name and component.get("name") == project_name:
            continue
        
        lic_names = []
        
        # Handle different license formats
        licenses = component.get("licenses", [])
        if isinstance(licenses, str):
            lic_names.append(licenses)
        elif isinstance(licenses, list):
            for license_info in licenses:
                if isinstance(license_info, dict):
                    lic_name = license_info.get("license") or license_info.get("spdxId") or license_info.get("name", "UNKNOWN")
                else:
                    lic_name = str(license_info)
                lic_names.append(lic_name)
        
        rows.append({
            "component": component.get("name", "UNKNOWN"),
            "version": component.get("version", "UNKNOWN"),
            "license": delimiter.join(lic_names) if lic_names else "UNKNOWN"
        })
    
    df = pd.DataFrame(rows)
    return df.sort_values(["component", "version"])

def save_csv(df: pd.DataFrame, output_dir: Path) -> None:
    """Save DataFrame as CSV."""
    base_filename = "report_license.csv"
    counter = 0
    while True:
        if counter == 0:
            output_file = output_dir / base_filename
        else:
            name, ext = base_filename.rsplit('.', 1)
            output_file = output_dir / f"{name}_{counter}.{ext}"
        
        if not output_file.exists():
            break
        counter += 1
    
    df.to_csv(output_file, index=False)
    console.print(f"[green]✓ CSV report saved: {output_file}[/green]")

def save_json(df: pd.DataFrame, output_dir: Path) -> None:
    """Save DataFrame as JSON grouped by component."""
    base_filename = "report_license.json"
    counter = 0
    while True:
        if counter == 0:
            output_file = output_dir / base_filename
        else:
            name, ext = base_filename.rsplit('.', 1)
            output_file = output_dir / f"{name}_{counter}.{ext}"
        
        if not output_file.exists():
            break
        counter += 1
    
    # Group by component and convert to JSON
    grouped_data = {}
    for component_name, group in df.groupby("component"):
        grouped_data[component_name] = group.drop("component", axis=1).to_dict("records")
    
    with open(output_file, 'w') as f:
        json.dump(grouped_data, f, indent=2)
    
    console.print(f"[green]✓ JSON report saved: {output_file}[/green]")

def save_html(df: pd.DataFrame, output_dir: Path, project_name: str, version_id: str = None) -> None:
    """Save DataFrame as searchable HTML."""
    base_filename = "report_license.html"
    counter = 0
    while True:
        if counter == 0:
            output_file = output_dir / base_filename
        else:
            name, ext = base_filename.rsplit('.', 1)
            output_file = output_dir / f"{name}_{counter}.{ext}"
        
        if not output_file.exists():
            break
        counter += 1
    
    template = Template(HTML_TEMPLATE)
    
    # Calculate summary statistics
    unique_licenses = set()
    for licenses in df['license'].str.split(' | '):
        unique_licenses.update(licenses)
    
    html_content = template.render(
        project_name=project_name,
        version_id=version_id,
        generated_at=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_components=len(df),
        unique_licenses=len(unique_licenses),
        data=df.to_dict(orient="records")
    )
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    console.print(f"[green]✓ HTML report saved: {output_file}[/green]")

def fetch_component_licenses(component_id: str) -> List[Dict]:
    """Fetch licenses for a specific component."""
    try:
        response = requests.get(f"{BASE_URL}/components/{component_id}/licenses", 
                              headers=HEADERS, 
                              timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []

def fetch_components_with_licenses(components: List[Dict], skip_individual: bool = False) -> List[Dict]:
    """Fetch licenses for components that don't have them."""
    if skip_individual:
        console.print(f"[blue]Skipping individual license fetching (--no-individual-licenses flag set)[/blue]")
        return components
    
    enhanced_components = []
    license_fetch_attempts = 0
    license_fetch_failures = 0
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Fetching component licenses...", total=len(components))
        
        for component in components:
            # If component already has licenses, use them
            if component.get("licenses"):
                enhanced_components.append(component)
            else:
                # Try to fetch licenses for this component
                component_id = component.get("id")
                if component_id:
                    license_fetch_attempts += 1
                    licenses = fetch_component_licenses(component_id)
                    if not licenses:
                        license_fetch_failures += 1
                    component["licenses"] = licenses
                enhanced_components.append(component)
            
            progress.advance(task, 1)
    
    if license_fetch_attempts > 0:
        if license_fetch_failures == license_fetch_attempts:
            console.print(f"[yellow]⚠ Individual license fetching not available ({license_fetch_failures}/{license_fetch_attempts} failed)[/yellow]")
        elif license_fetch_failures > 0:
            console.print(f"[yellow]⚠ Some license fetches failed ({license_fetch_failures}/{license_fetch_attempts})[/yellow]")
        else:
            console.print(f"[green]✓ Successfully fetched licenses for {license_fetch_attempts} components[/green]")
    
    return enhanced_components

def get_project_name_from_sbom(sbom_data: Dict) -> Optional[str]:
    """Extract project name from SBOM data (SPDX or CycloneDX format)."""
    if "name" in sbom_data:
        name = sbom_data["name"]
        if name and name != "UNKNOWN":
            cleaned = re.split(r"\s+SBOM$", name)[0]
            cleaned = cleaned.rsplit(' ', 1)[0].strip()
            if cleaned:
                return cleaned
    if "packages" in sbom_data:
        if sbom_data["packages"]:
            for pkg in sbom_data["packages"]:
                pkg_name = pkg.get("name")
                if pkg_name and pkg_name != "UNKNOWN" and not pkg_name.startswith("/"):
                    return pkg_name
            first_package = sbom_data["packages"][0]
            package_name = first_package.get("name")
            if package_name and package_name != "UNKNOWN":
                return package_name
    elif "components" in sbom_data:
        if sbom_data["components"]:
            for comp in sbom_data["components"]:
                comp_name = comp.get("name")
                if comp_name and comp_name != "UNKNOWN" and not comp_name.startswith("/"):
                    return comp_name
            first_component = sbom_data["components"][0]
            component_name = first_component.get("name")
            if component_name and component_name != "UNKNOWN":
                return component_name
    if "metadata" in sbom_data:
        metadata = sbom_data["metadata"]
        if "name" in metadata:
            name = metadata["name"]
            if name and name != "UNKNOWN":
                return name
        if "component" in metadata:
            component = metadata["component"]
            name = component.get("name")
            if name and name != "UNKNOWN":
                return name
    return None

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate license reports from Finite State API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --project-id 3161401371292730239
  %(prog)s --project "WebGoat" --format csv,html
  %(prog)s --version-id 3045724872466332389 --format json
        """
    )
    
    # Project selection (mutually exclusive)
    project_group = parser.add_mutually_exclusive_group(required=True)
    project_group.add_argument("--project-id", help="Project ID to fetch latest version")
    project_group.add_argument("--project", help="Project name to resolve and fetch latest version")
    project_group.add_argument("--version-id", help="Specific version ID to process")
    
    # Optional arguments
    parser.add_argument("--source", choices=["sbom", "components"], default="sbom",
                       help="Data source (default: sbom)")
    parser.add_argument("--format", default="csv", 
                       help="Output formats: csv, json, html (comma-separated for multiple)")
    parser.add_argument("--outdir", type=Path, default=Path("./reports"),
                       help="Output directory (default: ./reports)")
    parser.add_argument("--delimiter", default=" | ",
                       help="Delimiter for multiple licenses (default: ' | ')")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode to test available endpoints")
    parser.add_argument("--no-individual-licenses", action="store_true",
                       help="Skip individual license fetching (since it often fails)")
    
    args = parser.parse_args()
    
    # Validate environment
    validate_environment()
    
    # Debug mode: test available endpoints
    if args.debug:
        test_available_endpoints()
        return
    
    # Create output directory
    args.outdir.mkdir(parents=True, exist_ok=True)
    
    # Determine project and version information
    project_name = "Unknown Project"
    version_id = None
    project_id = None
    
    if args.project:
        console.print(f"[blue]Searching for project: {args.project}[/blue]")
        project_id, version_id = get_project_and_latest_version_id_by_name(args.project)
        if not project_id:
            console.print(f"[red]Error: Project '{args.project}' not found[/red]")
            sys.exit(1)
        project_name = args.project
    elif args.project_id:
        project_id = args.project_id
        version_id = get_latest_version_id_by_project_id(project_id)
        if not version_id:
            console.print(f"[red]Error: No latest version found for project ID '{project_id}'[/red]")
            sys.exit(1)
        # Get project name from the project data
        projects = fetch_all_projects()
        project_name = None
        for project in projects:
            if project.get("id") == project_id:
                project_name = project.get("name")
                break
        if not project_name:
            project_name = f"Project {project_id}"
    elif args.version_id:
        version_id = args.version_id
        # We'll extract the project name from components after fetching them
        project_name = "Unknown Project"
    
    # Fetch components based on data source and project/version selection
    components = []
    all_components = None  # Cache for reuse
    sbom_data = None  # Store SBOM data for project name extraction
    
    # First, ensure we have a version_id for SBOM approach
    if not version_id and project_id:
        # Get latest version if not specified
        console.print(f"[blue]Getting latest version for project {project_id}...[/blue]")
        all_components = fetch_components(None)
        version_id = get_latest_version_id(project_id)
        if version_id:
            console.print(f"[blue]Using latest version: {version_id}[/blue]")
        else:
            console.print(f"[yellow]No version ID found for project {project_id}, will use component filtering[/yellow]")
    
    # Now try SBOM approach if we have a version_id and source is sbom
    if args.source == "sbom" and version_id:
        try:
            console.print("[blue]Attempting to fetch SBOM...[/blue]")
            sbom_data = fetch_sbom_json(version_id)
            
            if has_license_data(sbom_data):
                components = extract_components_from_sbom(sbom_data)
                console.print(f"[green]✓ Successfully extracted {len(components)} components from SBOM[/green]")
            else:
                console.print("[yellow]SBOM missing license info, falling back to component API...[/yellow]")
                try:
                    components = fetch_components(version_id)
                except Exception as e:
                    console.print(f"[yellow]Component API failed ({e}), using all components with filtering...[/yellow]")
                    if all_components is None:
                        all_components = fetch_components(None)
                    if version_id:
                        components = filter_components_by_version(all_components, version_id)
        except Exception as e:
            console.print(f"[yellow]SBOM fetch failed ({e}), falling back to component API...[/yellow]")
            try:
                components = fetch_components(version_id)
            except Exception as e2:
                console.print(f"[yellow]Component API also failed ({e2}), using all components with filtering...[/yellow]")
                if all_components is None:
                    all_components = fetch_components(None)
                if version_id:
                    components = filter_components_by_version(all_components, version_id)
    else:
        # Fetch all components and filter (when source is components or no version_id)
        if not version_id:
            console.print("[blue]No version ID available, fetching all components and filtering by project...[/blue]")
        else:
            console.print("[blue]Fetching components via API...[/blue]")
        
        if all_components is None:
            all_components = fetch_components(None)
        
        if project_id:
            # Filter by project
            components = filter_components_by_project(all_components, project_id)
            
            # Filter by version if specified
            if version_id:
                components = filter_components_by_version(components, version_id)
        elif version_id:
            # Filter by version only
            components = filter_components_by_version(all_components, version_id)
    
    if not components:
        console.print("[red]Error: No components found[/red]")
        sys.exit(1)
    
    console.print(f"[green]✓ Found {len(components)} components[/green]")
    
    # Extract project name from components if we only have version_id
    if args.version_id and project_name == "Unknown Project":
        if sbom_data:
            # Try to get project name from SBOM data first
            extracted_project_name = get_project_name_from_sbom(sbom_data)
            if extracted_project_name:
                project_name = extracted_project_name
        else:
            # Fall back to component-based extraction
            extracted_project_name = get_project_name_from_components(components, version_id)
            if extracted_project_name:
                project_name = extracted_project_name
    
    # Fetch licenses for components that don't have them
    components = fetch_components_with_licenses(components, args.no_individual_licenses)
    
    # Transform to DataFrame
    df = transform_to_dataframe(components, args.delimiter, project_name)
    
    # Determine output formats
    formats = [f.strip() for f in args.format.split(",")]
    valid_formats = ["csv", "json", "html"]
    
    # Generate reports
    for fmt in formats:
        if fmt == "csv":
            save_csv(df, args.outdir)
        elif fmt == "json":
            save_json(df, args.outdir)
        elif fmt == "html":
            save_html(df, args.outdir, project_name, version_id)
        elif fmt == "sbom":
            console.print(f"[yellow]Warning: 'sbom' is not a valid output format. Use --source sbom to use SBOM as data source.[/yellow]")
            console.print(f"[yellow]Valid output formats are: {', '.join(valid_formats)}[/yellow]")
        else:
            console.print(f"[yellow]Warning: Unknown format '{fmt}', skipping[/yellow]")
            console.print(f"[yellow]Valid formats are: {', '.join(valid_formats)}[/yellow]")
    
    console.print(f"\n[green]✓ License report generation complete![/green]")
    console.print(f"[blue]Output directory: {args.outdir.absolute()}[/blue]")

if __name__ == "__main__":
    main() 