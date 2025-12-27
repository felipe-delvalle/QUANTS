#!/usr/bin/env python3
"""
Local testing script for Antigravity MCP Server
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8080"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")
    return True

def test_status():
    """Test status endpoint"""
    print("Testing status endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    print("✓ Status check passed")
    return True

def test_mcp_tools_list():
    """Test MCP tools/list"""
    print("Testing MCP tools/list...")
    response = requests.post(
        f"{BASE_URL}/mcp",
        json={
            "method": "tools/list",
            "params": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) > 0
    print(f"✓ Found {len(data['result']['tools'])} tools")
    return True

def test_mcp_resources_list():
    """Test MCP resources/list"""
    print("Testing MCP resources/list...")
    response = requests.post(
        f"{BASE_URL}/mcp",
        json={
            "method": "resources/list",
            "params": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "resources" in data["result"]
    print(f"✓ Found {len(data['result']['resources'])} resources")
    return True

def test_calculate_gravity():
    """Test calculate_gravity tool"""
    print("Testing calculate_gravity tool...")
    response = requests.post(
        f"{BASE_URL}/mcp",
        json={
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
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]
    print(f"✓ Result: {data['result']['content'][0]['text']}")
    return True

def test_antigravity_status():
    """Test antigravity_status tool"""
    print("Testing antigravity_status tool...")
    response = requests.post(
        f"{BASE_URL}/mcp",
        json={
            "method": "tools/call",
            "params": {
                "name": "antigravity_status",
                "arguments": {}
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    print("✓ Status tool working")
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("Antigravity MCP Server - Local Tests")
    print("=" * 50)
    print()
    
    try:
        test_health_check()
        test_status()
        test_mcp_tools_list()
        test_mcp_resources_list()
        test_calculate_gravity()
        test_antigravity_status()
        
        print()
        print("=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0
    
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to server")
        print("  Make sure the server is running: python main.py")
        return 1
    
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

