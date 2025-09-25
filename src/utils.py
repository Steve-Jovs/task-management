from datetime import datetime, date
from typing import Any, Optional
import re

class InputValidator:
    """Handles input validation for the application."""
    
    @staticmethod
    def validate_string(value: str, field_name: str, max_length: int = 255) -> str:
        """Validate string input."""
        if not value or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        
        value = value.strip()
        if len(value) > max_length:
            raise ValueError(f"{field_name} cannot exceed {max_length} characters")
        
        # Basic sanitization
        if re.search(r'[<>{}]', value):
            raise ValueError(f"{field_name} contains invalid characters")
        
        return value
    
    @staticmethod
    def validate_date(date_str: str) -> Optional[date]:
        """Validate and parse date string."""
        if not date_str:
            return None
        
        try:
            # Support multiple date formats
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y.%m.%d'):
                try:
                    parsed_date = datetime.strptime(date_str, fmt).date()
                    if parsed_date < date.today():
                        raise ValueError("Date cannot be in the past")
                    return parsed_date
                except ValueError:
                    continue
            
            raise ValueError("Invalid date format. Use YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY")
        except ValueError as e:
            raise ValueError(f"Invalid date: {e}")
    
    @staticmethod
    def validate_priority(priority: str) -> str:
        """Validate priority level."""
        valid_priorities = {'Low', 'Medium', 'High'}
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return priority
    
    @staticmethod
    def validate_status(status: str) -> str:
        """Validate task status."""
        valid_statuses = {'Pending', 'In Progress', 'Completed'}
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return status
    
    @staticmethod
    def validate_task_id(task_id: str) -> int:
        """Validate task ID."""
        try:
            task_id_int = int(task_id)
            if task_id_int <= 0:
                raise ValueError("Task ID must be a positive integer")
            return task_id_int
        except ValueError:
            raise ValueError("Task ID must be a valid integer")

class DateUtils:
    """Utility functions for date operations."""
    
    @staticmethod
    def format_date(dt: Optional[date]) -> str:
        """Format date for display."""
        if not dt:
            return "Not set"
        return dt.strftime('%Y-%m-%d')
    
    @staticmethod
    def days_until_due(due_date: Optional[date]) -> Optional[int]:
        """Calculate days until due date."""
        if not due_date:
            return None
        return (due_date - date.today()).days