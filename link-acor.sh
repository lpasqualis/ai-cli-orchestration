#!/bin/bash
# Quick script to link ACOR development version to current project
# Can be copied to other projects or run remotely

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Default ACOR location (update this to your ACOR development path)
DEFAULT_ACOR_DIR="/Users/lpasqualis/Dropbox/prj/acor-cli"

echo -e "${GREEN}ACOR Development Linker${NC}"
echo "======================="
echo ""

# Allow override via environment variable or argument
ACOR_DIR=${ACOR_DEV_PATH:-${1:-$DEFAULT_ACOR_DIR}}

# Check if ACOR directory exists
if [ ! -d "$ACOR_DIR" ]; then
    echo -e "${RED}Error: ACOR directory not found at: $ACOR_DIR${NC}"
    echo ""
    echo "Please specify the correct path:"
    echo "  $0 /path/to/acor-cli"
    echo ""
    echo "Or set the ACOR_DEV_PATH environment variable:"
    echo "  export ACOR_DEV_PATH=/path/to/acor-cli"
    exit 1
fi

# Check for install-dev.sh in ACOR directory
if [ ! -f "$ACOR_DIR/install-dev.sh" ]; then
    echo -e "${RED}Error: install-dev.sh not found in $ACOR_DIR${NC}"
    echo "This doesn't appear to be an ACOR development directory"
    exit 1
fi

# Run the install-dev script from ACOR
echo -e "${YELLOW}Installing ACOR from: $ACOR_DIR${NC}"
echo ""

# Execute the install-dev script
"$ACOR_DIR/install-dev.sh" "$@"