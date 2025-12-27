#!/bin/bash
# Install AlwaysOnTop (Open-Source) for macOS

set -e

echo "📦 Installing AlwaysOnTop (Open-Source)..."

# Get latest release URL
echo "🔍 Finding latest release..."
RELEASE_URL=$(curl -s https://api.github.com/repos/itsabhishekolkha/AlwaysOnTop/releases/latest | grep "browser_download_url.*\.dmg" | cut -d '"' -f 4)

if [ -z "$RELEASE_URL" ]; then
    echo "❌ Could not find download URL"
    echo "   Please download manually from: https://github.com/itsabhishekolkha/AlwaysOnTop/releases"
    exit 1
fi

echo "📥 Downloading from: $RELEASE_URL"
DMG_FILE="/tmp/AlwaysOnTop.dmg"

# Download DMG
curl -L -o "$DMG_FILE" "$RELEASE_URL"

# Mount DMG
echo "📂 Mounting DMG..."
MOUNT_POINT=$(hdiutil attach "$DMG_FILE" | grep -o '/Volumes/.*' | head -1)

if [ -z "$MOUNT_POINT" ]; then
    echo "❌ Failed to mount DMG"
    exit 1
fi

# Find app in mounted volume
APP_PATH=$(find "$MOUNT_POINT" -name "AlwaysOnTop.app" -type d | head -1)

if [ -z "$APP_PATH" ]; then
    echo "❌ Could not find AlwaysOnTop.app in DMG"
    hdiutil detach "$MOUNT_POINT" 2>/dev/null || true
    exit 1
fi

# Copy to Applications
echo "📋 Installing to Applications folder..."
cp -R "$APP_PATH" /Applications/

# Unmount DMG
echo "🗑️  Cleaning up..."
hdiutil detach "$MOUNT_POINT" 2>/dev/null || true
rm "$DMG_FILE"

echo ""
echo "✅ AlwaysOnTop installed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Open Applications folder and launch AlwaysOnTop"
echo "2. Grant Accessibility permissions:"
echo "   - System Settings > Privacy & Security > Accessibility"
echo "   - Click + and add AlwaysOnTop"
echo "3. If you see a security warning:"
echo "   - System Settings > Privacy & Security > General"
echo "   - Click 'Open Anyway' next to AlwaysOnTop"
echo ""
echo "💡 Default shortcut: Option + Command + P (to pin window on top)"
echo ""

