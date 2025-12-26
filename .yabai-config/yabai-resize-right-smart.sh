#!/bin/bash
# Alt+Ctrl+L: Expand window to the RIGHT

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')
SPLIT_CHILD=$(echo "$WINDOW_INFO" | jq -r '.["split-child"]')

if [ "$SPLIT_CHILD" = "first_child" ]; then
    # LEFT window: shrink it (make opposing window bigger)
    yabai -m window --resize right:-50:0 2>/dev/null
else
    # RIGHT window: shrink it (make opposing window bigger)
    yabai -m window --resize left:-50:0 2>/dev/null
fi
