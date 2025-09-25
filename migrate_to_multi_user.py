#!/usr/bin/env python3
"""
Migration script to convert single-user task manager to multi-user.
"""

import sys
import os
import getpass
import hashlib

# Add the current directory to Python path so we can import from src
sys.path.insert(0, os.path.dirname(__file__))

def migrate_to_multi_user():
    """Migrate database from single-user to multi-user schema."""
    print("🔄 Migrating to Multi-User System")
    print("=" * 50)
    
    try:
        # Import after adding to path
        from src.database import DatabaseConnection
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    
    # Get database connection
    db = DatabaseConnection()
    
    if not db.connect():
        print("❌ Failed to connect to database")
        return False
    
    try:
        # Step 1: Backup current tasks (optional)
        print("1. Checking current tasks...")
        current_tasks = db.fetch_all("SELECT * FROM tasks")
        print(f"   Found {len(current_tasks)} existing tasks")
        
        # Step 2: Create users table
        print("2. Creating users table...")
        db.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Step 3: Create default admin user
        print("3. Creating default admin user...")
        default_password = "admin123"  # You should change this!
        password_hash = hashlib.sha256(default_password.encode()).hexdigest()
        
        # Check if admin user already exists
        existing_admin = db.fetch_one("SELECT user_id FROM users WHERE username = 'admin'")
        if not existing_admin:
            db.execute_query(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                ('admin', password_hash)
            )
            print("   ✅ Admin user created (username: 'admin', password: 'admin123')")
        else:
            print("   ℹ️  Admin user already exists")
        
        # Step 4: Get the admin user ID
        admin_user = db.fetch_one("SELECT user_id FROM users WHERE username = 'admin'")
        admin_user_id = admin_user['user_id']
        print(f"   Admin user ID: {admin_user_id}")
        
        # Step 5: Check if tasks table already has user_id column
        print("4. Checking current table structure...")
        table_columns = db.fetch_all("DESCRIBE tasks")
        has_user_id = any(column['Field'] == 'user_id' for column in table_columns)
        
        if has_user_id:
            print("   ℹ️  user_id column already exists")
            
            # Check if there are tasks without user_id assigned
            orphaned_tasks = db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id IS NULL")
            if orphaned_tasks['count'] > 0:
                print(f"   Assigning {orphaned_tasks['count']} orphaned tasks to admin...")
                db.execute_query("UPDATE tasks SET user_id = %s WHERE user_id IS NULL", (admin_user_id,))
        else:
            # Step 6: Add user_id column to tasks table
            print("5. Adding user_id column to tasks table...")
            db.execute_query("ALTER TABLE tasks ADD COLUMN user_id INT")
            
            # Step 7: Assign all existing tasks to admin user
            print("6. Assigning existing tasks to admin user...")
            db.execute_query("UPDATE tasks SET user_id = %s WHERE user_id IS NULL", (admin_user_id,))
            
            # Step 8: Modify user_id to be NOT NULL
            print("7. Setting user_id as required...")
            db.execute_query("ALTER TABLE tasks MODIFY COLUMN user_id INT NOT NULL")
            
            # Step 9: Add foreign key constraint
            print("8. Adding foreign key constraint...")
            db.execute_query("""
                ALTER TABLE tasks 
                ADD FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            """)
            
            # Step 10: Create index for better performance
            print("9. Creating index on user_id...")
            db.execute_query("CREATE INDEX idx_user_id ON tasks(user_id)")
            
            # Step 11: Create additional indexes for better multi-user performance
            print("10. Creating additional indexes...")
            db.execute_query("CREATE INDEX idx_user_status ON tasks(user_id, status)")
            db.execute_query("CREATE INDEX idx_user_priority ON tasks(user_id, priority_level)")
        
        print("✅ Migration completed successfully!")
        
        # Summary
        users_count = db.fetch_one("SELECT COUNT(*) as count FROM users")['count']
        tasks_count = db.fetch_one("SELECT COUNT(*) as count FROM tasks")['count']
        admin_tasks = db.fetch_one("SELECT COUNT(*) as count FROM tasks WHERE user_id = %s", (admin_user_id,))['count']
        
        print(f"\n📊 Migration Summary:")
        print(f"   Total users: {users_count}")
        print(f"   Total tasks: {tasks_count}")
        print(f"   Tasks assigned to admin: {admin_tasks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

def test_multi_user_setup():
    """Test the multi-user setup."""
    print("\n🧪 Testing multi-user setup...")
    
    try:
        from src.database import DatabaseConnection
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    db = DatabaseConnection()
    if not db.connect():
        return False
    
    try:
        # Test users table
        users = db.fetch_all("SELECT user_id, username FROM users")
        print(f"✅ Users table: {len(users)} users")
        for user in users:
            print(f"   - {user['username']} (ID: {user['user_id']})")
        
        # Test tasks table structure
        columns = db.fetch_all("DESCRIBE tasks")
        user_id_column = next((col for col in columns if col['Field'] == 'user_id'), None)
        if user_id_column:
            print("✅ user_id column exists in tasks table")
        else:
            print("❌ user_id column missing")
            return False
        
        # Test tasks per user
        user_tasks = db.fetch_all("""
            SELECT u.username, COUNT(t.task_id) as task_count 
            FROM users u 
            LEFT JOIN tasks t ON u.user_id = t.user_id 
            GROUP BY u.user_id, u.username
        """)
        print("✅ Task distribution:")
        for ut in user_tasks:
            print(f"   - {ut['username']}: {ut['task_count']} tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        db.disconnect()

def main():
    """Main migration function."""
    print("🚀 Task Manager Multi-User Migration")
    print("=" * 50)
    
    print("This script will:")
    print("1. Create a users table")
    print("2. Create a default admin user")
    print("3. Add user_id column to tasks table")
    print("4. Assign existing tasks to admin user")
    print("5. Set up proper constraints and indexes")
    
    confirm = input("\nContinue with migration? (y/N): ").strip().lower()
    if confirm not in ('y', 'yes'):
        print("Migration cancelled.")
        return
    
    if migrate_to_multi_user():
        print("\n✅ Migration successful! Testing setup...")
        if test_multi_user_setup():
            print("\n🎉 Multi-user setup is ready!")
            print("\nNext steps:")
            print("1. Make sure you have the updated multi-user code files")
            print("2. Run 'python -m src.cli' to start the application")
            print("3. Login with username 'admin' and password 'admin123'")
            print("4. Change the admin password immediately!")
        else:
            print("❌ Setup test failed. Please check the database manually.")
    else:
        print("❌ Migration failed.")

if __name__ == '__main__':
    main()