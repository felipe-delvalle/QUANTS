# yabai Keyboard Shortcuts

## Current Setup ✅

**skhd is installed and running**
- Config file: `~/.config/skhd/skhdrc`
- Service: Running

---

## Shortcuts Reference

### Window Focus (Alt + Arrow Keys)
- `Alt + H` - Focus window to the left
- `Alt + J` - Focus window below
- `Alt + K` - Focus window above
- `Alt + L` - Focus window to the right

### Window Swap (Alt + Shift + Arrow Keys)
- `Alt + Shift + H` - Swap window left
- `Alt + Shift + J` - Swap window down
- `Alt + Shift + K` - Swap window up
- `Alt + Shift + L` - Swap window right

### Window Resize (Alt + Ctrl + Arrow Keys)
- `Alt + Ctrl + H` - Resize left (shrink)
- `Alt + Ctrl + J` - Resize down (grow)
- `Alt + Ctrl + K` - Resize up (shrink)
- `Alt + Ctrl + L` - Resize right (grow)

### Window Management
- `Alt + F` - Toggle float (make window float)
- `Alt + T` - Toggle always on top (sticky)
- `Alt + M` - Toggle fullscreen
- `Alt + C` - Close window

### Layout Management
- `Alt + B` - Switch to BSP layout
- `Alt + S` - Switch to Stack layout
- `Alt + D` - Switch to Float layout
- `Alt + R` - Rotate layout 90 degrees

### Space Management (Alt + Number)
- `Alt + 1-9` - Switch to space 1-9

### Window Balance
- `Alt + E` - Balance all windows (equal sizes)

### Service Management
- `Alt + Shift + R` - Restart yabai service

---

## Customizing Shortcuts

Edit `~/.config/skhd/skhdrc` to change shortcuts.

**After editing:**
```bash
skhd --restart-service
```

**Format:**
```
modifier - key : command
```

**Modifiers:**
- `alt` - Option key
- `shift` - Shift key
- `ctrl` - Control key
- `cmd` - Command key
- `fn` - Function key

**Examples:**
```bash
# Change focus to use Cmd instead of Alt
cmd - h : yabai -m window --focus west

# Add a shortcut for specific app
alt - p : [app="Spotify"] yabai -m window --toggle float
```

---

## Troubleshooting

**If shortcuts don't work:**
1. Check skhd is running: `launchctl list | grep skhd`
2. Check logs: `tail -f /tmp/skhd_freedom.err.log`
3. Grant permissions: System Settings > Privacy & Security > Accessibility (add skhd)
4. Restart: `skhd --restart-service`

