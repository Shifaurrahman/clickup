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
    
    task_data = {
        "name": name,
        "description": description,
        "status": status,
        "priority": priority,
    }
    
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
    except Exception as e:
        print(f"Error getting task: {e}")
        return None
    
    name = input(f"\nNew name (leave blank to keep '{current['name']}'): ").strip()
    description = input("New description (leave blank to skip): ").strip()
    status = input("New status (to do/in progress/complete, blank to skip): ").strip().lower()
    
    update_data = {}
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    if status:
        update_data['status'] = status
    
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


def task_management_menu(api, list_id):
    """Menu for managing tasks in a list"""
    while True:
        print("\n" + "="*60)
        print("TASK MANAGEMENT MENU")
        print("="*60)
        print("1. View all tasks")
        print("2. Create new task")
        print("3. Update existing task")
        print("4. Add comment to task")
        print("5. Delete task")
        print("6. View task details")
        print("0. Go back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            try:
                tasks = api.get(f"list/{list_id}/task?archived=false")
                print(f"\n✓ Found {len(tasks['tasks'])} task(s)")
                for task in tasks['tasks']:
                    print(f"\n  • {task['name']}")
                    print(f"    ID: {task['id']}")
                    print(f"    Status: {task['status']['status']}")
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
                    add_comment_to_task(api, task['id'])
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif choice == "5":
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
        
        elif choice == "6":
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
                    print(f"URL: {details['url']}")
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
    
    while True:
        # Get workspaces
        try:
            teams = api.get("team")
            workspace = select_from_list(teams['teams'], "workspace")
            if not workspace:
                print("\nExiting...")
                break
            
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
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            continue


if __name__ == "__main__":
    main()