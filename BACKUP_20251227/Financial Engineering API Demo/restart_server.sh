#!/bin/bash
# FastAPI Server Restart Script
# Quickly restart the FastAPI server without auto-reload

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Full path to project directory
PROJECT_DIR="/Users/freedom/QUANTS/Work/Financial Engineering API Demo"
cd "$PROJECT_DIR" || {
    echo -e "${RED}Error: Cannot access project directory: $PROJECT_DIR${NC}"
    exit 1
}

# Check if venv exists
VENV_PATH="$PROJECT_DIR/venv"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
    echo -e "${YELLOW}Run ./build.sh first${NC}"
    exit 1
fi

# Activate venv
source "$VENV_PATH/bin/activate"

# Find and kill existing uvicorn processes
echo -e "${YELLOW}Stopping existing server...${NC}"
pkill -f "uvicorn api_service:app" || echo "No existing server found"

# Wait a moment for process to fully terminate
sleep 1

# Start server (auto-reload disabled to avoid restarts on code changes)
echo -e "${GREEN}Starting FastAPI server on http://127.0.0.1:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo -e "${YELLOW}Working directory: $PROJECT_DIR${NC}"
echo ""

# Start uvicorn without auto-reload
uvicorn api_service:app --host 127.0.0.1 --port 8000

