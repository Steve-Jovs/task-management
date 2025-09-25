#!/usr/bin/env python3
"""
Interactive setup script for Task Manager application.
Run this script to configure and test your environment.
"""

import os
import sys
import subprocess
import getpass

# Add the src directory to Python path so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import DatabaseConfig
except ImportError:
    print("❌ Could not import config. Make sure you're running from the project root directory.")
    sys.exit(1)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Checking dependencies...")
    try:
        import pymysql
        print("✅ PyMySQL is installed")
        return True
    except ImportError:
        print("❌ PyMySQL is not installed")
        install = input("Install it now? (y/N): ").strip().lower()
        if install in ('y', 'yes'):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMySQL"])
                print("✅ PyMySQL installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install PyMySQL. Please install it manually: pip install PyMySQL")
                return False
        return False

def configure_database():
    """Interactive database configuration."""
    print("\n🗄️  Database Configuration")
    print("=" * 40)
    
    # Test current configuration first
    print("Testing current configuration...")
    if DatabaseConfig.test_connection():
        print("✅ Current configuration works!")
        change = input("\nDo you want to change the configuration anyway? (y/N): ").strip().lower()
        if change not in ('y', 'yes'):
            return
    else:
        print("❌ Current configuration failed. Let's update it.")
    
    # Get new configuration
    print("\nEnter new database configuration (press Enter to keep current value):")
    
    new_host = input(f"Host [{DatabaseConfig.HOST}]: ").strip()
    if new_host:
        DatabaseConfig.HOST = new_host
    
    new_port = input(f"Port [{DatabaseConfig.PORT}]: ").strip()
    if new_port:
        try:
            DatabaseConfig.PORT = int(new_port)
        except ValueError:
            print("❌ Invalid port number, keeping current value")
    
    new_user = input(f"User [{DatabaseConfig.USER}]: ").strip()
    if new_user:
        DatabaseConfig.USER = new_user
    
    new_db = input(f"Database [{DatabaseConfig.DATABASE}]: ").strip()
    if new_db:
        DatabaseConfig.DATABASE = new_db
    
    new_password = input("Password (leave empty to keep current): ").strip()
    if new_password:
        DatabaseConfig.PASSWORD = new_password
    
    print("✅ Configuration updated")

def test_database_connection():
    """Test database connection."""
    print("\n🔌 Testing database connection...")
    if DatabaseConfig.test_connection():
        print("✅ Database connection successful!")
        return True
    else:
        print("❌ Database connection failed")
        print("\nTroubleshooting tips:")
        print("1. Ensure MySQL server is running")
        print("2. Check your username and password")
        print("3. Verify the database exists")
        print("4. Check if MySQL is on the default port (3306)")
        return False

def create_config_file():
    """Create a permanent config file if it doesn't exist."""
    config_content = f'''import os

class DatabaseConfig:
    """Database configuration settings."""
    
    HOST = '{DatabaseConfig.HOST}'
    USER = '{DatabaseConfig.USER}'
    PASSWORD = '{DatabaseConfig.PASSWORD}'
    DATABASE = '{DatabaseConfig.DATABASE}'
    PORT = {DatabaseConfig.PORT}
    
    @classmethod
    def get_connection_params(cls):
        return {{
            'host': cls.HOST,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE,
            'port': cls.PORT
        }}
    
    @classmethod
    def test_connection(cls):
        try:
            import pymysql
            params = cls.get_connection_params()
            connection = pymysql.connect(**params)
            connection.close()
            return True
        except Exception:
            return False
'''
    
    config_path = os.path.join('src', 'config.py')
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"✅ Configuration saved to {config_path}")

def main():
    """Main setup function."""
    print("🚀 Task Manager Application Setup")
    print("=" * 50)
    
    # Run checks
    if not check_python_version():
        return
    
    if not check_dependencies():
        print("❌ Please install required dependencies first")
        return
    
    # Configure database
    configure_database()
    
    # Test connection
    if test_database_connection():
        # Save configuration
        create_config_file()
        
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. The application is ready to use!")
        print("2. Run 'python -m src.cli' to start the application")
        
        # Check if database tables exist
        check_tables = input("\nCheck if database tables exist? (y/N): ").strip().lower()
        if check_tables in ('y', 'yes'):
            check_database_tables()
    else:
        print("\n❌ Setup failed. Please fix the issues above and run this script again.")

def check_database_tables():
    """Check if database tables exist and create them if needed."""
    try:
        from src.database import DatabaseConnection
        
        db = DatabaseConnection()
        if db.connect():
            # Check if tasks table exists
            result = db.fetch_one("SHOW TABLES LIKE 'tasks'")
            if result:
                print("✅ Database tables exist")
            else:
                print("❌ Tasks table not found")
                create = input("Create tables now? (y/N): ").strip().lower()
                if create in ('y', 'yes'):
                    create_database_tables()
            db.disconnect()
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

def create_database_tables():
    """Create the necessary database tables."""
    try:
        from src.database import DatabaseConnection
        
        db = DatabaseConnection()
        if db.connect():
            # Create tasks table
            db.execute_query('''
                CREATE TABLE IF NOT EXISTS tasks (
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
            print("✅ Database tables created successfully!")
            db.disconnect()
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == '__main__':
    main()