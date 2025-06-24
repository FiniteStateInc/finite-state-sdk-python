#!/bin/bash

# Finite State REST API Tools - Setup Script
# ==========================================
#
# This script sets up the environment for the Finite State REST API Tools.
# It creates a virtual environment, installs dependencies, and checks configuration.
#
# Requirements:
# - Python 3.11 or higher
# - Internet connection for pip installs
# - Finite State API access
#
# Usage:
#   ./setup_rest_tools.sh
#
# After setup, activate the environment and set your API token:
#   source .venv/bin/activate
#   export FINITE_STATE_AUTH_TOKEN='your_token_here'
#   python report_license.py --help

set -e

echo "🚀 Setting up Finite State REST API Tools"
echo "========================================="

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11 or higher is required. Found: $python_version"
    echo "Please upgrade Python and try again."
    echo ""
    echo "Installation options:"
    echo "- macOS: brew install python@3.11"
    echo "- Ubuntu/Debian: sudo apt install python3.11"
    echo "- Windows: Download from python.org"
    exit 1
fi

echo "✓ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment for this script
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed successfully"

# Check environment variables
echo ""
echo "🔐 Environment Variables Check"
echo "=============================="

if [ -z "$FINITE_STATE_AUTH_TOKEN" ]; then
    echo "⚠️  FINITE_STATE_AUTH_TOKEN is not set"
    echo "   Set it with: export FINITE_STATE_AUTH_TOKEN='your_token_here'"
    echo "   Or add it to your shell profile (.bashrc, .zshrc, etc.)"
    echo ""
    echo "   Example:"
    echo "   echo 'export FINITE_STATE_AUTH_TOKEN=\"your_token_here\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
else
    echo "✓ FINITE_STATE_AUTH_TOKEN is set"
fi

if [ -z "$FINITE_STATE_DOMAIN" ]; then
    echo "⚠️  FINITE_STATE_DOMAIN is not set"
    echo "   Set it with: export FINITE_STATE_DOMAIN='your_domain.finitestate.io'"
    echo "   This is required for the tools to work"
else
    echo "✓ FINITE_STATE_DOMAIN is set to: $FINITE_STATE_DOMAIN"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "⚠️  IMPORTANT: Virtual environment activation"
echo "============================================="
echo "The virtual environment was activated for this setup script, but you need"
echo "to activate it manually in your shell session to use the tools:"
echo ""
echo "   source .venv/bin/activate"
echo ""
echo "Or use the provided activation script:"
echo "   source activate_env.sh"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Activate the virtual environment (see above)"
echo "2. Set your FINITE_STATE_AUTH_TOKEN if not already set"
echo "3. Test the installation: python report_license.py --help"
echo ""
echo "🚀 Available Tools:"
echo "=================="
echo "• report_license.py - Generate license reports (CSV, JSON, HTML)"
echo ""
echo "🚀 Quick Start Examples:"
echo "======================="
echo "# Get help for license report tool"
echo "python report_license.py --help"
echo ""
echo "# Generate CSV report for a project"
echo "python report_license.py --project-id -8938301768799071505 --format csv"
echo ""
echo "# Generate HTML report for a project by name"
echo "python report_license.py --project \"WebGoat\" --format html"
echo ""
echo "# Generate all formats for a specific version"
echo "python report_license.py --version-id 3045724872466332389 --format csv,json,html"
echo ""
echo "📖 For more information, see README.md"
echo "🐛 For issues, check the README.md troubleshooting section" 