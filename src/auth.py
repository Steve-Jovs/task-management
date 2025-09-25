import hashlib
import getpass
from typing import Optional, Tuple
from .database import DatabaseConnection
from .utils import InputValidator

class AuthenticationManager:
    """Handles user authentication and registration."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.current_user: Optional[dict] = None
        self.validator = InputValidator()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self) -> bool:
        """Register a new user."""
        print("\n👤 User Registration")
        print("-" * 30)
        
        try:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")
            confirm_password = getpass.getpass("Confirm Password: ")
            email = input("Email (optional): ").strip()
            
            # Validate inputs
            username = self.validator.validate_string(username, "Username", 50)
            if not password:
                raise ValueError("Password cannot be empty")
            if password != confirm_password:
                raise ValueError("Passwords do not match")
            
            # Check if username exists
            existing = self.db.fetch_one("SELECT user_id FROM users WHERE username = %s", (username,))
            if existing:
                raise ValueError("Username already exists")
            
            # Insert new user
            password_hash = self.hash_password(password)
            query = """
                INSERT INTO users (username, password_hash, email) 
                VALUES (%s, %s, %s)
            """
            cursor = self.db.execute_query(query, (username, password_hash, email))
            
            if cursor:
                print("✅ Registration successful! Please log in.")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def login(self) -> bool:
        """Authenticate user."""
        print("\n🔐 User Login")
        print("-" * 30)
        
        try:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")
            
            if not username or not password:
                raise ValueError("Username and password are required")
            
            # Get user from database
            query = "SELECT user_id, username, password_hash, email, created_at FROM users WHERE username = %s"
            user = self.db.fetch_one(query, (username,))
            
            if not user:
                raise ValueError("User not found")
            
            # Verify password
            password_hash = self.hash_password(password)
            if user['password_hash'] != password_hash:
                raise ValueError("Invalid password")
            
            self.current_user = user
            print(f"✅ Welcome back, {username}!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def logout(self) -> None:
        """Log out current user."""
        if self.current_user:
            print(f"👋 Goodbye, {self.current_user['username']}!")
            self.current_user = None
        else:
            print("ℹ️  No user is currently logged in")
    
    def is_authenticated(self) -> bool:
        """Check if user is logged in."""
        return self.current_user is not None
    
    def get_current_user_id(self) -> Optional[int]:
        """Get current user's ID."""
        return self.current_user['user_id'] if self.current_user else None