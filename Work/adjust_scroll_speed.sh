#!/bin/bash
# Adjust Horizontal Mouse Scroll Speed on macOS
# Higher values = faster horizontal scrolling

echo "🖱️  Horizontal Scroll Speed Adjuster"
echo "======================================"
echo ""

# Current settings
echo "Current horizontal scroll settings:"
HORIZONTAL_SCROLL=$(defaults read -g com.apple.swipescrolldirection 2>/dev/null)
HORIZONTAL_SCALING=$(defaults read com.apple.driver.AppleBluetoothMultitouch.mouse MouseHorizontalScroll 2>/dev/null || defaults read -g com.apple.mouse.scaling 2>/dev/null)
echo "   Horizontal scroll scaling: ${HORIZONTAL_SCALING:-Not set (using default)}"
echo ""

# Function to set horizontal scroll speed
set_horizontal_scroll_speed() {
    local speed=$1
    echo "Setting horizontal scroll speed to: $speed"
    
    # Primary method: Mouse horizontal scroll scaling
    defaults write -g com.apple.mouse.scaling -float $speed
    
    # Alternative: Bluetooth mouse horizontal scroll (if applicable)
    defaults write com.apple.driver.AppleBluetoothMultitouch.mouse MouseHorizontalScroll -int $(echo "$speed * 10" | bc | cut -d. -f1)
    
    # Also try the scroll wheel scaling
    defaults write -g com.apple.scrollwheel.scaling -float $speed
    
    echo "✅ Horizontal scroll speed set to $speed"
    echo "⚠️  You may need to log out and back in (or restart) for changes to take full effect"
    echo "   Or try: killall Finder"
}

# Interactive menu
echo "Select horizontal scroll speed:"
echo "1. Slow (0.5)"
echo "2. Normal (1.0) - default"
echo "3. Fast (2.0)"
echo "4. Very Fast (3.0)"
echo "5. Extra Fast (4.0)"
echo "6. Custom value"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        set_horizontal_scroll_speed 0.5
        ;;
    2)
        set_horizontal_scroll_speed 1.0
        ;;
    3)
        set_horizontal_scroll_speed 2.0
        ;;
    4)
        set_horizontal_scroll_speed 3.0
        ;;
    5)
        set_horizontal_scroll_speed 4.0
        ;;
    6)
        read -p "Enter custom speed (e.g., 2.5): " custom_speed
        set_horizontal_scroll_speed $custom_speed
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "💡 Tip: If changes don't take effect immediately, try:"
echo "   killall Finder"
echo "   Or log out and back in"
echo ""
echo "📝 Note: macOS has limited built-in control for horizontal scroll."
echo "   For better control, consider using Mos or LinearMouse (brew install --cask mos)"

