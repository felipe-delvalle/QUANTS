# Logitech G Hub - Alt + Right Click for yabai Resize

## Problem
The macro is only sending a right-click, not Alt + Right Click together.

## Solution
Configure the macro to **hold Alt while right-clicking**, not press Alt then right-click separately.

## Step-by-Step Configuration

### In Logitech G Hub Macro Editor:

1. **ON PRESS Section:**
   - Add: **Hold ALT** (not just press ALT)
   - Add: **Right Click** (while ALT is held)
   - Make sure both happen **simultaneously**, not sequentially

2. **ON RELEASE Section:**
   - Add: **Release Right Click**
   - Add: **Release ALT**

### Key Points:
- ✅ **Hold ALT** + **Right Click** together (simultaneous)
- ❌ NOT: Press ALT → wait → Right Click (sequential)
- The delay between ALT and Right Click should be **0ms** or minimal

### Alternative Configuration:

If the macro editor doesn't support "hold", try:
- **ON PRESS:** ALT (press) + Right Click (press) - both at the same time
- **ON RELEASE:** Right Click (release) + ALT (release) - both at the same time

## Testing

After configuring:
1. Hold the macro button
2. Drag your mouse
3. Window should resize (yabai will detect Alt + Right Click + Drag)

## Current yabai Config
- `mouse_modifier alt` - expects Alt key
- `mouse_action2 resize` - right-click performs resize
- Location: `~/.config/yabai/yabairc`

