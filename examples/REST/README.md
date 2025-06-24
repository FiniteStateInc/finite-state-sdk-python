# Finite State REST API Scripts

A collection of Python CLI tools that interact with the Finite State REST API to generate reports and perform various operations.

## Current Scripts

### License Report Generator (`report_license.py`)

A comprehensive tool that pulls license data from the Finite State REST API and generates reports in CSV, JSON, and searchable HTML formats.

**Features:**
- **Flexible Output Formats**: Generate CSV, JSON, and searchable HTML reports
- **Smart Project Selection**: Use project ID, project name, or specific version ID
- **Rate Limiting**: Built-in exponential backoff for API rate limits

## Prerequisites

- Python ≥ 3.11 (tested on 3.12)
- Finite State API access token
- Required Python packages (see requirements.txt)

## Installation

### Option 1: Automated Setup (Recommended)

Use the provided setup script for a quick, automated installation:

```bash
# Make the script executable (if needed)
chmod +x setup_rest_tools.sh

# Run the setup script
./setup_rest_tools.sh
```

The setup script will:
- Check Python version requirements (3.11+)
- Create a virtual environment
- Install all dependencies
- Verify environment variables
- Provide next steps and examples

After running the setup script, activate the environment:
```bash
source .venv/bin/activate
```

### Option 2: Manual Installation

If you prefer manual installation or the setup script doesn't work for your environment:

1. **Clone or navigate to the project directory:**
   ```bash
   cd /path/to/finite-state-sdk-python/examples/REST
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   export FINITE_STATE_AUTH_TOKEN="your_api_token_here"
   export FINITE_STATE_DOMAIN="your_domain.finitestate.io"
   ```

## Usage

### License Report Generator

#### Basic Examples

**Generate CSV report for a project by ID:**
```bash
python report_license.py --project-id 3161401371292730239
```

**Generate multiple formats for a project by name:**
```bash
python report_license.py --project "WebGoat" --format csv,html
```

**Generate JSON report for a specific version:**
```bash
python report_license.py --version-id 3045724872466332389 --format json
```

#### Command Line Options

```bash
usage: report_license.py (--project-id ID | --project NAME | --version-id ID)
                    [--source sbom|components] [--format csv|json|html]
                    [--outdir DIR] [--delimiter DELIM] 
```

#### Project Selection (Required - choose one)
- `--project-id ID` - Fetch latest version of the given project ID
- `--project NAME` - Resolve project name to ID, then fetch latest version
- `--version-id ID` - Skip project lookup, operate on specific version

#### Optional Arguments
- `--source {sbom,components}` - Data source (default: sbom)
- `--format FORMAT` - Output formats: csv, json, html (comma-separated for multiple)
- `--outdir DIR` - Output directory (default: ./reports)
- `--delimiter DELIM` - Delimiter for multiple licenses (default: " | ")

### Output Files

Reports are generated in the specified output directory (default: `./reports/`):

- `report_license.csv` - Tabular data in CSV format
- `report_license.json` - Data grouped by component in JSON format
- `report_license.html` - Searchable HTML report with DataTables

## Troubleshooting

### Common Issues

**"FINITE_STATE_AUTH_TOKEN environment variable is required"**
- Ensure you've set the environment variable correctly
- Check that your shell session has the variable loaded

**"Project not found"**
- Verify the project name or ID exists in your Finite State instance
- Check your API token has access to the project

**"No components found"**
- The project version may not have any components
- Try a different version or project

**"Individual license fetching not available"**
- This is expected - individual component license endpoints may not be available
- The tool will use whatever license data is available in the component data

## API Endpoints Used

The tools interact with these Finite State API endpoints:

- `GET /components` - List all components (with pagination)
- `GET /components?versionId={id}` - Get components for specific version
- `GET /sboms/spdx/{versionId}` - Download SPDX SBOM
- `GET /sboms/cyclonedx/{versionId}` - Download CycloneDX SBOM
- `GET /components/{componentId}/licenses` - Get component licenses (may not be available)

## Contributing

When contributing to these tools:

1. Follow the existing code style and patterns
2. Add appropriate error handling
3. Include progress indicators for long-running operations
4. Test with the provided test constants
5. Update documentation for new features
6. Add new scripts to this README

## License

This tool is part of the Finite State SDK Python project. See the main LICENSE file for details. 