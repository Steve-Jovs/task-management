# Task Management Application

A secure, multi-user command-line task management application built with Python and MySQL.  
Features a robust CLI interface, user authentication, and comprehensive task management capabilities.

## ✨ Features

- 🔐 **Multi-User Authentication** – Secure user registration and login system
  
- ✅ **Task Management** – Add, update, delete, and complete tasks
  
- 🔍 **Smart Filtering** – Filter tasks by status, priority, due date
  
- 📊 **Statistics** – Visual task statistics and progress tracking
  
- 🔒 **Security First** – Password hashing, user isolation, secure configuration
  
- 💾 **MySQL Persistence** – Reliable data storage with raw SQL queries
  
- 🎯 **OOP Design** – Clean, maintainable object-oriented architecture
  
- ⚡ **Custom Algorithms** – Efficient sorting and filtering implementations  

## 🛠 Technology Stack
- **Backend:** Python 3.8+
  
- **Database:** MySQL
  
- **Authentication:** Custom secure authentication system
  
- **CLI Framework:** Python `cmd` module
  
- **Security:** SHA-256 password hashing  

## 📋 Prerequisites

- Python 3.8+  
- MySQL Server 5.7 or higher  
- Git  

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

1. Clone and setup environment:

```bash
git clone <repository-url>
cd task-manager
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

2. Run secure setup wizard

```bash
python setup_new_user.py
```

3. Start the application

```bash
python -m src.cli
```
### Method 2: Manual Setup
1. Configure environment variables
```
bash
cp .env.example .env
# Edit .env with your database credentials
```

2. Install dependencies

```bash
pip install -r requirements.txt
```
3. Initialize database

```bash
python setup_database.py
```
4. Run the application

```bash
python -m src.cli
```
## Security Setup
This application uses environment variables for secure configuration. No passwords are stored in the code.

First-Time Security Configuration:
```bash
# Run the interactive setup script
python setup_new_user.py

# Or manually create .env file from example
cp .env.example .env
# Edit .env with your actual database credentials
```
## Important Security Notes:
- The .env file is automatically ignored by Git

- Database passwords are never stored in source code

- Passwords are hashed using SHA-256

- Users can only access their own tasks

- Use different passwords for development and production

### Application Usage
## Starting the Application
```bash
python -m src.cli
```
You'll see the authentication menu:

```text
🔐 Task Manager - Authentication Required
==================================================
1. Login
2. Register
3. Exit

Choose option (1-3):
```
## Default Admin Account
- Username: `admin`

- Password: `admin123` (change this immediately after first login)

## Available Commands
Authentication Commands
- `whoami` - Show current user information

- `logout` - Log out current user

- `users` - List all users (admin only)

Task Management Commands
- `add` - Add a new task

- `list` - List all tasks

- `list status=Completed` - Filter tasks by status

- `list priority=High` - Filter tasks by priority

- `update [task_id]` - Update a task's details

- `complete [task_id]` - Mark a task as completed

- `delete [task_id]` - Delete a task

- `search [keyword]` - Search tasks by keyword

Utility Commands
- `menu` - Show main menu

- `stats` - Show task statistics

- `clear` - Clear the screen

- `help` - Show command help

- `exit` - Exit the application

## Examples
```bash
# Add a new task
task_manager> add
Title: Complete project proposal
Description: Finish the Q4 project proposal document
Due date: 2024-12-15
Priority: High

# List all pending tasks
task_manager> list status=Pending

# Mark task #3 as completed
task_manager> complete 3

# Search for tasks containing "meeting"
task_manager> search meeting

# Show statistics
task_manager> stats
```

## Project Structure
```text
task-manager/
├── src/                 # Source code
│   ├── __init__.py     # Package initialization
│   ├── __main__.py     # Application entry point
│   ├── auth.py         # Authentication management
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration settings
│   ├── database.py     # Database connection handling
│   ├── models.py       # Data models (Task class)
│   ├── task_manager.py # Core business logic
│   └── utils.py        # Utility functions
├── tests/              # Test cases
├── docs/               # Documentation
├── .env.example        # Example environment configuration
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
├── setup.py           # Package installation script
└── README.md          # This file
```

## Database Schema
### Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
### Tasks Table
```sql
CREATE TABLE tasks (
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
    INDEX idx_user_status (user_id, status),
    INDEX idx_user_priority (user_id, priority_level)
);
```

## Technical Features
### Security Implementation
- Password Hashing: SHA-256 with salt

- User Isolation: Users can only access their own tasks

- Input Validation: Comprehensive validation and sanitization

- SQL Injection Protection: Parameterized queries

- Secure Configuration: Environment-based secrets management

### Performance Optimizations
- Efficient Sorting: Custom merge sort algorithm implementation

- Database Indexing: Optimized indexes for common queries

- Memory Management: Intelligent caching with database synchronization

- Thread Safety: Locking mechanisms for concurrent operations

### Error Handling
- Graceful Degradation: Fallback mechanisms for database failures

- User-Friendly Messages: Clear, actionable error messages

- Comprehensive Logging: Detailed logging for debugging

- Input Validation: Protection against invalid user input

## Development
### Setting Up Development Environment
1. Fork and clone the repository

```bash
git clone https://github.com/yourusername/task-manager.git
cd task-manager
```

2. Set up development environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for development tools
```

3. Run tests

```bash
python -m pytest tests/
python -m unittest discover tests/
```

### Code Style
This project follows Python PEP 8 style guide:

- Use 4 spaces for indentation

- Maximum line length of 88 characters

- Comprehensive docstrings for all functions and classes

- Type hints for better code clarity

### Adding New Features
1. Create a feature branch

2. Implement your changes with tests

3. Ensure all tests pass

4. Submit a pull request

## Troubleshooting
### Common Issues
Database Connection Failed

```bash
# Check MySQL service is running
sudo service mysql start  # Linux/macOS
# or
net start mysql          # Windows

# Verify credentials in .env file
cat .env
```

### Module Not Found Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

Permission Denied Errors

```bash
# Set proper file permissions
chmod 600 .env
chmod +x *.py
```

### Getting Help
1. Check the troubleshooting section above

2. Review the application logs for error details

3. Check if your database is running and accessible

4. Verify your .env configuration matches your database setup

## API Documentation
While this is primarily a CLI application, the core classes can be used as a Python API:

## Basic Usage Example
```python
from src.database import DatabaseConnection
from src.auth import AuthenticationManager
from src.task_manager import TaskManager

# Initialize components
db = DatabaseConnection()
auth = AuthenticationManager(db)
task_manager = TaskManager(db, auth)

# Use the task manager programmatically
if auth.login('username', 'password'):
    tasks = task_manager.list_tasks()
    statistics = task_manager.get_statistics()
```

Acknowledgments
- Built with pure Python and MySQL (no ORM)

- Custom algorithms for sorting and filtering

- Secure authentication implementation

- Comprehensive error handling and validation


Note: This application is designed for educational purposes and demonstrates secure coding practices, proper architecture, and comprehensive feature implementation. Always follow security best practices when deploying to production environments.

<div align="center">
Built with ❤️ using Python and MySQL

Happy task managing! 🎯
</div>
