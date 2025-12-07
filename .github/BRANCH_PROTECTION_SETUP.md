# Branch Protection Setup Guide

## 🔒 Setting Up Branch Protection Rules

This guide will help you set up branch protection rules on GitHub to ensure code quality and prevent accidental pushes to main/master branches.

## 📋 Steps to Set Up Branch Protection

### 1. Navigate to Repository Settings
1. Go to your GitHub repository: `https://github.com/felipe-delvalle/QUANTS`
2. Click on **Settings** (top right)
3. Click on **Branches** (left sidebar)

### 2. Add Branch Protection Rule

#### For `main` or `master` branch:
1. Click **Add rule** or **Edit** if rule exists
2. Under **Branch name pattern**, enter: `main` (or `master`)
3. Configure the following settings:

#### ✅ Recommended Settings:

**Protect matching branches:**
- ✅ Require a pull request before merging
  - ✅ Require approvals: **1** (or more)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (if you have CODEOWNERS file)
  
- ✅ Require status checks to pass before merging
  - Select: **All required status checks must pass**
  - (Add status checks after setting up CI/CD)
  
- ✅ Require conversation resolution before merging
- ✅ Require signed commits (optional, for extra security)
- ✅ Require linear history (optional, keeps history clean)
- ✅ Include administrators (recommended)

**Restrict who can push to matching branches:**
- ✅ Restrict pushes that create matching branches (recommended)

**Rules applied to everyone including administrators:**
- ✅ Do not allow bypassing the above settings

### 3. For Feature Branches (Optional)

Create a rule for `feature/*` branches:
- Branch name pattern: `feature/*`
- ✅ Require pull request before merging
- ✅ Require 1 approval
- ✅ Allow force pushes (optional, for rebasing)
- ✅ Allow deletions (optional)

### 4. Save Settings

Click **Create** or **Save changes**

## 🛡️ What This Protects Against

- ✅ Accidental direct pushes to main/master
- ✅ Merging without code review
- ✅ Merging broken code (if CI/CD is set up)
- ✅ Force pushes that rewrite history (optional)

## 🔄 Workflow After Protection

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add feature"
   ```

3. **Push to remote:**
   ```bash
   git push -u origin feature/my-feature
   ```

4. **Create Pull Request:**
   - Go to GitHub repository
   - Click "Compare & pull request"
   - Fill out PR template
   - Request review

5. **After approval, merge:**
   - Use "Squash and merge" or "Merge commit"
   - Delete branch after merge

## 📝 Additional Recommendations

### Create CODEOWNERS File
Create `.github/CODEOWNERS` to automatically assign reviewers:

```
# Default owners
* @felipe-delvalle

# Specific paths
/Work/ @felipe-delvalle
/.github/ @felipe-delvalle
```

### Set Up Status Checks
After creating GitHub Actions workflows, add them as required status checks in branch protection settings.

## ⚠️ Important Notes

- **Administrators**: If "Include administrators" is checked, even repo admins must follow these rules
- **Force Push**: Disabling force push prevents history rewriting (recommended for main)
- **Status Checks**: These require CI/CD workflows to be set up first

## 🆘 Troubleshooting

**Can't push to protected branch?**
- Create a feature branch instead
- Create a PR to merge into protected branch

**Need to bypass protection?**
- Temporarily uncheck "Include administrators"
- Or disable the rule temporarily
- Re-enable after making changes

---

**Status:** ⚠️ **Manual Setup Required** - Branch protection must be configured on GitHub's web interface
