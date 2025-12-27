# yabai Complete Command Reference

## Official Documentation Sources

1. **GitHub Wiki**: https://github.com/koekeishiya/yabai/wiki
2. **Commands Wiki**: https://github.com/koekeishiya/yabai/wiki/Commands
3. **Configuration Wiki**: https://github.com/koekeishiya/yabai/wiki/Configuration

---

## Service Management

```bash
yabai --start-service      # Start yabai service
yabai --stop-service       # Stop yabai service
yabai --restart-service    # Restart yabai service
yabai --check-service      # Check if service is running
yabai --version            # Show version
```

---

## Window Commands (`yabai -m window`)

### Window Focus
```bash
yabai -m window --focus north      # Focus window above
yabai -m window --focus south      # Focus window below
yabai -m window --focus east       # Focus window to the right
yabai -m window --focus west       # Focus window to the left
yabai -m window --focus next       # Focus next window
yabai -m window --focus prev       # Focus previous window
yabai -m window --focus recent     # Focus most recently used window
yabai -m window --focus mouse      # Focus window under mouse cursor
yabai -m window --focus <window-id> # Focus specific window by ID
```

### Window Swap
```bash
yabai -m window --swap north       # Swap window with window above
yabai -m window --swap south       # Swap window with window below
yabai -m window --swap east        # Swap window with window to the right
yabai -m window --swap west        # Swap window with window to the left
yabai -m window --swap <window-id>  # Swap with specific window
```

### Window Resize
```bash
yabai -m window --resize left:<pixels>:0      # Resize left (negative to shrink)
yabai -m window --resize right:<pixels>:0     # Resize right (positive to grow)
yabai -m window --resize top:0:<pixels>      # Resize top (negative to shrink)
yabai -m window --resize bottom:0:<pixels>   # Resize bottom (positive to grow)
yabai -m window --resize absolute:<width>:<height>  # Set absolute size
```

### Window Movement
```bash
yabai -m window --move absolute:<x>:<y>       # Move to absolute position
yabai -m window --move relative:<x>:<y>      # Move relative to current position
```

### Window State
```bash
yabai -m window --toggle float               # Toggle floating state
yabai -m window --toggle sticky               # Toggle always on top (sticky)
yabai -m window --toggle zoom-fullscreen      # Toggle fullscreen
yabai -m window --toggle zoom-parent          # Toggle zoom parent
yabai -m window --toggle split               # Toggle split type (horizontal/vertical)
yabai -m window --toggle pip                 # Toggle picture-in-picture mode
```

### Window Space Management
```bash
yabai -m window --space next                 # Move window to next space
yabai -m window --space prev                 # Move window to previous space
yabai -m window --space <space-number>       # Move window to specific space
yabai -m window --space recent               # Move window to most recent space
```

### Window Display Management
```bash
yabai -m window --display next               # Move window to next display
yabai -m window --display prev               # Move window to previous display
yabai -m window --display <display-id>       # Move window to specific display
```

### Window Close/Minimize
```bash
yabai -m window --close                      # Close current window
yabai -m window --minimize                   # Minimize current window
```

### Window Grid (Positioning)
```bash
yabai -m window --grid <cols>:<rows>:<x>:<y>:<width>:<height>
# Example: yabai -m window --grid 4:4:1:1:2:2
# 4x4 grid, position at (1,1), size 2x2
```

---

## Space Commands (`yabai -m space`)

### Space Focus
```bash
yabai -m space --focus 1                    # Focus space 1
yabai -m space --focus 2                    # Focus space 2-9
yabai -m space --focus next                 # Focus next space
yabai -m space --focus prev                 # Focus previous space
yabai -m space --focus recent               # Focus most recent space
yabai -m space --focus <space-id>           # Focus by space ID
```

### Space Layout
```bash
yabai -m space --layout bsp                 # Set BSP (Binary Space Partitioning) layout
yabai -m space --layout stack              # Set Stack layout
yabai -m space --layout float              # Set Float layout
yabai -m space --layout tile               # Set Tile layout (if available)
```

### Space Rotation
```bash
yabai -m space --rotate 90                 # Rotate layout 90 degrees clockwise
yabai -m space --rotate 270                # Rotate layout 270 degrees (90 counter-clockwise)
```

### Space Balance
```bash
yabai -m space --balance                  # Balance all windows equally
```

### Space Padding
```bash
yabai -m space --padding abs:<top>:<right>:<bottom>:<left>
yabai -m space --padding abs:10:10:10:10   # Set padding for all sides
```

