# Yabai Work Recovery Guide

## Quick Recovery Steps

### 1. Check All Branches for Yabai Files
```bash
# List all branches
git branch -a

# Check each branch for yabai files
git ls-tree -r --name-only <branch-name> | grep -i yabai

# If found, checkout that branch or recover the file
git checkout <branch-name> -- Work/yabai_keyboard_shortcuts.md
```

### 2. Check Git Reflog (Recent Branch Changes)
```bash
# See recent branch switches
git reflog --all | grep checkout

# Go back to the commit before you switched branches
git reflog
# Find the commit hash before the branch change, then:
git checkout <commit-hash>
# Copy your files, then return to your current branch
```

### 3. Check for Deleted Files in Git History
```bash
# Find when yabai files were deleted
git log --all --full-history --diff-filter=D --summary -- "*yabai*"

# Recover from a specific commit
git show <commit-hash>:Work/yabai_keyboard_shortcuts.md > Work/yabai_keyboard_shortcuts.md
```

### 4. Check Stashed Changes
```bash
# List all stashes
git stash list

# If you see a stash with yabai work:
git stash show -p stash@{0} | grep -A 100 "yabai"
# Or apply the stash
git stash apply stash@{0}
```

### 5. Check for Unreachable Objects
```bash
# Find unreachable commits/objects
git fsck --unreachable

# If you find yabai-related objects, recover them
git show <object-hash> > recovered_file.md
```

### 6. Check Recent Commits
```bash
# Find commits mentioning yabai
git log --all --oneline --grep="yabai" -i

# Check what files were in those commits
git show <commit-hash> --name-only
```

## Expected Yabai Files (Based on Project Structure)

Based on your project, you should have these yabai files:
- `Work/yabai_keyboard_shortcuts.md`
- `Work/yabai_settings_guide.md`
- `Work/yabai_complete_reference.md`
- `Work/yabai_save_space_guide.md`
- `Work/yabai_smart_resize_development_guide.md`
- `Work/yabai_smart_resize_final_summary.md`
- `Work/yabai_permissions_guide.md`
- `Work/yabai_commands.md`
- `Work/skhd_explanation.md`
- `.yabai-config/README.md`

## Automated Recovery

Run the recovery script:
```bash
./recover_yabai_work.sh
```

## If Files Are Completely Lost

If the files were never committed and are truly lost:

1. **Check your editor's local history** (VS Code/Cursor has local history)
2. **Check Time Machine backups** (if enabled on macOS)
3. **Check if files are in another directory** or on another machine
4. **Recreate from memory** - the files were recently viewed, so you might remember the content

## Prevention for Future

To prevent this in the future:
```bash
# Always commit or stash before switching branches
git add .
git commit -m "WIP: yabai configuration"
# OR
git stash save "yabai work in progress"

# Then switch branches
git checkout <other-branch>
```

