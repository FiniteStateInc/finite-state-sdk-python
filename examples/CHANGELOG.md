# Changelog

## [Unreleased]

### Added
- New `run_reports.py` script to execute multiple reports in sequence
  - Default behavior excludes vulnerability severity trends report
  - Support for specifying output directory
  - Option to include/exclude specific reports
  - CSV output enabled by default

### Changed
- Bug fixes
- Standardized CSV handling across all reports:
  - Default CSV filenames based on script names
  - Consistent column naming
  - Support for custom output paths
- Added group information to reports:
  - `report_assets_over_time.py`
  - `report_uploads_over_time.py`
  - `report_vulnerabilities_over_time.py`
  - `report_asset_risk_scores.py`
  - `report_asset_version_comparison.py`
- Made `--secrets-file` parameter optional in all reports
  - Reports now default to loading from `.env` in working directory
  - `--secrets-file` only required if `.env` not found in working directory

### Performance
- Optimized `report_vulnerability_severity_trends.py`:
  - Added batch processing with configurable batch size
  - Improved progress reporting
  - Added timeout handling and retry mechanism
  - Added concurrent processing for findings

### Documentation
- Updated `reports_README.md`:
  - Added detailed output field descriptions for each report
  - Added section for `run_reports.py` with usage examples
  - Clarified environment setup requirements
  - Added troubleshooting section

### Fixed
- Fixed TypeError issues in reports by correcting function calls
- Improved error handling and reporting across all scripts
- Fixed CSV output path handling in `run_reports.py` 