# Yabai Smart Resize Configuration

This directory contains the yabai smart resize scripts and skhd configuration that enable intelligent window resizing.

## Files

- `yabai-resize-left-smart.sh` - Script for Alt+Ctrl+K (expand window to the LEFT)
- `yabai-resize-right-smart.sh` - Script for Alt+Ctrl+L (expand window to the RIGHT)
- `skhdrc` - skhd keyboard shortcut configuration

## Installation

Copy the scripts to your local bin directory:
```bash
cp yabai-resize-left-smart.sh ~/.local/bin/
cp yabai-resize-right-smart.sh ~/.local/bin/
chmod +x ~/.local/bin/yabai-resize-*-smart.sh
```

Copy the skhd config:
```bash
cp skhdrc ~/.config/skhd/skhdrc
```

Then reload skhd:
```bash
skhd --reload
```

## Features

- **Display-aware**: Only affects windows on the same display
- **App-agnostic**: Works for any app based on window position, not app name
- **Opposing window fallback**: When primary resize fails (e.g., at screen edge), expands the opposing window to achieve the same visual effect
- **Frame-based detection**: Uses window position (< 30% = left, > 70% = right)

## Usage

- **Alt+Ctrl+K**: Expand current window to the LEFT
- **Alt+Ctrl+L**: Expand current window to the RIGHT

## How It Works

1. Tries to expand the window directly in the requested direction
2. If that fails (window at edge), finds the opposing window in the split
3. Shrinks the opposing window, which expands the current window

## Commit History

- **2025-12-26**: Initial commit with working smart resize implementation
  - Commit: `08b1a88`
  - Branch: `yabai-smart-resize-20251226`

