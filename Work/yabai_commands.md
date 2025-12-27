# yabai Quick Reference

## Installation Complete! ✅

yabai is installed at: `/Users/freedom/.local/bin/yabai`

## Grant Permissions (Required!)

**Go to System Settings:**
1. Open **System Settings** > **Privacy & Security** > **Accessibility**
2. Click the **+** button
3. Navigate to and add: `/Users/freedom/.local/bin/yabai`
4. Make sure the checkbox is enabled

## Service Management

```bash
yabai --start-service      # Start yabai
yabai --stop-service       # Stop yabai
yabai --restart-service    # Restart yabai
```

## Floating Windows

```bash
# Toggle current window to float
yabai -m window --toggle float

# Pin window on top (sticky)
yabai -m window --toggle sticky

# Make specific window float
yabai -m window <window-id> --toggle float

# List all windows
yabai -m query --windows
```

## Window Management

```bash
# Focus windows
yabai -m window --focus north
yabai -m window --focus south
yabai -m window --focus east
yabai -m window --focus west

# Swap windows
yabai -m window --swap north
yabai -m window --swap south

# Resize windows
yabai -m window --resize left:-100:0
yabai -m window --resize right:100:0
```

## Configuration

Config file: `~/.config/yabai/yabairc`

After editing, restart: `yabai --restart-service`

## Keyboard Shortcuts (with skhd)

To set up keyboard shortcuts, install skhd:
```bash
brew install koekeishiya/formulae/skhd
```

Then configure `~/.config/skhd/skhdrc` with your preferred shortcuts.

