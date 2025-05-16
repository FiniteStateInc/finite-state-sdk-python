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
python report_asset_version_comparison.py --secrets-file .env --csv [output_file.csv]
```
**Output:** CSV file with columns:
- Asset Name
- Version
- Risk Score
- Vulnerabilities

### 2. Asset Risk Scores Report
**Script:** `report_asset_risk_scores.py`
**Purpose:** Analyze risk scores across all assets to identify high-risk items.
**Usage:**
```bash
python report_asset_risk_scores.py --secrets-file .env --csv [output_file.csv]
```
**Output:** CSV file with risk scores and associated metrics for each asset.

### 3. Vulnerability Severity Trends Report
**Script:** `report_vulnerability_severity_trends.py`
**Purpose:** Track changes in vulnerability severity over time.
**Usage:**
```bash
python report_vulnerability_severity_trends.py --secrets-file .env --csv [output_file.csv]
```
**Output:** CSV file showing vulnerability severity trends over time.

### 4. Vulnerabilities Over Time Report
**Script:** `report_vulnerabilities_over_time.py`
**Purpose:** Track vulnerability counts across asset versions over time.
**Usage:**
```bash
python report_vulnerabilities_over_time.py --secrets-file .env --csv [output_file.csv] [--debug]
```
**Output:** CSV file with historical vulnerability data.

### 5. Assets Over Time Report
**Script:** `report_assets_over_time.py`
**Purpose:** Track changes in assets over time.
**Usage:**
```bash
python report_assets_over_time.py --secrets-file .env --csv [output_file.csv]
```
**Output:** CSV file showing asset changes over time.

### 6. Uploads Over Time Report
**Script:** `report_uploads_over_time.py`
**Purpose:** Track upload activity and types.
**Usage:**
```bash
python report_uploads_over_time.py --secrets-file .env --csv [output_file.csv]
```
**Output:** CSV file with upload history and statistics.

## Common Options

Most reports support the following options:
- `--secrets-file`: Path to your .env file (required)
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