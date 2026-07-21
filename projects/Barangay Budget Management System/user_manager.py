import sqlite3
from datetime import datetime

class UserManager:
    def __init__(self):
        self.db_path = 'barangay_budget.db'
    
    def add_user(self, username, password, full_name, position, access_level):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, full_name, position, access_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, full_name, position, access_level))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
        finally:
            conn.close()
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, full_name, position, access_level, is_active FROM users')
        users = cursor.fetchall()
        conn.close()
        
        return users
    
    def update_user(self, user_id, username, full_name, position, access_level, is_active):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET username=?, full_name=?, position=?, access_level=?, is_active=?
            WHERE id=?
        ''', (username, full_name, position, access_level, is_active, user_id))
        
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        conn.close()
    
    def reset_password(self, user_id, new_password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET password=? WHERE id=?', (new_password, user_id))
        conn.commit()
        conn.close()