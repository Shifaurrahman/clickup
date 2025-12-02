import requests
import json
from datetime import datetime


class ClickUpAPI:
    """ClickUp API Client"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.clickup.com/api/v2"
        self.base_url_v3 = "https://api.clickup.com/api/v3"
        self.headers = {
            "Authorization": self.api_token
        }
    
    def get(self, endpoint, use_v3=False):
        """Make GET request"""
        base = self.base_url_v3 if use_v3 else self.base_url
        url = f"{base}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint, data, use_v3=False):
        """Make POST request"""
        base = self.base_url_v3 if use_v3 else self.base_url
        url = f"{base}/{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def put(self, endpoint, data, use_v3=False):
        """Make PUT request"""
        base = self.base_url_v3 if use_v3 else self.base_url
        url = f"{base}/{endpoint}"
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint):
        """Make DELETE request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json() if response.text else {}


def select_from_list(items, item_type, key='name'):
    """Helper function to let user select from a list"""
    if not items:
        print(f"\n⚠️  No {item_type}s found!")
        return None
    
    print(f"\n{'='*60}")
    print(f"Available {item_type}s:")
    print('='*60)
    for i, item in enumerate(items, 1):
        print(f"{i}. {item[key]} (ID: {item['id']})")
    
    while True:
        try:
            choice = input(f"\nSelect {item_type} (1-{len(items)}) or 0 to cancel: ").strip()
            choice = int(choice)
            if choice == 0:
                return None
            if 1 <= choice <= len(items):
                return items[choice - 1]
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")


def create_custom_task(api, list_id):
    """Create a task with user input"""
    print("\n" + "="*60)
    print("CREATE NEW TASK")
    print("="*60)
    
    name = input("Task name: ").strip()
    if not name:
        print("Task name is required!")
        return None
    
    description = input("Description (optional): ").strip()
    
    print("\nPriority levels:")
    print("1 = Urgent, 2 = High, 3 = Normal, 4 = Low")
    priority = input("Priority (1-4, default 3): ").strip()
    priority = int(priority) if priority.isdigit() and 1 <= int(priority) <= 4 else 3
    
    print("\nStatus options: to do, in progress, complete")
    status = input("Status (default 'to do'): ").strip().lower()
    if not status:
        status = "to do"
    
    # Date inputs
    print("\n--- Date Settings ---")
    start_date_str = input("Start date (YYYY-MM-DD, leave blank to skip): ").strip()
    start_time_str = input("Start time (HH:MM 24-hour format, leave blank to skip): ").strip()
    
    due_date_str = input("Due date (YYYY-MM-DD, leave blank to skip): ").strip()
    due_time_str = input("Due time (HH:MM 24-hour format, leave blank to skip): ").strip()
    
    task_data = {
        "name": name,
        "description": description,
        "status": status,
        "priority": priority,
    }
    
    # Convert start date to Unix timestamp if provided
    if start_date_str:
        try:
            if start_time_str:
                dt = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
                task_data["start_date_time"] = True
            else:
                dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                task_data["start_date_time"] = False
            
            # Convert to Unix timestamp in milliseconds
            task_data["start_date"] = int(dt.timestamp() * 1000)
            
        except ValueError:
            print("⚠️  Invalid start date/time format, skipping start date...")
    
    # Convert due date to Unix timestamp if provided
    if due_date_str:
        try:
            if due_time_str:
                dt = datetime.strptime(f"{due_date_str} {due_time_str}", "%Y-%m-%d %H:%M")
                task_data["due_date_time"] = True
            else:
                dt = datetime.strptime(due_date_str, "%Y-%m-%d")
                task_data["due_date_time"] = False
            
            # Convert to Unix timestamp in milliseconds
            task_data["due_date"] = int(dt.timestamp() * 1000)
            
        except ValueError:
            print("⚠️  Invalid due date/time format, skipping due date...")
    
    try:
        task = api.post(f"list/{list_id}/task", task_data)
        print(f"\n✓ Task created successfully!")
        print(f"  Name: {task['name']}")
        print(f"  ID: {task['id']}")
        print(f"  URL: {task['url']}")
        return task
    except Exception as e:
        print(f"\n✗ Failed to create task: {e}")
        return None


