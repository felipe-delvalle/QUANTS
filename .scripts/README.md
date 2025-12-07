# Scripts Directory

This directory contains utility scripts for Git workflow automation.

## Available Scripts

### `auto_commit.sh`
Automatically commits changes to prevent work loss.

**Usage:**
```bash
./auto_commit.sh                    # Auto-generate commit message
./auto_commit.sh "Custom message"   # Use custom message
```

**Features:**
- Stages all changes automatically
- Generates smart commit messages
- Shows what will be committed
- Reminds to push after commit

**When to use:**
- After accepting AI changes
- Before closing IDE
- Periodically during work
- Before switching branches

## Adding New Scripts

When adding new scripts:
1. Make them executable: `chmod +x script_name.sh`
2. Add usage documentation in this README
3. Follow the same style as `auto_commit.sh`
4. Use colors for output (see `auto_commit.sh` for examples)
