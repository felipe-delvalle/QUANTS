#!/bin/bash
# yabai Installation and Setup Script
# Uses asmvik fork with codesigned binary (no CLT required)

set -e

echo "🚀 Installing yabai (codesigned binary - no CLT needed)..."

# Install yabai using asmvik installer (codesigned, no CLT required)
if ! command -v yabai &> /dev/null; then
    echo "📦 Installing yabai binary..."
    echo "   Using asmvik fork with codesigned release"
    echo "   Installing to ~/.local/bin (no sudo required)"
    
    # Create local bin directory if it doesn't exist
    mkdir -p ~/.local/bin ~/.local/man
    
    # Install to user's local directory
    curl -L https://raw.githubusercontent.com/asmvik/yabai/master/scripts/install.sh | sh /dev/stdin ~/.local/bin ~/.local/man
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "📝 Adding ~/.local/bin to PATH in ~/.zshrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Verify installation
    if command -v yabai &> /dev/null; then
        echo "✅ yabai installed successfully"
        yabai --version
    else
        echo "⚠️  yabai installed but not in PATH yet"
        echo "   Run: source ~/.zshrc or restart terminal"
        echo "   Or try Homebrew method..."
        brew install asmvik/formulae/yabai || {
            echo "❌ Installation methods failed"
            exit 1
        }
    fi
else
    echo "✅ yabai is already installed"
    yabai --version
fi

# Create config directory
mkdir -p ~/.config/yabai

# Create yabai config file if it doesn't exist
if [ ! -f ~/.config/yabai/yabairc ]; then
    echo "📝 Creating yabai configuration file..."
    cat > ~/.config/yabai/yabairc << 'EOF'
#!/usr/bin/env sh

# Global settings
yabai -m config layout bsp
yabai -m config window_gap 6
yabai -m config top_padding 10
yabai -m config bottom_padding 10
yabai -m config left_padding 10
yabai -m config right_padding 10
yabai -m config window_shadow on

# Floating window rules
yabai -m rule --add app="^System Settings$" manage=off
yabai -m rule --add app="^System Preferences$" manage=off
yabai -m rule --add app="^Calculator$" manage=off
yabai -m rule --add app="^Dictionary$" manage=off

# Configure scripting addition (if SIP is disabled)
# Uncomment the lines below if you've disabled SIP and configured sudoers
# yabai -m signal --add event=dock_did_restart action="sudo yabai --load-sa"
# sudo yabai --load-sa

# Start yabai service
yabai --start-service

echo "yabai config loaded"
EOF
    chmod +x ~/.config/yabai/yabairc
    echo "✅ Configuration file created at ~/.config/yabai/yabairc"
else
    echo "✅ Configuration file already exists"
fi

# Start yabai service
echo "🔄 Starting yabai service..."
yabai --start-service 2>&1 || echo "⚠️  Service start may require permissions"

echo ""
echo "✅ yabai installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Grant Accessibility Permissions:"
echo "   - Go to System Settings > Privacy & Security > Accessibility"
echo "   - Click the + button and add yabai"
echo "   - Location: $(which yabai)"
echo ""
echo "2. (Optional) If you disabled SIP, configure scripting addition:"
echo "   - Run: sudo visudo -f /private/etc/sudoers.d/yabai"
echo "   - Add: $(whoami) ALL=(root) NOPASSWD: sha256:$(shasum -a 256 $(which yabai) | cut -d ' ' -f 1) $(which yabai) --load-sa"
echo "   - Then uncomment the scripting addition lines in ~/.config/yabai/yabairc"
echo ""
echo "💡 Useful commands:"
echo "   yabai --restart-service          # Restart yabai"
echo "   yabai --stop-service             # Stop yabai"
echo "   yabai -m window --toggle float   # Toggle floating for current window"
echo "   yabai -m window --toggle sticky  # Pin window on top"
echo ""

