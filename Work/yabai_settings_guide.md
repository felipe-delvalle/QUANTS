# yabai Settings & Configuration Guide

## Your Current Configuration

Location: `~/.config/yabai/yabairc`

### Current Settings:

- **Layout**: `bsp` (Binary Space Partitioning)
- **Window Gap**: `6` pixels
- **Padding**: `10` pixels (all sides)
- **Window Shadow**: `on`
- **Floating Apps**: System Settings, Calculator, Dictionary

---

## All Available yabai Settings

### Layout Settings

```bash
# Layout modes
yabai -m config layout bsp          # Binary Space Partitioning (default)
yabai -m config layout stack         # Stack layout
yabai -m config layout float         # All windows float

# Window placement
yabai -m config window_placement first_child    # New windows go to first position
yabai -m config window_placement second_child   # New windows go to second position (default)
```

### Spacing & Padding

```bash
# Padding (space around screen edges)
yabai -m config top_padding 10
yabai -m config bottom_padding 10
yabai -m config left_padding 10
yabai -m config right_padding 10

# Window gap (space between windows)
yabai -m config window_gap 6
```

### Window Appearance

```bash
# Window shadows
yabai -m config window_shadow on
yabai -m config window_shadow off

# Window opacity (requires SIP disabled)
yabai -m config window_opacity on
yabai -m config active_window_opacity 1.0      # Fully opaque
yabai -m config normal_window_opacity 0.9      # 90% opacity
```

### Focus & Mouse Behavior

```bash
# Mouse follows focus
yabai -m config mouse_follows_focus on
yabai -m config mouse_follows_focus off

# Focus follows mouse
yabai -m config focus_follows_mouse off         # No auto-focus
yabai -m config focus_follows_mouse autoraise   # Focus and raise on hover
yabai -m config focus_follows_mouse autofocus   # Focus on hover (no raise)

# Mouse modifier key
yabai -m config mouse_modifier fn              # Function key
yabai -m config mouse_modifier shift           # Shift key
yabai -m config mouse_modifier alt             # Option/Alt key
yabai -m config mouse_modifier cmd             # Command key

# Mouse actions (when modifier is held)
yabai -m config mouse_action1 move            # Left click + modifier = move
yabai -m config mouse_action2 resize           # Right click + modifier = resize
```

### External Bar (Status Bar Integration)

```bash
# External bar (for status bars like sketchybar)
yabai -m config external_bar all 0 0          # all displays, top, no offset
yabai -m config external_bar main 0 30        # main display, top, 30px offset
```

### Split Ratio

```bash
# Initial split ratio for new windows
yabai -m config split_ratio 0.50              # 50/50 split (default)
yabai -m config split_ratio 0.60              # 60/40 split
```

### Auto-Balance

```bash
# Automatically balance window sizes
yabai -m config auto_balance on
yabai -m config auto_balance off
```

### Topmost (Floating Windows)

```bash
# Keep floating windows on top
yabai -m config topmost on
yabai -m config topmost off
```

---

## Window Rules

### Floating Specific Apps	

```
# Make an app always float
yabai -m rule --add app="^AppName$" manage=off

# Examples:
yabai -m rule --add app="^Calculator$" manage=off
yabai -m rule --add app="^System Settings$" manage=off
yabai -m rule --add app="^Spotify$" manage=off
```

### Window Size Rules

```bash
# Set specific size for app
yabai -m rule --add app="^AppName$" grid=4:4:1:1:2:2

# Grid format: grid=cols:rows:x:y:width:height
# Example: 4x4 grid, position 1,1, size 2x2
```

### Space Rules

```bash
# Send app to specific space
yabai -m rule --add app="^AppName$" space=2

# Send app to current space
yabai -m rule --add app="^AppName$" space=^
```

### Label Rules

```bash
# Apply rules based on window title
yabai -m rule --add title="^.*YouTube.*$" manage=off
```

---

## Viewing Current Settings

```bash
# View all current config
yabai -m config

# View specific setting
yabai -m config layout
yabai -m config window_gap
```

---

## Applying Settings

### Method 1: Edit Config File

1. Edit `~/.config/yabai/yabairc`
2. Add or modify settings
3. Restart: `yabai --restart-service`

### Method 2: Command Line (Temporary)

```bash
# Change setting temporarily (until restart)
yabai -m config layout stack

# To make permanent, add to yabairc file
```

---

## Example Enhanced Configuration

```bash
#!/usr/bin/env sh

# Layout
yabai -m config layout bsp
yabai -m config window_placement second_child
yabai -m config split_ratio 0.50
yabai -m config auto_balance on

# Spacing
yabai -m config window_gap 8
yabai -m config top_padding 15
yabai -m config bottom_padding 15
yabai -m config left_padding 15
yabai -m config right_padding 15

# Appearance
yabai -m config window_shadow on
yabai -m config topmost on

# Mouse
yabai -m config mouse_follows_focus off
yabai -m config focus_follows_mouse autoraise
yabai -m config mouse_modifier fn
yabai -m config mouse_action1 move
yabai -m config mouse_action2 resize

# Floating apps
yabai -m rule --add app="^System Settings$" manage=off
yabai -m rule --add app="^Calculator$" manage=off
yabai -m rule --add app="^Dictionary$" manage=off
yabai -m rule --add app="^Spotify$" manage=off

# Start service
yabai --start-service
```

---

## Useful Commands

```bash
# Reload config
yabai --restart-service

# View all windows
yabai -m query --windows

# View all spaces
yabai -m query --spaces

# View all displays
yabai -m query --displays
```
