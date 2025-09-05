#!/bin/bash
# ACOR Development Installation Script
# Installs the development version of ACOR into another project's environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located (ACOR project root)
ACOR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${GREEN}ACOR Development Installation${NC}"
echo "=============================="
echo ""
echo -e "ACOR source: ${BLUE}$ACOR_DIR${NC}"
echo -e "Target project: ${BLUE}$(pwd)${NC}"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -g, --global   Install globally in current environment"
    echo "  -f, --force    Force reinstall even if already installed"
    echo "  -v, --venv     Create/use virtual environment in current directory"
    echo ""
    echo "Examples:"
    echo "  # Install in current environment"
    echo "  $0"
    echo ""
    echo "  # Create venv if needed and install"
    echo "  $0 --venv"
    echo ""
    echo "  # Force reinstall"
    echo "  $0 --force"
    exit 0
}

# Parse arguments
FORCE_INSTALL=false
CREATE_VENV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            ;;
        -f|--force)
            FORCE_INSTALL=true
            shift
            ;;
        -v|--venv)
            CREATE_VENV=true
            shift
            ;;
        -g|--global)
            # For future use
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            ;;
    esac
done

# Check if we're in the ACOR directory itself
if [ "$(pwd)" = "$ACOR_DIR" ]; then
    echo -e "${YELLOW}You're in the ACOR project directory.${NC}"
    echo "To install ACOR here, use: ./install.sh"
    echo ""
    echo "To install ACOR in another project:"
    echo "  1. cd /path/to/other/project"
    echo "  2. $0"
    exit 0
fi

# Handle virtual environment
if [ "$CREATE_VENV" = true ] && [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Activating local virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}Warning: No virtual environment active${NC}"
        echo "Consider using --venv flag or activating a virtual environment"
        echo ""
        read -p "Continue with system Python? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled"
            exit 1
        fi
    fi
else
    echo -e "${GREEN}✓ Using virtual environment: $VIRTUAL_ENV${NC}"
fi

# Check if ACOR is already installed
if pip show acor &> /dev/null; then
    INSTALLED_VERSION=$(pip show acor | grep "Version:" | cut -d' ' -f2)
    INSTALLED_LOCATION=$(pip show acor | grep "Location:" | cut -d' ' -f2)
    
    echo -e "${YELLOW}ACOR is already installed:${NC}"
    echo "  Version: $INSTALLED_VERSION"
    echo "  Location: $INSTALLED_LOCATION"
    echo ""
    
    if [ "$FORCE_INSTALL" = false ]; then
        read -p "Reinstall with development version? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled"
            exit 1
        fi
    fi
    
    # Uninstall existing version
    echo -e "${YELLOW}Removing existing ACOR installation...${NC}"
    pip uninstall -y acor
fi

# Install ACOR in editable mode from development directory
echo -e "${YELLOW}Installing ACOR from development source...${NC}"
pip install -e "$ACOR_DIR"
echo -e "${GREEN}✓ ACOR development version installed${NC}"

# Verify installation
echo ""
echo -e "${GREEN}Verification:${NC}"

# Check if acor command is available
if command -v acor &> /dev/null; then
    VERSION=$(acor --version 2>&1)
    echo -e "  ${GREEN}✓${NC} $VERSION"
    
    # Show location
    ACOR_LOCATION=$(pip show acor | grep "Editable project location:" | cut -d' ' -f4)
    if [ -n "$ACOR_LOCATION" ]; then
        echo -e "  ${GREEN}✓${NC} Linked to: ${BLUE}$ACOR_LOCATION${NC}"
    fi
else
    echo -e "  ${YELLOW}!${NC} acor command not in PATH"
    echo "  Try: python -m acor --version"
fi

# Create a project-specific configuration if it doesn't exist
if [ ! -f ".acor/config.yaml" ]; then
    echo ""
    echo -e "${YELLOW}Creating default ACOR configuration...${NC}"
    mkdir -p .acor
    cat > .acor/config.yaml << EOF
# ACOR Configuration
version: "1"
tools_dirs:
  - ".acor/tools"
  - "tools"
timeout: 120
EOF
    echo -e "${GREEN}✓ Created .acor/config.yaml${NC}"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "You can now use ACOR in this project:"
echo "  acor --help        # Show available commands"
echo "  acor status        # Check ACOR status"
echo "  acor <tool> [args] # Run a tool"
echo ""
echo "Development mode notes:"
echo "  • Changes to ACOR source code take effect immediately"
echo "  • No need to reinstall after modifying ACOR"
echo "  • Source location: $ACOR_DIR"

# If venv was created or activated, remind user
if [ "$CREATE_VENV" = true ] || [ -d "venv" ]; then
    echo ""
    echo "Remember to activate the virtual environment:"
    echo "  source venv/bin/activate"
fi