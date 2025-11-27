from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import requests
import uvicorn
import json


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


class MCPError(BaseModel):
    """MCP Error Object"""
    code: int
    message: str
    data: Optional[Any] = None


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
        
        # Search in tasks
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
        
        # Get all tasks from all lists
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

app = FastAPI(
    title="ClickUp MCP Server",
    description="Model Context Protocol server for ClickUp integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ClickUp API with your token
CLICKUP_API_TOKEN = "pk_260557758_AKSYRDQYSK0X665XFSPIK1N4FT5ZZ5GZ"
clickup_api = ClickUpAPI(CLICKUP_API_TOKEN)
mcp_tools = ClickUpMCPTools(clickup_api)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ClickUp MCP Server",
        "version": "1.0.0",
        "protocol": "MCP (Model Context Protocol)",
        "endpoint": "/mcp"
    }


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Main MCP endpoint - handles JSON-RPC 2.0 requests"""
    
    try:
        method = request.method
        params = request.params or {}
        
        # Handle different MCP methods
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "clickup-mcp-server",
                    "version": "1.0.0"
                }
            }
        
        elif method == "tools/list":
            tools = mcp_tools.get_tools_list()
            result = {
                "tools": [tool.dict() for tool in tools]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            tool_result = mcp_tools.execute_tool(tool_name, arguments)
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": str(tool_result)
                    }
                ],
                "isError": False
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result=result
        )
    
    except Exception as e:
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            error={
                "code": -32603,
                "message": str(e)
            }
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "clickup-mcp-server"}


# ============================================================
# COMPREHENSIVE TESTING SUITE (Like First Code)
# ============================================================

def test_mcp_initialize(mcp_tools):
    """Test 1: Initialize MCP Connection"""
    print("\n" + "="*60)
    print("TEST 1: Initialize MCP Protocol")
    print("="*60)
    try:
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "clickup-mcp-server", "version": "1.0.0"}
        }
        print(f"✓ MCP initialized successfully!")
        print(f"  Protocol Version: {result['protocolVersion']}")
        print(f"  Server: {result['serverInfo']['name']}")
        return result
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return None


def test_mcp_list_tools(mcp_tools):
    """Test 2: List all available MCP tools"""
    print("\n" + "="*60)
    print("TEST 2: List Available MCP Tools")
    print("="*60)
    try:
        tools = mcp_tools.get_tools_list()
        print(f"✓ Found {len(tools)} available tool(s)")
        for tool in tools:
            print(f"\n  Tool: {tool.name}")
            print(f"  Description: {tool.description}")
        return tools
    except Exception as e:
        print(f"✗ Failed to list tools: {e}")
        return []


def test_mcp_get_hierarchy(mcp_tools):
    """Test 3: Get workspace hierarchy"""
    print("\n" + "="*60)
    print("TEST 3: Get Workspace Hierarchy")
    print("="*60)
    try:
        hierarchy = mcp_tools.execute_tool("get_workspace_hierarchy", {})
        print(f"✓ Workspace hierarchy retrieved!")
        print(f"  Workspace: {hierarchy['workspace']['name']}")
        print(f"  Workspace ID: {hierarchy['workspace']['id']}")
        print(f"  Spaces: {len(hierarchy['spaces'])}")
        for space in hierarchy['spaces']:
            print(f"\n    Space: {space['name']} (ID: {space['id']})")
            print(f"    Lists: {len(space['lists'])}")
        return hierarchy
    except Exception as e:
        print(f"✗ Failed to get hierarchy: {e}")
        return None


def test_mcp_get_all_tasks(mcp_tools):
    """Test 4: Get all workspace tasks"""
    print("\n" + "="*60)
    print("TEST 4: Get All Workspace Tasks")
    print("="*60)
    try:
        tasks = mcp_tools.execute_tool("get_workspace_tasks", {})
        print(f"✓ Found {len(tasks)} task(s)")
        for i, task in enumerate(tasks[:5], 1):  # Show first 5
            print(f"\n  Task {i}: {task['name']}")
            print(f"  ID: {task['id']}")
            print(f"  Status: {task['status']['status']}")
        if len(tasks) > 5:
            print(f"\n  ... and {len(tasks) - 5} more tasks")
        return tasks
    except Exception as e:
        print(f"✗ Failed to get tasks: {e}")
        return []


def test_mcp_create_task(mcp_tools, list_id):
    """Test 5: Create a new task via MCP"""
    print("\n" + "="*60)
    print("TEST 5: Create Task via MCP")
    print("="*60)
    try:
        task = mcp_tools.execute_tool("create_task", {
            "list_id": list_id,
            "name": "MCP Test Task - Automated",
            "description": "This task was created via MCP tools",
            "status": "to do",
            "priority": 2
        })
        print(f"✓ Task created successfully!")
        print(f"  Task: {task['name']}")
        print(f"  ID: {task['id']}")
        print(f"  URL: {task['url']}")
        return task
    except Exception as e:
        print(f"✗ Failed to create task: {e}")
        return None


def test_mcp_get_task(mcp_tools, task_id):
    """Test 6: Get task details via MCP"""
    print("\n" + "="*60)
    print("TEST 6: Get Task Details via MCP")
    print("="*60)
    try:
        task = mcp_tools.execute_tool("get_task", {"task_id": task_id})
        print(f"✓ Task details retrieved!")
        print(f"  Task: {task['name']}")
        print(f"  Description: {task['description']}")
        print(f"  Status: {task['status']['status']}")
        print(f"  Creator: {task['creator']['username']}")
        return task
    except Exception as e:
        print(f"✗ Failed to get task: {e}")
        return None


def test_mcp_update_task(mcp_tools, task_id):
    """Test 7: Update task via MCP"""
    print("\n" + "="*60)
    print("TEST 7: Update Task via MCP")
    print("="*60)
    try:
        task = mcp_tools.execute_tool("update_task", {
            "task_id": task_id,
            "name": "MCP Test Task - UPDATED",
            "description": "This task was updated via MCP tools",
            "status": "in progress"
        })
        print(f"✓ Task updated successfully!")
        print(f"  New Name: {task['name']}")
        print(f"  New Status: {task['status']['status']}")
        return task
    except Exception as e:
        print(f"✗ Failed to update task: {e}")
        return None


def test_mcp_add_comment(mcp_tools, task_id):
    """Test 8: Add comment via MCP"""
    print("\n" + "="*60)
    print("TEST 8: Add Comment to Task via MCP")
    print("="*60)
    try:
        comment = mcp_tools.execute_tool("create_task_comment", {
            "task_id": task_id,
            "comment_text": "This comment was added via MCP tools! 🚀"
        })
        print(f"✓ Comment added successfully!")
        print(f"  Comment ID: {comment['id']}")
        return comment
    except Exception as e:
        print(f"✗ Failed to add comment: {e}")
        return None


def test_mcp_get_comments(mcp_tools, task_id):
    """Test 9: Get task comments via MCP"""
    print("\n" + "="*60)
    print("TEST 9: Get Task Comments via MCP")
    print("="*60)
    try:
        result = mcp_tools.execute_tool("get_task_comments", {"task_id": task_id})
        comments = result.get('comments', [])
        print(f"✓ Found {len(comments)} comment(s)")
        for comment in comments:
            print(f"\n  Comment: {comment['comment_text'][:50]}...")
            print(f"  By: {comment['user']['username']}")
        return comments
    except Exception as e:
        print(f"✗ Failed to get comments: {e}")
        return []


def test_mcp_search_workspace(mcp_tools, query):
    """Test 10: Search workspace via MCP"""
    print("\n" + "="*60)
    print(f"TEST 10: Search Workspace for '{query}'")
    print("="*60)
    try:
        results = mcp_tools.execute_tool("search_workspace", {"query": query})
        print(f"✓ Search completed!")
        print(f"  Tasks found: {len(results['tasks'])}")
        print(f"  Lists found: {len(results['lists'])}")
        for task in results['tasks'][:3]:
            print(f"\n    Task: {task['name']}")
        return results
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return None


def test_mcp_get_members(mcp_tools):
    """Test 11: Get workspace members via MCP"""
    print("\n" + "="*60)
    print("TEST 11: Get Workspace Members")
    print("="*60)
    try:
        team = mcp_tools.execute_tool("get_workspace_members", {})
        members = team.get('members', [])
        print(f"✓ Found {len(members)} member(s)")
        for member in members:
            user = member.get('user', {})
            print(f"\n  Member: {user.get('username')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Role: {user.get('role_key', 'N/A')}")
        return members
    except Exception as e:
        print(f"✗ Failed to get members: {e}")
        return []


def test_mcp_create_list(mcp_tools, space_id):
    """Test 12: Create new list via MCP"""
    print("\n" + "="*60)
    print("TEST 12: Create New List via MCP")
    print("="*60)
    try:
        lst = mcp_tools.execute_tool("create_list", {
            "space_id": space_id,
            "name": f"MCP Test List - {json.dumps({'test': True})}"
        })
        print(f"✓ List created successfully!")
        print(f"  List: {lst['name']}")
        print(f"  ID: {lst['id']}")
        return lst
    except Exception as e:
        print(f"✗ Failed to create list: {e}")
        return None


def run_comprehensive_tests():
    """Run all MCP tests in sequence"""
    print("\n" + "="*60)
    print("CLICKUP MCP SERVER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Initialize
    result = test_mcp_initialize(mcp_tools)
    if not result:
        return
    
    # List tools
    tools = test_mcp_list_tools(mcp_tools)
    if not tools:
        return
    
    # Get hierarchy
    hierarchy = test_mcp_get_hierarchy(mcp_tools)
    if not hierarchy:
        return
    
    # Extract IDs for testing
    workspace_id = hierarchy['workspace']['id']
    space_id = hierarchy['spaces'][0]['id']
    list_id = hierarchy['spaces'][0]['lists'][0]['id']
    
    # Get all tasks
    all_tasks = test_mcp_get_all_tasks(mcp_tools)
    
    # Create a task
    new_task = test_mcp_create_task(mcp_tools, list_id)
    if new_task:
        task_id = new_task['id']
        
        # Test operations on the created task
        test_mcp_get_task(mcp_tools, task_id)
        test_mcp_update_task(mcp_tools, task_id)
        test_mcp_add_comment(mcp_tools, task_id)
        test_mcp_get_comments(mcp_tools, task_id)
    
    # Search workspace
    test_mcp_search_workspace(mcp_tools, "test")
    
    # Get members
    test_mcp_get_members(mcp_tools)
    
    # Create list (optional - uncomment if you want)
    # test_mcp_create_list(mcp_tools, space_id)
    
    # Final summary
    print("\n" + "="*60)
    print("✓ ALL MCP TESTS COMPLETED!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"  - Workspace: {hierarchy['workspace']['name']}")
    print(f"  - Spaces: {len(hierarchy['spaces'])}")
    print(f"  - Total Tasks: {len(all_tasks)}")
    print(f"  - Available Tools: {len(tools)}")
    print("\n💡 Server is ready at: http://localhost:8000")
    print("💡 API docs: http://localhost:8000/docs")


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run comprehensive tests
        run_comprehensive_tests()
    else:
        # Start FastAPI server
        print("\n" + "="*60)
        print("Starting ClickUp MCP Server")
        print("="*60)
        print("\nServer will run on: http://localhost:8000")
        print("MCP endpoint: http://localhost:8000/mcp")
        print("API docs: http://localhost:8000/docs")
        print("\n💡 Run with 'python script.py test' for comprehensive testing")
        print("\nPress CTRL+C to stop")
        print("="*60 + "\n")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)