def update_existing_task(api, task_id):
    """Update a task with user input"""
    print("\n" + "="*60)
    print("UPDATE TASK")
    print("="*60)
    
    # Get current task details
    try:
        current = api.get(f"task/{task_id}")
        print(f"\nCurrent task: {current['name']}")
        print(f"Current status: {current['status']['status']}")
        
        # Display current dates
        if current.get('start_date'):
            start_ts = int(current['start_date']) / 1000
            start_dt = datetime.fromtimestamp(start_ts)
            print(f"Current start date: {start_dt.strftime('%Y-%m-%d %H:%M')}")
        
        if current.get('due_date'):
            due_ts = int(current['due_date']) / 1000
            due_dt = datetime.fromtimestamp(due_ts)
            print(f"Current due date: {due_dt.strftime('%Y-%m-%d %H:%M')}")
            
    except Exception as e:
        print(f"Error getting task: {e}")
        return None
    
    name = input(f"\nNew name (leave blank to keep '{current['name']}'): ").strip()
    description = input("New description (leave blank to skip): ").strip()
    status = input("New status (to do/in progress/complete, blank to skip): ").strip().lower()
    
    # Date updates
    print("\n--- Update Dates (leave blank to keep current) ---")
    start_date_str = input("Start date (YYYY-MM-DD or 'clear' to remove): ").strip()
    start_time_str = input("Start time (HH:MM 24-hour format): ").strip()
    
    due_date_str = input("Due date (YYYY-MM-DD or 'clear' to remove): ").strip()
    due_time_str = input("Due time (HH:MM 24-hour format): ").strip()
    
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    if status:
        update_data['status'] = status
    
    # Handle start date
    if start_date_str:
        if start_date_str.lower() == 'clear':
            update_data['start_date'] = None
        else:
            try:
                if start_time_str:
                    dt = datetime.strptime(f"{start_date_str} {start_time_str}", "%Y-%m-%d %H:%M")
                    update_data["start_date_time"] = True
                else:
                    dt = datetime.strptime(start_date_str, "%Y-%m-%d")
                    update_data["start_date_time"] = False
                
                update_data["start_date"] = int(dt.timestamp() * 1000)
                
            except ValueError:
                print("⚠️  Invalid start date/time format, skipping...")
    
    # Handle due date
    if due_date_str:
        if due_date_str.lower() == 'clear':
            update_data['due_date'] = None
        else:
            try:
                if due_time_str:
                    dt = datetime.strptime(f"{due_date_str} {due_time_str}", "%Y-%m-%d %H:%M")
                    update_data["due_date_time"] = True
                else:
                    dt = datetime.strptime(due_date_str, "%Y-%m-%d")
                    update_data["due_date_time"] = False
                
                update_data["due_date"] = int(dt.timestamp() * 1000)
                
            except ValueError:
                print("⚠️  Invalid due date/time format, skipping...")
    
    if not update_data:
        print("No changes to make!")
        return None
    
    try:
        task = api.put(f"task/{task_id}", update_data)
        print(f"\n✓ Task updated successfully!")
        print(f"  Name: {task['name']}")
        print(f"  Status: {task['status']['status']}")
        return task
    except Exception as e:
        print(f"\n✗ Failed to update task: {e}")
        return None


