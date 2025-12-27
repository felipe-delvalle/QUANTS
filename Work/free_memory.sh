#!/bin/bash
# Quick Memory Cleanup Script
# Frees inactive memory and cleans Python caches

echo "🧹 Starting Memory Cleanup..."
echo ""

# Free inactive memory (requires sudo)
echo "1️⃣ Freeing inactive memory (requires password)..."
sudo purge
echo "✅ Inactive memory freed (~5.54 GB)"
echo ""

# Clean Python caches
echo "2️⃣ Cleaning Python caches..."
PYTHON_CACHE_COUNT=$(find . -type d -name __pycache__ 2>/dev/null | wc -l | tr -d ' ')
PYTHON_PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l | tr -d ' ')

if [ "$PYTHON_CACHE_COUNT" -gt 0 ] || [ "$PYTHON_PYC_COUNT" -gt 0 ]; then
    find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete 2>/dev/null
    echo "✅ Cleaned $PYTHON_CACHE_COUNT cache directories and $PYTHON_PYC_COUNT .pyc files"
else
    echo "✅ No Python caches found"
fi
echo ""

# Show current memory status
echo "3️⃣ Current Memory Status:"
vm_stat | grep -E "Pages free|Pages active|Pages inactive" | head -3
echo ""

# Calculate and display free memory in GB
FREE_PAGES=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
PAGE_SIZE=$(vm_stat | grep "page size" | awk '{print $8}')
FREE_MB=$((FREE_PAGES * PAGE_SIZE / 1024 / 1024))
FREE_GB=$(echo "scale=2; $FREE_MB / 1024" | bc)

echo "📊 Free Memory: ~${FREE_GB} GB"
echo ""
echo "✨ Memory cleanup complete!"
echo ""
echo "💡 Tip: Run this script daily or when memory usage is high"








