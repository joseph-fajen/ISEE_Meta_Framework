#!/bin/bash

# Install ISEE development aliases in shell configuration
# Usage: ./install-aliases.sh [--shell bash|zsh] [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ALIASES_FILE="$SCRIPT_DIR/dev-aliases.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Parse arguments
SHELL_TYPE=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --shell)
            SHELL_TYPE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--shell bash|zsh] [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --shell bash|zsh    Specify shell type (auto-detected if not provided)"
            echo "  --dry-run          Show what would be done without making changes"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Auto-detect shell if not specified
if [ -z "$SHELL_TYPE" ]; then
    if [ -n "$BASH_VERSION" ]; then
        SHELL_TYPE="bash"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_TYPE="zsh"
    else
        # Try to detect from $SHELL environment variable
        case "$SHELL" in
            */bash)
                SHELL_TYPE="bash"
                ;;
            */zsh)
                SHELL_TYPE="zsh"
                ;;
            *)
                error "Could not auto-detect shell type. Please specify with --shell bash or --shell zsh"
                exit 1
                ;;
        esac
    fi
fi

log "Detected/specified shell: $SHELL_TYPE"

# Determine config file
case "$SHELL_TYPE" in
    bash)
        CONFIG_FILES=("$HOME/.bashrc" "$HOME/.bash_profile")
        ;;
    zsh)
        CONFIG_FILES=("$HOME/.zshrc")
        ;;
    *)
        error "Unsupported shell: $SHELL_TYPE"
        exit 1
        ;;
esac

# Find existing config file or use the primary one
CONFIG_FILE=""
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        CONFIG_FILE="$file"
        break
    fi
done

if [ -z "$CONFIG_FILE" ]; then
    CONFIG_FILE="${CONFIG_FILES[0]}"
    warning "No existing config file found, will create: $CONFIG_FILE"
fi

log "Target configuration file: $CONFIG_FILE"

# Check if aliases are already installed
ALIAS_MARKER="# ISEE Meta Framework development aliases"
ALIAS_SOURCE_LINE="source \"$ALIASES_FILE\""

if [ -f "$CONFIG_FILE" ] && grep -q "$ALIAS_MARKER" "$CONFIG_FILE"; then
    warning "ISEE aliases appear to already be installed in $CONFIG_FILE"
    echo "If you want to reinstall, please remove the existing lines and run this script again."
    echo "Look for lines containing: $ALIAS_MARKER"
    exit 0
fi

# Show what will be added
INSTALL_BLOCK="
$ALIAS_MARKER
if [ -f \"$ALIASES_FILE\" ]; then
    $ALIAS_SOURCE_LINE
fi"

log "The following will be added to $CONFIG_FILE:"
echo "----------------------------------------"
echo "$INSTALL_BLOCK"
echo "----------------------------------------"

if [ "$DRY_RUN" = true ]; then
    log "Dry run mode - no changes made"
    exit 0
fi

# Confirm installation
read -p "Do you want to proceed with the installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Installation cancelled"
    exit 0
fi

# Install aliases
log "Installing ISEE development aliases..."

# Create config file if it doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    touch "$CONFIG_FILE"
fi

# Add aliases to config file
echo "$INSTALL_BLOCK" >> "$CONFIG_FILE"

success "ISEE development aliases installed successfully!"
echo ""
echo "Next steps:"
echo "1. Reload your shell configuration:"
echo "   source $CONFIG_FILE"
echo ""
echo "2. Or restart your terminal"
echo ""
echo "3. Run 'isee-help' to see available commands"
echo ""
echo "4. Start developing with 'isee-setup'"

# Offer to reload immediately
echo ""
read -p "Would you like to reload your shell configuration now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Reloading shell configuration..."
    source "$CONFIG_FILE"
    success "Configuration reloaded! Try running 'isee-help'"
fi