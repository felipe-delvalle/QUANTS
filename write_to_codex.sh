#!/bin/bash

# ============================================================
# Write Command for Codex Max 5 (Continue.dev)
# ============================================================
# This script writes the exact command to send context to
# GPT-5.1-Codex-Max in Continue.dev to a file you can copy
#
# Usage:
#   ./write_to_codex.sh <file_path> [prompt]
#   ./write_to_codex.sh --folder <path> [prompt]
#   ./write_to_codex.sh --codebase [prompt]
# ============================================================

WORKSPACE_ROOT="/Users/freedom/QUANTS"
OUTPUT_FILE="$WORKSPACE_ROOT/.codex_command.txt"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Write Command for Codex Max 5               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Function to write file command
write_file_command() {
    local file_path="$1"
    local prompt="${2:-Analyze this code}"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${YELLOW}⚠ File not found: $file_path${NC}"
        exit 1
    fi
    
    # Convert to absolute path if relative
    if [[ ! "$file_path" = /* ]]; then
        file_path="$WORKSPACE_ROOT/$file_path"
    fi
    
    # Convert to relative path from workspace root for Continue
    local rel_path="${file_path#$WORKSPACE_ROOT/}"
    
    local command="@file $rel_path $prompt"
    
    echo "$command" > "$OUTPUT_FILE"
    
    # Try to copy to clipboard on macOS
    if command -v pbcopy &> /dev/null; then
        echo "$command" | pbcopy
        echo -e "${GREEN}✓${NC} Command written to: ${CYAN}$OUTPUT_FILE${NC}"
        echo -e "${GREEN}✓${NC} Command copied to clipboard!"
    else
        echo -e "${GREEN}✓${NC} Command written to: ${CYAN}$OUTPUT_FILE${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📋 Command ready to use:${NC}"
    echo -e "${BLUE}$command${NC}"
    echo ""
    echo -e "${GREEN}📝 Next steps:${NC}"
    echo "1. Open Continue: ${BLUE}Ctrl+Shift+L${NC} (or ${BLUE}Cmd+Shift+L${NC} on Mac)"
    if command -v pbcopy &> /dev/null; then
        echo "2. Paste the command (already in clipboard!)"
    else
        echo "2. Copy the command from ${CYAN}$OUTPUT_FILE${NC} or above"
    fi
    echo "3. Press Enter in Continue chat"
    echo ""
    echo -e "${CYAN}💡 Tip:${NC} The command is ready to paste!"
}

# Function to write folder command
write_folder_command() {
    local folder_path="$1"
    local prompt="${2:-Analyze this folder}"
    
    if [ ! -d "$folder_path" ]; then
        echo -e "${YELLOW}⚠ Folder not found: $folder_path${NC}"
        exit 1
    fi
    
    # Convert to absolute path if relative
    if [[ ! "$folder_path" = /* ]]; then
        folder_path="$WORKSPACE_ROOT/$folder_path"
    fi
    
    # Convert to relative path from workspace root for Continue
    local rel_path="${folder_path#$WORKSPACE_ROOT/}"
    
    local command="@folder $rel_path $prompt"
    
    echo "$command" > "$OUTPUT_FILE"
    
    # Try to copy to clipboard on macOS
    if command -v pbcopy &> /dev/null; then
        echo "$command" | pbcopy
        echo -e "${GREEN}✓${NC} Command written to: ${CYAN}$OUTPUT_FILE${NC}"
        echo -e "${GREEN}✓${NC} Command copied to clipboard!"
    else
        echo -e "${GREEN}✓${NC} Command written to: ${CYAN}$OUTPUT_FILE${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📋 Command ready to use:${NC}"
    echo -e "${BLUE}$command${NC}"
    echo ""
    echo -e "${GREEN}📝 Next steps:${NC}"
    echo "1. Open Continue: ${BLUE}Ctrl+Shift+L${NC} (or ${BLUE}Cmd+Shift+L${NC} on Mac)"
    if command -v pbcopy &> /dev/null; then
        echo "2. Paste the command (already in clipboard!)"
    else
        echo "2. Copy the command from ${CYAN}$OUTPUT_FILE${NC} or above"
    fi
    echo "3. Press Enter in Continue chat"
}

# Function to write codebase command
write_codebase_command() {
    local prompt="${1:-Analyze the codebase}"
    
    local command="@codebase $prompt"
    
    echo "$command" > "$OUTPUT_FILE"
    
    # Try to copy to clipboard on macOS
    if command -v pbcopy &> /dev/null; then
        echo "$command" | pbcopy
        echo -e "${GREEN}✓${NC} Command written to: ${CYAN}$OUTPUT_FILE${NC}"
        echo -e "${GREEN}✓${NC} Command copied to clipboard!"
    else
        echo -e "${GREEN}✓${NC} Command written to: ${CYAN}$OUTPUT_FILE${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📋 Command ready to use:${NC}"
    echo -e "${BLUE}$command${NC}"
    echo ""
    echo -e "${GREEN}📝 Next steps:${NC}"
    echo "1. Open Continue: ${BLUE}Ctrl+Shift+L${NC} (or ${BLUE}Cmd+Shift+L${NC} on Mac)"
    if command -v pbcopy &> /dev/null; then
        echo "2. Paste the command (already in clipboard!)"
    else
        echo "2. Copy the command from ${CYAN}$OUTPUT_FILE${NC} or above"
    fi
    echo "3. Press Enter in Continue chat"
}

# Main logic
case "$1" in
    --folder)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Usage: $0 --folder <folder_path> [prompt]${NC}"
            exit 1
        fi
        write_folder_command "$2" "$3"
        ;;
    --codebase)
        write_codebase_command "$2"
        ;;
    --help|-h)
        echo "Usage:"
        echo "  $0 <file_path> [prompt]     Write command for a file"
        echo "  $0 --folder <path> [prompt] Write command for a folder"
        echo "  $0 --codebase [prompt]      Write command for codebase"
        echo ""
        echo "The command will be written to: .codex_command.txt"
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
        write_file_command "$1" "$2"
        ;;
esac

echo ""
echo -e "${GREEN}✓${NC} Codex Max 5 is configured as default in Continue.dev"
