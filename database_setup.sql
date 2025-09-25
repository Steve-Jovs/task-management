-- database_setup.sql
CREATE DATABASE IF NOT EXISTS task_manager;
USE task_manager;

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
);

-- Optional: Create a dedicated user for the application (recommended for security)
CREATE USER IF NOT EXISTS 'task_user'@'localhost' IDENTIFIED BY 'task_password';
GRANT ALL PRIVILEGES ON task_manager.* TO 'task_user'@'localhost';
FLUSH PRIVILEGES;