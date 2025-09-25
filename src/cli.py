import cmd
import sys
from datetime import date
from typing import Dict, Any, Optional
from .task_manager import TaskManager
from .database import DatabaseConnection
from .auth import AuthenticationManager
from .utils import InputValidator, DateUtils

class TaskManagerCLI(cmd.Cmd):
    """Command-line interface for the Multi-User Task Management application."""
    
    intro = """
╔══════════════════════════════════════════════════════════════╗
║                 TASK MANAGEMENT APPLICATION                  ║
║                    Multi-User Edition                        ║
╚══════════════════════════════════════════════════════════════╝

Type 'help' for available commands or 'menu' to see the main menu.
"""
    prompt = 'task_manager> '
    
    def __init__(self, task_manager: TaskManager, auth_manager: AuthenticationManager):
        super().__init__()
        self.task_manager = task_manager
        self.auth = auth_manager
        self.validator = InputValidator()
        self.date_utils = DateUtils()
        
        # Try to auto-login or show auth menu
        if not self.auth.is_authenticated():
            self.show_auth_menu()
        else:
            self.prompt = f'task_manager({self.auth.current_user["username"]})> '
    
    def show_auth_menu(self):
        """Show authentication menu."""
        print("\n🔐 Task Manager - Authentication Required")
        print("=" * 50)
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        
        while True:
            choice = input("\nChoose option (1-3): ").strip()
            
            if choice == '1':
                if self.auth.login():
                    self.task_manager._load_tasks()  # Load user's tasks
                    self.prompt = f'task_manager({self.auth.current_user["username"]})> '
                    self.display_statistics()
                    break
                else:
                    print("❌ Login failed. Please try again.")
            elif choice == '2':
                if self.auth.register_user():
                    print("✅ Registration successful! Please log in.")
                else:
                    print("❌ Registration failed. Please try again.")
            elif choice == '3':
                print("👋 Goodbye!")
                exit()
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    def preloop(self) -> None:
        """Display welcome message for authenticated user."""
        if self.auth.is_authenticated():
            self.display_statistics()
    
    def display_statistics(self) -> None:
        """Display task statistics for current user."""
        if not self.auth.is_authenticated():
            print("❌ Please log in to view statistics")
            return
            
        stats = self.task_manager.get_statistics()
        user = self.auth.current_user['username']
        print(f"\n📊 Task Statistics for {user}:")
        print(f"   Total Tasks: {stats['total_tasks']}")
        print(f"   ✅ Completed: {stats['completed']}")
        print(f"   ⏳ Pending: {stats['pending']}")
        print(f"   🔄 In Progress: {stats['in_progress']}")
        print(f"   ⚠️  High Priority: {stats['high_priority']}")
        print(f"   📅 Overdue: {stats['overdue']}")
        print()
    
    def do_menu(self, arg: str) -> None:
        """Display the main menu."""
        if not self.auth.is_authenticated():
            print("❌ Please log in first")
            self.show_auth_menu()
            return
            
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. add      - Add a new task")
        print("2. list     - List all tasks (with optional filters)")
        print("3. update   - Update a task's details")
        print("4. complete - Mark a task as completed")
        print("5. delete   - Delete a task")
        print("6. stats    - Show task statistics")
        print("7. search   - Search tasks by keyword")
        print("8. whoami   - Show current user information")
        print("9. logout   - Log out current user")
        print("10. help    - Show available commands")
        print("11. exit    - Exit the application")
        print("="*60)
    
    def do_whoami(self, arg: str) -> None:
        """Show current user information."""
        if not self.auth.is_authenticated():
            print("❌ Not logged in")
            return
            
        user = self.auth.current_user
        print(f"\n👤 User Information:")
        print(f"   Username: {user['username']}")
        print(f"   User ID: {user['user_id']}")
        if 'email' in user and user['email']:
            print(f"   Email: {user['email']}")
        if 'created_at' in user and user['created_at']:
            print(f"   Member since: {user['created_at']}")
    
    def do_logout(self, arg: str) -> None:
        """Log out current user."""
        if not self.auth.is_authenticated():
            print("ℹ️  No user is currently logged in")
            return
            
        username = self.auth.current_user['username']
        self.auth.logout()
        self.task_manager._load_tasks()  # Clear tasks from memory
        self.prompt = 'task_manager> '
        print(f"✅ Logged out successfully. Goodbye, {username}!")
        self.show_auth_menu()
    
    def do_add(self, arg: str) -> None:
        """Add a new task.
        Usage: add
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in to add tasks")
            self.show_auth_menu()
            return
            
        try:
            print("\n🎯 ADD NEW TASK")
            print("-" * 40)
            
            title = input("Title: ").strip()
            description = input("Description (optional): ").strip()
            due_date_str = input("Due date (YYYY-MM-DD, optional): ").strip()
            priority = input("Priority (Low/Medium/High) [Medium]: ").strip() or "Medium"
            
            # Validate inputs
            title = self.validator.validate_string(title, "Title")
            due_date = self.validator.validate_date(due_date_str) if due_date_str else None
            priority = self.validator.validate_priority(priority)
            
            if self.task_manager.add_task(title, description, due_date, priority):
                print("✅ Task added successfully!")
            else:
                print("❌ Failed to add task.")
                
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def do_list(self, arg: str) -> None:
        """List tasks with optional filtering.
        Usage: list [status=STATUS] [priority=PRIORITY] [due_date=DATE]
        Examples:
          list
          list status=Completed
          list priority=High status=Pending
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in to list tasks")
            self.show_auth_menu()
            return
            
        try:
            filters = self._parse_filters(arg)
            tasks = self.task_manager.list_tasks(filters)
            
            if not tasks:
                print("📭 No tasks found.")
                return
            
            user = self.auth.current_user['username']
            print(f"\n📋 TASK LIST for {user} ({len(tasks)} tasks)")
            print("="*80)
            
            for i, task in enumerate(tasks, 1):
                status_icon = "✅" if task.status == "Completed" else "🔄" if task.status == "In Progress" else "⏳"
                priority_icon = "⚡" if task.priority_level == "High" else "🔶" if task.priority_level == "Medium" else "🔷"
                due_info = f"Due: {self.date_utils.format_date(task.due_date)}"
                days_left = self.date_utils.days_until_due(task.due_date)
                
                if days_left is not None:
                    if days_left < 0:
                        due_info += " 📅 OVERDUE!"
                    elif days_left == 0:
                        due_info += " 📅 Due today!"
                    elif days_left <= 3:
                        due_info += f" 📅 {days_left} days left!"
                
                print(f"{i:2d}. {status_icon} {priority_icon} {task.title}")
                print(f"     ID: {task.task_id} | Status: {task.status} | Priority: {task.priority_level}")
                print(f"     {due_info}")
                if task.description:
                    print(f"     Description: {task.description[:100]}{'...' if len(task.description) > 100 else ''}")
                print("-" * 80)
                
        except Exception as e:
            print(f"❌ Error listing tasks: {e}")
    
    def _parse_filters(self, filter_str: str) -> Dict[str, Any]:
        """Parse filter string into dictionary."""
        filters = {}
        if not filter_str:
            return filters
        
        try:
            for part in filter_str.split():
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.lower().strip()
                    value = value.strip()
                    
                    if key == 'status':
                        filters['status'] = self.validator.validate_status(value)
                    elif key == 'priority':
                        filters['priority'] = self.validator.validate_priority(value)
                    elif key == 'due_date':
                        filters['due_date'] = self.validator.validate_date(value)
        except ValueError as e:
            print(f"⚠️  Filter warning: {e}")
        
        return filters
    
    def do_update(self, arg: str) -> None:
        """Update a task's details.
        Usage: update TASK_ID
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in to update tasks")
            self.show_auth_menu()
            return
            
        try:
            if not arg:
                task_id_str = input("Enter task ID to update: ").strip()
            else:
                task_id_str = arg.strip()
            
            task_id = self.validator.validate_task_id(task_id_str)
            task = self.task_manager.get_task(task_id)
            
            if not task:
                print(f"❌ Task with ID {task_id} not found or you don't have permission to access it.")
                return
            
            print(f"\n✏️  UPDATE TASK {task_id}: {task.title}")
            print("-" * 50)
            
            updates = {}
            
            # Get updated values
            new_title = input(f"Title [{task.title}]: ").strip()
            if new_title:
                updates['title'] = self.validator.validate_string(new_title, "Title")
            
            new_desc = input(f"Description [{task.description}]: ").strip()
            if new_desc != task.description:
                updates['description'] = new_desc
            
            current_due = self.date_utils.format_date(task.due_date)
            new_due = input(f"Due date [{current_due}]: ").strip()
            if new_due and new_due != current_due:
                updates['due_date'] = self.validator.validate_date(new_due)
            
            new_priority = input(f"Priority ({task.priority_level}): ").strip()
            if new_priority and new_priority != task.priority_level:
                updates['priority_level'] = self.validator.validate_priority(new_priority)
            
            new_status = input(f"Status ({task.status}): ").strip()
            if new_status and new_status != task.status:
                updates['status'] = self.validator.validate_status(new_status)
            
            if updates and self.task_manager.update_task(task_id, **updates):
                print("✅ Task updated successfully!")
            else:
                print("ℹ️  No changes made or update failed.")
                
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error updating task: {e}")
    
    def do_complete(self, arg: str) -> None:
        """Mark a task as completed.
        Usage: complete TASK_ID
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in to complete tasks")
            self.show_auth_menu()
            return
            
        try:
            if not arg:
                task_id_str = input("Enter task ID to mark as completed: ").strip()
            else:
                task_id_str = arg.strip()
            
            task_id = self.validator.validate_task_id(task_id_str)
            
            if self.task_manager.mark_completed(task_id):
                print("✅ Task marked as completed!")
            else:
                print("❌ Failed to mark task as completed. Task not found or no permission.")
                
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error completing task: {e}")
    
    def do_delete(self, arg: str) -> None:
        """Delete a task.
        Usage: delete TASK_ID
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in to delete tasks")
            self.show_auth_menu()
            return
            
        try:
            if not arg:
                task_id_str = input("Enter task ID to delete: ").strip()
            else:
                task_id_str = arg.strip()
            
            task_id = self.validator.validate_task_id(task_id_str)
            task = self.task_manager.get_task(task_id)
            
            if not task:
                print(f"❌ Task with ID {task_id} not found or you don't have permission to access it.")
                return
            
            print(f"\n🗑️  DELETE TASK")
            print(f"Title: {task.title}")
            print(f"ID: {task.task_id}")
            
            confirm = input("Are you sure you want to delete this task? (y/N): ").strip().lower()
            if confirm in ('y', 'yes'):
                if self.task_manager.delete_task(task_id):
                    print("✅ Task deleted successfully!")
                else:
                    print("❌ Failed to delete task.")
            else:
                print("ℹ️  Deletion cancelled.")
                
        except ValueError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
    
    def do_stats(self, arg: str) -> None:
        """Display task statistics."""
        if not self.auth.is_authenticated():
            print("❌ Please log in to view statistics")
            self.show_auth_menu()
            return
            
        self.display_statistics()
    
    def do_search(self, arg: str) -> None:
        """Search tasks by keyword in title or description.
        Usage: search KEYWORD
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in to search tasks")
            self.show_auth_menu()
            return
            
        try:
            if not arg:
                keyword = input("Enter search keyword: ").strip()
            else:
                keyword = arg.strip()
            
            if not keyword:
                print("❌ Please provide a search keyword.")
                return
            
            tasks = self.task_manager.list_tasks()
            matching_tasks = []
            
            for task in tasks:
                if (keyword.lower() in task.title.lower() or 
                    keyword.lower() in task.description.lower()):
                    matching_tasks.append(task)
            
            if not matching_tasks:
                print(f"🔍 No tasks found matching '{keyword}'.")
                return
            
            user = self.auth.current_user['username']
            print(f"\n🔍 SEARCH RESULTS for '{keyword}' ({len(matching_tasks)} tasks for {user})")
            print("="*80)
            
            for i, task in enumerate(matching_tasks, 1):
                status_icon = "✅" if task.status == "Completed" else "🔄" if task.status == "In Progress" else "⏳"
                print(f"{i:2d}. {status_icon} {task.title} (ID: {task.task_id})")
                if task.description:
                    desc_lower = task.description.lower()
                    keyword_lower = keyword.lower()
                    if keyword_lower in desc_lower:
                        start = desc_lower.find(keyword_lower)
                        excerpt = task.description[max(0, start-20):start+50]
                        print(f"     ...{excerpt}...")
                print("-" * 80)
                
        except Exception as e:
            print(f"❌ Error searching tasks: {e}")
    
    def do_users(self, arg: str) -> None:
        """List all users (admin only).
        Usage: users
        """
        if not self.auth.is_authenticated():
            print("❌ Please log in first")
            return
            
        # Basic admin check (you might want to enhance this)
        if self.auth.current_user['username'] != 'admin':
            print("❌ Administrator access required")
            return
            
        try:
            users = self.task_manager.db.fetch_all("SELECT user_id, username, email, created_at FROM users ORDER BY created_at")
            
            if not users:
                print("📭 No users found.")
                return
            
            print(f"\n👥 USER LIST ({len(users)} users)")
            print("="*60)
            
            for user in users:
                print(f"ID: {user['user_id']} | Username: {user['username']}")
                if user['email']:
                    print(f"   Email: {user['email']}")
                print(f"   Created: {user['created_at']}")
                print("-" * 60)
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")
    
    def do_clear(self, arg: str) -> None:
        """Clear the screen."""
        print("\n" * 100)
    
    def do_exit(self, arg: str) -> bool:
        """Exit the application."""
        if self.auth.is_authenticated():
            username = self.auth.current_user['username']
            print(f"\n👋 Thank you for using Task Manager, {username}! Goodbye!")
        else:
            print("\n👋 Goodbye!")
        return True
    
    def emptyline(self) -> None:
        """Do nothing when empty line is entered."""
        pass
    
    def default(self, line: str) -> None:
        """Handle unknown commands."""
        print(f"❌ Unknown command: {line}")
        print("Type 'help' for available commands or 'menu' for the main menu.")

def main():
    """Main entry point for the CLI application."""
    try:
        # Initialize database connection
        db = DatabaseConnection()
        if not db.connect():
            print("❌ Failed to connect to database. Please check your database configuration.")
            sys.exit(1)
        
        # Initialize authentication manager
        auth_manager = AuthenticationManager(db)
        
        # Initialize task manager
        task_manager = TaskManager(db, auth_manager)
        
        # Start CLI
        cli = TaskManagerCLI(task_manager, auth_manager)
        cli.cmdloop()
        
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.disconnect()

if __name__ == '__main__':
    main()