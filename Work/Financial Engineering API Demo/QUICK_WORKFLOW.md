# 🚀 Quick Workflow Reference

## One-Time Setup

```bash
cd "Work/Financial Engineering API Demo"
./scripts/setup_isolated_workflow.sh
```

This will:
- Create `financial-api-dev` branch
- Protect yabai files from accidental commits
- Set up safety hooks

## Daily Workflow

### 1. Start Working
```bash
cd "Work/Financial Engineering API Demo"
git checkout financial-api-dev
```

### 2. Make Changes
Work normally in this directory.

### 3. Stage Files (Safe)
```bash
./scripts/stage_financial_api.sh
```

### 4. Verify Safety
```bash
./scripts/check_yabai.sh
```

### 5. Commit
```bash
git commit -m "your message"
git push origin financial-api-dev
```

## ⚠️ Before Every Commit

Always run:
```bash
./scripts/check_yabai.sh
```

This ensures no yabai files are accidentally committed.

## 🆘 If You See Yabai Files Staged

```bash
git reset HEAD Work/yabai*.md
git reset HEAD .yabai-config/
```

Then use `./scripts/stage_financial_api.sh` again.

## 📚 Full Guide

See `WORKFLOW_GUIDE.md` for detailed instructions.