def create_subtask(api, parent_task_id):
    """Create a subtask under a parent task"""
    print("\n" + "="*60)
    print("CREATE SUBTASK")
    print("="*60)
    
    name = input("Subtask name: ").strip()
    if not name:
        print("Subtask name is required!")
        return None
    
    description = input("Description (optional): ").strip()
    
    print("\nStatus options: to do, in progress, complete")
    status = input("Status (default 'to do'): ").strip().lower()
    if not status:
        status = "to do"
    
    subtask_data = {
        "name": name,
        "description": description,
        "status": status,
        "parent": parent_task_id
    }
    
    try:
        # Get parent task to find list_id
        parent = api.get(f"task/{parent_task_id}")
        list_id = parent['list']['id']
        
        subtask = api.post(f"list/{list_id}/task", subtask_data)
        print(f"\n✓ Subtask created successfully!")
        print(f"  Name: {subtask['name']}")
        print(f"  ID: {subtask['id']}")
        return subtask
    except Exception as e:
        print(f"\n✗ Failed to create subtask: {e}")
        return None


def add_checklist_to_task(api, task_id):
    """Add a checklist to a task"""
    print("\n" + "="*60)
    print("ADD CHECKLIST TO TASK")
    print("="*60)
    
    checklist_name = input("Checklist name: ").strip()
    if not checklist_name:
        print("Checklist name is required!")
        return None
    
    try:
        checklist_data = {"name": checklist_name}
        checklist = api.post(f"task/{task_id}/checklist", checklist_data)
        print(f"\n✓ Checklist created successfully!")
        print(f"  Name: {checklist['checklist']['name']}")
        print(f"  ID: {checklist['checklist']['id']}")
        
        # Ask if user wants to add items
        add_items = input("\nAdd checklist items now? (yes/no): ").strip().lower()
        if add_items == 'yes':
            checklist_id = checklist['checklist']['id']
            while True:
                item_name = input("\nChecklist item name (or 'done' to finish): ").strip()
                if item_name.lower() == 'done':
                    break
                if item_name:
                    try:
                        item_data = {"name": item_name}
                        api.post(f"checklist/{checklist_id}/checklist_item", item_data)
                        print(f"  ✓ Added: {item_name}")
                    except Exception as e:
                        print(f"  ✗ Failed to add item: {e}")
        
        return checklist
    except Exception as e:
        print(f"\n✗ Failed to create checklist: {e}")
        return None


def add_task_dependency(api, task_id):
    """Add a dependency to a task"""
    print("\n" + "="*60)
    print("ADD TASK DEPENDENCY")
    print("="*60)
    
    print("\nDependency types:")
    print("1. This task is waiting on another task")
    print("2. Another task is waiting on this task")
    dep_type = input("Select dependency type (1-2): ").strip()
    
    depends_on = input("\nEnter the task ID this depends on: ").strip()
    if not depends_on:
        print("Task ID is required!")
        return None
    
    try:
        if dep_type == "1":
            # This task depends on another (waiting_on)
            dependency_data = {
                "depends_on": depends_on,
                "dependency_of": task_id
            }
        else:
            # Another task depends on this (blocking)
            dependency_data = {
                "depends_on": task_id,
                "dependency_of": depends_on
            }
        
        result = api.post(f"task/{task_id}/dependency", dependency_data)
        print(f"\n✓ Dependency added successfully!")
        return result
    except Exception as e:
        print(f"\n✗ Failed to add dependency: {e}")
        return None


def track_time_on_task(api, task_id):
    """Track time on a task"""
    print("\n" + "="*60)
    print("TRACK TIME ON TASK")
    print("="*60)
    
    # Get team_id from task
    try:
        task = api.get(f"task/{task_id}")
        team_id = task['team_id']
    except Exception as e:
        print(f"Error getting task: {e}")
        return None
    
    description = input("Time entry description: ").strip()
    duration_hours = input("Duration in hours (e.g., 2.5): ").strip()
    
    try:
        duration_ms = int(float(duration_hours) * 3600000)  # Convert hours to milliseconds
        
        time_data = {
            "description": description,
            "duration": duration_ms,
            "tid": task_id
        }
        
        result = api.post(f"team/{team_id}/time_entries", time_data)
        print(f"\n✓ Time tracked successfully!")
        print(f"  Duration: {duration_hours} hours")
        return result
    except Exception as e:
        print(f"\n✗ Failed to track time: {e}")
        return None


