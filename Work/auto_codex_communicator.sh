#!/bin/bash

# ============================================================
# Automated Codex Communicator
# ============================================================
# Monitors goal files and automatically prepares commands for Codex
# Since Continue.dev doesn't have a public API, this prepares commands
# that can be sent via the Continue extension interface
#
# Usage:
#   ./auto_codex_communicator.sh          # Check for new tasks
#   ./auto_codex_communicator.sh watch   # Watch mode (monitors files)
# ============================================================

WORKSPACE_ROOT="/Users/freedom/QUANTS"
GOALS_FILE="$WORKSPACE_ROOT/Work/ai_goals.md"
CHANNEL_FILE="$WORKSPACE_ROOT/Work/codex_cursor_channel.md"
COMMAND_FILE="$WORKSPACE_ROOT/.codex_command.txt"
LAST_CHECK_FILE="$WORKSPACE_ROOT/.last_codex_check.txt"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

check_for_codex_tasks() {
    local current_hash=$(md5 -q "$GOALS_FILE" 2>/dev/null || echo "0")
    local last_hash=$(cat "$LAST_CHECK_FILE" 2>/dev/null || echo "")
    
    if [ "$current_hash" != "$last_hash" ]; then
        echo "$current_hash" > "$LAST_CHECK_FILE"
        
        # Check for [CODEX_TURN] status
        if grep -q "\[CODEX_TURN\]" "$GOALS_FILE"; then
            # Find the goal with CODEX_TURN
            local goal_section=$(awk '/## Goal:/{p=1} p{print} /^---$/{if(p) exit}' "$GOALS_FILE" | grep -A 50 "\[CODEX_TURN\]" | head -30)
            
            if [ -n "$goal_section" ]; then
                local goal_title=$(echo "$goal_section" | grep "## Goal:" | sed 's/## Goal: //')
                
                echo -e "${GREEN}✓${NC} Found task for Codex: ${BLUE}$goal_title${NC}"
                echo ""
                
                # Prepare command
                local command="@file Work/ai_goals.md Review the goal with status [CODEX_TURN]. Complete your assigned tasks and update the progress log. After completion, update status to [CURSOR_TURN] if tasks are assigned to Cursor, or [COMPLETE] if done, and reply in codex_cursor_channel.md"
                
                echo "$command" > "$COMMAND_FILE"
                
                # Copy to clipboard
                if command -v pbcopy &> /dev/null; then
                    echo "$command" | pbcopy
                    echo -e "${GREEN}✓${NC} Command prepared and copied to clipboard!"
                else
                    echo -e "${GREEN}✓${NC} Command prepared in: ${CYAN}$COMMAND_FILE${NC}"
                fi
                
                echo ""
                echo -e "${YELLOW}📋 Command:${NC}"
                echo -e "${BLUE}$command${NC}"
                echo ""
                echo -e "${CYAN}💡 Note:${NC} Continue.dev doesn't have a public API, so you'll need to:"
                echo "   1. Open Continue (Cmd+Shift+L)"
                echo "   2. Paste the command (already in clipboard)"
                echo "   3. Or use the Continue extension's API if available"
                
                return 0
            fi
        fi
        
        # Check for new messages from Codex in channel
        local last_codex_msg=$(grep "From: Codex" "$CHANNEL_FILE" | tail -1)
        if [ -n "$last_codex_msg" ]; then
            echo -e "${GREEN}✓${NC} New message from Codex detected"
            echo -e "${BLUE}$last_codex_msg${NC}"
        fi
    fi
    
    return 1
}

case "$1" in
    watch)
        echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
        echo -e "${BLUE}║  Watching for Codex Tasks (Ctrl+C to stop)    ║${NC}"
        echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
        echo ""
        
        while true; do
            if check_for_codex_tasks; then
                echo ""
                echo -e "${YELLOW}⏳ Waiting for next update...${NC}"
            fi
            sleep 5
        done
        ;;
    *)
        check_for_codex_tasks
        if [ $? -eq 1 ]; then
            echo -e "${CYAN}ℹ${NC} No new tasks for Codex found"
        fi
        ;;
esac

