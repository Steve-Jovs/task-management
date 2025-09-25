import unittest
from datetime import date
from src.models import Task
from src.utils import InputValidator

class TestTask(unittest.TestCase):
    def test_task_creation(self):
        task = Task(title="Test Task", description="Test Description")
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "Pending")
    
    def test_task_validation(self):
        with self.assertRaises(ValueError):
            Task(title="")  # Empty title should raise error
        
        with self.assertRaises(ValueError):
            Task(title="Valid", priority_level="Invalid")
    
    def test_task_to_dict(self):
        task = Task(title="Test", priority_level="High")
        task_dict = task.to_dict()
        self.assertEqual(task_dict['title'], "Test")
        self.assertEqual(task_dict['priority_level'], "High")

class TestInputValidator(unittest.TestCase):
    def test_validate_string(self):
        self.assertEqual(InputValidator.validate_string("test", "Test"), "test")
        
        with self.assertRaises(ValueError):
            InputValidator.validate_string("", "Test")
    
    def test_validate_date(self):
        future_date = date.today().replace(year=date.today().year + 1)
        future_str = future_date.strftime('%Y-%m-%d')
        self.assertEqual(InputValidator.validate_date(future_str), future_date)
        
        with self.assertRaises(ValueError):
            InputValidator.validate_date("invalid-date")

if __name__ == '__main__':
    unittest.main()