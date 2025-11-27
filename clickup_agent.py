import requests
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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


class IntelligentClickUpAgent:
    """AI-Powered ClickUp Agent for task creation and analysis"""
    
    def __init__(self, clickup_api_token, openai_api_key):
        self.clickup = ClickUpAPI(clickup_api_token)
        self.openai = OpenAI(api_key=openai_api_key)
    
    def create_task_from_natural_language(self, list_id, description):
        """
        Create a task from natural language description using AI
        Example: "Schedule a high priority meeting with the dev team next Friday at 2pm 
                  to discuss the new API integration project"
        """
        print(f"\n🤖 AI is analyzing your request...")
        
        prompt = f"""Parse this task description and extract structured information:

Task Description: {description}

Return ONLY a JSON object with these fields (no markdown, no explanation):
{{
    "name": "brief task title",
    "description": "detailed description",
    "priority": 1-4 (1=urgent, 2=high, 3=normal, 4=low),
    "status": "to do" or "in progress" or "complete"
}}

Be concise but capture all important details."""

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a task parser. Return only valid JSON, no markdown, no explanation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            task_data = json.loads(response_text.strip())
            
            print(f"✓ AI parsed task:")
            print(f"  Name: {task_data['name']}")
            print(f"  Priority: {task_data['priority']}")
            print(f"  Status: {task_data['status']}")
            
            # Create task in ClickUp
            task = self.clickup.post(f"list/{list_id}/task", task_data)
            print(f"\n✓ Task created successfully!")
            print(f"  ID: {task['id']}")
            print(f"  URL: {task['url']}")
            
            return task
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def analyze_tasks(self, list_id):
        """
        Analyze all tasks in a list and provide AI-powered insights
        """
        print(f"\n🤖 Fetching and analyzing tasks...")
        
        try:
            # Get all tasks
            response = self.clickup.get(f"list/{list_id}/task?archived=false")
            tasks = response.get('tasks', [])
            
            if not tasks:
                print("No tasks found to analyze!")
                return None
            
            print(f"✓ Found {len(tasks)} task(s)")
            
            # Prepare task summary for AI
            task_summary = []
            for task in tasks:
                task_summary.append({
                    "name": task['name'],
                    "status": task['status']['status'],
                    "priority": task.get('priority', {}).get('priority', 'none'),
                    "description": task.get('description', 'N/A')
                })
            
            prompt = f"""Analyze these tasks and provide insights:

Tasks:
{json.dumps(task_summary, indent=2)}

Provide:
1. Overall project health assessment
2. Task distribution by status
3. Priority breakdown
4. Potential bottlenecks or risks
5. Recommendations for improvement

Be concise and actionable."""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a project analyst. Provide clear, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            print("\n" + "="*60)
            print("AI ANALYSIS REPORT")
            print("="*60)
            print(analysis)
            print("="*60)
            
            return analysis
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def smart_task_update(self, task_id, update_request):
        """
        Update a task using natural language
        Example: "Change priority to urgent and mark as in progress"
        """
        print(f"\n🤖 AI is processing your update request...")
        
        try:
            # Get current task
            current_task = self.clickup.get(f"task/{task_id}")
            
            prompt = f"""Based on this update request, generate the changes needed:

Current Task:
- Name: {current_task['name']}
- Status: {current_task['status']['status']}
- Priority: {current_task.get('priority', {}).get('priority', 'none')}

Update Request: {update_request}

Return ONLY a JSON object with fields that need updating (no markdown):
{{
    "name": "new name if changed",
    "status": "to do/in progress/complete if changed",
    "priority": 1-4 if changed,
    "description": "new description if changed"
}}

Only include fields that should be updated. If no change needed, return {{}}.
"""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a task update parser. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            update_data = json.loads(response_text.strip())
            
            if not update_data:
                print("No changes detected!")
                return None
            
            print(f"✓ AI determined these updates:")
            for key, value in update_data.items():
                print(f"  {key}: {value}")
            
            # Apply updates
            updated_task = self.clickup.put(f"task/{task_id}", update_data)
            print(f"\n✓ Task updated successfully!")
            
            return updated_task
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def generate_task_report(self, list_id):
        """
        Generate a formatted report of all tasks
        """
        print(f"\n🤖 Generating task report...")
        
        try:
            response = self.clickup.get(f"list/{list_id}/task?archived=false")
            tasks = response.get('tasks', [])
            
            if not tasks:
                print("No tasks found!")
                return None
            
            task_details = []
            for task in tasks:
                task_details.append({
                    "name": task['name'],
                    "status": task['status']['status'],
                    "priority": task.get('priority', {}).get('priority', 'none'),
                    "creator": task['creator']['username'],
                    "url": task['url']
                })
            
            prompt = f"""Create a professional project status report from these tasks:

{json.dumps(task_details, indent=2)}

Format as:
## Project Status Report

### Summary
[Brief overview]

### Task Breakdown
[Organized by status]

### Key Metrics
[Statistics]

### Action Items
[What needs attention]

Be professional and concise."""

            response = self.openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional report writer. Create clear, structured reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            report = response.choices[0].message.content
            
            print("\n" + "="*60)
            print(report)
            print("="*60)
            
            return report
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return None


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


