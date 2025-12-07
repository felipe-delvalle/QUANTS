#!/bin/bash
# Safe RAM and Cache Cleanup Script for macOS
# This script safely cleans up caches and frees memory

set -e  # Exit on error

echo "🧹 Starting Safe Cache Cleanup..."
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to calculate directory size
get_size() {
    if [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        echo "0B"
    fi
}

# 1. Clean Python cache files
echo -e "${BLUE}1. Cleaning Python cache files...${NC}"
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l | tr -d ' ')

if [ "$PYCACHE_COUNT" -gt 0 ] || [ "$PYC_COUNT" -gt 0 ]; then
    echo "   Found $PYCACHE_COUNT __pycache__ directories and $PYC_COUNT .pyc files"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    echo -e "   ${GREEN}✓ Python cache cleaned${NC}"
else
    echo "   No Python cache files found"
fi
echo ""

# 2. Clean .DS_Store files
echo -e "${BLUE}2. Cleaning .DS_Store files...${NC}"
DSSTORE_COUNT=$(find . -name ".DS_Store" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DSSTORE_COUNT" -gt 0 ]; then
    echo "   Found $DSSTORE_COUNT .DS_Store files"
    find . -name ".DS_Store" -delete 2>/dev/null || true
    echo -e "   ${GREEN}✓ .DS_Store files removed${NC}"
else
    echo "   No .DS_Store files found"
fi
echo ""

# 3. Clean user cache (safe - only caches, not data)
echo -e "${BLUE}3. Cleaning user caches...${NC}"
USER_CACHE_DIR="$HOME/Library/Caches"
if [ -d "$USER_CACHE_DIR" ]; then
    # Clean common safe caches
    CACHE_SIZE_BEFORE=$(du -sh "$USER_CACHE_DIR" 2>/dev/null | cut -f1 || echo "0B")
    echo "   User cache size before: $CACHE_SIZE_BEFORE"
    
    # Clean specific safe caches (not touching important data)
    rm -rf ~/Library/Caches/com.apple.dt.Xcode/* 2>/dev/null || true
    rm -rf ~/Library/Caches/Homebrew/* 2>/dev/null || true
    rm -rf ~/Library/Caches/pip/* 2>/dev/null || true
    
    echo -e "   ${GREEN}✓ User caches cleaned${NC}"
else
    echo "   User cache directory not found"
fi
echo ""

# 4. Clean pip cache
echo -e "${BLUE}4. Cleaning pip cache...${NC}"
if command -v pip &> /dev/null; then
    PIP_CACHE_SIZE=$(pip cache info 2>/dev/null | grep "Cache size:" | awk '{print $3}' || echo "0B")
    if [ "$PIP_CACHE_SIZE" != "0B" ] && [ -n "$PIP_CACHE_SIZE" ]; then
        echo "   Pip cache size: $PIP_CACHE_SIZE"
        pip cache purge 2>/dev/null || true
        echo -e "   ${GREEN}✓ Pip cache purged${NC}"
    else
        echo "   No pip cache found"
    fi
else
    echo "   Pip not found, skipping"
fi
echo ""

# 5. Clean LaTeX build artifacts (optional - keeping PDFs)
echo -e "${BLUE}5. Cleaning LaTeX build artifacts...${NC}"
LATEX_DIR="Work/LaTeX Papers/paper_output"
if [ -d "$LATEX_DIR" ]; then
    # Remove auxiliary files but keep PDFs
    find "$LATEX_DIR" -type f \( -name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.toc" -o -name "*.fdb_latexmk" -o -name "*.fls" -o -name "*.synctex.gz" \) -delete 2>/dev/null || true
    echo -e "   ${GREEN}✓ LaTeX auxiliary files cleaned (PDFs preserved)${NC}"
else
    echo "   LaTeX output directory not found"
fi
echo ""

# 6. Purge memory (macOS specific - safe)
echo -e "${BLUE}6. Purging memory...${NC}"
if [ "$(uname)" == "Darwin" ]; then
    # Show memory before
    echo "   Memory before purge:"
    FREE_BEFORE=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    INACTIVE_BEFORE=$(vm_stat | grep "Pages inactive" | awk '{print $3}' | sed 's/\.//')
    echo "     Free: $(echo "$FREE_BEFORE * 16384 / 1024 / 1024 / 1024" | bc 2>/dev/null | xargs printf "%.2f") GB"
    echo "     Inactive: $(echo "$INACTIVE_BEFORE * 16384 / 1024 / 1024 / 1024" | bc 2>/dev/null | xargs printf "%.2f") GB"
    
    # Try to purge (will prompt for password)
    echo ""
    echo "   Attempting to purge inactive memory..."
    echo "   (If prompted, enter your password)"
    
    if sudo -n purge 2>/dev/null; then
        # Passwordless sudo worked
        echo -e "   ${GREEN}✓ Memory purged${NC}"
    else
        # Need password - provide instructions
        echo -e "   ${YELLOW}⚠ Password required for memory purge${NC}"
        echo ""
        echo "   To complete RAM cleanup, run:"
        echo -e "   ${BLUE}   sudo purge${NC}"
        echo ""
        echo "   Or run the full cleanup with:"
        echo -e "   ${BLUE}   bash Work/purge_memory.sh${NC}"
    fi
else
    echo "   Not macOS, skipping memory purge"
fi
echo ""

# 7. Clean npm cache (if exists)
echo -e "${BLUE}7. Cleaning npm cache...${NC}"
if command -v npm &> /dev/null; then
    npm cache verify 2>/dev/null || true
    echo -e "   ${GREEN}✓ npm cache verified${NC}"
else
    echo "   npm not found, skipping"
fi
echo ""

# 8. Summary
echo "=================================="
echo -e "${GREEN}✨ Cleanup Complete!${NC}"
echo ""
echo "Summary:"
echo "  • Python cache files: Cleaned"
echo "  • .DS_Store files: Cleaned"
echo "  • User caches: Cleaned"
echo "  • Pip cache: Cleaned"
echo "  • LaTeX artifacts: Cleaned (PDFs preserved)"
echo ""
echo "To free more RAM, you can also:"
echo "  • Close unused applications"
echo "  • Restart your Mac (most effective)"
echo "  • Check Activity Monitor for memory-heavy processes"
echo ""