def set_custom_field(api, task_id):
    """Set a custom field value on a task"""
    print("\n" + "="*60)
    print("SET CUSTOM FIELD")
    print("="*60)
    
    # Get task to find custom fields
    try:
        task = api.get(f"task/{task_id}")
        custom_fields = task.get('custom_fields', [])
        
        if not custom_fields:
            print("\n⚠️  No custom fields available for this task!")
            return None
        
        print("\nAvailable custom fields:")
        for i, field in enumerate(custom_fields, 1):
            print(f"{i}. {field['name']} (Type: {field['type']})")
        
        choice = int(input(f"\nSelect field (1-{len(custom_fields)}): ").strip())
        if choice < 1 or choice > len(custom_fields):
            print("Invalid choice!")
            return None
        
        field = custom_fields[choice - 1]
        field_id = field['id']
        field_type = field['type']
        
        # Get value based on field type
        if field_type == 'drop_down':
            print("\nAvailable options:")
            for i, option in enumerate(field['type_config']['options'], 1):
                print(f"{i}. {option['name']}")
            opt_choice = int(input("Select option: ").strip()) - 1
            value = field['type_config']['options'][opt_choice]['id']
        elif field_type == 'number':
            value = int(input("Enter number value: ").strip())
        elif field_type == 'currency':
            value = int(float(input("Enter currency value: ").strip()) * 100)  # Convert to cents
        else:
            value = input("Enter value: ").strip()
        
        # Set the custom field
        result = api.post(f"task/{task_id}/field/{field_id}", {"value": value})
        print(f"\n✓ Custom field set successfully!")
        return result
        
    except Exception as e:
        print(f"\n✗ Failed to set custom field: {e}")
        return None


def add_comment_to_task(api, task_id):
    """Add a comment to a task"""
    print("\n" + "="*60)
    print("ADD COMMENT TO TASK")
    print("="*60)
    
    comment_text = input("Enter your comment: ").strip()
    if not comment_text:
        print("Comment cannot be empty!")
        return None
    
    try:
        comment = api.post(f"task/{task_id}/comment", {"comment_text": comment_text})
        print(f"\n✓ Comment added successfully!")
        return comment
    except Exception as e:
        print(f"\n✗ Failed to add comment: {e}")
        return None


def update_list(api, list_id):
    """Update a list with user input"""
    print("\n" + "="*60)
    print("UPDATE LIST")
    print("="*60)
    
    # Get current list details
    try:
        current = api.get(f"list/{list_id}")
        print(f"\nCurrent list: {current['name']}")
    except Exception as e:
        print(f"Error getting list: {e}")
        return None
    
    name = input(f"\nNew name (leave blank to keep '{current['name']}'): ").strip()
    description = input("New description (leave blank to skip): ").strip()
    
    print("\nPriority levels:")
    print("1 = Urgent, 2 = High, 3 = Normal, 4 = Low")
    priority = input("Priority (1-4, blank to skip): ").strip()
    
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['content'] = description
    if priority and priority.isdigit() and 1 <= int(priority) <= 4:
        update_data['priority'] = int(priority)
    
    if not update_data:
        print("No changes to make!")
        return None
    
    try:
        lst = api.put(f"list/{list_id}", update_data)
        print(f"\n✓ List updated successfully!")
        print(f"  Name: {lst['name']}")
        return lst
    except Exception as e:
        print(f"\n✗ Failed to update list: {e}")
        return None


