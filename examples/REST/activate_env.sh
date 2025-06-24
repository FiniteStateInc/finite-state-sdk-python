#!/bin/bash

# Finite State REST API Scripts - Virtual Environment Activation

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Run setup_license_report.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "✓ Virtual environment activated!"
echo "You can now run the REST API scripts."
echo ""
echo "Available scripts:"
echo "  python report_license.py --help"
echo ""
echo "To deactivate, run: deactivate" 