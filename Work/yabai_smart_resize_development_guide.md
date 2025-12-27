# Yabai Smart Resize Development Guide

## Problem-Solving Methodology

This guide documents the successful approach to developing and debugging yabai resize scripts with intelligent detection and fallback logic.

## Key Principles

### 1. Test First, Then Fix
- Always test detection logic before implementing resize commands
- Verify window state queries work correctly
- Test edge cases (single window, windows at edges, etc.)

### 2. Iterative Development
- Start with basic detection
- Add error handling
- Implement fallback logic
- Test each iteration

### 3. Verify Before Reporting
- Test syntax validation: `bash -n script.sh`
- Test detection logic with current window state
- Test script execution (even if resize fails, script should not error)
- Report test results before claiming success

## Development Workflow

### Step 1: Understand the Current State
```bash
# Get current window info
yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)'

# Check window properties
yabai -m query --windows | jq -r '.[] | select(."has-focus" == true) | {
  app, 
  "is-floating": ."is-floating",
  "split-type": ."split-type",
  "split-child": ."split-child",
  frame
}'

# Check display dimensions
yabai -m query --displays | jq -r '.[0] | .frame'
```

### Step 2: Test Detection Logic
```bash
# Test frame-based detection
WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
DISPLAY_WIDTH=$(yabai -m query --displays | jq -r '.[0].frame.w')
WINDOW_X=$(echo "$WINDOW_INFO" | jq -r '.frame.x')

# Test left edge detection (< 30%)
IS_LEFT=$(echo "$WINDOW_X $DISPLAY_WIDTH" | awk '{if (($1 / $2) * 100 < 30) print "LEFT"; else print "RIGHT"}')
echo "Detection: $IS_LEFT"

# Test right edge detection (> 70%)
WINDOW_W=$(echo "$WINDOW_INFO" | jq -r '.frame.w')
IS_RIGHT=$(echo "$WINDOW_X $WINDOW_W $DISPLAY_WIDTH" | awk '{right_edge = $1 + $2; if ((right_edge / $3) * 100 > 70) print "RIGHT"; else print "LEFT"}')
echo "Detection: $IS_RIGHT"
```

### Step 3: Test Opposing Window Detection
```bash
# Find opposing window in vertical split
CURRENT_ID=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true) | .id')

# For left window, find right window
OPPOSING=$(yabai -m query --windows | jq -r ".[] | select(.\"split-type\" == \"vertical\" and .\"split-child\" == \"second_child\" and .id != $CURRENT_ID) | .id" | head -1)

# For right window, find left window
OPPOSING=$(yabai -m query --windows | jq -r ".[] | select(.\"split-type\" == \"vertical\" and .\"split-child\" == \"first_child\" and .id != $CURRENT_ID) | .id" | head -1)

echo "Opposing window ID: $OPPOSING"
```

### Step 4: Test Script Execution
```bash
# Syntax validation
bash -n script.sh && echo "✓ Syntax OK"

# Test execution (even if resize fails, script should not error)
./script.sh && echo "✓ Executed without errors"
```

### Step 5: Implement Error Handling
```bash
# Try primary action, fallback to opposing window if it fails
if ! yabai -m window --resize left:50:0 2>/dev/null; then
    # Find and resize opposing window
    OPPOSING_WINDOW=$(yabai -m query --windows | jq -r "...")
    if [ -n "$OPPOSING_WINDOW" ]; then
        yabai -m window "$OPPOSING_WINDOW" --resize right:50:0 2>/dev/null || true
    fi
fi
```

## Detection Logic Patterns

### Frame-Based Detection (Recommended)
Use window frame position relative to display instead of relying solely on `split-child`:

```bash
# Left window detection: left edge < 30% of display
IS_LEFT_WINDOW=$(echo "$WINDOW_X $DISPLAY_WIDTH" | awk '{if (($1 / $2) * 100 < 30) print "1"; else print "0"}')

# Right window detection: right edge > 70% of display  
IS_RIGHT_WINDOW=$(echo "$WINDOW_X $WINDOW_WIDTH $DISPLAY_WIDTH" | awk '{right_edge = $1 + $2; if ((right_edge / $3) * 100 > 70) print "1"; else print "0"}')
```

### Fallback Chain
1. Try frame-based detection
2. Fallback to `split-child` if frame calculation fails
3. Fallback to default action if both fail

## Resize Logic Patterns

### Primary Action with Opposing Window Fallback
When a resize fails (window at edge), expand the opposing window instead:

