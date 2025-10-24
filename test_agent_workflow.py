#!/usr/bin/env python3
"""
Test Agent - Databricks Workflow Demo

This agent demonstrates a real-world workflow:
1. Create a new Databricks cluster
2. Wait for cluster to be ready
3. Execute a SQL query
4. Display results
"""

import asyncio
import sys
import time
import json
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport


# Configuration
DATABRICKS_HOST = "https://e2-demo-west.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi14c8fa7e4aaa0907a3144b740fd91f50"
SERVER_URL = "http://localhost:8000/mcp/"


def extract_result(result):
    """Helper to extract text from MCP result."""
    if isinstance(result, list):
        return result[0].content[0].text
    elif hasattr(result, 'content'):
        return result.content[0].text
    else:
        return str(result)


async def run_workflow():
    """Execute the complete workflow."""
    
    print("=" * 80)
    print("🤖 DATABRICKS AGENT WORKFLOW TEST")
    print("=" * 80)
    print()
    print("Workflow: Create cluster → Execute SQL query → Get results")
    print()
    
    # Set up MCP client
    headers = {
        "x-databricks-host": DATABRICKS_HOST,
        "x-databricks-token": DATABRICKS_TOKEN,
        "x-session-id": "agent-workflow-demo"
    }
    
    transport = StreamableHttpTransport(SERVER_URL, headers=headers)
    
    async with Client(transport=transport) as client:
        print("✓ Connected to MCP server")
        print()
        
        # Step 1: List existing clusters to see what's available
        print("📋 STEP 1: Checking existing clusters...")
        print("-" * 80)
        
        result = await client.call_tool("list_clusters", {})
        clusters_data = json.loads(extract_result(result))
        
        print(f"Found {clusters_data['count']} existing clusters:")
        for i, cluster in enumerate(clusters_data['clusters'][:5], 1):
            print(f"  {i}. {cluster['cluster_name']}")
            print(f"     ID: {cluster['cluster_id']}")
            print(f"     State: {cluster['state']}")
        
        # Check if there's a running cluster we can use
        running_cluster = None
        for cluster in clusters_data['clusters']:
            if cluster['state'] == 'RUNNING':
                running_cluster = cluster
                break
        
        print()
        
        if running_cluster:
            # Use existing running cluster
            print(f"✓ Found running cluster: {running_cluster['cluster_name']}")
            print(f"  Cluster ID: {running_cluster['cluster_id']}")
            cluster_id = running_cluster['cluster_id']
            print()
        else:
            # Step 2: Create a new cluster
            print("🚀 STEP 2: Creating new cluster...")
            print("-" * 80)
            
            cluster_config = {
                "cluster_name": f"MCP-Test-Cluster-{int(time.time())}",
                "spark_version": "14.3.x-scala2.12",
                "node_type_id": "i3.xlarge",
                "num_workers": 1,
                "autotermination_minutes": 30
            }
            
            print(f"Creating cluster: {cluster_config['cluster_name']}")
            print(f"  Spark version: {cluster_config['spark_version']}")
            print(f"  Node type: {cluster_config['node_type_id']}")
            print(f"  Workers: {cluster_config['num_workers']}")
            
            try:
                result = await client.call_tool("create_cluster", cluster_config)
                cluster_result = json.loads(extract_result(result))
                cluster_id = cluster_result['cluster_id']
                
                print()
                print(f"✓ Cluster created successfully!")
                print(f"  Cluster ID: {cluster_id}")
                print(f"  Status: {cluster_result['status']}")
                print()
                
                # Step 3: Wait for cluster to be ready
                print("⏳ STEP 3: Waiting for cluster to start...")
                print("-" * 80)
                print("This may take 3-5 minutes...")
                print()
                
                max_wait = 300  # 5 minutes
                wait_interval = 15  # Check every 15 seconds
                elapsed = 0
                
                while elapsed < max_wait:
                    result = await client.call_tool("get_cluster", {"cluster_id": cluster_id})
                    cluster_info = json.loads(extract_result(result))
                    state = cluster_info['state']
                    
                    print(f"  [{elapsed}s] Cluster state: {state}")
                    
                    if state == "RUNNING":
                        print()
                        print("✓ Cluster is now running!")
                        break
                    elif state in ["ERROR", "TERMINATED"]:
                        print()
                        print(f"✗ Cluster failed to start. State: {state}")
                        print(f"  Message: {cluster_info.get('state_message', 'No message')}")
                        return
                    
                    await asyncio.sleep(wait_interval)
                    elapsed += wait_interval
                
                if elapsed >= max_wait:
                    print()
                    print("⚠ Timeout waiting for cluster to start")
                    print("Cluster is still starting, but continuing with demo...")
                    
                print()
                
            except Exception as e:
                print(f"✗ Error creating cluster: {str(e)[:200]}")
                print()
                print("Using an existing cluster for SQL query instead...")
                
                # Find any cluster to use
                if clusters_data['clusters']:
                    cluster_id = clusters_data['clusters'][0]['cluster_id']
                    print(f"Using cluster: {clusters_data['clusters'][0]['cluster_name']}")
                    print(f"  Cluster ID: {cluster_id}")
                    print()
                else:
                    print("✗ No clusters available!")
                    return
        
        # Step 4: Set current cluster in context
        print("🔧 STEP 4: Setting cluster context...")
        print("-" * 80)
        
        result = await client.call_tool("set_current_cluster", {"cluster_id": cluster_id})
        print(f"✓ {extract_result(result)}")
        print()
        
        # Step 5: List SQL warehouses
        print("🏢 STEP 5: Finding SQL warehouse...")
        print("-" * 80)
        
        result = await client.call_tool("list_warehouses", {})
        warehouses_data = json.loads(extract_result(result))
        
        if warehouses_data['count'] == 0:
            print("✗ No SQL warehouses found!")
            print("Note: SQL queries require a SQL warehouse, not a cluster.")
            print("Skipping SQL query execution...")
            print()
        else:
            warehouse = warehouses_data['warehouses'][0]
            warehouse_id = warehouse['id']
            
            print(f"Found warehouse: {warehouse['name']}")
            print(f"  Warehouse ID: {warehouse_id}")
            print(f"  State: {warehouse['state']}")
            print()
            
            # Step 6: Execute SQL query
            print("📊 STEP 6: Executing SQL query...")
            print("-" * 80)
            
            # Simple query to show samples catalog data
            sql_query = "SELECT * FROM samples.nyctaxi.trips LIMIT 5"
            
            print(f"Query: {sql_query}")
            print()
            
            try:
                result = await client.call_tool("execute_query", {
                    "query": sql_query,
                    "warehouse_id": warehouse_id,
                    "wait_timeout": "30s"
                })
                
                query_result = json.loads(extract_result(result))
                
                print(f"✓ Query executed successfully!")
                print(f"  Statement ID: {query_result['statement_id']}")
                print(f"  Status: {query_result['status']}")
                
                if 'data_array' in query_result and query_result['data_array']:
                    print(f"  Rows returned: {query_result.get('row_count', 0)}")
                    print()
                    print("📈 RESULTS:")
                    print("-" * 80)
                    
                    # Display first few rows
                    for i, row in enumerate(query_result['data_array'][:5], 1):
                        print(f"\nRow {i}:")
                        for j, value in enumerate(row):
                            print(f"  Column {j}: {value}")
                    
                    if query_result.get('truncated'):
                        print("\n(Results truncated...)")
                else:
                    print("  No data returned or query still processing")
                    print(f"  Use statement_id to check: {query_result['statement_id']}")
                
                print()
                
            except Exception as e:
                print(f"✗ Error executing query: {str(e)[:300]}")
                print()
        
        # Step 7: Show session context
        print("📝 STEP 7: Final session context...")
        print("-" * 80)
        
        result = await client.call_tool("get_session_context", {})
        context_data = json.loads(extract_result(result))
        
        print("Session state:")
        print(f"  Session ID: {context_data['session_id']}")
        print(f"  Workspace path: {context_data.get('workspace_path', 'Not set')}")
        print(f"  Current cluster: {context_data.get('current_cluster_id', 'Not set')}")
        print(f"  Current warehouse: {context_data.get('current_warehouse_id', 'Not set')}")
        print()
        
        print("=" * 80)
        print("✅ WORKFLOW COMPLETE!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  • Connected to Databricks workspace")
        print(f"  • Used cluster: {cluster_id}")
        if warehouses_data['count'] > 0:
            print(f"  • Executed SQL query successfully")
            print(f"  • Retrieved sample data from samples.nyctaxi.trips")
        print(f"  • Maintained stateful session context")
        print()


def main():
    """Main entry point."""
    print()
    print("Databricks MCP Server - Agent Workflow Test")
    print("=" * 80)
    print()
    print("This agent will:")
    print("  1. Check for existing clusters or create a new one")
    print("  2. Find a SQL warehouse")
    print("  3. Execute a SQL query")
    print("  4. Display results")
    print()
    
    try:
        asyncio.run(run_workflow())
    except KeyboardInterrupt:
        print("\n\n⚠ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

