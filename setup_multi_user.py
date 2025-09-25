#!/usr/bin/env python3
"""
Setup script for multi-user task manager.
"""

import sys
import os
import getpass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseConnection

def setup_multi_user_database():
    """Create multi-user database schema."""
    print("🗄️ Multi-User Task Manager Database Setup")
    print("=" * 50)
    
    # Get database connection
    db = DatabaseConnection()
    
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Create users table
        print("Creating users table...")
        db.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Modify tasks table
        print("Modifying tasks table...")
        db.execute_query('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE,
                priority_level ENUM('Low', 'Medium', 'High') NOT NULL DEFAULT 'Medium',
                status ENUM('Pending', 'In Progress', 'Completed') NOT NULL DEFAULT 'Pending',
                creation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_user_status (user_id, status)
            )
        ''')
        
        # Create admin user
        create_admin = input("Create admin user? (y/N): ").strip().lower()
        if create_admin in ('y', 'yes'):
            from auth import AuthenticationManager
            auth = AuthenticationManager(db)
            
            username = input("Admin username [admin]: ").strip() or "admin"
            password = getpass.getpass("Admin password: ")
            
            # Hash password and insert
            password_hash = auth.hash_password(password)
            db.execute_query(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            print(f"✅ Admin user '{username}' created")
        
        print("✅ Multi-user database setup completed!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
    finally:
        db.disconnect()

if __name__ == '__main__':
    setup_multi_user_database()