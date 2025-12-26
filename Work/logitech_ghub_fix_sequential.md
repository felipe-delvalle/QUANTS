# Fix Logitech G Hub Sequential Alt + Right Click

## Problem
Even with 0ms delay, Alt and Right Click are happening sequentially (very fast but still sequential).

## Solution Options

### Option 1: Small Delay (Recommended)
Instead of 0ms, try a **10-20ms delay** so Alt is definitely held BEFORE Right Click:

**WHILE HOLDING:**
1. ALT (press) - delay: 0ms
2. Right Click (press) - delay: **10-20ms** after ALT

This ensures Alt is held when Right Click happens, which yabai needs.

### Option 2: Change yabai Modifier
If the macro still doesn't work, we can change yabai to use a different modifier that works better with your macro setup.

### Option 3: Use Different Mouse Button
Configure the macro on a different mouse button that might work better.

## Test Configuration

Try this in Logitech G Hub:

**WHILE HOLDING:**
- ALT (press) - 0ms
- Right Click (press) - **15ms delay** (after ALT)

**ON RELEASE:**
- Right Click (release) - 0ms  
- ALT (release) - 0ms

The key is: Alt must be **held down** when Right Click happens, not just pressed at the same time.

