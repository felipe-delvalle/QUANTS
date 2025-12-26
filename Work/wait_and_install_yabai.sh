#!/bin/bash
# Wait for Command Line Tools and Install yabai

echo "⏳ Waiting for Command Line Tools to be installed..."
echo "   (Make sure you complete the GUI installer if it's open)"
echo ""

MAX_WAIT=300  # 5 minutes
ELAPSED=0
CHECK_INTERVAL=5

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if xcode-select -p &> /dev/null; then
        echo "✅ Command Line Tools are ready!"
        echo ""
        # Run the installation script
        exec ./Work/install_yabai.sh
        exit 0
    fi
    
    echo "   Still waiting... ($ELAPSED seconds)"
    sleep $CHECK_INTERVAL
    ELAPSED=$((ELAPSED + CHECK_INTERVAL))
done

echo "❌ Timeout waiting for Command Line Tools"
echo "   Please complete the installation manually and run: ./Work/install_yabai.sh"
exit 1

