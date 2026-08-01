# database.py
import sqlite3
import hashlib
import os
import time
from datetime import datetime, date

class DatabaseManager:
    def __init__(self, db_path="barangay_budget.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn
    
    def execute_query(self, query, params=()):
        """Execute a query with automatic connection management"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_many(self, query, params_list):
        """Execute multiple queries"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def fetch_one(self, query, params=()):
        """Fetch a single row"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def fetch_all(self, query, params=()):
        """Fetch all rows"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT NOT NULL,
                    category_type TEXT CHECK(category_type IN ('income', 'expense')) NOT NULL,
                    description TEXT
                )
            ''')
            
            # Transactions table
            cursor.execute('''
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id),
                    FOREIGN KEY (prepared_by) REFERENCES users(user_id),
                    FOREIGN KEY (approved_by) REFERENCES users(user_id)
                )
            ''')
            
            # Budget allocation table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budget_allocation (
                    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fiscal_year INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    allocated_amount DECIMAL(15,2) NOT NULL,
                    remaining_amount DECIMAL(15,2) NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )
            ''')
            
            # Cash balance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cash_balance (
                    balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_balance DECIMAL(15,2) DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            
            # Insert default data
            self.insert_default_data(conn)
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def insert_default_data(self, conn):
        """Insert default categories and admin user"""
        cursor = conn.cursor()
        
        # Default categories
        categories = [
            # Income Categories
            ('Internal Revenue Allotment', 'income', 'IRA from national government'),
            ('Local Tax Collection', 'income', 'Business permits, fees'),
            ('Service Income', 'income', 'Barangay services and facilities'),
            ('Donations', 'income', 'Private and public donations'),
            
            # Expense Categories
            ('Personnel Services', 'expense', 'Salaries and benefits'),
            ('Maintenance and Operating', 'expense', 'Office supplies, utilities'),
            ('Capital Outlay', 'expense', 'Equipment and infrastructure'),
            ('Social Services', 'expense', 'Health, education, welfare programs'),
            ('Grants and Donations', 'expense', 'Financial assistance to constituents')
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO categories (category_name, category_type, description) VALUES (?, ?, ?)",
            categories
        )
        
        # Default admin user
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, full_name, position, access_level) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Barangay Administrator', 'Barangay Captain', 'admin'))
        
        # Initial cash balance
        cursor.execute('''
            INSERT OR IGNORE INTO cash_balance (current_balance) VALUES (0)
        ''')
        
        conn.commit()