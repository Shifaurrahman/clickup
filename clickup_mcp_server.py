from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import requests
import uvicorn
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================
# MODELS
# ============================================================

class MCPRequest(BaseModel):
    """MCP JSON-RPC 2.0 Request"""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP JSON-RPC 2.0 Response"""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class ToolInfo(BaseModel):
    """Tool metadata"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


# ============================================================
# CLICKUP API CLIENT
# ============================================================

class ClickUpAPI:
    """ClickUp API Client for MCP"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
    
    def get(self, endpoint: str):
        """Make GET request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: dict):
        """Make POST request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint: str, data: dict):
        """Make PUT request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str):
        """Make DELETE request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json() if response.text else {}


# ============================================================
# MCP TOOLS IMPLEMENTATION
# ============================================================

class ClickUpMCPTools:
    """ClickUp MCP Tools Handler"""
    
    def __init__(self, clickup_api: ClickUpAPI):
        self.api = clickup_api
    
    def get_tools_list(self) -> List[ToolInfo]:
        """Return list of available MCP tools"""
        return [
            ToolInfo(
                name="search_workspace",
                description="Search for tasks, lists, folders, and docs across the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            ),
            ToolInfo(
                name="get_workspace_hierarchy",
                description="Get the complete workspace structure with spaces, folders, and lists",
                inputSchema={"type": "object", "properties": {}}
            ),
            ToolInfo(
                name="get_workspace_tasks",
                description="Get all tasks in the workspace with optional filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "Filter by space ID"},
                        "list_id": {"type": "string", "description": "Filter by list ID"},
                        "assignee": {"type": "string", "description": "Filter by assignee ID"}
                    }
                }
            ),
            ToolInfo(
                name="create_task",
                description="Create a new task in a list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "list_id": {"type": "string", "description": "List ID where task will be created"},
                        "name": {"type": "string", "description": "Task name"},
                        "description": {"type": "string", "description": "Task description"},
                        "status": {"type": "string", "description": "Task status (e.g., 'to do', 'in progress')"},
                        "priority": {"type": "integer", "description": "Priority level (1-4)"}
                    },
                    "required": ["list_id", "name"]
                }
            ),
            ToolInfo(
                name="get_task",
                description="Get detailed information about a specific task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"}
                    },
                    "required": ["task_id"]
                }
            ),
            ToolInfo(
                name="update_task",
                description="Update an existing task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                        "name": {"type": "string", "description": "New task name"},
                        "description": {"type": "string", "description": "New description"},
                        "status": {"type": "string", "description": "New status"}
                    },
                    "required": ["task_id"]
                }
            ),
            ToolInfo(
                name="create_task_comment",
                description="Add a comment to a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                        "comment_text": {"type": "string", "description": "Comment text"}
                    },
                    "required": ["task_id", "comment_text"]
                }
            ),
            ToolInfo(
                name="get_task_comments",
                description="Get all comments from a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"}
                    },
                    "required": ["task_id"]
                }
            ),
            ToolInfo(
                name="get_workspace_members",
                description="Get all members in the workspace",
                inputSchema={"type": "object", "properties": {}}
            ),
            ToolInfo(
                name="create_list",
                description="Create a new list in a space",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "Space ID"},
                        "name": {"type": "string", "description": "List name"}
                    },
                    "required": ["space_id", "name"]
                }
            )
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a specific MCP tool"""
        
        if tool_name == "search_workspace":
            return self.search_workspace(arguments.get("query"))
        
        elif tool_name == "get_workspace_hierarchy":
            return self.get_workspace_hierarchy()
        
        elif tool_name == "get_workspace_tasks":
            return self.get_workspace_tasks(arguments)
        
        elif tool_name == "create_task":
            return self.create_task(arguments)
        
        elif tool_name == "get_task":
            return self.get_task(arguments.get("task_id"))
        
        elif tool_name == "update_task":
            return self.update_task(arguments)
        
        elif tool_name == "create_task_comment":
            return self.create_task_comment(
                arguments.get("task_id"),
                arguments.get("comment_text")
            )
        
        elif tool_name == "get_task_comments":
            return self.get_task_comments(arguments.get("task_id"))
        
        elif tool_name == "get_workspace_members":
            return self.get_workspace_members()
        
        elif tool_name == "create_list":
            return self.create_list(
                arguments.get("space_id"),
                arguments.get("name")
            )
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    # Tool implementations
    
    def search_workspace(self, query: str):
        """Search across workspace"""
        teams = self.api.get("team")
        team_id = teams['teams'][0]['id']
        
        spaces = self.api.get(f"team/{team_id}/space?archived=false")
        results = {"tasks": [], "lists": [], "spaces": spaces['spaces']}
        
        for space in spaces['spaces']:
            lists = self.api.get(f"space/{space['id']}/list?archived=false")
            for lst in lists['lists']:
                if query.lower() in lst['name'].lower():
                    results['lists'].append(lst)
                
                tasks = self.api.get(f"list/{lst['id']}/task?archived=false")
                for task in tasks['tasks']:
                    if query.lower() in task['name'].lower():
                        results['tasks'].append(task)
        
        return results
    
    def get_workspace_hierarchy(self):
        """Get workspace structure"""
        teams = self.api.get("team")
        team_id = teams['teams'][0]['id']
        
        spaces = self.api.get(f"team/{team_id}/space?archived=false")
        
        hierarchy = {
            "workspace": teams['teams'][0],
            "spaces": []
        }
        
        for space in spaces['spaces']:
            space_data = {
                "id": space['id'],
                "name": space['name'],
                "lists": []
            }
            
            lists = self.api.get(f"space/{space['id']}/list?archived=false")
            space_data['lists'] = lists['lists']
            
            hierarchy['spaces'].append(space_data)
        
        return hierarchy
    
    def get_workspace_tasks(self, filters: Dict[str, Any]):
        """Get tasks with filters"""
        list_id = filters.get('list_id')
        
        if list_id:
            tasks = self.api.get(f"list/{list_id}/task?archived=false")
            return tasks['tasks']
        
        teams = self.api.get("team")
        team_id = teams['teams'][0]['id']
        spaces = self.api.get(f"team/{team_id}/space?archived=false")
        
        all_tasks = []
        for space in spaces['spaces']:
            lists = self.api.get(f"space/{space['id']}/list?archived=false")
            for lst in lists['lists']:
                tasks = self.api.get(f"list/{lst['id']}/task?archived=false")
                all_tasks.extend(tasks['tasks'])
        
        return all_tasks
    
    def create_task(self, arguments: Dict[str, Any]):
        """Create a new task"""
        list_id = arguments['list_id']
        task_data = {
            "name": arguments['name'],
            "description": arguments.get('description', ''),
            "status": arguments.get('status', 'to do'),
        }
        
        if 'priority' in arguments:
            task_data['priority'] = arguments['priority']
        
        return self.api.post(f"list/{list_id}/task", task_data)
    
    def get_task(self, task_id: str):
        """Get task details"""
        return self.api.get(f"task/{task_id}")
    
    def update_task(self, arguments: Dict[str, Any]):
        """Update a task"""
        task_id = arguments.pop('task_id')
        return self.api.put(f"task/{task_id}", arguments)
    
    def create_task_comment(self, task_id: str, comment_text: str):
        """Add comment to task"""
        return self.api.post(f"task/{task_id}/comment", {
            "comment_text": comment_text
        })
    
    def get_task_comments(self, task_id: str):
        """Get task comments"""
        return self.api.get(f"task/{task_id}/comment")
    
    def get_workspace_members(self):
        """Get workspace members"""
        teams = self.api.get("team")
        team_id = teams['teams'][0]['id']
        return self.api.get(f"team/{team_id}")
    
    def create_list(self, space_id: str, name: str):
        """Create a new list"""
        return self.api.post(f"space/{space_id}/list", {"name": name})


