# transaction_manager.py
from datetime import datetime, date
from database import DatabaseManager

class TransactionManager:
    def __init__(self, db_manager, auth_system, cash_manager=None):
        self.db_manager = db_manager
        self.auth_system = auth_system
        self.cash_manager = cash_manager
    
    def can_add_transaction(self):
        """Check if current user has permission to add transactions"""
        if not self.auth_system.is_logged_in():
            return False
        
        user_access = self.auth_system.current_user['access_level']
        # Admin, Treasurer, and Kagawad can add transactions
        return user_access in ['admin', 'treasurer', 'kagawad']
    
    def can_approve_transactions(self):
        """Check if current user has permission to approve transactions"""
        if not self.auth_system.is_logged_in():
            return False
        
        user_access = self.auth_system.current_user['access_level']
        # Only Admin and Treasurer can approve transactions
        return user_access in ['admin', 'treasurer']
    
    def can_view_transactions(self):
        """Check if current user has permission to view transactions"""
        if not self.auth_system.is_logged_in():
            return False
        
        user_access = self.auth_system.current_user['access_level']
        # All users can view transactions
        return user_access in ['admin', 'treasurer', 'kagawad', 'viewer']
    
    def generate_transaction_number(self, category_type):
        prefix = "INC" if category_type == "income" else "EXP"
        today = datetime.now().strftime("%Y%m%d")
        
        with self.db_manager.get_connection() as conn:
            last_trans = conn.execute(
                "SELECT transaction_number FROM transactions WHERE transaction_number LIKE ? ORDER BY transaction_id DESC LIMIT 1",
                (f"{prefix}-{today}-%",)
            ).fetchone()
            
            if last_trans:
                last_seq = int(last_trans['transaction_number'].split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            return f"{prefix}-{today}-{new_seq:04d}"
    
    def add_transaction(self, transaction_data):
        # Check if user has permission to add transactions
        if not self.can_add_transaction():
            raise PermissionError("You do not have permission to add transactions. Required access level: admin, treasurer, or kagawad")
        
        transaction_number = self.generate_transaction_number(transaction_data['category_type'])
        
        with self.db_manager.get_connection() as conn:
            # Get category_id from category_type and category_name
            category = conn.execute(
                "SELECT category_id FROM categories WHERE category_name = ? AND category_type = ?",
                (transaction_data['category_name'], transaction_data['category_type'])
            ).fetchone()
            
            if not category:
                raise ValueError("Invalid category")
            
            # Determine transaction status based on user access level
            user_access = self.auth_system.current_user['access_level']
            if user_access in ['admin', 'treasurer']:
                # Admin and treasurer transactions are auto-approved
                status = 'approved'
            else:
                # Kagawad transactions require approval
                status = 'pending'
            
            # Insert transaction
            conn.execute('''
                INSERT INTO transactions (
                    transaction_number, transaction_date, category_id, amount, 
                    description, payee_payer, payment_method, check_number, prepared_by, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_number,
                transaction_data['transaction_date'],
                category['category_id'],
                transaction_data['amount'],
                transaction_data['description'],
                transaction_data.get('payee_payer'),
                transaction_data.get('payment_method', 'cash'),
                transaction_data.get('check_number'),
                self.auth_system.current_user['user_id'],
                status
            ))
            
            # Update cash balance if transaction is approved and payment method is cash
            # AND if cash_manager is available
            if (self.cash_manager and 
                status == 'approved' and 
                transaction_data.get('payment_method') == 'cash'):
                self.cash_manager.update_balance(
                    transaction_data['amount'],
                    transaction_data['category_type'],
                    f"Transaction: {transaction_data['description']}"
                )
            
            return transaction_number
    
    def approve_transaction(self, transaction_id):
        # Check if user has permission to approve transactions
        if not self.can_approve_transactions():
            raise PermissionError("You do not have permission to approve transactions. Required access level: admin or treasurer")
        
        with self.db_manager.get_connection() as conn:
            # Get transaction details
            transaction = conn.execute(
                "SELECT * FROM transactions WHERE transaction_id = ?",
                (transaction_id,)
            ).fetchone()
            
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Update transaction status
            conn.execute(
                "UPDATE transactions SET status = 'approved', approved_by = ? WHERE transaction_id = ?",
                (self.auth_system.current_user['user_id'], transaction_id)
            )
            
            # Update cash balance if payment method is cash AND cash_manager is available
            if self.cash_manager and transaction['payment_method'] == 'cash':
                category = conn.execute(
                    "SELECT category_type FROM categories WHERE category_id = ?",
                    (transaction['category_id'],)
                ).fetchone()
                
                if category:
                    self.cash_manager.update_balance(
                        transaction['amount'],
                        category['category_type'],
                        f"Approved: {transaction['description']}"
                    )
    
    def reject_transaction(self, transaction_id):
        """Reject a pending transaction"""
        # Check if user has permission to approve/reject transactions
        if not self.can_approve_transactions():
            raise PermissionError("You do not have permission to reject transactions. Required access level: admin or treasurer")
        
        with self.db_manager.get_connection() as conn:
            conn.execute(
                "UPDATE transactions SET status = 'rejected', approved_by = ? WHERE transaction_id = ?",
                (self.auth_system.current_user['user_id'], transaction_id)
            )
    
    def get_transactions(self, start_date=None, end_date=None, status=None):
        # Check if user has permission to view transactions
        if not self.can_view_transactions():
            raise PermissionError("You do not have permission to view transactions")
        
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
        
        query += " ORDER BY t.transaction_date DESC, t.created_at DESC"
        
        with self.db_manager.get_connection() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]
    
    def get_pending_transactions(self):
        """Get all pending transactions (for approval)"""
        # Check if user has permission to view transactions
        if not self.can_view_transactions():
            raise PermissionError("You do not have permission to view transactions")
        
        with self.db_manager.get_connection() as conn:
            transactions = conn.execute('''
                SELECT t.*, c.category_name, c.category_type, u.full_name as prepared_by_name
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                JOIN users u ON t.prepared_by = u.user_id
                WHERE t.status = 'pending'
                ORDER BY t.transaction_date DESC, t.created_at DESC
            ''').fetchall()
            
            return [dict(row) for row in transactions]
    
    def get_pending_transactions_count(self):
        """Get count of pending transactions"""
        try:
            with self.db_manager.get_connection() as conn:
                result = conn.execute(
                    "SELECT COUNT(*) as count FROM transactions WHERE status = 'pending'"
                ).fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting pending transactions count: {e}")
            return 0
    
    def get_todays_transactions_count(self):
        """Get count of today's transactions"""
        try:
            today = datetime.now().date().isoformat()
            with self.db_manager.get_connection() as conn:
                result = conn.execute(
                    "SELECT COUNT(*) as count FROM transactions WHERE transaction_date = ?",
                    (today,)
                ).fetchone()
                return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting today's transactions count: {e}")
            return 0
    
    def get_monthly_totals(self, year=None, month=None):
        """Get monthly income and expense totals"""
        try:
            if year is None:
                year = datetime.now().year
            if month is None:
                month = datetime.now().month
            
            with self.db_manager.get_connection() as conn:
                # Monthly income
                income_result = conn.execute('''
                    SELECT COALESCE(SUM(t.amount), 0) as total_income
                    FROM transactions t
                    JOIN categories c ON t.category_id = c.category_id
                    WHERE strftime('%Y', t.transaction_date) = ? 
                    AND strftime('%m', t.transaction_date) = ?
                    AND c.category_type = 'income' AND t.status = 'approved'
                ''', (str(year), f"{month:02d}")).fetchone()
                
                # Monthly expenses
                expense_result = conn.execute('''
                    SELECT COALESCE(SUM(t.amount), 0) as total_expense
                    FROM transactions t
                    JOIN categories c ON t.category_id = c.category_id
                    WHERE strftime('%Y', t.transaction_date) = ? 
                    AND strftime('%m', t.transaction_date) = ?
                    AND c.category_type = 'expense' AND t.status = 'approved'
                ''', (str(year), f"{month:02d}")).fetchone()
                
                return {
                    'income': income_result['total_income'] if income_result else 0,
                    'expense': expense_result['total_expense'] if expense_result else 0
                }
                
        except Exception as e:
            print(f"Error getting monthly totals: {e}")
            return {'income': 0, 'expense': 0}