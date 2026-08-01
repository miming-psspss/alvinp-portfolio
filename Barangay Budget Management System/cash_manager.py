# cash_manager.py
from datetime import datetime
import random

class CashManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_current_balance(self):
        """Get the current cash balance"""
        result = self.db_manager.fetch_one(
            "SELECT current_balance FROM cash_balance ORDER BY balance_id DESC LIMIT 1"
        )
        return result['current_balance'] if result else 0
    
    def update_balance(self, amount, transaction_type, description=""):
        """Update cash balance when transactions are made"""
        current_balance = self.get_current_balance()
        
        if transaction_type == 'income':
            new_balance = current_balance + amount
        elif transaction_type == 'expense':
            new_balance = current_balance - amount
        else:
            raise ValueError("Transaction type must be 'income' or 'expense'")
        
        # Update balance
        self.db_manager.execute_query(
            "INSERT INTO cash_balance (current_balance) VALUES (?)",
            (new_balance,)
        )
        
        return new_balance
    
    def get_balance_history(self, days=30):
        """Get cash balance history for the specified number of days"""
        history = self.db_manager.fetch_all('''
            SELECT current_balance, last_updated 
            FROM cash_balance 
            WHERE date(last_updated) >= date('now', ?)
            ORDER BY last_updated DESC
        ''', (f'-{days} days',))
        
        return [dict(row) for row in history]
    
    def get_cash_adjustment_category_id(self):
        """Get the category ID for cash adjustments"""
        result = self.db_manager.fetch_one(
            "SELECT category_id FROM categories WHERE category_name = 'Cash Adjustment'"
        )
        if result:
            return result['category_id']
        else:
            # Create the category if it doesn't exist
            self.db_manager.execute_query(
                "INSERT INTO categories (category_name, category_type, description) VALUES (?, ?, ?)",
                ('Cash Adjustment', 'income', 'Cash management adjustments')
            )
            result = self.db_manager.fetch_one(
                "SELECT category_id FROM categories WHERE category_name = 'Cash Adjustment'"
            )
            return result['category_id'] if result else None
    
    def add_cash_adjustment(self, amount, description, user_id, adjustment_type='income'):
        """Add cash adjustment (not counted in monthly income/expense)"""
        try:
            # Use the database manager's built-in method for cash adjustments
            transaction_number = self.db_manager.add_cash_adjustment(amount, description, user_id)
            
            # Update cash balance
            self.update_balance(amount, adjustment_type, description)
            
            return transaction_number
            
        except Exception as e:
            raise e
    
    def add_income_adjustment(self, amount, description, user_id):
        """Add income cash adjustment"""
        return self.add_cash_adjustment(amount, description, user_id, 'income')
    
    def add_expense_adjustment(self, amount, description, user_id):
        """Add expense cash adjustment"""
        return self.add_cash_adjustment(amount, description, user_id, 'expense')
    
    def get_cash_adjustments(self, start_date=None, end_date=None):
        """Get all cash adjustment transactions"""
        return self.db_manager.get_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type='cash_adjustment'
        )
    
    def get_financial_summary(self):
        """Get comprehensive financial summary"""
        current_balance = self.get_current_balance()
        
        # Get monthly regular transactions (exclude cash adjustments)
        monthly_financials = self.db_manager.get_monthly_financials()
        
        # Get cash adjustments for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        start_date = f"{current_year}-{current_month:02d}-01"
        if current_month == 12:
            end_date = f"{current_year}-12-31"
        else:
            end_date = f"{current_year}-{current_month+1:02d}-01"
        
        cash_adjustments = self.get_cash_adjustments(start_date, end_date)
        total_adjustments = sum(adj['amount'] for adj in cash_adjustments if adj['status'] == 'approved')
        
        return {
            'current_balance': current_balance,
            'monthly_income': monthly_financials['income'],
            'monthly_expenses': monthly_financials['expense'],
            'cash_adjustments': total_adjustments,
            'net_cash_flow': monthly_financials['income'] - monthly_financials['expense'] + total_adjustments
        }