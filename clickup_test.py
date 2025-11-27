import requests
import json


class ClickUpAPI:
    """ClickUp API Client"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": self.api_token
        }
    
    def get(self, endpoint):
        """Make GET request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data):
        """Make POST request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint, data):
        """Make PUT request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint):
        """Make DELETE request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json() if response.text else {}


def test_authentication(api):
    """Test 1: Verify API authentication"""
    print("\n" + "="*60)
    print("TEST 1: Authentication & Get User Info")
    print("="*60)
    try:
        user = api.get("user")
        print(f"✓ Authenticated successfully!")
        print(f"  User: {user['user']['username']}")
        print(f"  Email: {user['user']['email']}")
        return user
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return None


def test_get_workspaces(api):
    """Test 2: Get all workspaces (teams)"""
    print("\n" + "="*60)
    print("TEST 2: Get Workspaces (Teams)")
    print("="*60)
    try:
        teams = api.get("team")
        print(f"✓ Found {len(teams['teams'])} workspace(s)")
        for team in teams['teams']:
            print(f"\n  Workspace: {team['name']}")
            print(f"  ID: {team['id']}")
        return teams['teams']
    except Exception as e:
        print(f"✗ Failed to get workspaces: {e}")
        return []


def test_get_spaces(api, team_id):
    """Test 3: Get all spaces in a workspace"""
    print("\n" + "="*60)
    print("TEST 3: Get Spaces")
    print("="*60)
    try:
        spaces = api.get(f"team/{team_id}/space?archived=false")
        print(f"✓ Found {len(spaces['spaces'])} space(s)")
        for space in spaces['spaces']:
            print(f"\n  Space: {space['name']}")
            print(f"  ID: {space['id']}")
        return spaces['spaces']
    except Exception as e:
        print(f"✗ Failed to get spaces: {e}")
        return []


def test_get_lists(api, space_id):
    """Test 4: Get lists (projects) in a space"""
    print("\n" + "="*60)
    print("TEST 4: Get Lists (Projects)")
    print("="*60)
    try:
        lists = api.get(f"space/{space_id}/list?archived=false")
        print(f"✓ Found {len(lists['lists'])} list(s)")
        for lst in lists['lists']:
            print(f"\n  List: {lst['name']}")
            print(f"  ID: {lst['id']}")
        return lists['lists']
    except Exception as e:
        print(f"✗ Failed to get lists: {e}")
        return []


def test_get_tasks(api, list_id):
    """Test 5: Get all tasks in a list"""
    print("\n" + "="*60)
    print("TEST 5: Get Tasks")
    print("="*60)
    try:
        tasks = api.get(f"list/{list_id}/task?archived=false")
        print(f"✓ Found {len(tasks['tasks'])} task(s)")
        for task in tasks['tasks']:
            print(f"\n  Task: {task['name']}")
            print(f"  ID: {task['id']}")
            print(f"  Status: {task['status']['status']}")
            if task.get('due_date'):
                print(f"  Due Date: {task['due_date']}")
        return tasks['tasks']
    except Exception as e:
        print(f"✗ Failed to get tasks: {e}")
        return []


def test_create_task(api, list_id):
    """Test 6: Create a new task"""
    print("\n" + "="*60)
    print("TEST 6: Create New Task")
    print("="*60)
    try:
        task_data = {
            "name": "Test Task from Python API",
            "description": "This task was created via ClickUp API using Python",
            "status": "to do",
            "priority": 3,
        }
        task = api.post(f"list/{list_id}/task", task_data)
        print(f"✓ Task created successfully!")
        print(f"  Task: {task['name']}")
        print(f"  ID: {task['id']}")
        print(f"  URL: {task['url']}")
        return task
    except Exception as e:
        print(f"✗ Failed to create task: {e}")
        return None


def test_update_task(api, task_id):
    """Test 7: Update an existing task"""
    print("\n" + "="*60)
    print("TEST 7: Update Task")
    print("="*60)
    try:
        update_data = {
            "name": "Updated Task from Python API",
            "description": "This task was UPDATED via ClickUp API",
            "status": "in progress"
        }
        task = api.put(f"task/{task_id}", update_data)
        print(f"✓ Task updated successfully!")
        print(f"  Task: {task['name']}")
        print(f"  Status: {task['status']['status']}")
        return task
    except Exception as e:
        print(f"✗ Failed to update task: {e}")
        return None


def test_get_task_details(api, task_id):
    """Test 8: Get detailed task information"""
    print("\n" + "="*60)
    print("TEST 8: Get Task Details")
    print("="*60)
    try:
        task = api.get(f"task/{task_id}")
        print(f"✓ Task details retrieved!")
        print(f"  Task: {task['name']}")
        print(f"  Description: {task['description']}")
        print(f"  Status: {task['status']['status']}")
        print(f"  Creator: {task['creator']['username']}")
        print(f"  Date Created: {task['date_created']}")
        return task
    except Exception as e:
        print(f"✗ Failed to get task details: {e}")
        return None


def test_get_docs(api, workspace_id):
    """Test 9: Get Documents/Pages in workspace"""
    print("\n" + "="*60)
    print("TEST 9: Get Documents/Pages")
    print("="*60)
    try:
        # ClickUp Docs API endpoint
        docs = api.get(f"team/{workspace_id}/docs")
        if 'docs' in docs:
            print(f"✓ Found {len(docs['docs'])} document(s)")
            for doc in docs['docs']:
                print(f"\n  Document: {doc.get('name', 'Untitled')}")
                print(f"  ID: {doc['id']}")
                if 'date_created' in doc:
                    print(f"  Created: {doc['date_created']}")
        return docs.get('docs', [])
    except Exception as e:
        print(f"✗ Failed to get documents: {e}")
        print(f"  Note: Docs API may require Business+ plan or specific permissions")
        return []


def test_get_doc_content(api, doc_id):
    """Test 10: Get specific document content"""
    print("\n" + "="*60)
    print("TEST 10: Get Document Content")
    print("="*60)
    try:
        doc = api.get(f"doc/{doc_id}")
        print(f"✓ Document content retrieved!")
        print(f"  Name: {doc.get('name', 'Untitled')}")
        print(f"  Content Preview: {doc.get('content', 'N/A')[:200]}...")
        return doc
    except Exception as e:
        print(f"✗ Failed to get document content: {e}")
        return None


def test_add_task_comment(api, task_id):
    """Test 11: Add comment to a task"""
    print("\n" + "="*60)
    print("TEST 11: Add Comment to Task")
    print("="*60)
    try:
        comment_data = {
            "comment_text": "This comment was added via Python API! 🚀"
        }
        comment = api.post(f"task/{task_id}/comment", comment_data)
        print(f"✓ Comment added successfully!")
        print(f"  Comment ID: {comment['id']}")
        return comment
    except Exception as e:
        print(f"✗ Failed to add comment: {e}")
        return None


def test_delete_task(api, task_id):
    """Test 12: Delete a task"""
    print("\n" + "="*60)
    print("TEST 12: Delete Task")
    print("="*60)
    try:
        result = api.delete(f"task/{task_id}")
        print(f"✓ Task deleted successfully!")
        return result
    except Exception as e:
        print(f"✗ Failed to delete task: {e}")
        return None


def main():
    """Main test execution"""
    print("\n" + "="*60)
    print("CLICKUP API TESTING SCRIPT")
    print("="*60)
    
    # YOUR API TOKEN
    API_TOKEN = "pk_260557758_AKSYRDQYSK0X665XFSPIK1N4FT5ZZ5GZ"
    
    # Initialize API client
    api = ClickUpAPI(API_TOKEN)
    
    # Run tests
    user = test_authentication(api)
    if not user:
        return
    
    teams = test_get_workspaces(api)
    if not teams:
        return
    
    team_id = teams[0]['id']
    spaces = test_get_spaces(api, team_id)
    
    if not spaces:
        print("\n⚠️  No spaces found.")
        return
    
    space_id = spaces[0]['id']
    lists = test_get_lists(api, space_id)
    
    if not lists:
        print("\n⚠️  No lists found.")
        return
    
    list_id = lists[0]['id']
    tasks = test_get_tasks(api, list_id)
    
    # Create and manipulate a task
    new_task = test_create_task(api, list_id)
    if new_task:
        test_update_task(api, new_task['id'])
        test_get_task_details(api, new_task['id'])
        test_add_task_comment(api, new_task['id'])
        
        # Optional: Delete the test task (uncomment if you want to clean up)
        # test_delete_task(api, new_task['id'])
    
    # Try to get documents (may require Business+ plan)
    docs = test_get_docs(api, team_id)
    if docs:
        # Get content of first document
        test_get_doc_content(api, docs[0]['id'])
    
    print("\n" + "="*60)
    print("✓ ALL TESTS COMPLETED!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"  - Workspace: {teams[0]['name']}")
    print(f"  - Spaces: {len(spaces)}")
    print(f"  - Lists: {len(lists)}")
    print(f"  - Tasks: {len(tasks)}")
    print(f"  - Documents: {len(docs)}")


if __name__ == "__main__":
    main()