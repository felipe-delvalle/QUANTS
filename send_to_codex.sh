#!/bin/bash

# ============================================================
# Send Context to Codex Max 5 (Continue.dev)
# ============================================================
# This script helps you send files, code, or context to 
# GPT-5.1-Codex-Max in Continue.dev
#
# Usage:
#   ./send_to_codex.sh <file_path>          # Send a file
#   ./send_to_codex.sh <file_path> "prompt" # Send with custom prompt
#   ./send_to_codex.sh --folder <path>      # Send entire folder
#   ./send_to_codex.sh --codebase           # Reference entire codebase
# ============================================================

WORKSPACE_ROOT="/Users/freedom/QUANTS"
CONTINUE_CONFIG="$WORKSPACE_ROOT/.continue/config.json"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Send to Codex Max 5 (Continue.dev)          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Continue is configured
if [ ! -f "$CONTINUE_CONFIG" ]; then
    echo -e "${YELLOW}⚠ Warning: Continue config not found${NC}"
    exit 1
fi

# Function to send a file
send_file() {
    local file_path="$1"
    local prompt="${2:-Analyze this code}"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${YELLOW}⚠ File not found: $file_path${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Preparing to send: ${BLUE}$file_path${NC}"
    echo -e "${GREEN}✓${NC} Prompt: ${BLUE}$prompt${NC}"
    echo ""
    echo -e "${YELLOW}📋 Instructions for Continue.dev:${NC}"
    echo "1. Press ${BLUE}Ctrl+Shift+L${NC} to open Continue chat"
    echo "2. Type: ${BLUE}@file $file_path${NC}"
    echo "3. Then type your prompt: ${BLUE}$prompt${NC}"
    echo ""
    echo -e "${GREEN}Or use this command in Continue:${NC}"
    echo -e "${BLUE}@file $file_path $prompt${NC}"
}

# Function to send a folder
send_folder() {
    local folder_path="$1"
    local prompt="${2:-Analyze this folder}"
    
    if [ ! -d "$folder_path" ]; then
        echo -e "${YELLOW}⚠ Folder not found: $folder_path${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓${NC} Preparing to send folder: ${BLUE}$folder_path${NC}"
    echo -e "${GREEN}✓${NC} Prompt: ${BLUE}$prompt${NC}"
    echo ""
    echo -e "${YELLOW}📋 Instructions for Continue.dev:${NC}"
    echo "1. Press ${BLUE}Ctrl+Shift+L${NC} to open Continue chat"
    echo "2. Type: ${BLUE}@folder $folder_path${NC}"
    echo "3. Then type your prompt: ${BLUE}$prompt${NC}"
    echo ""
    echo -e "${GREEN}Or use this command in Continue:${NC}"
    echo -e "${BLUE}@folder $folder_path $prompt${NC}"
}

# Function to reference codebase
send_codebase() {
    local prompt="${1:-Analyze the codebase}"
    
    echo -e "${GREEN}✓${NC} Preparing to reference entire codebase"
    echo -e "${GREEN}✓${NC} Prompt: ${BLUE}$prompt${NC}"
    echo ""
    echo -e "${YELLOW}📋 Instructions for Continue.dev:${NC}"
    echo "1. Press ${BLUE}Ctrl+Shift+L${NC} to open Continue chat"
    echo "2. Type: ${BLUE}@codebase${NC}"
    echo "3. Then type your prompt: ${BLUE}$prompt${NC}"
    echo ""
    echo -e "${GREEN}Or use this command in Continue:${NC}"
    echo -e "${BLUE}@codebase $prompt${NC}"
}

# Main logic
case "$1" in
    --folder)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Usage: $0 --folder <folder_path> [prompt]${NC}"
            exit 1
        fi
        send_folder "$2" "$3"
        ;;
    --codebase)
        send_codebase "$2"
        ;;
    --help|-h)
        echo "Usage:"
        echo "  $0 <file_path> [prompt]     Send a file to Codex Max 5"
        echo "  $0 --folder <path> [prompt] Send a folder to Codex Max 5"
        echo "  $0 --codebase [prompt]      Reference entire codebase"
        echo ""
        echo "Examples:"
        echo "  $0 script.py 'Review this code for bugs'"
        echo "  $0 --folder src/ 'Analyze this directory'"
        echo "  $0 --codebase 'Find all API endpoints'"
        ;;
    "")
        echo -e "${YELLOW}Usage: $0 <file_path> [prompt]${NC}"
        echo "Use --help for more options"
        exit 1
        ;;
    *)
        send_file "$1" "$2"
        ;;
esac

echo ""
echo -e "${GREEN}✓${NC} Codex Max 5 is configured as default in Continue.dev"
echo -e "${BLUE}💡 Tip:${NC} You can also use @code, @docs, @diff, @terminal in Continue"
