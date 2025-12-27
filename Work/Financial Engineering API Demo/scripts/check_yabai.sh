#!/bin/bash
# Check if any yabai files are staged or modified
# Usage: ./scripts/check_yabai.sh

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

ERROR=0

# Check staged files
STAGED_YABAI=$(git diff --cached --name-only | grep -i "yabai" || true)
if [ -n "$STAGED_YABAI" ]; then
    echo "❌ ERROR: Yabai files are staged for commit:"
    echo "$STAGED_YABAI" | sed 's/^/  - /'
    ERROR=1
fi

# Check modified files
MODIFIED_YABAI=$(git status --short | grep -i "yabai" || true)
if [ -n "$MODIFIED_YABAI" ]; then
    echo "⚠️  WARNING: Yabai files have uncommitted changes:"
    echo "$MODIFIED_YABAI" | sed 's/^/  - /'
    if [ $ERROR -eq 0 ]; then
        echo "  (These are not staged, so safe to commit)"
    fi
fi

if [ $ERROR -eq 0 ] && [ -z "$MODIFIED_YABAI" ]; then
    echo "✅ No yabai files in staging area or modified"
    exit 0
elif [ $ERROR -eq 0 ]; then
    exit 0
else
    echo ""
    echo "💡 To unstage yabai files:"
    echo "   git reset HEAD Work/yabai*.md"
    exit 1
fi

