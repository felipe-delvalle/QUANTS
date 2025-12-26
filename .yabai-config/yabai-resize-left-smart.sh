#!/bin/bash
# Alt+Ctrl+K: Expand window to the LEFT
# Works for any app based on window position, not app name
# When primary resize fails, expands opposing window to achieve same effect

# Get current window info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')
CURRENT_DISPLAY=$(echo "$WINDOW_INFO" | jq -r '.display')

# Alt+K should expand window to the LEFT
# Try to expand left edge left first
if ! yabai -m window --resize left:-50:0 2>/dev/null; then
    # Can't expand left (at edge), expand the right window to the left instead
    # This shrinks the right window, making the left window wider
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r ".[] | select(.display == $CURRENT_DISPLAY and .\"split-type\" == \"vertical\" and .\"split-child\" == \"second_child\" and .id != $CURRENT_ID) | .id" | head -1)
    if [ -n "$OPPOSING_WINDOW" ]; then
        # Expand right window to the left (shrink it from left)
        yabai -m window "$OPPOSING_WINDOW" --resize left:50:0 2>/dev/null || true
    fi
fi
