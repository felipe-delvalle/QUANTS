# What is skhd?

**skhd** stands for **Simple Hotkey Daemon**. It's a lightweight keyboard shortcut manager for macOS that works perfectly with yabai.

## What it does:
- Listens for keyboard shortcuts you define
- Executes commands (like yabai window management) when you press those shortcuts
- Runs in the background as a service
- Very fast and efficient

## Why you need it:
yabai itself doesn't handle keyboard shortcuts - it only manages windows. skhd is the "bridge" that connects your keyboard presses to yabai commands.

**Example:**
- You press: `Alt + H`
- skhd detects it
- skhd runs: `yabai -m window --focus west`
- yabai moves focus to the left window

## Without skhd:
You'd have to type commands in Terminal every time you want to manage windows.

## With skhd:
You press keyboard shortcuts and windows move instantly!

