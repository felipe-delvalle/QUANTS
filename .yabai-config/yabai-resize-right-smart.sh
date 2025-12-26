#!/bin/bash
# Alt+Ctrl+L: Expand window to the RIGHT
# Works for any app based on window position, not app name
# When primary resize fails, expands opposing window to achieve same effect

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')

# Alt+L should expand window to the RIGHT
# Try to expand right edge right first
if ! yabai -m window --resize right:50:0 2>/dev/null; then
    # Can't expand right (at edge), expand the left window to the right instead
    # This shrinks the left window, making the right window wider
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"first_child\" and .id != $CURRENT_ID) | .id" | head -1)
    if [ -n "$OPPOSING_WINDOW" ]; then
        # Expand left window to the right (shrink it from right)
        yabai -m window "$OPPOSING_WINDOW" --resize right:-50:0 2>/dev/null || true
    fi
fi
