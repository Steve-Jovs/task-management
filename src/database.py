import pymysql
import logging
from typing import Optional, Dict, Any
from .config import DatabaseConfig  # Add this import

class DatabaseConnection:
    """Handles MySQL database connection and operations."""
    
    def __init__(self, host: str = None, user: str = None, 
                 password: str = None, database: str = None, port: int = None):
        # Use provided parameters or fall back to config defaults
        config = DatabaseConfig.get_connection_params()
        self.host = host or config['host']
        self.user = user or config['user']
        self.password = password or config['password']
        self.database = database or config['database']
        self.port = port or config['port']
        self.connection: Optional[pymysql.Connection] = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True  # Add this for better transaction handling
            )
            self.logger.info("Database connection established successfully")
            return True
        except pymysql.Error as e:
            self.logger.error(f"Database connection failed: {e}")
            # Provide helpful error messages
            if "Access denied" in str(e):
                self.logger.error("Please check your MySQL username and password in src/config.py")
            elif "Unknown database" in str(e):
                self.logger.error("Please run the database setup script first")
            elif "Can't connect to MySQL server" in str(e):
                self.logger.error("Please ensure MySQL server is running")
            return False
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[pymysql.cursors.Cursor]:
        """Execute SQL query with error handling."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                return cursor
        except pymysql.Error as e:
            self.logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Execute query and fetch all results."""
        cursor = self.execute_query(query, params)
        return cursor.fetchall() if cursor else []
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute query and fetch single result."""
        cursor = self.execute_query(query, params)
        return cursor.fetchone() if cursor else None