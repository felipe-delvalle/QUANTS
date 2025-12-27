#!/bin/bash
# Setup isolated workflow for Financial Engineering API Demo
# This script sets up protection for yabai files and creates helper scripts

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "🔧 Setting up isolated workflow for Financial Engineering API Demo..."
echo ""

# 1. Create dedicated branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/financial-api-dev; then
    echo "📦 Creating dedicated branch: financial-api-dev"
    git checkout -b financial-api-dev
    echo "✅ Branch created"
else
    echo "✅ Branch 'financial-api-dev' already exists"
    read -p "Switch to it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout financial-api-dev
    fi
fi

echo ""

# 2. Add yabai files to local exclude
echo "🛡️  Protecting yabai files..."
if ! grep -q "yabai" .git/info/exclude 2>/dev/null; then
    echo "" >> .git/info/exclude
    echo "# Yabai configuration files - protected from accidental commits" >> .git/info/exclude
    echo "Work/yabai*" >> .git/info/exclude
    echo ".yabai-config/" >> .git/info/exclude
    echo "✅ Added yabai files to .git/info/exclude"
else
    echo "✅ Yabai files already in .git/info/exclude"
fi

echo ""

# 3. Create pre-commit hook
echo "🪝 Setting up pre-commit hook..."
HOOK_FILE=".git/hooks/pre-commit"
if [ ! -f "$HOOK_FILE" ] || ! grep -q "yabai" "$HOOK_FILE" 2>/dev/null; then
    cat >> "$HOOK_FILE" << 'EOF'
#!/bin/bash
# Prevent committing yabai files
STAGED_YABAI=$(git diff --cached --name-only | grep -i "yabai" || true)
if [ -n "$STAGED_YABAI" ]; then
    echo "❌ Error: Attempting to commit yabai files!"
    echo ""
    echo "The following yabai files are staged:"
    echo "$STAGED_YABAI" | sed 's/^/  - /'
    echo ""
    echo "To unstage them:"
    echo "  git reset HEAD Work/yabai*.md"
    echo "  git reset HEAD .yabai-config/"
    echo ""
    exit 1
fi
EOF
    chmod +x "$HOOK_FILE"
    echo "✅ Pre-commit hook created"
else
    echo "✅ Pre-commit hook already exists"
fi

echo ""

# 4. Make helper scripts executable
echo "🔨 Making helper scripts executable..."
chmod +x "$PROJECT_DIR/scripts/stage_financial_api.sh"
chmod +x "$PROJECT_DIR/scripts/check_yabai.sh"
echo "✅ Scripts are executable"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Work in: cd 'Work/Financial Engineering API Demo'"
echo "  2. Stage files: ./scripts/stage_financial_api.sh"
echo "  3. Check safety: ./scripts/check_yabai.sh"
echo "  4. Commit: git commit -m 'your message'"
echo ""
echo "💡 The pre-commit hook will prevent committing yabai files automatically."