### Space Gap
```bash
yabai -m space --gap abs:<gap>            # Set window gap
yabai -m space --gap abs:6                # Set gap to 6 pixels
```

---

## Display Commands (`yabai -m display`)

### Display Focus
```bash
yabai -m display --focus next              # Focus next display
yabai -m display --focus prev              # Focus previous display
yabai -m display --focus <display-id>      # Focus specific display
```

### Display Space
```bash
yabai -m display --space next              # Move to next space on display
yabai -m display --space prev              # Move to previous space on display
yabai -m display --space <space-number>    # Move to specific space
```

---

## Query Commands (`yabai -m query`)

### Query Windows
```bash
yabai -m query --windows                   # List all windows (JSON)
yabai -m query --windows --space <space>   # Windows in specific space
yabai -m query --windows --display <display> # Windows on specific display
yabai -m query --windows --window <window-id> # Specific window info
```

### Query Spaces
```bash
yabai -m query --spaces                   # List all spaces (JSON)
yabai -m query --spaces --space <space-id> # Specific space info
yabai -m query --spaces --display <display-id> # Spaces on display
```

### Query Displays
```bash
yabai -m query --displays                 # List all displays (JSON)
yabai -m query --displays --display <display-id> # Specific display info
```

### Query Windows (Filtered)
```bash
yabai -m query --windows --window-focused    # Currently focused window
yabai -m query --windows --window-minimized  # Minimized windows
yabai -m query --windows --window-floating    # Floating windows
yabai -m query --windows --window-sticky      # Sticky windows
```

---

## Config Commands (`yabai -m config`)

### Layout Configuration
```bash
yabai -m config layout bsp                 # Set BSP layout
yabai -m config layout stack               # Set Stack layout
yabai -m config layout float              # Set Float layout
yabai -m config window_placement first_child   # New windows go first
yabai -m config window_placement second_child  # New windows go second (default)
yabai -m config split_ratio 0.50         # Set split ratio (50/50)
yabai -m config auto_balance on           # Auto-balance windows
yabai -m config auto_balance off         # Disable auto-balance
```

### Spacing Configuration
```bash
yabai -m config window_gap 6              # Set gap between windows
yabai -m config top_padding 10            # Top padding
yabai -m config bottom_padding 10         # Bottom padding
yabai -m config left_padding 10           # Left padding
yabai -m config right_padding 10          # Right padding
```

### Appearance Configuration
```bash
yabai -m config window_shadow on          # Enable window shadows
yabai -m config window_shadow off         # Disable window shadows
yabai -m config window_opacity on         # Enable opacity (requires SIP disabled)
yabai -m config active_window_opacity 1.0 # Active window opacity
yabai -m config normal_window_opacity 0.9 # Normal window opacity
yabai -m config topmost on                # Keep floating windows on top
yabai -m config topmost off               # Don't keep floating on top
```

### Focus Configuration
```bash
yabai -m config mouse_follows_focus on    # Mouse follows keyboard focus
yabai -m config mouse_follows_focus off   # Mouse doesn't follow focus
yabai -m config focus_follows_mouse off   # No auto-focus
yabai -m config focus_follows_mouse autoraise  # Focus and raise on hover
yabai -m config focus_follows_mouse autofocus  # Focus on hover (no raise)
```

### Mouse Configuration
```bash
yabai -m config mouse_modifier fn         # Function key modifier
yabai -m config mouse_modifier shift      # Shift key modifier
yabai -m config mouse_modifier alt        # Alt/Option key modifier
yabai -m config mouse_modifier cmd        # Command key modifier
yabai -m config mouse_action1 move        # Left click + modifier = move
yabai -m config mouse_action2 resize      # Right click + modifier = resize
```

### External Bar Configuration
```bash
yabai -m config external_bar all 0 0      # All displays, top, no offset
yabai -m config external_bar main 0 30    # Main display, top, 30px offset
yabai -m config external_bar off          # Disable external bar
```

### View/Set Configuration
```bash
yabai -m config                           # View all current config
yabai -m config <setting>                 # View specific setting value
```

---

## Rule Commands (`yabai -m rule`)

