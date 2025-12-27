#!/bin/bash
# Stop FastAPI Server

PROJECT_DIR="/Users/freedom/QUANTS/Work/Financial Engineering API Demo"
cd "$PROJECT_DIR" 2>/dev/null || true

pkill -f "uvicorn api_service:app" && echo "Server stopped" || echo "No server running"

