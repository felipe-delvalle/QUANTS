#!/bin/bash
# Alt+Ctrl+K: Expand window to the LEFT

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')
SPLIT_CHILD=$(echo "$WINDOW_INFO" | jq -r '.["split-child"]')

if [ "$SPLIT_CHILD" = "first_child" ]; then
    # LEFT window: shrink right window from left to expand this window
    OPPOSING=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"second_child\" and .id != $CURRENT_ID and .\"is-visible\" == true) | .id" | head -1)
    if [ -n "$OPPOSING" ]; then
        yabai -m window "$OPPOSING" --resize left:50:0 2>/dev/null
    fi
else
    # RIGHT window: shrink left window from right to expand this window left
    OPPOSING=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"first_child\" and .id != $CURRENT_ID and .\"is-visible\" == true) | .id" | head -1)
    if [ -n "$OPPOSING" ]; then
        yabai -m window "$OPPOSING" --resize right:-50:0 2>/dev/null
    fi
fi
