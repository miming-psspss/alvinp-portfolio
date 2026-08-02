# database_fixed.py
import sqlite3
import hashlib
import os
import time
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="barangay_budget.db"):
        self.db_path = db_path
        self._connection = None
        self.init_database()
    
    def get_connection(self):
        """Get a single persistent connection to avoid locking issues"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path, 
                timeout=30.0,
                check_same_thread=False  # Allow same thread to reuse connection
            )
            self._connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=NORMAL")
            self._connection.execute("PRAGMA busy_timeout=10000")  # 10 second timeout
        return self._connection
    
    def execute_query(self, query, params=()):
        """Execute a query with retry logic"""
        conn = self.get_connection()
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    # If still locked after retries, close and reopen connection
                    self.close_connection()
                    raise e
            except Exception as e:
                conn.rollback()
                raise e
    
    def fetch_one(self, query, params=()):
        """Fetch a single row"""
        cursor = self.execute_query(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query, params=()):
        """Fetch all rows"""
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def close_connection(self):
        """Close the database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def init_database(self):
        """Initialize database tables"""
        # Users table
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                position TEXT NOT NULL,
                access_level TEXT CHECK(access_level IN ('admin', 'treasurer', 'kagawad', 'viewer')) DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL,
                category_type TEXT CHECK(category_type IN ('income', 'expense')) NOT NULL,
                description TEXT
            )
        ''')
        
        # Transactions table - UPDATED WITH TRANSACTION_TYPE
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_number TEXT UNIQUE NOT NULL,
                transaction_date DATE NOT NULL,
                category_id INTEGER NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                description TEXT NOT NULL,
                payee_payer TEXT,
                payment_method TEXT CHECK(payment_method IN ('cash', 'check', 'bank_transfer')) DEFAULT 'cash',
                check_number TEXT,
                prepared_by INTEGER NOT NULL,
                approved_by INTEGER,
                status TEXT CHECK(status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
                transaction_type TEXT CHECK(transaction_type IN ('regular', 'cash_adjustment')) DEFAULT 'regular',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(category_id),
                FOREIGN KEY (prepared_by) REFERENCES users(user_id),
                FOREIGN KEY (approved_by) REFERENCES users(user_id)
            )
        ''')
        
        # Cash balance table
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS cash_balance (
                balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_balance DECIMAL(15,2) DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default data
        self.insert_default_data()
        
        # Add transaction_type to existing transactions if not exists
        self.migrate_transaction_type()
    
    def migrate_transaction_type(self):
        """Add transaction_type column to existing transactions table if needed"""
        try:
            # Check if transaction_type column exists
            with self.get_connection() as conn:
                result = conn.execute("PRAGMA table_info(transactions)").fetchall()
                columns = [column[1] for column in result]
                
                if 'transaction_type' not in columns:
                    print("Adding transaction_type column to transactions table...")
                    conn.execute('ALTER TABLE transactions ADD COLUMN transaction_type TEXT CHECK(transaction_type IN ("regular", "cash_adjustment")) DEFAULT "regular"')
                    conn.commit()
                    print("Transaction_type column added successfully.")
        except Exception as e:
            print(f"Error migrating transaction_type: {e}")
    
    def insert_default_data(self):
        """Insert default categories and admin user"""
        # Default categories
        categories = [
            ('Internal Revenue Allotment', 'income', 'IRA from national government'),
            ('Local Tax Collection', 'income', 'Business permits, fees'),
            ('Service Income', 'income', 'Barangay services and facilities'),
            ('Donations', 'income', 'Private and public donations'),
            ('Personnel Services', 'expense', 'Salaries and benefits'),
            ('Maintenance and Operating', 'expense', 'Office supplies, utilities'),
            ('Capital Outlay', 'expense', 'Equipment and infrastructure'),
            ('Social Services', 'expense', 'Health, education, welfare programs'),
            ('Grants and Donations', 'expense', 'Financial assistance to constituents'),
            ('Cash Adjustment', 'income', 'Cash management adjustments')  # Added for cash adjustments
        ]
        
        for category in categories:
            self.execute_query(
                "INSERT OR IGNORE INTO categories (category_name, category_type, description) VALUES (?, ?, ?)",
                category
            )
        
        # Default admin user
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        self.execute_query('''
            INSERT OR IGNORE INTO users (username, password, full_name, position, access_level) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Barangay Administrator', 'Barangay Captain', 'admin'))
        
        # Add default kagawad user for testing
        hashed_kagawad_password = hashlib.sha256("kagawad123".encode()).hexdigest()
        self.execute_query('''
            INSERT OR IGNORE INTO users (username, password, full_name, position, access_level) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('kagawad', hashed_kagawad_password, 'Barangay Kagawad', 'Kagawad', 'kagawad'))
        
        # Add default treasurer user
        hashed_treasurer_password = hashlib.sha256("treasurer123".encode()).hexdigest()
        self.execute_query('''
            INSERT OR IGNORE INTO users (username, password, full_name, position, access_level) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('treasurer', hashed_treasurer_password, 'Barangay Treasurer', 'Treasurer', 'treasurer'))
        
        # Initial cash balance
        self.execute_query('''
            INSERT OR IGNORE INTO cash_balance (current_balance) VALUES (0)
        ''')
    
    # ========== USER MANAGEMENT METHODS ==========
    
    def add_user(self, username, password, full_name, position, access_level='viewer'):
        """Add a new user to the system"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            self.execute_query('''
                INSERT INTO users (username, password, full_name, position, access_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, full_name, position, access_level))
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return False
    
    def get_all_users(self):
        """Get all users from the database"""
        return self.fetch_all('''
            SELECT user_id, username, full_name, position, access_level, is_active, created_at 
            FROM users 
            ORDER BY created_at DESC
        ''')
    
    def get_user_by_id(self, user_id):
        """Get a specific user by ID"""
        return self.fetch_one('''
            SELECT user_id, username, full_name, position, access_level, is_active, created_at 
            FROM users 
            WHERE user_id = ?
        ''', (user_id,))
    
    def get_user_by_username(self, username):
        """Get a user by username (for login)"""
        return self.fetch_one('''
            SELECT user_id, username, password, full_name, position, access_level, is_active 
            FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
    
    def update_user(self, user_id, username, full_name, position, access_level, is_active):
        """Update user information"""
        try:
            self.execute_query('''
                UPDATE users 
                SET username = ?, full_name = ?, position = ?, access_level = ?, is_active = ?
                WHERE user_id = ?
            ''', (username, full_name, position, access_level, 1 if is_active else 0, user_id))
            return True
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return False
    
    def delete_user(self, user_id):
        """Delete a user from the system"""
        # Prevent deleting the last admin user
        admin_count = self.fetch_one('SELECT COUNT(*) as count FROM users WHERE access_level = "admin" AND is_active = 1')
        user_to_delete = self.get_user_by_id(user_id)
        
        if user_to_delete and user_to_delete['access_level'] == 'admin' and admin_count['count'] <= 1:
            return False, "Cannot delete the last active admin user"
        
        try:
            self.execute_query('DELETE FROM users WHERE user_id = ?', (user_id,))
            return True, "User deleted successfully"
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"
    
    def reset_password(self, user_id, new_password):
        """Reset a user's password"""
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        self.execute_query('UPDATE users SET password = ? WHERE user_id = ?', (hashed_password, user_id))
        return True
    
    def change_password(self, user_id, current_password, new_password):
        """Change password with current password verification"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        current_hashed = hashlib.sha256(current_password.encode()).hexdigest()
        if user['password'] != current_hashed:
            return False, "Current password is incorrect"
        
        new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
        self.execute_query('UPDATE users SET password = ? WHERE user_id = ?', (new_hashed, user_id))
        return True, "Password changed successfully"
    
    def get_active_users_count(self):
        """Get count of active users"""
        result = self.fetch_one('SELECT COUNT(*) as count FROM users WHERE is_active = 1')
        return result['count'] if result else 0
    
    def get_users_by_access_level(self, access_level):
        """Get users by specific access level"""
        return self.fetch_all('''
            SELECT user_id, username, full_name, position, access_level, is_active, created_at 
            FROM users 
            WHERE access_level = ? AND is_active = 1
            ORDER BY full_name
        ''', (access_level,))
    
    def deactivate_user(self, user_id):
        """Deactivate a user (soft delete)"""
        # Prevent deactivating the last admin user
        admin_count = self.fetch_one('SELECT COUNT(*) as count FROM users WHERE access_level = "admin" AND is_active = 1')
        user_to_deactivate = self.get_user_by_id(user_id)
        
        if user_to_deactivate and user_to_deactivate['access_level'] == 'admin' and admin_count['count'] <= 1:
            return False, "Cannot deactivate the last active admin user"
        
        self.execute_query('UPDATE users SET is_active = 0 WHERE user_id = ?', (user_id,))
        return True, "User deactivated successfully"
    
    def activate_user(self, user_id):
        """Activate a previously deactivated user"""
        self.execute_query('UPDATE users SET is_active = 1 WHERE user_id = ?', (user_id,))
        return True, "User activated successfully"
    
    def validate_user_credentials(self, username, password):
        """Validate user login credentials"""
        user = self.get_user_by_username(username)
        if not user:
            return False, None
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] == hashed_password:
            user_data = {
                'user_id': user['user_id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'position': user['position'],
                'access_level': user['access_level']
            }
            return True, user_data
        
        return False, None
    
    def is_username_available(self, username, exclude_user_id=None):
        """Check if username is available"""
        if exclude_user_id:
            result = self.fetch_one(
                'SELECT COUNT(*) as count FROM users WHERE username = ? AND user_id != ?',
                (username, exclude_user_id)
            )
        else:
            result = self.fetch_one(
                'SELECT COUNT(*) as count FROM users WHERE username = ?',
                (username,)
            )
        
        return result['count'] == 0 if result else True
    
    # ========== TRANSACTION METHODS ==========
    
    def get_cash_balance(self):
        """Get current cash balance"""
        result = self.fetch_one('SELECT current_balance FROM cash_balance ORDER BY balance_id DESC LIMIT 1')
        return result['current_balance'] if result else 0.0
    
    def update_cash_balance(self, amount):
        """Update cash balance"""
        self.execute_query('INSERT INTO cash_balance (current_balance) VALUES (?)', (amount,))
        return True
    
    def add_transaction(self, transaction_data):
        """Add a new transaction"""
        try:
            # Generate transaction number
            prefix = "INC" if transaction_data.get('category_type') == 'income' else "EXP"
            today = datetime.now().strftime("%Y%m%d")
            
            last_trans = self.fetch_one(
                "SELECT transaction_number FROM transactions WHERE transaction_number LIKE ? ORDER BY transaction_id DESC LIMIT 1",
                (f"{prefix}-{today}-%",)
            )
            
            if last_trans:
                last_seq = int(last_trans['transaction_number'].split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            transaction_number = f"{prefix}-{today}-{new_seq:04d}"
            
            # Insert transaction
            self.execute_query('''
                INSERT INTO transactions (
                    transaction_number, transaction_date, category_id, amount,
                    description, payee_payer, payment_method, check_number,
                    prepared_by, status, transaction_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_number,
                transaction_data.get('transaction_date', datetime.now().date().isoformat()),
                transaction_data['category_id'],
                transaction_data['amount'],
                transaction_data['description'],
                transaction_data.get('payee_payer', ''),
                transaction_data.get('payment_method', 'cash'),
                transaction_data.get('check_number', None),
                transaction_data['prepared_by'],
                transaction_data.get('status', 'pending'),
                transaction_data.get('transaction_type', 'regular')  # Default to regular
            ))
            
            return transaction_number
        except Exception as e:
            raise e
    
    def add_cash_adjustment(self, amount, description, user_id):
        """Add a cash adjustment transaction (not counted in monthly income/expense)"""
        try:
            # Generate cash adjustment transaction number
            today = datetime.now().strftime("%Y%m%d")
            last_trans = self.fetch_one(
                "SELECT transaction_number FROM transactions WHERE transaction_number LIKE ? ORDER BY transaction_id DESC LIMIT 1",
                (f"CA-{today}-%",)
            )
            
            if last_trans:
                last_seq = int(last_trans['transaction_number'].split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            transaction_number = f"CA-{today}-{new_seq:04d}"
            
            # Get cash adjustment category ID
            cash_category = self.fetch_one(
                "SELECT category_id FROM categories WHERE category_name = 'Cash Adjustment'"
            )
            
            if not cash_category:
                raise ValueError("Cash Adjustment category not found")
            
            # Insert as cash adjustment
            self.execute_query('''
                INSERT INTO transactions (
                    transaction_number, transaction_date, category_id, amount,
                    description, prepared_by, status, transaction_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_number,
                datetime.now().date().isoformat(),
                cash_category['category_id'],
                amount,
                description,
                user_id,
                'approved',  # Auto-approve cash adjustments
                'cash_adjustment'  # Mark as cash adjustment
            ))
            
            return transaction_number
        except Exception as e:
            raise e
    
    def get_transactions(self, start_date=None, end_date=None, status=None, transaction_type=None):
        """Get transactions with filters"""
        query = '''
            SELECT t.*, c.category_name, c.category_type, u.full_name as prepared_by_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            JOIN users u ON t.prepared_by = u.user_id
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND t.transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND t.transaction_date <= ?"
            params.append(end_date)
        if status:
            query += " AND t.status = ?"
            params.append(status)
        if transaction_type:
            query += " AND t.transaction_type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY t.transaction_date DESC, t.created_at DESC"
        
        return self.fetch_all(query, params)
    
    def get_monthly_financials(self, year=None, month=None):
        """Get monthly financial data (only regular transactions)"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        # Monthly Income: Only regular approved income transactions
        monthly_income = self.fetch_one('''
            SELECT COALESCE(SUM(t.amount), 0) as total_income 
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE strftime('%Y', t.transaction_date) = ? 
            AND strftime('%m', t.transaction_date) = ?
            AND c.category_type = 'income' 
            AND t.status = 'approved'
            AND t.transaction_type = 'regular'  -- EXCLUDE CASH ADJUSTMENTS
        ''', (str(year), f"{month:02d}"))
        
        # Monthly Expenses: Only regular approved expense transactions
        monthly_expense = self.fetch_one('''
            SELECT COALESCE(SUM(t.amount), 0) as total_expense 
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE strftime('%Y', t.transaction_date) = ? 
            AND strftime('%m', t.transaction_date) = ?
            AND c.category_type = 'expense' 
            AND t.status = 'approved'
            AND t.transaction_type = 'regular'  -- EXCLUDE CASH ADJUSTMENTS
        ''', (str(year), f"{month:02d}"))
        
        return {
            'income': monthly_income['total_income'] if monthly_income else 0,
            'expense': monthly_expense['total_expense'] if monthly_expense else 0
        }

# Singleton instance for easy access
db_manager = DatabaseManager()

# Example usage:
if __name__ == "__main__":
    # Test user management functions
    db = DatabaseManager()
    
    # Get all users
    users = db.get_all_users()
    print("All Users:")
    for user in users:
        print(f"ID: {user['user_id']}, Username: {user['username']}, Name: {user['full_name']}, Role: {user['access_level']}")
    
    # Validate credentials
    success, user_data = db.validate_user_credentials("admin", "admin123")
    print(f"\nAdmin login successful: {success}")
    if success:
        print(f"User data: {user_data}")
    
    # Test monthly financials
    financials = db.get_monthly_financials()
    print(f"\nMonthly Financials:")
    print(f"Income: ₱{financials['income']:,.2f}")
    print(f"Expense: ₱{financials['expense']:,.2f}")