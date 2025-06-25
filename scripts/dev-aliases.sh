#!/bin/bash

# Development aliases and functions for ISEE Meta Framework
# Source this file in your shell configuration (.bashrc, .zshrc, etc.)
# Usage: source scripts/dev-aliases.sh

# Get the project directory (assuming this script is in scripts/ subdirectory)
ISEE_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
export ISEE_COLOR_RED='\033[0;31m'
export ISEE_COLOR_GREEN='\033[0;32m'
export ISEE_COLOR_YELLOW='\033[1;33m'
export ISEE_COLOR_BLUE='\033[0;34m'
export ISEE_COLOR_NC='\033[0m' # No Color

# Helper function to check if we're in the ISEE project directory
_isee_check_dir() {
    if [ "$PWD" != "$ISEE_PROJECT_DIR" ]; then
        echo -e "${ISEE_COLOR_YELLOW}[WARNING]${ISEE_COLOR_NC} Not in ISEE project directory. Current: $PWD"
        echo -e "${ISEE_COLOR_BLUE}[INFO]${ISEE_COLOR_NC} Expected: $ISEE_PROJECT_DIR"
        echo -e "${ISEE_COLOR_BLUE}[INFO]${ISEE_COLOR_NC} Run 'isee-cd' to navigate to project directory"
        return 1
    fi
    return 0
}

# Navigation aliases
alias isee-cd='cd "$ISEE_PROJECT_DIR" && pwd'
alias isee-scripts='cd "$ISEE_PROJECT_DIR/scripts" && pwd'

# Development server management
alias isee-start='$ISEE_PROJECT_DIR/scripts/dev-server.sh start'
alias isee-stop='$ISEE_PROJECT_DIR/scripts/dev-server.sh stop'
alias isee-restart='$ISEE_PROJECT_DIR/scripts/dev-server.sh restart'
alias isee-status='$ISEE_PROJECT_DIR/scripts/dev-server.sh status'
alias isee-logs='$ISEE_PROJECT_DIR/scripts/dev-server.sh logs'

# Port management
alias isee-ports='$ISEE_PROJECT_DIR/scripts/check-ports.sh'
alias isee-kill-port='$ISEE_PROJECT_DIR/scripts/kill-port.sh'
alias isee-kill-dev-ports='$ISEE_PROJECT_DIR/scripts/kill-dev-ports.sh'

# Quick development workflow
alias isee-dev='isee-cd && isee-status && echo -e "\n${ISEE_COLOR_GREEN}Development environment ready!${ISEE_COLOR_NC}"'
alias isee-clean='isee-stop && isee-kill-dev-ports && echo -e "${ISEE_COLOR_GREEN}Development environment cleaned!${ISEE_COLOR_NC}"'

# Testing and validation
alias isee-test='cd "$ISEE_PROJECT_DIR" && python tests/test_runner.py --quick'
alias isee-test-full='cd "$ISEE_PROJECT_DIR" && python tests/test_runner.py'

# Configuration and environment
alias isee-config='cd "$ISEE_PROJECT_DIR" && python -c "import json; config=json.load(open(\"openrouter_config.json\")); print(f\"Configuration loaded: {len(config[\"models\"][\"api_models\"])} models available\")"'
alias isee-deps='cd "$ISEE_PROJECT_DIR" && pip install -r requirements.txt'

# Git shortcuts
alias isee-git-status='cd "$ISEE_PROJECT_DIR" && git status'
alias isee-git-log='cd "$ISEE_PROJECT_DIR" && git log --oneline -10'
alias isee-git-branch='cd "$ISEE_PROJECT_DIR" && git branch --show-current'

# Functions for more complex operations

