#!/bin/bash
# Alt+Ctrl+K: Expand window to the LEFT
# Works for any app based on window position, not app name
# Note: In BSP, expanding one window means shrinking the opposing window

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')
SPLIT_CHILD=$(echo "$WINDOW_INFO" | jq -r '.["split-child"]')

# Strategy: To expand to the LEFT, we need the DIVIDER to move LEFT
# In vertical split:
#   - first_child (left): resize left:-X moves divider left ✓
#   - second_child (right): resize right:+X moves divider left ✓  BUT this also moves window right
# Better approach: Always use the right window to do the resize when possible

if [ "$SPLIT_CHILD" = "first_child" ]; then
    # LEFT window - use opposing window (right) to resize
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"second_child\" and .id != $CURRENT_ID) | .id" | head -1)
    if [ -n "$OPPOSING_WINDOW" ]; then
        # Resize the right window to push divider left (expands left window)
        yabai -m window "$OPPOSING_WINDOW" --resize left:50:0 2>/dev/null || true
    fi
else
    # RIGHT window - expand left by having left window shrink from right
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"first_child\" and .id != $CURRENT_ID) | .id" | head -1)
    if [ -n "$OPPOSING_WINDOW" ]; then
        # Shrink left window from its right edge (pushes divider left)
        yabai -m window "$OPPOSING_WINDOW" --resize right:-50:0 2>/dev/null || true
    fi
fi