def main():
    """Main interactive program"""
    print("\n" + "="*60)
    print("🤖 CLICKUP INTELLIGENT AGENT")
    print("="*60)
    
    # Load configuration from .env file
    CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Validate API keys
    if not CLICKUP_API_TOKEN:
        print("\n⚠️  CLICKUP_API_TOKEN not found in .env file!")
        print("Please create a .env file with:")
        print("CLICKUP_API_TOKEN=your-clickup-token")
        return
    
    if not OPENAI_API_KEY:
        print("\n⚠️  OPENAI_API_KEY not found in .env file!")
        print("Please add to .env file:")
        print("OPENAI_API_KEY=your-openai-key")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
        return
    
    # Initialize agent
    agent = IntelligentClickUpAgent(CLICKUP_API_TOKEN, OPENAI_API_KEY)
    
    # Authenticate
    try:
        user = agent.clickup.get("user")
        print(f"\n✓ Authenticated as: {user['user']['username']}")
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return
    
    while True:
        try:
            # Get workspace
            teams = agent.clickup.get("team")
            workspace = select_from_list(teams['teams'], "workspace")
            if not workspace:
                print("\nExiting...")
                break
            
            # Get space
            spaces = agent.clickup.get(f"team/{workspace['id']}/space?archived=false")
            space = select_from_list(spaces['spaces'], "space")
            if not space:
                continue
            
            # Get list
            lists = agent.clickup.get(f"space/{space['id']}/list?archived=false")
            lst = select_from_list(lists['lists'], "list")
            if not lst:
                continue
            
            # AI Agent Menu
            while True:
                print("\n" + "="*60)
                print("🤖 AI AGENT MENU")
                print("="*60)
                print("1. 🧠 Create task from natural language")
                print("2. 📊 Analyze all tasks (AI insights)")
                print("3. ✏️  Update task with natural language")
                print("4. 📝 Generate task report")
                print("5. 👀 View all tasks (simple list)")
                print("0. Go back")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == "0":
                    break
                
                elif choice == "1":
                    print("\nExamples:")
                    print("  - 'High priority bug fix for login issue, assign to dev team'")
                    print("  - 'Schedule team meeting Friday 3pm to review Q4 goals'")
                    description = input("\nDescribe your task: ").strip()
                    if description:
                        agent.create_task_from_natural_language(lst['id'], description)
                
                elif choice == "2":
                    agent.analyze_tasks(lst['id'])
                
                elif choice == "3":
                    # Get tasks
                    response = agent.clickup.get(f"list/{lst['id']}/task?archived=false")
                    tasks = response.get('tasks', [])
                    task = select_from_list(tasks, "task")
                    if task:
                        print("\nExamples:")
                        print("  - 'Mark as complete and add high priority'")
                        print("  - 'Change status to in progress'")
                        update_request = input("\nHow to update: ").strip()
                        if update_request:
                            agent.smart_task_update(task['id'], update_request)
                
                elif choice == "4":
                    agent.generate_task_report(lst['id'])
                
                elif choice == "5":
                    try:
                        response = agent.clickup.get(f"list/{lst['id']}/task?archived=false")
                        tasks = response.get('tasks', [])
                        print(f"\n✓ Found {len(tasks)} task(s)")
                        for task in tasks:
                            print(f"\n  • {task['name']}")
                            print(f"    Status: {task['status']['status']}")
                            print(f"    Priority: {task.get('priority', {}).get('priority', 'N/A')}")
                    except Exception as e:
                        print(f"✗ Error: {e}")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            continue


if __name__ == "__main__":
    main()