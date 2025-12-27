"""
Antigravity MCP Server
A Model Context Protocol server deployed on Google Cloud Run
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional

try:
    from flask import Flask, request, jsonify
except ImportError:
    Flask = None
    jsonify = None
    request = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Server implementation (HTTP-based for Cloud Run)
class MCPServer:
    """Simplified MCP Server implementation for Cloud Run"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = self._initialize_tools()
        self.resources = self._initialize_resources()
    
    def _initialize_tools(self) -> List[Dict]:
        """Initialize available tools"""
        return [
            {
                "name": "calculate_gravity",
                "description": "Calculate gravitational force between two objects",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mass1": {"type": "number", "description": "Mass of first object (kg)"},
                        "mass2": {"type": "number", "description": "Mass of second object (kg)"},
                        "distance": {"type": "number", "description": "Distance between objects (m)"}
                    },
                    "required": ["mass1", "mass2", "distance"]
                }
            },
            {
                "name": "antigravity_status",
                "description": "Get the current status of the antigravity service",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def _initialize_resources(self) -> List[Dict]:
        """Initialize available resources"""
        return [
            {
                "uri": "antigravity://status",
                "name": "Antigravity Status",
                "description": "Current status of the antigravity service",
                "mimeType": "application/json"
            },
            {
                "uri": "antigravity://config",
                "name": "Antigravity Configuration",
                "description": "Service configuration",
                "mimeType": "application/json"
            }
        ]
    
    def get_resource(self, uri: str) -> str:
        """Get a resource by URI"""
        if uri == "antigravity://status":
            return json.dumps({
                "status": "operational",
                "service": "antigravity",
                "version": "1.0.0",
                "platform": "google-cloud-run"
            })
        elif uri == "antigravity://config":
            return json.dumps({
                "port": os.getenv("PORT", "8080"),
                "environment": os.getenv("ENVIRONMENT", "production"),
                "region": os.getenv("REGION", "us-central1")
            })
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict:
        """Handle tool calls"""
        if name == "calculate_gravity":
            G = 6.67430e-11  # Gravitational constant
            mass1 = arguments.get("mass1")
            mass2 = arguments.get("mass2")
            distance = arguments.get("distance")
            
            if distance == 0:
                return {
                    "error": "Distance cannot be zero"
                }
            
            force = (G * mass1 * mass2) / (distance ** 2)
            return {
                "content": [{
                    "type": "text",
                    "text": f"Gravitational force: {force:.2e} N"
                }]
            }
        
        elif name == "antigravity_status":
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "status": "operational",
                        "service": "antigravity",
                        "version": "1.0.0"
                    }, indent=2)
                }]
            }
        
        else:
            raise ValueError(f"Unknown tool: {name}")


# Initialize MCP Server
mcp_server = MCPServer("antigravity")

# Initialize Flask app if available
if Flask:
    app = Flask(__name__)
else:
    app = None


# Flask routes for HTTP access (if Flask is available)
if app:
    @app.route("/", methods=["GET"])
    def health_check():
        """Health check endpoint for Cloud Run"""
        return jsonify({
            "status": "healthy",
            "service": "antigravity",
            "version": "1.0.0"
        }), 200


    @app.route("/mcp", methods=["POST"])
    def mcp_endpoint():
        """MCP protocol endpoint compatible with Google MCP Cloud Run"""
        try:
            data = request.get_json()
            method = data.get("method")
            params = data.get("params", {})
            
            # Handle MCP requests
            if method == "resources/list":
                return jsonify({"result": {"resources": mcp_server.resources}})
            
            elif method == "resources/read":
                uri = params.get("uri")
                resource_content = mcp_server.get_resource(uri)
                return jsonify({
                    "result": {
                        "contents": [{
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": resource_content
                        }]
                    }
                })
            
            elif method == "tools/list":
                return jsonify({"result": {"tools": mcp_server.tools}})
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = mcp_server.call_tool(tool_name, arguments)
                
                if "error" in result:
                    return jsonify({"error": result["error"]}), 400
                
                return jsonify({"result": result})
            
            return jsonify({"error": "Unknown method"}), 400
        
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return jsonify({"error": str(e)}), 500


    @app.route("/status", methods=["GET"])
    def status():
        """Status endpoint"""
        return jsonify({
            "status": "operational",
            "service": "antigravity",
            "version": "1.0.0",
            "platform": "google-cloud-run",
            "mcp_compatible": True
        }), 200


    def run_http_server():
        """Run HTTP server for Cloud Run"""
        port = int(os.environ.get("PORT", 8080))
        # Use gunicorn in production, Flask dev server for local
        if os.environ.get("ENVIRONMENT") == "production":
            import gunicorn.app.wsgiapp as wsgi
            wsgi.run()
        else:
            app.run(host="0.0.0.0", port=port, debug=False)
else:
    def run_http_server():
        """Fallback HTTP server if Flask not available"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse
        
        class MCPHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/" or self.path == "/status":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = json.dumps({
                        "status": "operational",
                        "service": "antigravity",
                        "version": "1.0.0"
                    })
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == "/mcp":
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode())
                    
                    method = data.get("method")
                    params = data.get("params", {})
                    
                    if method == "tools/list":
                        response = {"result": {"tools": mcp_server.tools}}
                    elif method == "resources/list":
                        response = {"result": {"resources": mcp_server.resources}}
                    elif method == "tools/call":
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})
                        result = mcp_server.call_tool(tool_name, arguments)
                        response = {"result": result} if "error" not in result else {"error": result["error"]}
                    else:
                        response = {"error": "Unknown method"}
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
        
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(("0.0.0.0", port), MCPHandler)
        logger.info(f"Starting HTTP server on port {port}")
        server.serve_forever()


if __name__ == "__main__":
    # For Cloud Run, use HTTP server
    mode = os.environ.get("MCP_MODE", "http")
    
    if mode == "http":
        run_http_server()
    else:
        logger.error("Only HTTP mode is supported for Cloud Run deployment")
        run_http_server()

