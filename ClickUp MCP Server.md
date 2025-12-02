# ClickUp MCP Server - Setup & Run Guide

## 📋 What You Have

You have a **complete MCP server** written in Python that:
- Implements Model Context Protocol (MCP)
- Provides 10+ tools for ClickUp integration
- Can be used by AI assistants (Claude, ChatGPT, etc.)
- Has comprehensive testing built-in

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
pip install fastapi uvicorn requests pydantic python-dotenv
```

### Step 2: Save the Code

Save your MCP server code as `clickup_mcp_server.py`

### Step 3: Create .env File (Optional but Recommended)

Create `.env` file:
```bash
CLICKUP_API_TOKEN=pk_260557758_AKSYRDQYSK0X665XFSPIK1N4FT5ZZ5GZ
```

Update code to use .env:
```python
# Add at top of file
from dotenv import load_dotenv
load_dotenv()

# Replace hardcoded token with:
CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
```

## 🧪 Testing Your MCP Server

### Test Mode (Recommended First!)

Run comprehensive tests WITHOUT starting the server:

```bash
python clickup_mcp_server.py test
```

**This will test:**
- ✅ MCP initialization
- ✅ List all available tools
- ✅ Get workspace hierarchy
- ✅ Get all tasks
- ✅ Create task
- ✅ Update task
- ✅ Add comments
- ✅ Search workspace
- ✅ Get members
- ✅ And more!

### Server Mode

Start the MCP server:

```bash
python clickup_mcp_server.py
```

Server will run at:
- **Main endpoint:** http://localhost:8000
- **MCP endpoint:** http://localhost:8000/mcp
- **API docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

## 📡 Using Your MCP Server

### Option 1: Test with cURL

```bash
# Initialize MCP
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
  }'

# List available tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'

# Get workspace hierarchy
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_workspace_hierarchy",
      "arguments": {}
    }
  }'
```

### Option 2: Test with Python Script

```python
import requests

# Initialize
response = requests.post('http://localhost:8000/mcp', json={
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize"
})
print(response.json())

# List tools
response = requests.post('http://localhost:8000/mcp', json={
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
})
print(response.json())

# Create task
response = requests.post('http://localhost:8000/mcp', json={
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "create_task",
        "arguments": {
            "list_id": "YOUR_LIST_ID",
            "name": "Test Task from MCP",
            "description": "Created via MCP server",
            "priority": 2
        }
    }
})
print(response.json())
```

### Option 3: Connect to Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python",
      "args": ["/path/to/clickup_mcp_server.py"]
    }
  }
}
```

Or use remote connection:
```json
{
  "mcpServers": {
    "clickup": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

## 🛠️ Available MCP Tools

Your server provides these tools:

1. **search_workspace** - Search tasks, lists, folders
2. **get_workspace_hierarchy** - Get complete structure
3. **get_workspace_tasks** - Get all tasks with filters
4. **create_task** - Create new task
5. **get_task** - Get task details
6. **update_task** - Update existing task
7. **create_task_comment** - Add comment
8. **get_task_comments** - Get all comments
9. **get_workspace_members** - Get team members
10. **create_list** - Create new list

## 🎯 Example Usage Flow

### Step 1: Run Tests
```bash
python clickup_mcp_server.py test
```

### Step 2: Start Server
```bash
python clickup_mcp_server.py
```

### Step 3: Use the API
```bash
# Get workspace structure
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_workspace_hierarchy",
      "arguments": {}
    }
  }'
```

## 📊 Architecture

```
Your MCP Server (Python/FastAPI)
    ↓
JSON-RPC 2.0 Protocol
    ↓
ClickUp REST API
    ↓
Your ClickUp Workspace
```

## 🔒 Security Best Practices

1. **Use .env file** for API token
2. **Don't expose server publicly** without authentication
3. **Use HTTPS** in production
4. **Add rate limiting** for production use

## 🚨 Troubleshooting

### "Module not found: fastapi"
```bash
pip install fastapi uvicorn
```

### "Connection refused"
- Make sure server is running: `python clickup_mcp_server.py`
- Check port 8000 is not in use

### "CLICKUP_API_TOKEN not found"
- Create `.env` file with your token
- Or update code with hardcoded token (not recommended)

### Server starts but tests fail
- Check your ClickUp API token is valid
- Verify you have workspaces and lists in ClickUp

## 💡 Next Steps

1. **Test the server:** `python clickup_mcp_server.py test`
2. **Start the server:** `python clickup_mcp_server.py`
3. **Connect to Claude Desktop** or other MCP clients
4. **Build custom workflows** using the MCP tools

## 🎓 What Makes This MCP?

This is a valid MCP server because it:
- ✅ Implements JSON-RPC 2.0 protocol
- ✅ Has `initialize` method
- ✅ Has `tools/list` method
- ✅ Has `tools/call` method
- ✅ Returns proper MCP responses
- ✅ Follows MCP specification

You can use it with ANY MCP-compatible client!