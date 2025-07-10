# Implementation Plan: PDF Reporting Suite

This document outlines the steps to create a suite of Python scripts that generate PDF reports based on data from the Finite State REST API.

---

## Phase 1: Setup and Shared Utilities

This phase establishes the foundation for all reports, promoting code reuse and consistency.

### Step 1.1: Update Environment
- **Action:** Ensure your Python environment has the necessary packages.
- **Command:**
  ```bash
  pip install -r examples/REST/requirements.txt
  ```

### Step 1.2: Create the Utility Module
- **Action:** Create a new file named `report_utils.py` inside the `examples/REST/` directory.
- **Purpose:** This file will hold common functions shared across all reporting scripts.
- **File:** `examples/REST/report_utils.py`

### Step 1.3: Implement Authentication Helper
- **Action:** In `report_utils.py`, add a function to handle authentication.
- **Details:** This function should load credentials from a `.env` file and return an auth token using `finite_state_sdk.get_auth_token`.
- **Example Function in `report_utils.py`:**
  ```python
  import os
  from dotenv import load_dotenv
  import finite_state_sdk

  def get_token():
      load_dotenv()
      client_id = os.environ.get("CLIENT_ID")
      client_secret = os.environ.get("CLIENT_SECRET")
      if not client_id or not client_secret:
          raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env")
      return finite_state_sdk.get_auth_token(client_id, client_secret)
  ```

### Step 1.4: Implement PDF Table Helper
- **Action:** In `report_utils.py`, add a function to render a pandas DataFrame as a table in a PDF.
- **Purpose:** This will be reused in any report that needs to display tabular data.
- **Details:** The function should accept an `fpdf2.FPDF` object and a `pandas.DataFrame` as arguments.
- **Example Function in `report_utils.py`:**
  ```python
  from fpdf import FPDF
  import pandas as pd

  def output_df_to_pdf(pdf, df):
      # Your implementation to render a df to a table
      pass
  ```

---

## Phase 2: Vulnerability Summary Report

This report will list CVEs in a PDF table.

### Step 2.1: Create Script
- **Action:** Create the file `report_vulnerability_summary.py` in `examples/REST/`.

### Step 2.2: Fetch CVE Data
- **Action:** In the script, implement a function `fetch_vulnerabilities(token, org_context)` that calls the `/public/v0/cves` endpoint using `requests`. Handle pagination.

### Step 2.3: Process Data
- **Action:** Implement a function `process_cves(cve_data)` that takes the raw JSON and returns a cleaned pandas DataFrame with columns like `cveId`, `severity`, `risk`, etc.

### Step 2.4: Generate PDF
- **Action:** Implement `generate_pdf(df, output_filename)`. This function will use `fpdf2` to create the PDF, add a title, and call the `output_df_to_pdf` utility to add the table.

### Step 2.5: Main Execution Block
- **Action:** In the `if __name__ == '__main__':` block, set up argument parsing for the output filename, call the functions in order, and save the report.

---

## Phase 3: Vulnerabilities Over Time Report

This report will show a line chart of vulnerability counts over time.

### Step 3.1: Create Script
- **Action:** Create the file `report_vulnerability_trend.py` in `examples/REST/`.

### Step 3.2: Fetch Data
- **Action:** Implement `fetch_vulnerability_counts(token, org_context)`. It should use `finite_state_sdk.get_asset_versions()` and then loop to call `finite_state_sdk.get_findings(..., count=True)` for each version.
- **Return:** A list of tuples or dicts containing `(creation_date, vulnerability_count)`.

### Step 3.3: Create Chart
- **Action:** Implement `create_trend_chart(data, output_image_path)`. This function will load the data into a DataFrame, create a line plot using `seaborn.lineplot()`, and save the chart as a PNG.

### Step 3.4: Generate PDF
- **Action:** Implement `generate_pdf(chart_image_path, output_filename)`. This will create a PDF, add a title, and embed the chart image.

### Step 3.5: Main Execution Block
- **Action:** Set up argument parsing, call the functions, and remember to delete the temporary chart image file after the PDF is saved.

---

## Phase 4: Portfolio Usage Report

This report will summarize key usage metrics for the organization.

### Step 4.1: Create Script
- **Action:** Create the file `report_portfolio_usage.py` in `examples/REST/`.

### Step 4.2: Fetch Stats
- **Action:** Implement `fetch_portfolio_stats(token, org_context)`.
- **Details:**
    - Get project/component counts from the `X-Total-Count` header of the `/public/v0/projects` and `/public/v0/components` endpoints.
    - Fetch all scan data from the `/public/v0/scans` endpoint.

### Step 4.3: Create Chart
- **Action:** Implement `create_scan_status_chart(scan_data, output_image_path)`. This will use pandas to count scan statuses and `seaborn.barplot()` to create and save a bar chart image.

### Step 4.4: Generate PDF
- **Action:** Implement `generate_pdf(stats, chart_image_path, output_filename)`.
- **Details:** This function will create a PDF, add a title, write the text-based stats (total projects, etc.), and embed the bar chart image.

### Step 4.5: Main Execution Block
- **Action:** Tie everything together in the main block, including argument parsing and cleanup of the temporary image file.