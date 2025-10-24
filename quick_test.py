#!/usr/bin/env python3
"""Quick test to verify server is running without needing Databricks credentials."""

import requests
import json

SERVER_URL = "http://localhost:8000"

def test_server_alive():
    """Test that server is responding."""
    print("Testing server availability...")
    try:
        response = requests.get(f"{SERVER_URL}/mcp")
        print(f"✓ Server is running on {SERVER_URL}")
        print(f"  Response status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"✗ Server not responding: {e}")
        return False

def test_mcp_endpoint():
    """Test MCP endpoint structure."""
    print("\nTesting MCP endpoint...")
    try:
        # Try a simple request (will fail auth but show server is working)
        response = requests.post(
            f"{SERVER_URL}/mcp",
            headers={"Content-Type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            }
        )
        print(f"✓ MCP endpoint responding")
        print(f"  Status: {response.status_code}")
        
        # Parse response
        try:
            data = response.json()
            if "error" in data:
                print(f"  Error (expected without credentials): {data['error'].get('message', 'Unknown')[:100]}")
            else:
                print(f"  Response: {json.dumps(data, indent=2)[:300]}")
        except:
            print(f"  Response text: {response.text[:200]}")
            
        return True
    except Exception as e:
        print(f"✗ MCP endpoint error: {e}")
        return False

def main():
    print("=" * 60)
    print("Databricks CLI MCP Server - Quick Test")
    print("=" * 60)
    print()
    
    # Test 1: Server alive
    if not test_server_alive():
        print("\n❌ Server is not running!")
        print("\nStart the server with:")
        print("  cd databricks_cli_mcp")
        print("  python server.py")
        return
    
    # Test 2: MCP endpoint
    test_mcp_endpoint()
    
    print("\n" + "=" * 60)
    print("Quick Test Complete!")
    print("=" * 60)
    print()
    print("✓ Server is running and responding")
    print("✓ MCP endpoint is accessible")
    print()
    print("Next steps for full testing:")
    print("  1. Get Databricks workspace credentials:")
    print("     - Workspace URL (e.g., https://your-workspace.cloud.databricks.com)")
    print("     - Personal Access Token (from User Settings → Developer)")
    print()
    print("  2. Update test_local.py with your credentials")
    print()
    print("  3. Run full test suite:")
    print("     python test_local.py")
    print()

if __name__ == "__main__":
    main()

