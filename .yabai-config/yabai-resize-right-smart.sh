#!/bin/bash
# Alt+Ctrl+L: Expand window to the RIGHT
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

# Strategy: To expand to the RIGHT, we need the DIVIDER to move RIGHT
# In vertical split:
#   - first_child (left): resize right:+X moves divider right ✓
#   - second_child (right): resize left:-X moves divider right ✓  BUT this also moves window right
# Better approach: Always use the left window to do the resize when possible

if [ "$SPLIT_CHILD" = "first_child" ]; then
    # LEFT window - directly resize right
    yabai -m window --resize right:50:0 2>/dev/null || true
else
    # RIGHT window - use opposing window strategy
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"first_child\" and .id != $CURRENT_ID) | .id" | head -1)
    if [ -n "$OPPOSING_WINDOW" ]; then
        # Try direct resize first: resize left:-50 pushes divider right
        if ! yabai -m window --resize left:-50:0 2>/dev/null; then
            # Fallback: shrink left window from right, moving divider left to expand right window
            yabai -m window "$OPPOSING_WINDOW" --resize right:-50:0 2>/dev/null || true
        fi
    fi
fi
