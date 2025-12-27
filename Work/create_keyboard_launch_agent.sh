#!/bin/bash

# ============================================================
# Create Launch Agent for Persistent Keyboard Remapping
# ============================================================
# Makes the ±§ to `~ remapping persist across reboots
# ============================================================

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.user.keyremap.plist"

echo "Creating persistent keyboard remapping..."

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Create the plist file
cat > "$PLIST_FILE" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.user.keyremap</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/hidutil</string>
      <string>property</string>
      <string>--set</string>
      <string>{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x700000064,"HIDKeyboardModifierMappingDst":0x700000035}]}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
PLIST

# Load the launch agent
launchctl load "$PLIST_FILE" 2>/dev/null || launchctl load -w "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Launch agent created and loaded successfully!"
    echo ""
    echo "The ±§ to `~ remapping will now persist across reboots."
    echo ""
    echo "File location: $PLIST_FILE"
    echo ""
    echo "To remove this remapping later, run:"
    echo "  launchctl unload $PLIST_FILE"
    echo "  rm $PLIST_FILE"
else
    echo "✗ Failed to create launch agent"
    exit 1
fi

