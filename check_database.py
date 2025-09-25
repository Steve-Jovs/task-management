#!/usr/bin/env python3
"""
Check if database is properly set up.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.database import DatabaseConnection
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def check_database():
    """Check database connection and tables."""
    print("🔍 Checking database setup...")
    
    db = DatabaseConnection()
    
    if not db.connect():
        print("❌ Database connection failed")
        return False
    
    try:
        # Check if tasks table exists
        result = db.fetch_one("SHOW TABLES LIKE 'tasks'")
        if result:
            print("✅ Tasks table exists")
            
            # Check table structure
            columns = db.fetch_all("DESCRIBE tasks")
            print(f"✅ Table has {len(columns)} columns")
            
            # Count tasks
            count_result = db.fetch_one("SELECT COUNT(*) as count FROM tasks")
            print(f"✅ Database contains {count_result['count']} tasks")
            
            return True
        else:
            print("❌ Tasks table does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        db.disconnect()

if __name__ == '__main__':
    if check_database():
        print("\n🎉 Database is properly set up!")
        print("You can run 'python -m src.cli' to use the application.")
    else:
        print("\n❌ Database setup issues found.")
        print("Run 'python setup_database.py' to create the tables.")