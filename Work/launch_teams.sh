#!/bin/bash

# ============================================================
# Launch Microsoft Teams (or switch to it if already running)
# ============================================================
# This script will:
# - Switch to Teams if it's already running
# - Launch Teams if it's not running
# - Never opens duplicate instances
# ============================================================

TEAMS_APP="Microsoft Teams"

# Use AppleScript to activate Teams (works whether running or not)
# The 'activate' command will:
# - Bring Teams to front if already running
# - Launch Teams if not running
osascript <<EOF
tell application "$TEAMS_APP"
    activate
end tell
EOF

