# How to Save Spaces in yabai

## Understanding Spaces

yabai doesn't have built-in "save/restore" functionality, but you can:

1. **Label spaces** for easy reference
2. **Use scripts** to save and restore window layouts
3. **Create persistent space configurations**

## Method 1: Label Spaces

Label a space so you can reference it later:

```bash
# Label current space
yabai -m space --label work
yabai -m space --label personal
yabai -m space --label coding

# Reference by label
yabai -m window --space work
```

## Method 2: Save Window Layout Script

Create a script to save current window positions:

```bash
#!/bin/bash
# Save current space layout
yabai -m query --windows --space | jq '.[] | {app: .app, frame: .frame}' > ~/.yabai_layout_$(yabai -m query --spaces --space | jq '.index').json
```

## Method 3: Space Rules (Persistent)

Set rules so apps always go to specific spaces:

```bash
# In ~/.config/yabai/yabairc
yabai -m rule --add app="^Code$" space=1
yabai -m rule --add app="^Terminal$" space=2
yabai -m rule --add app="^Browser$" space=3
```

## Method 4: Manual Space Management

```bash
# Create new space
yabai -m space --create

# Destroy space
yabai -m space --destroy

# Focus space by number
yabai -m space --focus 1

# Focus space by label
yabai -m space --focus work
```

## Quick Reference

- **List all spaces:** `yabai -m query --spaces`
- **List windows in space:** `yabai -m query --windows --space`
- **Move window to space:** `yabai -m window --space 2`
- **Label space:** `yabai -m space --label mylabel`

