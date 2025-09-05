#!/bin/bash
# Quick reload script for ACOR development
# Use this when you've made changes and need to reload

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Reloading ACOR...${NC}"

# Check if we're in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "Error: No virtual environment found. Run ./install.sh first"
        exit 1
    fi
fi

# Reinstall in development mode (updates metadata, version, etc.)
pip install -e . --force-reinstall --no-deps --quiet

# Get version
VERSION=$(acor --version 2>&1)
echo -e "${GREEN}✓ $VERSION reloaded${NC}"

# Quick test
echo ""
echo "Testing installation:"
acor --help | head -n 3