### Add Rules
```bash
# Floating rules
yabai -m rule --add app="^AppName$" manage=off          # Don't manage (float)
yabai -m rule --add app="^Calculator$" manage=off      # Example: Calculator

# Space rules
yabai -m rule --add app="^AppName$" space=2            # Send to space 2
yabai -m rule --add app="^AppName$" space=^            # Send to current space

# Display rules
yabai -m rule --add app="^AppName$" display=2          # Send to display 2

# Grid/Size rules
yabai -m rule --add app="^AppName$" grid=4:4:1:1:2:2    # Grid positioning
# Format: grid=cols:rows:x:y:width:height

# Title-based rules
yabai -m rule --add title="^.*YouTube.*$" manage=off    # Float YouTube windows

# Multiple conditions
yabai -m rule --add app="^AppName$" space=2 manage=off # Multiple properties
```

### List Rules
```bash
yabai -m rule --list                     # List all active rules
```

### Remove Rules
```bash
yabai -m rule --remove <rule-id>          # Remove specific rule
yabai -m rule --remove-all                # Remove all rules
```

---

## Signal Commands (`yabai -m signal`)

### Add Signals (Event Handlers)
```bash
yabai -m signal --add event=window_created action="command"
yabai -m signal --add event=window_destroyed action="command"
yabai -m signal --add event=window_focused action="command"
yabai -m signal --add event=window_moved action="command"
yabai -m signal --add event=window_resized action="command"
yabai -m signal --add event=space_changed action="command"
yabai -m signal --add event=display_changed action="command"
```

### List Signals
```bash
yabai -m signal --list                    # List all active signals
```

### Remove Signals
```bash
yabai -m signal --remove <signal-id>      # Remove specific signal
yabai -m signal --remove-all              # Remove all signals
```

---

## Message Commands (`yabai -m message`)

```bash
yabai -m message <message>                # Send custom message (for scripting)
```

---

## Common Usage Patterns

### Move Window to Next Space and Follow
```bash
yabai -m window --space next; yabai -m space --focus next
```

### Move Window to Previous Space and Follow
```bash
yabai -m window --space prev; yabai -m space --focus prev
```

### Move Window to Specific Space
```bash
yabai -m window --space 2; yabai -m space --focus 2
```

### Balance Windows in Current Space
```bash
yabai -m space --balance
```

### Toggle Window Float and Sticky
```bash
yabai -m window --toggle float; yabai -m window --toggle sticky
```

### Get Window ID for Scripting
```bash
yabai -m query --windows --window-focused | jq -r '.id'
```

### Get Current Space Number
```bash
yabai -m query --spaces --space | jq -r '.index'
```

---

## Configuration File

Location: `~/.config/yabai/yabairc`

This file is executed as a shell script on startup. Add all your configuration commands here.

Example:
```bash
#!/usr/bin/env sh

# Layout
yabai -m config layout bsp
yabai -m config window_placement second_child
yabai -m config split_ratio 0.50

# Spacing
yabai -m config window_gap 6
yabai -m config top_padding 10
yabai -m config bottom_padding 10
yabai -m config left_padding 10
yabai -m config right_padding 10

# Appearance
yabai -m config window_shadow on

# Rules
yabai -m rule --add app="^System Settings$" manage=off
yabai -m rule --add app="^Calculator$" manage=off
```

---

## Integration with skhd

skhd (Simple Hotkey Daemon) is used to create keyboard shortcuts for yabai commands.

Config file: `~/.config/skhd/skhdrc`

Example shortcuts:
```bash
# Window focus
alt - h : yabai -m window --focus west
alt - j : yabai -m window --focus south
alt - k : yabai -m window --focus north
alt - l : yabai -m window --focus east

# Window swap
alt + shift - h : yabai -m window --swap west
alt + shift - j : yabai -m window --swap south
alt + shift - k : yabai -m window --swap north
alt + shift - l : yabai -m window --swap east

# Space navigation
alt - 1 : yabai -m space --focus 1
alt - 2 : yabai -m space --focus 2

# Move window to space
alt + shift - n : yabai -m window --space next; yabai -m space --focus next
```

---

## Tips

1. **View Current State**: Use `yabai -m query` commands to see current windows, spaces, and displays in JSON format
2. **Scripting**: Combine commands with `;` or use in shell scripts
3. **JSON Parsing**: Use `jq` to parse query results: `yabai -m query --windows | jq`
4. **Restart After Config Changes**: Always run `yabai --restart-service` after modifying `yabairc`
5. **Permissions**: Ensure yabai has Accessibility permissions in System Settings

---

## Additional Resources

- **GitHub Repository**: https://github.com/koekeishiya/yabai
- **Wiki**: https://github.com/koekeishiya/yabai/wiki
- **Issues**: https://github.com/koekeishiya/yabai/issues
- **skhd**: https://github.com/koekeishiya/skhd

