#!/bin/bash

# File Recovery Script - Recovers deleted files from git history, stashes, and branches

set -e

echo "=== Git File Recovery Tool ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

RECOVERY_DIR="./recovered_files"
mkdir -p "$RECOVERY_DIR"

echo -e "${BLUE}1. Checking for files in stashes...${NC}"
if git stash list > /dev/null 2>&1; then
    stash_count=$(git stash list | wc -l | tr -d ' ')
    if [ "$stash_count" -gt 0 ]; then
        echo -e "${GREEN}Found $stash_count stash(es)${NC}"
        git stash list
        echo ""
        echo "Files in stashes:"
        git stash show -p stash@{0} --name-only 2>/dev/null | head -20 || true
    else
        echo "No stashes found"
    fi
else
    echo "No stashes found"
fi
echo ""

echo -e "${BLUE}2. Checking for deleted files in git history...${NC}"
deleted_files=$(git log --all --full-history --diff-filter=D --name-only --pretty=format: | sort -u)
if [ -n "$deleted_files" ]; then
    echo -e "${GREEN}Found deleted files in history:${NC}"
    echo "$deleted_files" | head -20
    echo ""
    echo "Total unique deleted files: $(echo "$deleted_files" | wc -l | tr -d ' ')"
else
    echo "No deleted files found in git history"
fi
echo ""

echo -e "${BLUE}3. Checking for files in other branches not in current branch...${NC}"
current_branch=$(git branch --show-current)
other_branches=$(git branch -a | grep -v "$current_branch" | grep -v HEAD | sed 's/^[* ] //' | sed 's/remotes\///')

if [ -n "$other_branches" ]; then
    echo -e "${GREEN}Found other branches:${NC}"
    for branch in $other_branches; do
        branch_name=$(echo "$branch" | sed 's/^origin\///')
        echo "  - $branch_name"
        
        # Find files in this branch that don't exist in current branch
        branch_files=$(git ls-tree -r --name-only "$branch" 2>/dev/null | head -10)
        if [ -n "$branch_files" ]; then
            echo "    Sample files:"
            echo "$branch_files" | head -5 | sed 's/^/      /'
        fi
    done
else
    echo "No other branches found"
fi
echo ""

echo -e "${BLUE}4. Recent commits with file changes...${NC}"
echo "Last 10 commits:"
git log --oneline --name-status -10 | head -30
echo ""

echo -e "${YELLOW}=== Recovery Options ===${NC}"
echo ""
echo "To recover a specific file, use one of these commands:"
echo ""
echo "  From a specific commit:"
echo "    git checkout <commit-hash> -- <file-path>"
echo ""
echo "  From a stash:"
echo "    git checkout stash@{0} -- <file-path>"
echo ""
echo "  From another branch:"
echo "    git checkout <branch-name> -- <file-path>"
echo ""
echo "  List all files in a commit:"
echo "    git ls-tree -r --name-only <commit-hash>"
echo ""
echo "  Search for a file in all commits:"
echo "    git log --all --full-history -- <file-path>"
echo ""

# Interactive recovery function
recover_file() {
    local file_path=$1
    local source=$2
    
    if [ -z "$file_path" ]; then
        echo "Usage: recover_file <file-path> [commit-hash|branch-name|stash@{0}]"
        return 1
    fi
    
    if [ -z "$source" ]; then
        # Try to find the file in git history
        echo "Searching for $file_path in git history..."
        commits=$(git log --all --full-history --oneline -- "$file_path" | head -5)
        if [ -n "$commits" ]; then
            echo "Found in commits:"
            echo "$commits"
            latest_commit=$(echo "$commits" | head -1 | awk '{print $1}')
            echo ""
            echo "Recovering from latest commit: $latest_commit"
            git checkout "$latest_commit" -- "$file_path"
            echo "File recovered to: $file_path"
        else
            echo "File not found in git history"
        fi
    else
        echo "Recovering $file_path from $source..."
        git checkout "$source" -- "$file_path"
        echo "File recovered to: $file_path"
    fi
}

# If file path provided as argument, try to recover it
if [ $# -gt 0 ]; then
    recover_file "$@"
fi