# Quick development setup
isee-setup() {
    echo -e "${ISEE_COLOR_BLUE}[ISEE]${ISEE_COLOR_NC} Setting up development environment..."
    
    isee-cd
    
    echo -e "${ISEE_COLOR_BLUE}[ISEE]${ISEE_COLOR_NC} Checking dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo -e "${ISEE_COLOR_YELLOW}[WARNING]${ISEE_COLOR_NC} requirements.txt not found"
    fi
    
    echo -e "${ISEE_COLOR_BLUE}[ISEE]${ISEE_COLOR_NC} Cleaning up any existing processes..."
    isee-clean
    
    echo -e "${ISEE_COLOR_BLUE}[ISEE]${ISEE_COLOR_NC} Starting development server..."
    isee-start
    
    echo -e "${ISEE_COLOR_GREEN}[ISEE]${ISEE_COLOR_NC} Development environment ready!"
    echo -e "${ISEE_COLOR_GREEN}[ISEE]${ISEE_COLOR_NC} Server: http://localhost:5001"
}

# Full development workflow restart
isee-reset() {
    echo -e "${ISEE_COLOR_BLUE}[ISEE]${ISEE_COLOR_NC} Resetting development environment..."
    
    isee-cd
    isee-clean
    sleep 2
    isee-start
    
    echo -e "${ISEE_COLOR_GREEN}[ISEE]${ISEE_COLOR_NC} Development environment reset complete!"
}

# Show help for all ISEE commands
isee-help() {
    echo -e "${ISEE_COLOR_BLUE}ISEE Meta Framework - Development Commands${ISEE_COLOR_NC}"
    echo "=============================================="
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Navigation:${ISEE_COLOR_NC}"
    echo "  isee-cd              - Navigate to project directory"
    echo "  isee-scripts         - Navigate to scripts directory"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Server Management:${ISEE_COLOR_NC}"
    echo "  isee-start           - Start development server"
    echo "  isee-stop            - Stop development server"
    echo "  isee-restart         - Restart development server"
    echo "  isee-status          - Show server status"
    echo "  isee-logs            - Follow server logs"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Port Management:${ISEE_COLOR_NC}"
    echo "  isee-ports           - Check common development ports"
    echo "  isee-kill-port <n>   - Kill processes on specific port"
    echo "  isee-kill-dev-ports  - Kill processes on all dev ports"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Development Workflow:${ISEE_COLOR_NC}"
    echo "  isee-dev             - Quick development status check"
    echo "  isee-clean           - Clean up all development processes"
    echo "  isee-setup           - Full development environment setup"
    echo "  isee-reset           - Reset development environment"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Testing:${ISEE_COLOR_NC}"
    echo "  isee-test            - Run quick parameter validation tests"
    echo "  isee-test-full       - Run full test suite"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Configuration:${ISEE_COLOR_NC}"
    echo "  isee-config          - Check configuration status"
    echo "  isee-deps            - Install/update dependencies"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Git Shortcuts:${ISEE_COLOR_NC}"
    echo "  isee-git-status      - Git status"
    echo "  isee-git-log         - Git log (last 10 commits)"
    echo "  isee-git-branch      - Show current branch"
    echo ""
    echo -e "${ISEE_COLOR_GREEN}Help:${ISEE_COLOR_NC}"
    echo "  isee-help            - Show this help message"
    echo ""
    echo -e "${ISEE_COLOR_BLUE}Project Directory:${ISEE_COLOR_NC} $ISEE_PROJECT_DIR"
    echo -e "${ISEE_COLOR_BLUE}Server URL:${ISEE_COLOR_NC} http://localhost:5001"
}

# Auto-completion for some commands (bash/zsh compatible)
if [ -n "$BASH_VERSION" ]; then
    # Bash completion
    complete -W "3000 5000 5001 8000 8080 8888 9000" isee-kill-port
elif [ -n "$ZSH_VERSION" ]; then
    # Zsh completion
    compdef '_values "port" 3000 5000 5001 8000 8080 8888 9000' isee-kill-port
fi

# Welcome message
echo -e "${ISEE_COLOR_GREEN}ISEE Meta Framework development aliases loaded!${ISEE_COLOR_NC}"
echo -e "${ISEE_COLOR_BLUE}Run 'isee-help' for available commands${ISEE_COLOR_NC}"