def update_goal(api, goal_id):
    """Update a goal with user input"""
    print("\n" + "="*60)
    print("UPDATE GOAL")
    print("="*60)
    
    # Get current goal details
    try:
        current = api.get(f"goal/{goal_id}")
        print(f"\nCurrent goal: {current['name']}")
    except Exception as e:
        print(f"Error getting goal: {e}")
        return None
    
    name = input(f"\nNew name (leave blank to keep '{current['name']}'): ").strip()
    description = input("New description (leave blank to skip): ").strip()
    
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    
    if not update_data:
        print("No changes to make!")
        return None
    
    try:
        goal = api.put(f"goal/{goal_id}", update_data)
        print(f"\n✓ Goal updated successfully!")
        print(f"  Name: {goal['goal']['name']}")
        return goal
    except Exception as e:
        print(f"\n✗ Failed to update goal: {e}")
        return None


def create_doc(api, workspace_id):
    """Create a new doc"""
    print("\n" + "="*60)
    print("CREATE NEW DOC")
    print("="*60)
    
    name = input("Doc name/title: ").strip()
    if not name:
        print("Doc name is required!")
        return None
    
    try:
        doc_data = {
            "name": name,
            "create_page": True
        }
        doc = api.post(f"workspaces/{workspace_id}/docs", doc_data, use_v3=True)
        print(f"\n✓ Doc created successfully!")
        print(f"  Name: {doc.get('name')}")
        print(f"  ID: {doc.get('id')}")
        return doc
    except Exception as e:
        print(f"\n✗ Failed to create doc: {e}")
        return None


def create_page_in_doc(api, workspace_id, doc_id):
    """Create a page in a doc"""
    print("\n" + "="*60)
    print("CREATE PAGE IN DOC")
    print("="*60)
    
    name = input("Page name: ").strip()
    if not name:
        print("Page name is required!")
        return None
    
    content = input("Page content (optional): ").strip()
    
    page_data = {
        "name": name
    }
    if content:
        page_data["content"] = content
    
    try:
        page = api.post(f"workspaces/{workspace_id}/docs/{doc_id}/pages", page_data, use_v3=True)
        print(f"\n✓ Page created successfully!")
        print(f"  Name: {page.get('name')}")
        print(f"  ID: {page.get('id')}")
        return page
    except Exception as e:
        print(f"\n✗ Failed to create page: {e}")
        return None


def edit_page(api, workspace_id, doc_id, page_id):
    """Edit a page in a doc"""
    print("\n" + "="*60)
    print("EDIT PAGE")
    print("="*60)
    
    name = input("New page name (leave blank to skip): ").strip()
    content = input("New page content (leave blank to skip): ").strip()
    
    update_data = {}
    if name:
        update_data['name'] = name
    if content:
        update_data['content'] = content
    
    if not update_data:
        print("No changes to make!")
        return None
    
    try:
        page = api.put(f"workspaces/{workspace_id}/docs/{doc_id}/pages/{page_id}", update_data, use_v3=True)
        print(f"\n✓ Page updated successfully!")
        print(f"  Name: {page.get('name')}")
        return page
    except Exception as e:
        print(f"\n✗ Failed to update page: {e}")
        return None


def create_doc_in_space(api, workspace_id, space_id):
    """Create a new doc linked to a specific space"""
    print("\n" + "="*60)
    print("CREATE NEW DOC IN SPACE")
    print("="*60)
    
    name = input("Doc name/title: ").strip()
    if not name:
        print("Doc name is required!")
        return None
    
    try:
        doc_data = {
            "name": name,
            "parent": {
                "id": space_id,
                "type": 1  # Type 1 = Space
            },
            "create_page": True
        }
        doc = api.post(f"workspaces/{workspace_id}/docs", doc_data, use_v3=True)
        print(f"\n✓ Doc created successfully in Space!")
        print(f"  Name: {doc.get('name')}")
        print(f"  ID: {doc.get('id')}")
        return doc
    except Exception as e:
        print(f"\n✗ Failed to create doc: {e}")
        return None