**Left Resize (K key):**
- Left window expand left fails → Expand right window to left (pushes left window left)
- Right window shrink from left fails → Expand left window to right (pushes right window left)

**Right Resize (L key):**
- Right window shrink from right fails → Expand left window to right (pushes right window right)
- Left window expand right fails → Expand right window to left (pushes left window right)

### Implementation Pattern
```bash
if [ "$IS_LEFT_WINDOW" = "1" ]; then
    # Primary action
    if ! yabai -m window --resize left:50:0 2>/dev/null; then
        # Fallback: expand opposing window
        OPPOSING_WINDOW=$(find_opposing_window)
        if [ -n "$OPPOSING_WINDOW" ]; then
            yabai -m window "$OPPOSING_WINDOW" --resize opposite_direction 2>/dev/null || true
        fi
    fi
fi
```

## Testing Checklist

Before reporting success, verify:

- [ ] Syntax validation passes: `bash -n script.sh`
- [ ] Detection logic tested with current window state
- [ ] Opposing window detection works
- [ ] Script executes without errors (even if resize fails)
- [ ] Error handling suppresses yabai errors (`2>/dev/null`)
- [ ] Fallback logic executes when primary action fails
- [ ] Script always exits successfully (`|| true`)

## Common Issues and Solutions

### Issue: "cannot locate a bsp node fence"
**Cause:** Window is at edge or no adjacent window to resize against  
**Solution:** Implement opposing window fallback logic

### Issue: Detection always returns same value
**Cause:** Using only `split-child` which doesn't update when window moves  
**Solution:** Use frame-based detection (< 30% or > 70% of display)

### Issue: Opposing window not found
**Cause:** Query filtering too strict or window not in vertical split  
**Solution:** Use `id != CURRENT_ID` instead of `has-focus == false`, check `split-type == "vertical"`

## Best Practices

1. **Always suppress errors**: Use `2>/dev/null` to hide yabai error messages
2. **Always exit successfully**: Use `|| true` to ensure script doesn't fail
3. **Test detection first**: Verify logic before implementing resize commands
4. **Use frame-based detection**: More reliable than `split-child` alone
5. **Implement fallbacks**: Always have a backup plan when primary action fails
6. **Test iteratively**: Test each change before moving to next

## Example: Complete Resize Script Pattern

```bash
#!/bin/bash
# Get window and display info
WINDOW_INFO=$(yabai -m query --windows --window 2>/dev/null)
if [ -z "$WINDOW_INFO" ]; then
    WINDOW_INFO=$(yabai -m query --windows | jq -r '.[] | select(."has-focus" == true)')
fi

DISPLAY_WIDTH=$(yabai -m query --displays | jq -r '.[0].frame.w')
WINDOW_X=$(echo "$WINDOW_INFO" | jq -r '.frame.x')
CURRENT_ID=$(echo "$WINDOW_INFO" | jq -r '.id')

# Frame-based detection
if [ -n "$DISPLAY_WIDTH" ] && [ "$DISPLAY_WIDTH" != "0" ] && [ "$DISPLAY_WIDTH" != "null" ]; then
    IS_LEFT=$(echo "$WINDOW_X $DISPLAY_WIDTH" | awk '{if (($1 / $2) * 100 < 30) print "1"; else print "0"}')
    
    if [ "$IS_LEFT" = "1" ]; then
        # Primary action
        if ! yabai -m window --resize left:50:0 2>/dev/null; then
            # Fallback: expand opposing window
            OPPOSING=$(yabai -m query --windows | jq -r ".[] | select(.\"split-type\" == \"vertical\" and .\"split-child\" == \"second_child\" and .id != $CURRENT_ID) | .id" | head -1)
            if [ -n "$OPPOSING" ]; then
                yabai -m window "$OPPOSING" --resize left:-50:0 2>/dev/null || true
            fi
        fi
    else
        # Right window logic...
    fi
fi
```

## Success Criteria

A resize script is successful when:
1. ✅ Executes without errors (even if resize fails)
2. ✅ Detects window position correctly
3. ✅ Handles edge cases (windows at edges)
4. ✅ Falls back to opposing window when needed
5. ✅ Works for both left and right windows
6. ✅ Works when window crosses 70% threshold

## Reporting Results

When testing, always report:
- Detection results (what was detected)
- Script execution status (errors or success)
- Opposing window detection (found or not found)
- Any errors encountered and how they were handled

Example report:
```
✓ Syntax validation passed
✓ Detection: LEFT window (< 30%)
✓ Opposing window found: ID 9402
✓ Script executed without errors
```

