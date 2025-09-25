import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration settings with secure password handling."""
    
    HOST = os.getenv('DB_HOST', 'localhost')
    USER = os.getenv('DB_USER', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', '')  # MUST be set via environment variable
    DATABASE = os.getenv('DB_NAME', 'task_manager')
    PORT = int(os.getenv('DB_PORT', '3306'))
    
    @classmethod
    def get_connection_params(cls) -> Dict[str, Any]:
        """Get connection parameters as dictionary."""
        return {
            'host': cls.HOST,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE,
            'port': cls.PORT
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.PASSWORD:
            print("❌ Database password not set!")
            print("Please set the DB_PASSWORD environment variable")
            print("Example: export DB_PASSWORD=your_password")
            return False
        return True
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test database connection with current configuration."""
        if not cls.validate_config():
            return False
            
        try:
            import pymysql
            params = cls.get_connection_params()
            connection = pymysql.connect(**params)
            connection.close()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False