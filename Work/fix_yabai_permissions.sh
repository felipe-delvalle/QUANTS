#!/bin/bash
# Script to help fix yabai permissions

echo "🔍 Checking yabai permissions..."
echo ""

YABAI_PATH="$HOME/.local/bin/yabai"

if [ ! -f "$YABAI_PATH" ]; then
    echo "❌ yabai not found at $YABAI_PATH"
    exit 1
fi

echo "✅ yabai found at: $YABAI_PATH"
echo ""

echo "📋 To fix permissions:"
echo ""
echo "1. Open System Settings"
echo "2. Go to: Privacy & Security > Accessibility"
echo "3. Look for 'yabai' in the list"
echo ""
echo "   If yabai is NOT in the list:"
echo "   - Click the + button"
echo "   - Press Cmd+Shift+G"
echo "   - Type: $HOME/.local/bin"
echo "   - Select 'yabai'"
echo ""
echo "   If yabai IS in the list but unchecked:"
echo "   - Check the box next to it"
echo ""
echo "4. After enabling, run:"
echo "   yabai --restart-service"
echo ""

# Try to open System Settings to the right page
echo "🔧 Opening System Settings..."
open -a "System Settings" "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || {
    echo "   (Could not auto-open, please open manually)"
}

echo ""
echo "⏳ After you enable the permission, press Enter to continue..."
read -r

echo ""
echo "🔄 Restarting yabai service..."
yabai --stop-service 2>/dev/null
sleep 1
yabai --start-service

echo ""
echo "✅ Checking if yabai started successfully..."
sleep 2

if ps aux | grep -v grep | grep -q yabai; then
    echo "✅ yabai is running!"
    yabai --version
else
    echo "❌ yabai is not running. Check the error:"
    cat /tmp/yabai_freedom.err.log 2>/dev/null || echo "   (No error log found)"
    echo ""
    echo "💡 Make sure:"
    echo "   1. yabai is checked in Accessibility settings"
    echo "   2. You've restarted System Settings after enabling"
    echo "   3. Try logging out and back in if it still doesn't work"
fi

