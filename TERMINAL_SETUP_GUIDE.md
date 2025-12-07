# 🚀 Beautiful Git-Aware Terminal Setup Guide

## ✅ Installation Status

- **Git**: ✅ Installed (v2.39.3)
- **zsh**: ✅ Installed (v5.9) - Default shell
- **Starship Prompt**: ✅ Installed (v1.24.1)
- **Configuration**: ✅ Complete

## 🎨 What You Got

Your terminal now features:

- ✨ **Colorful, modern prompt** with Git branch always visible
- 🌿 **Git branch name** displayed prominently
- 📊 **Clear clean/dirty indicators** with icons:
  - ✓ = Up to date
  - 📝 = Modified/Untracked files
  - 🗑 = Deleted files
  - 🏳 = Conflicts
  - ⇡ = Ahead of remote
  - ⇣ = Behind remote
  - 📦 = Stashed changes
- 🎯 **50+ Git shortcuts** for faster workflow
- 🚀 **Fast performance** (Starship is written in Rust)

## 🔄 How to Reload Your Terminal

### Option 1: Reload in Current Terminal
```bash
source ~/.zshrc
```

### Option 2: Open New Terminal Window
- In Cursor: `Cmd + Shift + `` (backtick) to open integrated terminal
- Or: `Terminal` → `New Terminal`

### Option 3: Restart Cursor
- Close and reopen Cursor completely

## 🎯 Git Shortcuts Reference

### Status & Info
- `gs` - Git status
- `gss` - Git status (short format)
- `ginfo` - Show remotes, branches, and status

### Branch Operations
- `gb` - List branches
- `gba` - List all branches (local + remote)
- `gbr` - List remote branches
- `gco <branch>` - Checkout branch
- `gcb <branch>` - Create and checkout new branch
- `gbd <branch>` - Delete branch (local + remote)

### Commit Operations
- `ga <file>` - Add file
- `gaa` - Add all files
- `gap` - Interactive staging (patch mode)
- `gc` - Commit with editor
- `gcm "message"` - Commit with message
- `gca` - Amend last commit
- `gcam "message"` - Add all and commit

### Diff & Log
- `gd` - Show diff
- `gdc` - Show staged diff
- `gl` - Log (oneline, graph)
- `gla` - Log all branches
- `glog` - Pretty formatted log

### Push & Pull
- `gp` - Push
- `gpo` - Push to origin
- `gpu` - Push and set upstream
- `gpush` - Push current branch with upstream
- `gpl` - Pull
- `gplr` - Pull with rebase

### Stash Operations
- `gst` - Stash changes
- `gstl` - List stashes
- `gstp` - Pop stash
- `gsta` - Apply stash

### Reset & Clean
- `grh` - Reset HEAD (unstage)
- `grhh` - Hard reset to HEAD
- `gundo` - Undo last commit (keep changes)
- `gdiscard` - Discard changes to file
- `gdiscardall` - Discard all changes

## 🐛 Troubleshooting

### Git Branch Not Showing?

1. **Check if you're in a Git repository:**
   ```bash
   git status
   ```
   If you get "not a git repository", navigate to a Git repo first.

2. **Verify Starship is loaded:**
   ```bash
   which starship
   ```
   Should show: `/opt/homebrew/bin/starship`

3. **Check Starship config:**
   ```bash
   starship print-config | grep git_branch
   ```
   Should show Git branch configuration.

4. **Reload your shell:**
   ```bash
   source ~/.zshrc
   ```

5. **Check terminal compatibility:**
   - Make sure you're using zsh (not bash)
   - Verify: `echo $SHELL` should show `/bin/zsh`

### Colors Not Showing?

1. **Check terminal type:**
   ```bash
   echo $TERM
   ```
   Should show something like `xterm-256color` or `screen-256color`

2. **In Cursor's integrated terminal:**
   - Go to Settings → Terminal
   - Ensure "Terminal > Integrated: Shell Integration" is enabled

3. **Force color output:**
   ```bash
   export CLICOLOR=1
   export TERM=xterm-256color
   ```

### Prompt Looks Wrong?

1. **Verify Starship config exists:**
   ```bash
   ls -la ~/.config/starship.toml
   ```

2. **Test Starship directly:**
   ```bash
   starship prompt
   ```

3. **Check for errors:**
   ```bash
   source ~/.zshrc 2>&1 | grep -i error
   ```

### Shortcuts Not Working?

1. **Verify aliases are loaded:**
   ```bash
   alias | grep "^gs="
   ```
   Should show: `gs='git status'`

2. **Check for conflicts:**
   ```bash
   type gs
   ```
   Should show the alias definition

3. **Reload configuration:**
   ```bash
   source ~/.zshrc
   ```

## 🎨 Customizing Your Prompt

### Edit Starship Config
```bash
code ~/.config/starship.toml
# or
nano ~/.config/starship.toml
```

### Popular Customizations

**Change prompt symbol:**
Edit `~/.config/starship.toml`:
```toml
[character]
success_symbol = "[➜](bold green)"
error_symbol = "[✗](bold red)"
```

**Change Git branch color:**
```toml
[git_branch]
style = "bold blue"  # Change from purple to blue
```

**Hide certain modules:**
```toml
[python]
disabled = true  # Hide Python version
```

After editing, reload: `source ~/.zshrc`

## 📚 Alternative Themes (If You Want to Switch)

### Option 1: Oh My Zsh + Powerlevel10k
```bash
# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install Powerlevel10k
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# Edit ~/.zshrc
ZSH_THEME="powerlevel10k/powerlevel10k"
```

### Option 2: Oh My Zsh + Agnoster Theme
```bash
# Install Oh My Zsh (if not installed)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Edit ~/.zshrc
ZSH_THEME="agnoster"
```

## 🔒 Backup & Restore

### Your Current Backup
- Original `.zshrc` backed up to: `~/.zshrc.backup.20251207_145049`

### Restore Original Config
```bash
cp ~/.zshrc.backup.20251207_145049 ~/.zshrc
source ~/.zshrc
```

### Backup Current Config
```bash
cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
cp ~/.config/starship.toml ~/.config/starship.toml.backup.$(date +%Y%m%d_%H%M%S)
```

## 🎓 Quick Start Examples

```bash
# Navigate to your project
cd ~/QUANTS

# See your beautiful prompt with Git branch
# Prompt shows: on [main] with status indicators

# Check status
gs

# Stage and commit
gaa
gcm "Your commit message"

# Push to remote
gpush

# Create new branch
gcb feature/new-feature

# Switch branches
gco main
```

## 📖 Additional Resources

- **Starship Docs**: https://starship.rs/
- **Starship Config**: https://starship.rs/config/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf

## ✨ Enjoy Your Beautiful Terminal!

Your terminal is now configured with:
- ✅ Modern, colorful prompt
- ✅ Git branch always visible
- ✅ Clear status indicators
- ✅ 50+ Git shortcuts
- ✅ Professional appearance

Happy coding! 🚀
