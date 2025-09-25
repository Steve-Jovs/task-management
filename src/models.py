from datetime import datetime, date
from typing import Optional, Dict, Any
import re

class Task:
    """Represents a single task with validation and business logic."""
    
    VALID_PRIORITIES = {'Low', 'Medium', 'High'}
    VALID_STATUSES = {'Pending', 'In Progress', 'Completed'}
    
    def __init__(self, task_id: Optional[int] = None, title: str = "", 
                 description: str = "", due_date: Optional[date] = None,
                 priority_level: str = "Medium", status: str = "Pending",
                 creation_timestamp: Optional[datetime] = None):
        self._task_id = task_id
        self._title = title
        self._description = description
        self._due_date = due_date
        self._priority_level = priority_level
        self._status = status
        self._creation_timestamp = creation_timestamp or datetime.now()
        
        # Validate initial values
        self._validate()
    
    def _validate(self) -> None:
        """Validate all task attributes."""
        self._validate_title()
        self._validate_priority()
        self._validate_status()
        self._validate_due_date()
    
    def _validate_title(self) -> None:
        """Validate task title."""
        if not self._title or not self._title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self._title.strip()) > 255:
            raise ValueError("Task title cannot exceed 255 characters")
        if not re.match(r'^[a-zA-Z0-9\s\-\_\.\,]+$', self._title):
            raise ValueError("Title contains invalid characters")
    
    def _validate_priority(self) -> None:
        """Validate priority level."""
        if self._priority_level not in self.VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}")
    
    def _validate_status(self) -> None:
        """Validate task status."""
        if self._status not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")
    
    def _validate_due_date(self) -> None:
        """Validate due date."""
        if self._due_date and self._due_date < date.today():
            raise ValueError("Due date cannot be in the past")
    
    # Property getters with validation
    @property
    def task_id(self) -> Optional[int]:
        return self._task_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self._validate_title()
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
    
    @property
    def due_date(self) -> Optional[date]:
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: Optional[date]) -> None:
        self._due_date = value
        self._validate_due_date()
    
    @property
    def priority_level(self) -> str:
        return self._priority_level
    
    @priority_level.setter
    def priority_level(self, value: str) -> None:
        self._priority_level = value
        self._validate_priority()
    
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str) -> None:
        self._status = value
        self._validate_status()
    
    @property
    def creation_timestamp(self) -> datetime:
        return self._creation_timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for database operations."""
        return {
            'task_id': self._task_id,
            'title': self._title,
            'description': self._description,
            'due_date': self._due_date,
            'priority_level': self._priority_level,
            'status': self._status,
            'creation_timestamp': self._creation_timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task instance from dictionary."""
        return cls(
            task_id=data.get('task_id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            due_date=data.get('due_date'),
            priority_level=data.get('priority_level', 'Medium'),
            status=data.get('status', 'Pending'),
            creation_timestamp=data.get('creation_timestamp')
        )
    
    def __str__(self) -> str:
        due_date_str = self._due_date.strftime('%Y-%m-%d') if self._due_date else 'Not set'
        return (f"Task {self._task_id}: {self._title} "
                f"({self._status}, Priority: {self._priority_level}, Due: {due_date_str})")
    
    def __repr__(self) -> str:
        return f"Task(task_id={self._task_id}, title='{self._title}', status='{self._status}')"