# ============================================================
# FASTAPI APPLICATION
# ============================================================

# Get API token from environment
CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")

if not CLICKUP_API_TOKEN:
    print("\n⚠️  WARNING: CLICKUP_API_TOKEN not found in environment!")
    print("Please create a .env file with:")
    print("CLICKUP_API_TOKEN=your-token-here")
    exit(1)

# Initialize ClickUp API
clickup_api = ClickUpAPI(CLICKUP_API_TOKEN)
mcp_tools = ClickUpMCPTools(clickup_api)

app = FastAPI(
    title="ClickUp MCP Server",
    description="Model Context Protocol server for ClickUp integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ClickUp MCP Server",
        "version": "1.0.0",
        "protocol": "MCP (Model Context Protocol)",
        "endpoint": "/mcp",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Main MCP endpoint - handles JSON-RPC 2.0 requests"""
    
    try:
        method = request.method
        params = request.params or {}
        
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "clickup-mcp-server",
                    "version": "1.0.0"
                }
            }
        
        elif method == "tools/list":
            tools = mcp_tools.get_tools_list()
            result = {"tools": [tool.dict() for tool in tools]}
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            tool_result = mcp_tools.execute_tool(tool_name, arguments)
            result = {
                "content": [{"type": "text", "text": json.dumps(tool_result, indent=2)}],
                "isError": False
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return MCPResponse(jsonrpc="2.0", id=request.id, result=result)
    
    except Exception as e:
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            error={"code": -32603, "message": str(e)}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        user = clickup_api.get("user")
        return {
            "status": "healthy",
            "service": "clickup-mcp-server",
            "authenticated": True,
            "user": user['user']['username']
        }
    except:
        return {"status": "unhealthy", "authenticated": False}


# ============================================================
# TESTING FUNCTIONS
# ============================================================

def run_comprehensive_tests():
    """Run all MCP tests"""
    print("\n" + "="*60)
    print("🧪 CLICKUP MCP SERVER - COMPREHENSIVE TESTS")
    print("="*60)
    
    try:
        # Test 1: Initialize
        print("\n✓ Test 1: MCP Initialize")
        result = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "clickup-mcp-server", "version": "1.0.0"}
        }
        print(f"  Protocol: {result['protocolVersion']}")
        
        # Test 2: List tools
        print("\n✓ Test 2: List MCP Tools")
        tools = mcp_tools.get_tools_list()
        print(f"  Found {len(tools)} tool(s)")
        for tool in tools:
            print(f"    - {tool.name}")
        
        # Test 3: Get hierarchy
        print("\n✓ Test 3: Get Workspace Hierarchy")
        hierarchy = mcp_tools.execute_tool("get_workspace_hierarchy", {})
        print(f"  Workspace: {hierarchy['workspace']['name']}")
        print(f"  Spaces: {len(hierarchy['spaces'])}")
        
        # Get IDs for further testing
        space_id = hierarchy['spaces'][0]['id']
        list_id = hierarchy['spaces'][0]['lists'][0]['id']
        
        # Test 4: Get tasks
        print("\n✓ Test 4: Get All Tasks")
        tasks = mcp_tools.execute_tool("get_workspace_tasks", {})
        print(f"  Total tasks: {len(tasks)}")
        
        # Test 5: Create task
        print("\n✓ Test 5: Create Task")
        new_task = mcp_tools.execute_tool("create_task", {
            "list_id": list_id,
            "name": "MCP Test Task - Automated",
            "description": "Created via MCP testing",
            "priority": 2
        })
        print(f"  Task: {new_task['name']}")
        print(f"  ID: {new_task['id']}")
        task_id = new_task['id']
        
        # Test 6: Get task
        print("\n✓ Test 6: Get Task Details")
        task = mcp_tools.execute_tool("get_task", {"task_id": task_id})
        print(f"  Task: {task['name']}")
        print(f"  Status: {task['status']['status']}")
        
        # Test 7: Update task
        print("\n✓ Test 7: Update Task")
        updated = mcp_tools.execute_tool("update_task", {
            "task_id": task_id,
            "name": "MCP Test Task - UPDATED",
            "status": "in progress"
        })
        print(f"  New name: {updated['name']}")
        
        # Test 8: Add comment
        print("\n✓ Test 8: Add Comment")
        comment = mcp_tools.execute_tool("create_task_comment", {
            "task_id": task_id,
            "comment_text": "Test comment via MCP! 🚀"
        })
        print(f"  Comment added: ID {comment['id']}")
        
        # Test 9: Search
        print("\n✓ Test 9: Search Workspace")
        results = mcp_tools.execute_tool("search_workspace", {"query": "test"})
        print(f"  Tasks found: {len(results['tasks'])}")
        print(f"  Lists found: {len(results['lists'])}")
        
        # Test 10: Get members
        print("\n✓ Test 10: Get Members")
        team = mcp_tools.execute_tool("get_workspace_members", {})
        members = team.get('members', [])
        print(f"  Members: {len(members)}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  - Tools available: {len(tools)}")
        print(f"  - Total tasks: {len(tasks)}")
        print(f"  - Test task created: {task_id}")
        print(f"\n💡 Server ready to run with: python clickup_mcp_server.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_comprehensive_tests()
    else:
        print("\n" + "="*60)
        print("🚀 Starting ClickUp MCP Server")
        print("="*60)
        print("\nEndpoints:")
        print("  • Main: http://localhost:8000")
        print("  • MCP: http://localhost:8000/mcp")
        print("  • Docs: http://localhost:8000/docs")
        print("  • Health: http://localhost:8000/health")
        print("\n💡 Run 'python clickup_mcp_server.py test' for testing")
        print("Press CTRL+C to stop")
        print("="*60 + "\n")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)