def docs_management_menu(api, workspace_id, team_id):
    """Menu for managing docs"""
    while True:
        print("\n" + "="*60)
        print("DOCS MANAGEMENT")
        print("="*60)
        print("1. View all docs")
        print("2. Create new doc (workspace level)")
        print("3. Create new doc in a Space")
        print("4. Create page in a doc")
        print("5. Edit a page")
        print("0. Go back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            try:
                docs = api.get(f"workspaces/{workspace_id}/docs?deleted=false&archived=false&limit=50", use_v3=True)
                print(f"\n✓ Found {len(docs.get('docs', []))} doc(s)")
                for doc in docs.get('docs', []):
                    print(f"\n  • {doc.get('name', 'Untitled')}")
                    print(f"    ID: {doc['id']}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "2":
            create_doc(api, workspace_id)
        
        elif choice == "3":
            try:
                # Get spaces first
                spaces = api.get(f"team/{team_id}/space?archived=false")
                space = select_from_list(spaces['spaces'], "space")
                if space:
                    create_doc_in_space(api, workspace_id, space['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "4":
            try:
                docs = api.get(f"workspaces/{workspace_id}/docs?deleted=false&archived=false&limit=50", use_v3=True)
                doc = select_from_list(docs.get('docs', []), "doc")
                if doc:
                    create_page_in_doc(api, workspace_id, doc['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "5":
            try:
                docs = api.get(f"workspaces/{workspace_id}/docs?deleted=false&archived=false&limit=50", use_v3=True)
                doc = select_from_list(docs.get('docs', []), "doc")
                if doc:
                    # Get pages for the doc
                    doc_details = api.get(f"workspaces/{workspace_id}/docs/{doc['id']}", use_v3=True)
                    pages = doc_details.get('pages', [])
                    if pages:
                        page = select_from_list(pages, "page")
                        if page:
                            edit_page(api, workspace_id, doc['id'], page['id'])
                    else:
                        print("\n⚠️  No pages found in this doc!")
            except Exception as e:
                print(f"✗ Error: {e}")


def goals_management_menu(api, team_id):
    """Menu for managing goals"""
    while True:
        print("\n" + "="*60)
        print("GOALS MANAGEMENT")
        print("="*60)
        print("1. View all goals")
        print("2. Update a goal")
        print("0. Go back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            try:
                goals = api.get(f"team/{team_id}/goal")
                print(f"\n✓ Found {len(goals.get('goals', []))} goal(s)")
                for goal in goals.get('goals', []):
                    print(f"\n  • {goal['name']}")
                    print(f"    ID: {goal['id']}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "2":
            try:
                goals = api.get(f"team/{team_id}/goal")
                goal = select_from_list(goals.get('goals', []), "goal")
                if goal:
                    update_goal(api, goal['id'])
            except Exception as e:
                print(f"✗ Error: {e}")


def task_management_menu(api, list_id):
    """Menu for managing tasks in a list"""
    while True:
        print("\n" + "="*60)
        print("TASK MANAGEMENT MENU")
        print("="*60)
        print("1. View all tasks")
        print("2. Create new task")
        print("3. Update existing task")
        print("4. Delete task")
        print("5. View task details")
        print("6. Update this list")
        print("\n--- Advanced Task Features ---")
        print("7. Create subtask")
        print("8. Add checklist to task")
        print("9. Add task dependency")
        print("10. Track time on task")
        print("11. Set custom field")
        print("12. Add comment to task")
        print("0. Go back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false&subtasks=true")
                print(f"\n✓ Found {len(tasks['tasks'])} task(s)")
                for task in tasks['tasks']:
                    indent = "  "
                    if task.get('parent'):
                        indent = "    ↳ "  # Show subtasks with indentation
                    
                    print(f"\n{indent}• {task['name']}")
                    print(f"{indent}  ID: {task['id']}")
                    print(f"{indent}  Status: {task['status']['status']}")
                    
                    # Display dates if available
                    if task.get('start_date'):
                        start_ts = int(task['start_date']) / 1000
                        start_dt = datetime.fromtimestamp(start_ts)
                        print(f"{indent}  Start: {start_dt.strftime('%Y-%m-%d %H:%M')}")
                    
                    if task.get('due_date'):
                        due_ts = int(task['due_date']) / 1000
                        due_dt = datetime.fromtimestamp(due_ts)
                        print(f"{indent}  Due: {due_dt.strftime('%Y-%m-%d %H:%M')}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "2":
            create_custom_task(api, list_id)
        
        elif choice == "3":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    update_existing_task(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "4":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    confirm = input(f"\nAre you sure you want to delete '{task['name']}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        api.delete(f"task/{task['id']}")
                        print(f"\n✓ Task deleted!")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "5":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    details = api.get(f"task/{task['id']}")
                    print(f"\n{'='*60}")
                    print(f"TASK DETAILS")
                    print('='*60)
                    print(f"Name: {details['name']}")
                    print(f"Description: {details.get('description', 'N/A')}")
                    print(f"Status: {details['status']['status']}")
                    print(f"Priority: {details.get('priority', {}).get('priority', 'N/A')}")
                    print(f"Creator: {details['creator']['username']}")
                    
                    # Display dates
                    if details.get('start_date'):
                        start_ts = int(details['start_date']) / 1000
                        start_dt = datetime.fromtimestamp(start_ts)
                        print(f"Start Date: {start_dt.strftime('%Y-%m-%d %H:%M')}")
                    
                    if details.get('due_date'):
                        due_ts = int(details['due_date']) / 1000
                        due_dt = datetime.fromtimestamp(due_ts)
                        print(f"Due Date: {due_dt.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Display checklists
                    if details.get('checklists'):
                        print(f"\nChecklists: {len(details['checklists'])}")
                        for cl in details['checklists']:
                            print(f"  • {cl['name']} ({len(cl.get('items', []))} items)")
                    
                    # Display time tracked
                    if details.get('time_spent'):
                        hours = int(details['time_spent']) / 3600000
                        print(f"Time Tracked: {hours:.2f} hours")
                    
                    print(f"\nURL: {details['url']}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "6":
            update_list(api, list_id)
        
        elif choice == "7":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    create_subtask(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "8":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    add_checklist_to_task(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "9":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    add_task_dependency(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "10":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    track_time_on_task(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "11":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    set_custom_field(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "12":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                task = select_from_list(tasks['tasks'], "task")
                if task:
                    add_comment_to_task(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")


def main():
    """Main interactive program"""
    print("\n" + "="*60)
    print("CLICKUP INTERACTIVE API MANAGER")
    print("="*60)
    
    API_TOKEN = "pk_260557758_AKSYRDQYSK0X665XFSPIK1N4FT5ZZ5GZ"
    api = ClickUpAPI(API_TOKEN)
    
    # Authenticate
    try:
        user = api.get("user")
        print(f"\n✓ Authenticated as: {user['user']['username']}")
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return
    
    # Get workspace - let user select
    try:
        teams = api.get("team")
        workspace = select_from_list(teams['teams'], "workspace")
        if not workspace:
            print("\n✗ No workspace selected. Exiting...")
            return
        print(f"✓ Selected workspace: {workspace['name']}")
    except Exception as e:
        print(f"\n✗ Failed to get workspaces: {e}")
        return
    
    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Manage Tasks")
        print("2. Manage Docs")
        print("3. Manage Goals")
        print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            print("\nExiting...")
            break
        
        elif choice == "1":
            try:
                # Get spaces
                spaces = api.get(f"team/{workspace['id']}/space?archived=false")
                space = select_from_list(spaces['spaces'], "space")
                if not space:
                    continue
                
                # Get lists
                lists = api.get(f"space/{space['id']}/list?archived=false")
                lst = select_from_list(lists['lists'], "list")
                if not lst:
                    continue
                
                # Enter task management menu
                task_management_menu(api, lst['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "2":
            docs_management_menu(api, workspace['id'], workspace['id'])
        
        elif choice == "3":
            goals_management_menu(api, workspace['id'])


if __name__ == "__main__":
    main()