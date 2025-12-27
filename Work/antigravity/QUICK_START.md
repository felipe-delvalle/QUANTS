# Quick Start - Antigravity MCP Server

## 🚀 Deploy in 3 Steps

### 1. Set Your Google Cloud Project

```bash
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID
```

### 2. Deploy to Cloud Run

```bash
cd Work/antigravity
./deploy.sh
```

Or manually:

```bash
gcloud builds submit --config=cloudbuild.yaml
```

### 3. Get Service URL

```bash
gcloud run services describe antigravity \
  --region=us-central1 \
  --format='value(status.url)'
```

## 🧪 Test Locally First

### Start Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

### Run Tests

In another terminal:

```bash
python test_local.py
```

## 📡 Test the Deployed Service

```bash
# Set your service URL
SERVICE_URL=https://antigravity-xxxxx.run.app

# Health check
curl $SERVICE_URL/

# List tools
curl -X POST $SERVICE_URL/mcp \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/list","params":{}}'

# Calculate gravity
curl -X POST $SERVICE_URL/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "calculate_gravity",
      "arguments": {
        "mass1": 1000,
        "mass2": 2000,
        "distance": 10
      }
    }
  }'
```

## 🔗 Integrate with Google Antigravity

1. Get your service URL from step 3 above
2. In Antigravity IDE, add MCP server:
   - URL: `https://your-service-url.run.app/mcp`
   - Type: HTTP
3. Test in Antigravity chat:
   - "Calculate gravitational force between 1000kg and 2000kg objects 10m apart"

## 📚 More Information

- Full documentation: [README.md](README.md)
- Integration guide: [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md)

