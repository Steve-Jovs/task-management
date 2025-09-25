#!/usr/bin/env python3
"""
Simple database setup script for Task Manager application.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.database import DatabaseConnection
    from src.config import DatabaseConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def setup_database():
    """Create the tasks table if it doesn't exist."""
    print("🗄️  Task Manager Database Setup")
    print("=" * 40)
    
    db = DatabaseConnection()
    
    if not db.connect():
        print("❌ Failed to connect to database")
        print("Please check your configuration in src/config.py")
        return
    
    try:
        # Check if table already exists
        result = db.fetch_one("SHOW TABLES LIKE 'tasks'")
        if result:
            print("✅ Tasks table already exists")
            return
        
        # Create tasks table
        print("Creating tasks table...")
        db.execute_query('''
            CREATE TABLE tasks (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE,
                priority_level ENUM('Low', 'Medium', 'High') NOT NULL DEFAULT 'Medium',
                status ENUM('Pending', 'In Progress', 'Completed') NOT NULL DEFAULT 'Pending',
                creation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_due_date (due_date),
                INDEX idx_priority (priority_level),
                INDEX idx_status (status)
            )
        ''')
        
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
    finally:
        db.disconnect()

if __name__ == '__main__':
    setup_database()