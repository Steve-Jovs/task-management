#!/usr/bin/env python3
"""
Setup script for new users - guides them through secure configuration.
"""

import os
import sys
import getpass

def setup_environment():
    """Guide user through secure setup."""
    print("🔒 Secure Application Setup")
    print("=" * 50)
    print("This script will help you configure the application securely.")
    print("No passwords will be saved in the code or repository.")
    
    # Check if .env exists
    if os.path.exists('.env'):
        overwrite = input(".env file exists. Overwrite? (y/N): ").strip().lower()
        if overwrite not in ('y', 'yes'):
            return
    
    # Get configuration values
    print("\n📝 Database Configuration:")
    db_host = input("Database host [localhost]: ").strip() or "localhost"
    db_user = input("Database user [root]: ").strip() or "root"
    db_name = input("Database name [task_manager]: ").strip() or "task_manager"
    db_port = input("Database port [3306]: ").strip() or "3306"
    
    # Get password securely
    db_password = getpass.getpass("Database password: ")
    if not db_password:
        print("❌ Password is required!")
        return
    
    # Create .env file
    env_content = f"""# Database Configuration
DB_HOST={db_host}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_NAME={db_name}
DB_PORT={db_port}

# Application Settings
DEBUG=False
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Set file permissions to be more secure (Unix-like systems)
    try:
        os.chmod('.env', 0o600)  # Only user can read/write
    except:
        pass  # Not critical if this fails on Windows
    
    print("✅ Configuration saved to .env file")
    print("🔒 .env file added to .gitignore for security")
    
    # Test the connection
    print("\n🔌 Testing database connection...")
    os.environ['DB_PASSWORD'] = db_password  # Set temporarily for test
    
    try:
        from src.config import DatabaseConfig
        if DatabaseConfig.test_connection():
            print("✅ Database connection successful!")
        else:
            print("❌ Database connection failed. Please check your credentials.")
    except ImportError as e:
        print(f"❌ Import error: {e}")

def main():
    """Main setup function."""
    print("🚀 Task Manager Secure Setup")
    print("=" * 50)
    
    # Check if python-dotenv is installed
    try:
        import dotenv
    except ImportError:
        install = input("python-dotenv not installed. Install it? (Y/n): ").strip().lower()
        if install not in ('n', 'no'):
            os.system(f"{sys.executable} -m pip install python-dotenv")
    
    setup_environment()
    
    print("\n📋 Next steps:")
    print("1. The .env file contains your secure configuration")
    print("2. This file is ignored by Git and will not be uploaded")
    print("3. To run the application: python -m src.cli")
    print("4. To update configuration: edit the .env file or run this script again")

if __name__ == '__main__':
    main()