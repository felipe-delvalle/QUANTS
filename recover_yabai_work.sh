#!/bin/bash
# Script to recover lost yabai work after branch change

echo "🔍 Searching for yabai files in git history..."

# Check current branch
echo "Current branch:"
git branch --show-current

# Check all branches for yabai files
echo -e "\n📋 Checking all branches for yabai files:"
for branch in $(git branch -a | sed 's/remotes\///' | sed 's/^[ *]*//' | sort -u); do
    if [[ "$branch" != "HEAD" ]]; then
        echo "Checking branch: $branch"
        git ls-tree -r --name-only "$branch" 2>/dev/null | grep -i yabai | while read file; do
            echo "  Found: $file in $branch"
        done
    fi
done

# Check git reflog for recent branch changes
echo -e "\n📜 Recent branch changes (reflog):"
git reflog --all | grep -i "checkout\|branch" | head -20

# Check for deleted files in git history
echo -e "\n🗑️  Checking for deleted yabai files in git history:"
git log --all --full-history --diff-filter=D --summary -- "*yabai*" 2>/dev/null | head -50

# Check for yabai files in recent commits
echo -e "\n📝 Recent commits mentioning yabai:"
git log --all --oneline --grep="yabai" -i | head -10

# Check for yabai files in any commit
echo -e "\n📁 Yabai files found in git history:"
git log --all --pretty=format: --name-only --diff-filter=A | grep -i yabai | sort -u

# Check for stashed changes
echo -e "\n💾 Checking stashes:"
git stash list

# Check for unreachable objects
echo -e "\n🔎 Checking for unreachable yabai objects:"
git fsck --unreachable 2>/dev/null | grep -i yabai | head -10

echo -e "\n✅ Recovery script complete!"
echo "If you found files, you can recover them with:"
echo "  git checkout <branch> -- <file_path>"
echo "  or"
echo "  git show <commit>:<file_path> > <file_path>"

