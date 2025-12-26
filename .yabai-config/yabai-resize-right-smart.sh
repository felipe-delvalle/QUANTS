#!/bin/bash
# Alt+Ctrl+L: Expand window to the RIGHT
# Works for any app based on window position

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')
SPLIT_CHILD=$(echo "$WINDOW_INFO" | jq -r '.["split-child"]')

if [ "$SPLIT_CHILD" = "first_child" ]; then
    # LEFT window expanding right: direct resize
    yabai -m window --resize right:50:0 2>/dev/null
else
    # RIGHT window expanding right: shrink left window from right
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .id != $CURRENT_ID) | .id" | head -1)
    if [ -n "$OPPOSING_WINDOW" ]; then
        yabai -m window "$OPPOSING_WINDOW" --resize right:-50:0 2>/dev/null
    fi
fi
