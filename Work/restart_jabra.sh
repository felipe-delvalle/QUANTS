#!/bin/bash
# Restart Jabra Direct application and services

echo "Stopping Jabra Direct..."
killall "Jabra Direct" 2>/dev/null
killall "Jabra Softphone Service" 2>/dev/null
killall "Jabra ZoomPluginMacOS" 2>/dev/null
killall "Jabra Avaya Integration" 2>/dev/null
killall "Jabra Avaya3 Integration" 2>/dev/null
killall "Jabra Bria Integration" 2>/dev/null

# Wait for processes to fully terminate
sleep 2

echo "Starting Jabra Direct..."
open -a "Jabra Direct" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Jabra Direct restarted successfully"
    sleep 1
    echo "Current Jabra processes:"
    ps aux | grep -i jabra | grep -v grep | awk '{print $2, $11}' | head -5
else
    echo "✗ Failed to restart Jabra Direct"
    exit 1
fi



