# ClickUp Automation Toolkit

This repository contains several Python programs that demonstrate different ways to interact with the ClickUp REST API and Model Context Protocol (MCP). Each script focuses on a specific workflow, from manual testing to AI-assisted automation.

## Prerequisites

- Python 3.9+
- `pip install -r requirements.txt` (requests, fastapi, uvicorn, python-dotenv, openai, pydantic, etc.)
- A ClickUp personal API token (`CLICKUP_API_TOKEN`)
- An OpenAI API key (`OPENAI_API_KEY`) for the AI agent
- Optional `.env` file at the repo root:
  ```
  CLICKUP_API_TOKEN=pk_xxx
  OPENAI_API_KEY=sk-xxx
  ```

## File Overview

### `clickup_agent.py`
- **Purpose:** AI-powered CLI assistant that interprets natural language to create, analyze, update, and report on ClickUp tasks.
- **Input Source & Format:**
  - `.env` variables: `CLICKUP_API_TOKEN`, `OPENAI_API_KEY`.
  - CLI prompts including free-form natural language sentences (e.g., “Schedule a high priority meeting …”).
- **Output Format:** Console text that displays parsed JSON (task name, description, priority, status), success/error messages, and AI-generated analysis/report sections. Actual task objects are created/updated in ClickUp via REST calls.
- **Run:** `python clickup_agent.py` (ensure `.env` is present). Follow interactive menus.

### `clickup_app.py`
- **Purpose:** Manual ClickUp task manager CLI for CRUD operations without AI.
- **Input Source & Format:**
  - `API_TOKEN` constant near the top of the file (string).
  - CLI prompts for numeric selections (workspace/space/list index) and structured input fields (task name string, priority number 1-4, status choices).
- **Output Format:** Console menus, tabular-ish listings of ClickUp objects, and confirmation lines such as “✓ Task created successfully!” plus JSON snippets returned by the API.
- **Run:** `python clickup_app.py` (after editing `API_TOKEN`). Follow prompts to manage tasks.

### `clickup_mcp_server.py`
- **Purpose:** Production-ready FastAPI server exposing ClickUp capabilities through the Model Context Protocol for agent integrations.
- **Input Source & Format:**
  - `.env` variable: `CLICKUP_API_TOKEN`.
  - HTTP JSON-RPC requests to `POST /mcp` following MCP shape:
    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": { "name": "get_task", "arguments": {"task_id": "xxx"} }
    }
    ```
- **Output Format:** JSON-RPC 2.0 responses with `result` or `error` fields, plus standard FastAPI JSON for `/`, `/health`, `/docs`. Logs stream to stdout via uvicorn.
- **Run:** `python clickup_mcp_server.py` to start the API (defaults to `http://localhost:8000`). Use `python clickup_mcp_server.py test` to execute the built-in end-to-end test routine (requires valid ClickUp workspace data).

### `clickup_mcp_test.py`
- **Purpose:** Simplified FastAPI MCP server plus an extensive test harness mirroring `clickup_mcp_server.py`, typically used for experimenting with a fixed token before wiring up environment variables.
- **Input Source & Format:**
  - `CLICKUP_API_TOKEN` constant near the bottom of the file.
  - Optional CLI flag `test` to trigger a scripted workflow (no arguments required).
  - Same JSON-RPC payload format as the main server when running in API mode.
- **Output Format:** 
  - CLI test mode: verbose console logs enumerating each MCP call and result (plain text).
  - Server mode: JSON responses identical to `clickup_mcp_server.py`.
- **Run:** 
  - `python clickup_mcp_test.py` to launch the server.
  - `python clickup_mcp_test.py test` to run the scripted MCP workflow.

### `clickup_test.py`
- **Purpose:** Straightforward regression/test script that sequentially calls ClickUp API endpoints (auth, workspaces, spaces, lists, tasks, docs) to validate connectivity and permissions.
- **Input Source & Format:**
  - `API_TOKEN` constant near the bottom.
  - No interactive prompts; script sequentially uses the token to hit REST endpoints.
- **Output Format:** Deterministic console narration showing each step’s outcome and the key JSON values (names, IDs, counts). API calls may create/update tasks/comments directly in ClickUp.
- **Run:** `python clickup_test.py`.

## Differences at a Glance
- `clickup_agent.py`: AI-driven, natural-language interface powered by OpenAI; best for intelligent parsing/reporting.
- `clickup_app.py`: Manual CLI for CRUD, useful when you need precise control without AI behavior.
- `clickup_mcp_server.py`: Production-ready MCP server with `.env` loading, suitable for external agent integrations.
- `clickup_mcp_test.py`: Experimental MCP server + verbose test suite using hard-coded token; great for local exploration.
- `clickup_test.py`: Lightweight sequential regression tester to verify raw ClickUp API access before using other scripts.

## Suggested Usage Order
1. Update tokens in `.env` (or constants) and run `clickup_test.py` to confirm basic API access.
2. Experiment with manual task flows via `clickup_app.py`.
3. Stand up the MCP server (`clickup_mcp_server.py`) for integrations.
4. Use `clickup_agent.py` for AI-assisted task creation and analysis.

## Notes
- All scripts make live modifications in ClickUp; consider creating a sandbox workspace or test list.
- Clean up any test tasks/lists created by the demos to avoid clutter or quota issues.



Ready-to-Use Test Requests
1. Create Task in "API Demo" List
json{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_task",
    "arguments": {
      "list_id": "901813692160",
      "name": "New Task from Testing",
      "description": "Created for MCP testing",
      "priority": 2
    }
  }
}
2. Get Specific Task
json{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_task",
    "arguments": {
      "task_id": "86evnv1w1"
    }
  }
}
3. Update Task
json{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "update_task",
    "arguments": {
      "task_id": "86evnv1w1",
      "name": "Updated Task Name",
      "status": "in progress"
    }
  }
}
4. Add Comment
json{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "create_task_comment",
    "arguments": {
      "task_id": "86evnv1w1",
      "comment_text": "Testing comment via MCP!"
    }
  }
}
5. Get Comments
json{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_task_comments",
    "arguments": {
      "task_id": "86evnv1w1"
    }
  }
}
6. Search for "meeting"
json{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "search_workspace",
    "arguments": {
      "query": "meeting"
    }
  }
}
7. Get Tasks from "Project 1"
json{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "get_workspace_tasks",
    "arguments": {
      "list_id": "901813688963"
    }
  }
}
8. Create New List
json{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "create_list",
    "arguments": {
      "space_id": "90188383294",
      "name": "Test List from MCP"
    }
  }
}

🎯 Quick Copy-Paste Templates
Use these exact values in your tests:
For creating tasks:

list_id: "901813692160" (API Demo list)

For task operations:

task_id: "86evnv1w1" (Test Task from MCP)

For creating lists:

space_id: "90188383294"

All requests go to: POST http://127.0.0.1:8000/mcp