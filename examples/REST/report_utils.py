import os
from datetime import datetime

from dotenv import load_dotenv
from fpdf import FPDF
import requests


def get_api_config():
    """
    Load API config from .env and return base_url and headers.
    """
    load_dotenv()
    token = os.environ.get("FINITE_STATE_AUTH_TOKEN")
    domain = os.environ.get("FINITE_STATE_DOMAIN")

    if not token:
        raise ValueError("FINITE_STATE_AUTH_TOKEN must be set in .env")
    if not domain:
        raise ValueError("FINITE_STATE_DOMAIN must be set in .env")

    base_url = f"https://{domain}/api/public/v0"
    headers = {"X-Authorization": token}

    return base_url, headers


class PDF(FPDF):
    """
    Custom PDF class to handle headers and footers.
    """
    def header(self):
        # No header for this report
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def title_page(self, project_name, version_name):
        self.add_page()
        self.set_font('helvetica', 'B', 24)
        self.cell(0, 40, 'Project Risk Summary', 0, 1, 'C')

        self.set_font('helvetica', '', 16)
        self.cell(0, 15, f'Project: {project_name}', 0, 1, 'C')
        self.cell(0, 15, f'Version: {version_name}', 0, 1, 'C')
        self.cell(0, 15, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')

    def findings_breakdown_page(self, findings_counts):
        self.add_page()
        self.set_font('helvetica', 'B', 18)
        self.cell(0, 20, 'Findings Breakdown by Type', 0, 1, 'L')

        self.set_font('helvetica', '', 12)
        for f_type, count in findings_counts.items():
            self.cell(0, 10, f'- {f_type}: {count}', 0, 1, 'L')


def fetch_all_projects(base_url, headers):
    """Fetch all projects from the API."""
    all_projects = []
    offset = 0
    limit = 100
    while True:
        url = f"{base_url}/projects?limit={limit}&offset={offset}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json()
        if not projects:
            break
        all_projects.extend(projects)
        if len(projects) < limit:
            break
        offset += limit
    return all_projects


def get_project_id_by_name(base_url, headers, project_name):
    """Find a project ID by its name by fetching all projects."""
    print("Fetching all projects to find the correct ID...")
    projects = fetch_all_projects(base_url, headers)
    for project in projects:
        if project.get("name") == project_name:
            return project.get("id")
    return None


def get_latest_version_for_project(base_url, headers, project_id):
    """Get the latest version object for a given project ID from its default branch."""
    url = f"{base_url}/projects/{project_id}"
    print(f"Fetching project details from: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    project = response.json()
    
    latest_version = project.get("defaultBranch", {}).get("latestVersion")
    return latest_version
