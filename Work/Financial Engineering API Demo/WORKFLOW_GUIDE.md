# Financial Engineering API Demo - Isolated Workflow Guide

This guide helps you work **only** in the Financial Engineering API Demo project without accidentally modifying yabai configuration or other files.

## 🎯 Quick Start

### Option 1: Dedicated Branch (Recommended)

```bash
# Navigate to project
cd "Work/Financial Engineering API Demo"

# Create and switch to a dedicated branch
git checkout -b financial-api-dev

# Work normally - but only commit files from this directory
```

### Option 2: Use Git Sparse-Checkout (Advanced)

This makes git only track the Financial Engineering API Demo directory:

```bash
# Enable sparse-checkout
git config core.sparseCheckout true

# Create sparse-checkout file
echo "Work/Financial Engineering API Demo/*" > .git/info/sparse-checkout
echo "!.gitignore" >> .git/info/sparse-checkout
echo "!Work/yabai*" >> .git/info/sparse-checkout

# Apply sparse-checkout
git read-tree -mu HEAD
```

## 📋 Daily Workflow

### 1. Start Working Session

```bash
# Navigate to project
cd "Work/Financial Engineering API Demo"

# Ensure you're on the right branch
git checkout financial-api-dev

# Check what files are tracked (should only see Financial Engineering files)
git status
```

### 2. Make Changes

Work normally in the Financial Engineering API Demo directory. Git will track all changes, but you'll only commit what's in this directory.

### 3. Stage Only Financial Engineering Files

```bash
# Option A: Stage only this directory (safest)
git add "Work/Financial Engineering API Demo/"

# Option B: Use the helper script
../scripts/stage_financial_api.sh

# Option C: Stage specific files
git add "Work/Financial Engineering API Demo/api_service.py"
git add "Work/Financial Engineering API Demo/src/"
```

### 4. Commit Safely

```bash
# Verify what you're committing (should NOT see yabai files)
git status

# Commit
git commit -m "feat: your change description"

# Push to remote
git push origin financial-api-dev
```

## 🛡️ Protecting Yabai Files

### Method 1: Git Update-Index (Skip Worktree)

Prevent accidental commits of yabai files:

```bash
# Mark yabai files as "skip worktree" (git will ignore changes)
git update-index --skip-worktree Work/yabai*.md
git update-index --skip-worktree Work/.yabai-config/
git update-index --skip-worktree .yabai-config/

# To undo later:
git update-index --no-skip-worktree Work/yabai*.md
```

### Method 2: Use .git/info/exclude

Add yabai files to local exclude (not tracked by git):

```bash
# Add to .git/info/exclude (this file is NOT committed)
echo "Work/yabai*" >> .git/info/exclude
echo ".yabai-config/" >> .git/info/exclude
```

### Method 3: Pre-Commit Hook

Create a pre-commit hook to prevent committing yabai files:

```bash
# Create hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Prevent committing yabai files
if git diff --cached --name-only | grep -q "yabai"; then
    echo "❌ Error: Attempting to commit yabai files!"
    echo "Please unstage yabai files before committing."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

## 🔧 Helper Scripts

### Stage Only Financial Engineering Files

Create `../scripts/stage_financial_api.sh`:

```bash
#!/bin/bash
# Stage only Financial Engineering API Demo files
git add "Work/Financial Engineering API Demo/" --all
git status --short | grep "Work/Financial Engineering API Demo"
```

### Check for Accidental Yabai Changes

Create `../scripts/check_yabai.sh`:

```bash
#!/bin/bash
# Check if any yabai files are staged or modified
if git diff --cached --name-only | grep -q "yabai"; then
    echo "⚠️  WARNING: Yabai files are staged!"
    git diff --cached --name-only | grep "yabai"
    exit 1
fi

if git status --short | grep -q "yabai"; then
    echo "⚠️  WARNING: Yabai files have uncommitted changes!"
    git status --short | grep "yabai"
    exit 1
fi

echo "✅ No yabai files in staging area"
```

## 📝 Git Aliases (Optional)

Add these to `~/.gitconfig` or run:

```bash
# Only show Financial Engineering API Demo status
git config --global alias.fin-status '!git status --short -- "Work/Financial Engineering API Demo/"'

# Only diff Financial Engineering API Demo
git config --global alias.fin-diff '!git diff -- "Work/Financial Engineering API Demo/"'

# Stage only Financial Engineering API Demo
git config --global alias.fin-add '!git add "Work/Financial Engineering API Demo/"'

# Log only for Financial Engineering API Demo
git config --global alias.fin-log '!git log --oneline -- "Work/Financial Engineering API Demo/"'
```

Then use:
```bash
git fin-status
git fin-diff
git fin-add
git fin-log
```

## 🚨 Safety Checklist Before Committing

Always run this before committing:

```bash
# 1. Check what's staged
git status

# 2. Verify no yabai files
git diff --cached --name-only | grep -i yabai

# 3. Verify only Financial Engineering files
git diff --cached --name-only | grep -v "Financial Engineering API Demo"

# 4. If everything looks good, commit
git commit -m "your message"
```

## 🔄 Branch Strategy

### Recommended Branch Structure

```
main (protected)
  └── financial-api-dev (your working branch)
      └── financial-api-feature-* (feature branches)
```

### Creating Feature Branches

```bash
# From financial-api-dev
git checkout financial-api-dev
git pull origin financial-api-dev
git checkout -b financial-api-feature-new-endpoint

# Work on feature...
git add "Work/Financial Engineering API Demo/"
git commit -m "feat: add new endpoint"
git push origin financial-api-feature-new-endpoint

# Merge back to financial-api-dev
git checkout financial-api-dev
git merge financial-api-feature-new-endpoint
```

## 🎯 Best Practices

1. **Always work from the project directory**: `cd "Work/Financial Engineering API Demo"`
2. **Use dedicated branch**: `financial-api-dev` or feature branches
3. **Check before committing**: Always verify what's staged
4. **Use helper scripts**: Automate safety checks
5. **Keep yabai files excluded**: Use one of the protection methods above

## 🆘 If You Accidentally Stage Yabai Files

```bash
# Unstage yabai files
git reset HEAD Work/yabai*.md
git reset HEAD .yabai-config/

# Or unstage everything and start over
git reset HEAD

# Then stage only Financial Engineering files
git add "Work/Financial Engineering API Demo/"
```

## 📚 Additional Resources

- See `../YABAI_RECOVERY_GUIDE.md` for yabai file recovery
- See `../recover_files.sh` for general file recovery
- Git sparse-checkout docs: https://git-scm.com/docs/git-sparse-checkout

