#!/bin/bash
# Alt+Ctrl+K: Expand window to the LEFT
# Works for any app based on window position

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')
SPLIT_CHILD=$(echo "$WINDOW_INFO" | jq -r '.["split-child"]')

# Find opposing window
OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .id != $CURRENT_ID) | .id" | head -1)

if [ "$SPLIT_CHILD" = "first_child" ]; then
    # LEFT window expanding left: shrink right window from left
    if [ -n "$OPPOSING_WINDOW" ]; then
        yabai -m window "$OPPOSING_WINDOW" --resize left:50:0 2>/dev/null
    fi
else
    # RIGHT window expanding left: shrink left window from right
    if [ -n "$OPPOSING_WINDOW" ]; then
        yabai -m window "$OPPOSING_WINDOW" --resize right:-50:0 2>/dev/null
    fi
fi
