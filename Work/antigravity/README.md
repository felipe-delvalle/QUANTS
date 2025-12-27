# Antigravity MCP Server on Google Cloud Run

A Model Context Protocol (MCP) server deployed on Google Cloud Run that provides gravitational force calculations and service status.

## 🚀 Features

- **MCP Server**: Full Model Context Protocol implementation
- **HTTP API**: RESTful endpoints for Cloud Run
- **Gravitational Calculations**: Calculate gravitational force between objects
- **Health Checks**: Built-in health monitoring
- **Cloud Native**: Optimized for Google Cloud Run

## 📋 Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and configured
- Docker (for local testing)
- Python 3.11+

## 🏗️ Architecture

```
┌─────────────────┐
│   Cloud Run     │
│                 │
│  ┌───────────┐  │
│  │   Flask   │  │ ← HTTP API
│  └───────────┘  │
│  ┌───────────┐  │
│  │ MCP Server│  │ ← MCP Protocol
│  └───────────┘  │
└─────────────────┘
```

## 🚀 Quick Deploy

### Option 1: Using Cloud Build (Recommended)

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Submit build
gcloud builds submit --config=cloudbuild.yaml
```

### Option 2: Manual Deployment

```bash
# Build and push image
gcloud builds submit --tag gcr.io/$PROJECT_ID/antigravity

# Deploy to Cloud Run
gcloud run deploy antigravity \
  --image gcr.io/$PROJECT_ID/antigravity \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080
```

## 🧪 Local Testing

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run HTTP server
python main.py

# Or run MCP server in stdio mode
MCP_MODE=stdio python main.py
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8080/

# Status
curl http://localhost:8080/status

# MCP endpoint
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'
```

## 📡 API Endpoints

### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "antigravity",
  "version": "1.0.0"
}
```

### `GET /status`
Service status endpoint

**Response:**
```json
{
  "status": "operational",
  "service": "antigravity",
  "version": "1.0.0",
  "platform": "google-cloud-run"
}
```

### `POST /mcp`
MCP protocol endpoint

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "calculate_gravity",
    "arguments": {
      "mass1": 1000,
      "mass2": 2000,
      "distance": 10
    }
  }
}
```

**Response:**
```json
{
  "result": {
    "content": [{
      "type": "text",
      "text": "Gravitational force: 1.33e-06 N"
    }]
  }
}
```

## 🔧 MCP Tools

### `calculate_gravity`
Calculate gravitational force between two objects.

**Parameters:**
- `mass1` (number): Mass of first object in kg
- `mass2` (number): Mass of second object in kg
- `distance` (number): Distance between objects in meters

**Example:**
```json
{
  "name": "calculate_gravity",
  "arguments": {
    "mass1": 5.972e24,
    "mass2": 7.348e22,
    "distance": 384400000
  }
}
```

### `antigravity_status`
Get the current status of the antigravity service.

## 📦 MCP Resources

- `antigravity://status` - Current service status
- `antigravity://config` - Service configuration

## 🔐 Environment Variables

- `PORT`: Server port (default: 8080)
- `MCP_MODE`: Server mode - `http` or `stdio` (default: `http`)
- `ENVIRONMENT`: Environment name (default: `production`)
- `REGION`: GCP region (default: `us-central1`)

## 📊 Monitoring

Cloud Run provides built-in monitoring:
- Request logs in Cloud Logging
- Metrics in Cloud Monitoring
- Health check endpoints

## 🔄 CI/CD

The `cloudbuild.yaml` file configures automatic deployment:
1. Builds Docker image
2. Pushes to Container Registry
3. Deploys to Cloud Run

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

