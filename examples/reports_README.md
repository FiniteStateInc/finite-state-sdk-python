# Finite State SDK Reports

This document provides detailed information about the various reporting scripts available in the Finite State SDK.

## Setup

### Prerequisites
- Python 3.6 or higher
- Finite State SDK installed (`pip install finite-state-sdk`)
- Access to Finite State Platform

### Environment Setup
1. Create a `.env` file in your working directory with the following variables.  They may be obtained by contacting support@finitestate.io.

```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
ORGANIZATION_CONTEXT=your_org_context
```

2. Install required dependencies:
```bash
pip install python-dotenv finite-state-sdk
```

## Available Reports

### 1. Asset Version Comparison Report
**Script:** `report_asset_version_comparison.py`
**Purpose:** Compare different versions of assets to track security improvements or regressions.
**Usage:**
```bash
python report_asset_version_comparison.py --csv [output_file.csv]
```
**Output:** CSV file with columns:
- Asset Name
- Group
- Version
- Risk Score
- Vulnerabilities

### 2. Asset Risk Scores Report
**Script:** `report_asset_risk_scores.py`
**Purpose:** Analyze risk scores across all assets to identify high-risk items.
**Usage:**
```bash
python report_asset_risk_scores.py --csv [output_file.csv]
```
**Output:** CSV file with columns:
- Asset Name
- Group
- Version
- Risk Score

### 3. Vulnerability Severity Trends Report
**Script:** `report_vulnerability_severity_trends.py`
**Purpose:** Track changes in vulnerability severity over time.
**Usage:**
```bash
python report_vulnerability_severity_trends.py --csv [output_file.csv]
```
**Output:** CSV file with columns:
- Asset Name
- Group
- Version
- Created At
- Total Vulnerabilities
- High Severity Vulnerabilities
- High Severity Percentage

### 4. Vulnerabilities Over Time Report
**Script:** `report_vulnerabilities_over_time.py`
**Purpose:** Track vulnerability counts across asset versions over time.
**Usage:**
```bash
python report_vulnerabilities_over_time.py --csv [output_file.csv] [--debug]
```
**Output:** CSV file with columns:
- Asset Name
- Group
- Version
- Vulnerabilities

### 5. Assets Over Time Report
**Script:** `report_assets_over_time.py`
**Purpose:** Track changes in assets over time.
**Usage:**
```bash
python report_assets_over_time.py --csv [output_file.csv]
```
**Output:** CSV file with two sections:
1. Summary section:
   - Date
   - Number of Assets
2. Detailed section:
   - Date
   - Asset Name
   - Asset ID
   - Group
   - Created At

### 6. Uploads Over Time Report
**Script:** `report_uploads_over_time.py`
**Purpose:** Track upload activity and types.
**Usage:**
```bash
python report_uploads_over_time.py --csv [output_file.csv]
```
**Output:** CSV file with columns:
- date
- id
- name
- group
- createdAt

## Running Multiple Reports

### Report Runner Script
**Script:** `run_reports.py`
**Purpose:** Run multiple reports in sequence with a single command.
**Usage:**
```bash
python run_reports.py [options]
```

**Options:**
- `--secrets-file`: Path to your .env file (only required if .env not found in working directory)
- `--include-severity-trends`: Include the vulnerability severity trends report (excluded by default due to long runtime)
- `--reports`: Comma-separated list of specific reports to run (e.g., "assets_over_time,uploads_over_time")
- `--no-csv`: Disable CSV output (enabled by default)
- `--output-dir`: Directory to save CSV files (default: current directory)

**Example Usage:**
```bash
# Run all reports except severity trends
python run_reports.py

# Run all reports including severity trends
python run_reports.py --include-severity-trends

# Run specific reports
python run_reports.py --reports assets_over_time,uploads_over_time

# Run reports and save CSVs to a specific directory
python run_reports.py --output-dir ./reports
```

## Common Options

Most reports support the following options:
- `--secrets-file`: Path to your .env file (only required if .env not found in working directory)
- `--csv`: Export results to CSV file (optional)
- `--debug`: Enable debug output (optional)

## Best Practices

1. **Regular Reporting:**
   - Schedule regular runs of these reports to track trends
   - Use the CSV output for integration with other tools

2. **Data Analysis:**
   - Combine multiple reports for comprehensive analysis
   - Use the debug option when troubleshooting

3. **Security Considerations:**
   - Keep your .env file secure
   - Don't commit sensitive credentials to version control

## Troubleshooting

Common issues and solutions:
1. **Authentication Errors:**
   - Verify your .env file contains correct credentials
   - Check that your organization context is valid

2. **API Rate Limits:**
   - Reports may take time to complete for large datasets
   - Consider using pagination for large result sets

3. **Missing Data:**
   - Use the --debug flag to see detailed API responses
   - Verify asset version IDs are correct

## Support

For issues or questions:
1. Check the [Finite State SDK Documentation](https://finitestateinc.github.io/finite-state-sdk-python/)
2. Contact Finite State Support
3. Submit issues on the GitHub repository 