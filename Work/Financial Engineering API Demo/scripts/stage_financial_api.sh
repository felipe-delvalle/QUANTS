#!/bin/bash
# Stage only Financial Engineering API Demo files
# Usage: ./scripts/stage_financial_api.sh

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

# Check for yabai files in staging
if git diff --cached --name-only | grep -qi "yabai"; then
    echo "⚠️  WARNING: Yabai files are already staged!"
    echo "Unstaging yabai files..."
    git diff --cached --name-only | grep -i "yabai" | xargs git reset HEAD --
fi

# Stage only Financial Engineering API Demo files
echo "📦 Staging Financial Engineering API Demo files..."
git add "Work/Financial Engineering API Demo/"

# Show what's staged
echo ""
echo "✅ Staged files:"
git status --short | grep "Work/Financial Engineering API Demo" || echo "  (no changes to stage)"

# Check for any yabai files that might have been staged
if git diff --cached --name-only | grep -qi "yabai"; then
    echo ""
    echo "❌ ERROR: Yabai files were staged! Unstaging them..."
    git diff --cached --name-only | grep -i "yabai" | xargs git reset HEAD --
    exit 1
fi

echo ""
echo "✅ Safe to commit! Only Financial Engineering API Demo files are staged."

