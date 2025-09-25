#!/usr/bin/env python3

import os
import sys

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

def main():
    """Main entry point with secure configuration."""
    from src.config import DatabaseConfig
    from src.database import DatabaseConnection
    from src.cli import TaskManagerCLI
    from src.auth import AuthenticationManager
    from src.task_manager import TaskManager
    
    # Validate configuration before starting
    if not DatabaseConfig.validate_config():
        print("\n💡 Tip: Run 'python setup_new_user.py' to configure the application securely.")
        sys.exit(1)
    
    # Rest of your main function...
    try:
        db = DatabaseConnection()
        if not db.connect():
            sys.exit(1)
        
        auth_manager = AuthenticationManager(db)
        task_manager = TaskManager(db, auth_manager)
        cli = TaskManagerCLI(task_manager, auth_manager)
        cli.cmdloop()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.disconnect()

if __name__ == '__main__':
    main()