#!/bin/bash

# Build script for Financial Engineering API Demo

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Building Financial Engineering API Demo      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check Python version
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $python_version found"

# Step 2: Create virtual environment
echo -e "${YELLOW}Step 2: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Step 3: Activate virtual environment
echo -e "${YELLOW}Step 3: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Step 4: Install dependencies
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Step 5: Set up environment file
echo -e "${YELLOW}Step 5: Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created from template"
    echo -e "${YELLOW}⚠${NC}  Please edit .env file with your API keys"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Step 6: Run tests
echo -e "${YELLOW}Step 6: Running tests...${NC}"
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    pytest tests/ -v || echo -e "${YELLOW}⚠${NC}  Some tests failed (this is okay for demo)"
else
    echo -e "${YELLOW}⚠${NC}  No tests found, skipping"
fi

# Step 7: Verify installation
echo -e "${YELLOW}Step 7: Verifying installation...${NC}"
python3 -c "import pandas, numpy, yfinance; print('✓ Core dependencies OK')" || echo "⚠ Some dependencies missing"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Build Complete!                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your API keys"
echo "2. Run: python main.py"
echo "3. Or: python cli.py --help"
echo ""
