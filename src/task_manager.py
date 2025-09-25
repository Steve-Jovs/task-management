from typing import List, Optional, Dict, Any
from datetime import date, datetime
import threading
from .models import Task
from .database import DatabaseConnection
from .auth import AuthenticationManager

class TaskManager:
    """Manages task operations with database persistence and user isolation."""
    
    def __init__(self, db_connection: DatabaseConnection, auth_manager: AuthenticationManager):
        self.db = db_connection
        self.auth = auth_manager
        self._tasks: List[Task] = []
        self._lock = threading.Lock()
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load current user's tasks from database into memory."""
        if not self.auth.is_authenticated():
            with self._lock:
                self._tasks.clear()
            return
            
        try:
            user_id = self.auth.get_current_user_id()
            query = "SELECT * FROM tasks WHERE user_id = %s ORDER BY creation_timestamp DESC"
            results = self.db.fetch_all(query, (user_id,))
            
            with self._lock:
                self._tasks.clear()
                for task_data in results:
                    if task_data.get('due_date'):
                        task_data['due_date'] = task_data['due_date']
                    if task_data.get('creation_timestamp'):
                        if isinstance(task_data['creation_timestamp'], str):
                            task_data['creation_timestamp'] = datetime.fromisoformat(
                                task_data['creation_timestamp'].replace('Z', '+00:00')
                            )
                    
                    task = Task.from_dict(task_data)
                    self._tasks.append(task)
        except Exception as e:
            print(f"Error loading tasks: {e}")
    
    def add_task(self, title: str, description: str = "", due_date: Optional[date] = None,
                priority_level: str = "Medium") -> bool:
        """Add a new task for the current user."""
        if not self.auth.is_authenticated():
            print("❌ Please log in to add tasks")
            return False
            
        try:
            user_id = self.auth.get_current_user_id()
            task = Task(title=title, description=description, 
                       due_date=due_date, priority_level=priority_level)
            
            query = """
                INSERT INTO tasks (user_id, title, description, due_date, priority_level, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (user_id, task.title, task.description, task.due_date, 
                     task.priority_level, task.status)
            
            cursor = self.db.execute_query(query, params)
            if cursor:
                task_id = cursor.lastrowid
                task._task_id = task_id
                
                with self._lock:
                    self._tasks.insert(0, task)
                
                print(f"✅ Task added successfully with ID: {task_id}")
                return True
            return False
            
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID (only if owned by current user)."""
        if not self.auth.is_authenticated():
            return None
            
        user_id = self.auth.get_current_user_id()
        
        with self._lock:
            for task in self._tasks:
                if task.task_id == task_id:
                    if self._verify_task_ownership(task_id, user_id):
                        return task
                    return None
        
        if self._verify_task_ownership(task_id, user_id):
            task_data = self.db.fetch_one("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
            if task_data:
                task = Task.from_dict(task_data)
                with self._lock:
                    self._tasks.append(task)
                return task
        
        return None
    
    def _verify_task_ownership(self, task_id: int, user_id: int) -> bool:
        """Verify that the current user owns the specified task."""
        try:
            result = self.db.fetch_one(
                "SELECT user_id FROM tasks WHERE task_id = %s", 
                (task_id,)
            )
            return result and result['user_id'] == user_id
        except Exception:
            return False
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task details (only if owned by current user)."""
        if not self.auth.is_authenticated():
            print("❌ Please log in to update tasks")
            return False
            
        try:
            user_id = self.auth.get_current_user_id()
            
            if not self._verify_task_ownership(task_id, user_id):
                print(f"❌ Task with ID {task_id} not found or access denied")
                return False
            
            task = self.get_task(task_id)
            if not task:
                return False
            
            allowed_fields = {'title', 'description', 'due_date', 'priority_level', 'status'}
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            for field, value in updates.items():
                setattr(task, field, value)
            
            if updates:
                set_clause = ", ".join([f"{field} = %s" for field in updates.keys()])
                query = f"UPDATE tasks SET {set_clause} WHERE task_id = %s AND user_id = %s"
                params = tuple(updates.values()) + (task_id, user_id)
                
                if self.db.execute_query(query, params):
                    print(f"✅ Task {task_id} updated successfully")
                    return True
                return False
            else:
                print("ℹ️  No changes made")
                return True
                
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task from the system (only if owned by current user)."""
        if not self.auth.is_authenticated():
            print("❌ Please log in to delete tasks")
            return False
            
        try:
            user_id = self.auth.get_current_user_id()
            
            if not self._verify_task_ownership(task_id, user_id):
                print(f"❌ Task with ID {task_id} not found or access denied")
                return False
            
            query = "DELETE FROM tasks WHERE task_id = %s AND user_id = %s"
            if self.db.execute_query(query, (task_id, user_id)):
                with self._lock:
                    self._tasks = [task for task in self._tasks if task.task_id != task_id]
                print(f"✅ Task {task_id} deleted successfully")
                return True
            return False
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def list_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """List tasks for current user with optional filtering."""
        if not self.auth.is_authenticated():
            print("❌ Please log in to list tasks")
            return []
            
        with self._lock:
            tasks = self._tasks.copy()
        
        if filters:
            tasks = self._apply_filters(tasks, filters)
        
        return self._sort_tasks(tasks)
    
    def _apply_filters(self, tasks: List[Task], filters: Dict[str, Any]) -> List[Task]:
        """Apply filters to task list."""
        filtered_tasks = tasks
        
        if 'status' in filters:
            filtered_tasks = [t for t in filtered_tasks if t.status == filters['status']]
        
        if 'priority' in filters:
            filtered_tasks = [t for t in filtered_tasks if t.priority_level == filters['priority']]
        
        if 'due_date' in filters:
            filtered_tasks = [t for t in filtered_tasks if t.due_date == filters['due_date']]
        
        return filtered_tasks
    
    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority and due date using custom sorting algorithm."""
        if not tasks:
            return tasks
        
        return self._merge_sort(tasks)
    
    def _merge_sort(self, tasks: List[Task]) -> List[Task]:
        """Merge sort implementation for tasks."""
        if len(tasks) <= 1:
            return tasks
        
        mid = len(tasks) // 2
        left = self._merge_sort(tasks[:mid])
        right = self._merge_sort(tasks[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left: List[Task], right: List[Task]) -> List[Task]:
        """Merge two sorted lists of tasks."""
        merged = []
        i = j = 0
        
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        
        while i < len(left) and j < len(right):
            left_task = left[i]
            right_task = right[j]
            
            left_priority = priority_order.get(left_task.priority_level, 0)
            right_priority = priority_order.get(right_task.priority_level, 0)
            
            if left_priority > right_priority:
                merged.append(left_task)
                i += 1
            elif left_priority < right_priority:
                merged.append(right_task)
                j += 1
            else:
                if left_task.due_date and right_task.due_date:
                    if left_task.due_date < right_task.due_date:
                        merged.append(left_task)
                        i += 1
                    else:
                        merged.append(right_task)
                        j += 1
                elif left_task.due_date:
                    merged.append(left_task)
                    i += 1
                else:
                    merged.append(right_task)
                    j += 1
        
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged
    
    def mark_completed(self, task_id: int) -> bool:
        """Mark a task as completed (only if owned by current user)."""
        return self.update_task(task_id, status='Completed')
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics for current user."""
        if not self.auth.is_authenticated():
            return {
                'total_tasks': 0,
                'completed': 0,
                'pending': 0,
                'in_progress': 0,
                'high_priority': 0,
                'overdue': 0
            }
            
        user_id = self.auth.get_current_user_id()
        
        try:
            # Use individual queries to avoid complex SQL syntax issues
            total_result = self.db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s", (user_id,))
            completed_result = self.db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s AND status = 'Completed'", (user_id,))
            pending_result = self.db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s AND status = 'Pending'", (user_id,))
            in_progress_result = self.db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s AND status = 'In Progress'", (user_id,))
            high_priority_result = self.db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s AND priority_level = 'High'", (user_id,))
            overdue_result = self.db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s AND due_date < CURDATE() AND status != 'Completed'", (user_id,))
            
            return {
                'total_tasks': total_result['count'] if total_result else 0,
                'completed': completed_result['count'] if completed_result else 0,
                'pending': pending_result['count'] if pending_result else 0,
                'in_progress': in_progress_result['count'] if in_progress_result else 0,
                'high_priority': high_priority_result['count'] if high_priority_result else 0,
                'overdue': overdue_result['count'] if overdue_result else 0
            }
            
        except Exception as e:
            print(f"Error getting statistics from database: {e}")
            return self._get_statistics_from_memory()
    
    def _get_statistics_from_memory(self) -> Dict[str, Any]:
        """Fallback method to calculate statistics from in-memory tasks."""
        with self._lock:
            total = len(self._tasks)
            completed = len([t for t in self._tasks if t.status == 'Completed'])
            pending = len([t for t in self._tasks if t.status == 'Pending'])
            in_progress = len([t for t in self._tasks if t.status == 'In Progress'])
            high_priority = len([t for t in self._tasks if t.priority_level == 'High'])
            overdue = len([t for t in self._tasks if t.due_date and t.due_date < date.today() and t.status != 'Completed'])
        
        return {
            'total_tasks': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'high_priority': high_priority,
            'overdue': overdue
        }
    
    def search_tasks(self, keyword: str) -> List[Task]:
        """Search tasks by keyword in title or description."""
        if not self.auth.is_authenticated():
            return []
            
        user_id = self.auth.get_current_user_id()
        
        try:
            query = """
                SELECT * FROM tasks 
                WHERE user_id = %s 
                AND (title LIKE %s OR description LIKE %s)
                ORDER BY creation_timestamp DESC
            """
            search_term = f"%{keyword}%"
            results = self.db.fetch_all(query, (user_id, search_term, search_term))
            
            matching_tasks = []
            for task_data in results:
                task = Task.from_dict(task_data)
                matching_tasks.append(task)
            
            return matching_tasks
            
        except Exception as e:
            print(f"Error searching tasks: {e}")
            with self._lock:
                matching_tasks = []
                for task in self._tasks:
                    if (keyword.lower() in task.title.lower() or 
                        keyword.lower() in task.description.lower()):
                        matching_tasks.append(task)
                return matching_tasks
    
    def refresh_tasks(self) -> None:
        """Reload tasks from database (useful after user login/logout)."""
        self._load_tasks()