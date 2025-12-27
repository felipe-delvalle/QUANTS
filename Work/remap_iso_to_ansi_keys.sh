#!/bin/bash

# ============================================================
# Remap ISO ±§ keys to ANSI `~ keys
# ============================================================
# This remaps the ±§ key (ISO keyboard) to produce ` and ~
# ============================================================

# Key codes:
# 0x64 = ± (ISO keyboard, non-shifted) → should become ` (0x35)
# 0x64 + shift = § (ISO keyboard, shifted) → should become ~ (0x35 + shift)

echo "Remapping ±§ keys to `~ keys..."

# Create the remapping JSON
REMAP_JSON='{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x700000064,"HIDKeyboardModifierMappingDst":0x700000035}]}'

# Apply the remapping
hidutil property --set "$REMAP_JSON"

if [ $? -eq 0 ]; then
    echo "✓ Key remapping applied successfully!"
    echo ""
    echo "The ±§ key should now produce ` (backtick) and ~ (tilde with shift)"
    echo ""
    echo "Note: This remapping will be lost after reboot."
    echo "To make it persistent, run: ./create_keyboard_launch_agent.sh"
else
    echo "✗ Failed to apply key remapping"
    exit 1
fi

