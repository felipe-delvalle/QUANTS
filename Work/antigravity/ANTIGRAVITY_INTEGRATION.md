# Google Antigravity + Google MCP Cloud Run Integration

This guide explains how to integrate the Antigravity MCP server with Google Antigravity IDE and Google MCP Cloud Run.

## Overview

The Antigravity service is an MCP (Model Context Protocol) server that can be:
1. **Deployed to Google Cloud Run** - Accessible via HTTP
2. **Integrated with Google Antigravity IDE** - AI agents can use MCP tools
3. **Connected to Google MCP Cloud Run** - For deployment automation

## Architecture

```
┌─────────────────────┐
│ Google Antigravity  │
│       IDE           │
│                     │
│  AI Agents          │──┐
└─────────────────────┘  │
                         │ MCP Protocol
                         │ (HTTP/JSON)
                         │
┌─────────────────────┐  │
│  Antigravity MCP    │◄─┘
│  Server (Cloud Run) │
│                     │
│  - calculate_gravity│
│  - antigravity_status│
└─────────────────────┘
```

## Deployment Steps

### 1. Deploy to Google Cloud Run

```bash
cd Work/antigravity
./deploy.sh
```

Or manually:

```bash
# Set your project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Build and deploy
gcloud builds submit --config=cloudbuild.yaml
```

### 2. Get Service URL

```bash
SERVICE_URL=$(gcloud run services describe antigravity \
  --region=us-central1 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"
```

### 3. Configure Google Antigravity

In Google Antigravity IDE, add the MCP server configuration:

**Option A: Via Settings**
1. Open Antigravity Settings
2. Navigate to MCP Servers
3. Add new server:
   - **Name**: `antigravity-cloud-run`
   - **Type**: `HTTP`
   - **URL**: `https://your-service-url.run.app/mcp`
   - **Authentication**: None (or configure as needed)

**Option B: Via Configuration File**

Create or edit `~/.antigravity/mcp-servers.json`:

```json
{
  "servers": {
    "antigravity-cloud-run": {
      "type": "http",
      "url": "https://your-service-url.run.app/mcp",
      "description": "Antigravity MCP Server on Cloud Run"
    }
  }
}
```

## Testing the Integration

### Test from Command Line

```bash
# Health check
curl https://your-service-url.run.app/

# Test MCP endpoint
curl -X POST https://your-service-url.run.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'

# Test tool call
curl -X POST https://your-service-url.run.app/mcp \
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

### Test in Google Antigravity

1. Open Antigravity IDE
2. In the chat/agent interface, try:
   - "Use the antigravity service to calculate gravitational force between two objects"
   - "Check the status of the antigravity service"
3. The AI agent should automatically use the MCP tools

## Available MCP Tools

### `calculate_gravity`
Calculate gravitational force between two objects.

**Usage in Antigravity:**
```
Calculate the gravitational force between a 1000kg and 2000kg object 
that are 10 meters apart using the antigravity service.
```

### `antigravity_status`
Get the current status of the antigravity service.

**Usage in Antigravity:**
```
Check the status of the antigravity MCP server.
```

## Available MCP Resources

- `antigravity://status` - Service status information
- `antigravity://config` - Service configuration

## Integration with Google MCP Cloud Run

To use this service with Google's MCP Cloud Run server for deployment automation:

1. **Install Google MCP Cloud Run** (if not already installed):
   ```bash
   npm install -g @google-cloud/cloud-run-mcp
   ```

2. **Configure MCP Cloud Run** to use this service:
   ```json
   {
     "mcpServers": {
       "antigravity": {
         "url": "https://your-service-url.run.app/mcp"
       }
     }
   }
   ```

3. **Use in Antigravity**:
   - AI agents can now use both deployment tools (from MCP Cloud Run) and calculation tools (from this service)
   - Example: "Deploy a new service and calculate its resource requirements using gravitational force calculations"

## Security Considerations

1. **Authentication**: Consider adding authentication for production:
   - API keys
   - OAuth 2.0
   - Service account authentication

2. **Rate Limiting**: Implement rate limiting to prevent abuse

3. **CORS**: Configure CORS if accessing from web applications

4. **HTTPS**: Always use HTTPS in production (Cloud Run provides this by default)

## Troubleshooting

### Service Not Accessible
- Check Cloud Run service status: `gcloud run services describe antigravity --region=us-central1`
- Verify service URL is correct
- Check Cloud Run logs: `gcloud run services logs read antigravity --region=us-central1`

### MCP Connection Issues
- Verify the `/mcp` endpoint is accessible
- Check that requests use `Content-Type: application/json`
- Review service logs for errors

### Tool Not Found
- Verify tools are listed: `curl -X POST $SERVICE_URL/mcp -d '{"method":"tools/list","params":{}}'`
- Check tool name spelling in requests

## Next Steps

1. **Add More Tools**: Extend the service with additional calculation tools
2. **Add Authentication**: Implement API key or OAuth authentication
3. **Add Monitoring**: Set up Cloud Monitoring alerts
4. **Add Caching**: Implement response caching for frequently used calculations
5. **Add Webhooks**: Support webhook notifications for tool executions

## Resources

- [Google Antigravity Documentation](https://antigravityai.org/)
- [Google MCP Cloud Run GitHub](https://github.com/GoogleCloudPlatform/cloud-run-mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)

