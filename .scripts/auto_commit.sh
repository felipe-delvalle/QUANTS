#!/bin/bash

# ============================================================================
# Auto-Commit Script
# ============================================================================
# Automatically commits changes to prevent work loss
# Can be called manually or integrated into workflows
#
# Usage:
#   ./auto_commit.sh                    # Commit all changes with auto message
#   ./auto_commit.sh "Custom message"    # Commit with custom message
# ============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}✗ Error: Not in a Git repository${NC}"
    exit 1
fi

cd "$REPO_ROOT"

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${YELLOW}ℹ No changes to commit${NC}"
    exit 0
fi

# Get current branch
BRANCH=$(git branch --show-current)
if [ -z "$BRANCH" ]; then
    echo -e "${RED}✗ Error: Could not determine current branch${NC}"
    exit 1
fi

# Generate commit message
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    # Auto-generate commit message based on changes
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")
    UNSTAGED_FILES=$(git diff --name-only 2>/dev/null || echo "")
    UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null || echo "")
    
    # Count changes
    STAGED_COUNT=$(echo "$STAGED_FILES" | grep -c . || echo "0")
    UNSTAGED_COUNT=$(echo "$UNSTAGED_FILES" | grep -c . || echo "0")
    UNTRACKED_COUNT=$(echo "$UNTRACKED_FILES" | grep -c . || echo "0")
    
    # Build message
    PARTS=()
    if [ "$STAGED_COUNT" -gt 0 ] || [ "$UNSTAGED_COUNT" -gt 0 ] || [ "$UNTRACKED_COUNT" -gt 0 ]; then
        if [ "$UNTRACKED_COUNT" -gt 0 ]; then
            PARTS+=("Add $UNTRACKED_COUNT new file(s)")
        fi
        if [ "$STAGED_COUNT" -gt 0 ] || [ "$UNSTAGED_COUNT" -gt 0 ]; then
            MODIFIED_COUNT=$((STAGED_COUNT + UNSTAGED_COUNT))
            PARTS+=("Update $MODIFIED_COUNT file(s)")
        fi
        
        # Get file types
        ALL_FILES="$STAGED_FILES $UNSTAGED_FILES $UNTRACKED_FILES"
        FILE_TYPES=$(echo "$ALL_FILES" | sed 's/.*\.//' | sort -u | grep -v '^$' | head -3 | tr '\n' ',' | sed 's/,$//')
        
        if [ -n "$FILE_TYPES" ]; then
            COMMIT_MSG="Auto-commit: $(echo "${PARTS[@]}" | tr ' ' ' ') ($FILE_TYPES)"
        else
            COMMIT_MSG="Auto-commit: $(echo "${PARTS[@]}" | tr ' ' ' ')"
        fi
    else
        COMMIT_MSG="Auto-commit: Save work progress"
    fi
fi

# Stage all changes
echo -e "${BLUE}📦 Staging changes...${NC}"
git add -A

# Show what will be committed
echo -e "${BLUE}📋 Changes to commit:${NC}"
git status --short

# Commit
echo -e "${BLUE}💾 Committing changes...${NC}"
if git commit -m "$COMMIT_MSG"; then
    echo -e "${GREEN}✓ Successfully committed to branch: ${BRANCH}${NC}"
    echo -e "${GREEN}  Commit message: ${COMMIT_MSG}${NC}"
    echo ""
    echo -e "${YELLOW}💡 Remember to push: git push${NC}"
    echo -e "${YELLOW}   Or use shortcut: gpush${NC}"
    exit 0
else
    echo -e "${RED}✗ Failed to commit${NC}"
    exit 1
fi
