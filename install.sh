#!/bin/bash
# ACOR Installation Script
# Installs ACOR in development mode with virtual environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}ACOR Installation Script${NC}"
echo "========================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo -e "Using: ${YELLOW}$PYTHON_VERSION${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Install ACOR in development mode
echo -e "${YELLOW}Installing ACOR in development mode...${NC}"
pip install -e . --force-reinstall --no-deps
echo -e "${GREEN}✓ ACOR installed${NC}"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To use ACOR:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo "  2. Run ACOR:"
echo "     acor --help"
echo ""
echo "Quick test:"
echo "  acor --version"
echo "  acor status"
echo ""

# Test the installation
if command -v acor &> /dev/null; then
    VERSION=$(acor --version 2>&1)
    echo -e "${GREEN}✓ $VERSION installed successfully${NC}"
else
    echo -e "${YELLOW}Note: Run 'source venv/bin/activate' to use acor${NC}"
fi