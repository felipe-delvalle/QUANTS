# 🚀 FastAPI Server Management

Quick commands to manage your FastAPI server.

## Quick Restart (Recommended)

```bash
cd "Financial Engineering API Demo"
./restart_server.sh
```

This will:
- ✅ Stop any existing server
- ✅ Start server with **auto-reload** enabled
- ✅ Server runs on http://127.0.0.1:8000
- ✅ Automatically restarts when you change code files

**Press `Ctrl+C` to stop the server**

## Background Restart

To start the server in the background (non-blocking):

```bash
./restart.sh
```

Server will run in background. Check logs with:
```bash
tail -f server.log
```

## Stop Server

```bash
./stop_server.sh
```

## Manual Commands

If you prefer manual control:

```bash
# Activate venv
source venv/bin/activate

# Stop existing server
pkill -f "uvicorn api_service:app"

# Start with auto-reload (interactive)
uvicorn api_service:app --host 127.0.0.1 --port 8000 --reload

# Or start in background
nohup uvicorn api_service:app --host 127.0.0.1 --port 8000 --reload > server.log 2>&1 &
```

## Auto-Reload Feature

When using `--reload` flag:
- ✅ Server automatically restarts when Python files change
- ✅ No need to manually restart after code changes
- ✅ Perfect for development

## Troubleshooting

**Port already in use?**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

**Server not starting?**
```bash
# Check if venv is activated
which python  # Should show venv path

# Install missing dependencies
pip install -r requirements.txt
```

