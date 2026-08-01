# auth.py
import hashlib
from database import DatabaseManager

class AuthSystem:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_user = None
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        with self.db_manager.get_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username,)
            ).fetchone()
            
            if user and user['password'] == self.hash_password(password):
                self.current_user = dict(user)
                return True
        return False
    
    def logout(self):
        self.current_user = None
    
    def is_logged_in(self):
        return self.current_user is not None
    
    def require_auth(self):
        if not self.is_logged_in():
            raise PermissionError("Authentication required")
    
    def require_access_level(self, required_level):
        self.require_auth()
        access_levels = {'viewer': 1, 'treasurer': 2, 'admin': 3}
        user_level = access_levels.get(self.current_user['access_level'], 0)
        required_level_num = access_levels.get(required_level, 0)
        
        if user_level < required_level_num:
            raise PermissionError(f"Insufficient permissions. Required: {required_level}")