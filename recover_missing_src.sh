#!/bin/bash

# Recover missing src files from commit d733820

cd "/Users/freedom/QUANTS/Work/Financial Engineering API Demo"

COMMIT="d733820"

echo "=== Recovering missing src files from commit $COMMIT ==="
echo ""

# List all files in src directory from that commit
echo "Files in src/ from commit $COMMIT:"
git ls-tree -r --name-only $COMMIT | grep "^src/" | sort
echo ""

# Recover missing directories and files
echo "Recovering src files..."

# Recover config.py
if git ls-tree -r --name-only $COMMIT | grep -q "^src/config.py"; then
    echo "Recovering src/config.py..."
    git checkout $COMMIT -- src/config.py
else
    echo "src/config.py not found in commit"
fi

# Recover data directory
if git ls-tree -r --name-only $COMMIT | grep -q "^src/data/"; then
    echo "Recovering src/data/ directory..."
    git checkout $COMMIT -- src/data/
else
    echo "src/data/ not found in commit"
fi

# Recover trading directory
if git ls-tree -r --name-only $COMMIT | grep -q "^src/trading/"; then
    echo "Recovering src/trading/ directory..."
    git checkout $COMMIT -- src/trading/
else
    echo "src/trading/ not found in commit"
fi

# Recover backtesting
if git ls-tree -r --name-only $COMMIT | grep -q "^src/backtesting"; then
    echo "Recovering src/backtesting..."
    git checkout $COMMIT -- src/backtesting.py 2>/dev/null || git checkout $COMMIT -- src/backtesting/
else
    echo "src/backtesting not found in commit"
fi

# Recover analysis updates
if git ls-tree -r --name-only $COMMIT | grep -q "^src/analysis/"; then
    echo "Recovering src/analysis/ updates..."
    git checkout $COMMIT -- src/analysis/advanced_indicators.py 2>/dev/null
    git checkout $COMMIT -- src/analysis/__init__.py 2>/dev/null
    # Check for other analysis files
    git ls-tree -r --name-only $COMMIT | grep "^src/analysis/" | while read file; do
        if [ ! -f "$file" ]; then
            echo "Recovering $file..."
            git checkout $COMMIT -- "$file"
        fi
    done
fi

# Recover utils if needed
if git ls-tree -r --name-only $COMMIT | grep -q "^src/utils/"; then
    echo "Recovering src/utils/ directory..."
    git checkout $COMMIT -- src/utils/
fi

echo ""
echo "=== Recovery complete ==="
echo ""
echo "Recovered files:"
git status --short src/ | head -20
