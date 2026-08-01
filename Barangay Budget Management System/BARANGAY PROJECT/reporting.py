# reporting.py
from datetime import datetime, timedelta, date

class ReportGenerator:
    def __init__(self, db_manager, auth_system):
        self.db_manager = db_manager
        self.auth_system = auth_system
    
    def generate_daily_report(self, report_date=None):
        self.auth_system.require_auth()
        
        if report_date is None:
            report_date = date.today()  # Now date is defined
        
        try:
            transactions = self.db_manager.fetch_all('''
                SELECT t.*, c.category_name, c.category_type, u.full_name as prepared_by_name
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                JOIN users u ON t.prepared_by = u.user_id
                WHERE t.transaction_date = ? AND t.status = 'approved'
                ORDER BY t.created_at DESC
            ''', (report_date,))
            
            report = {
                'date': report_date,
                'total_income': 0,
                'total_expenses': 0,
                'transactions': [],
                'transaction_count': len(transactions)
            }
            
            for transaction in transactions:
                transaction_dict = dict(transaction)
                report['transactions'].append(transaction_dict)
                
                if transaction_dict['category_type'] == 'income':
                    report['total_income'] += transaction_dict['amount']
                else:
                    report['total_expenses'] += transaction_dict['amount']
            
            report['net_flow'] = report['total_income'] - report['total_expenses']
            return report
            
        except Exception as e:
            raise e
    
    def generate_monthly_report(self, year=None, month=None):
        self.auth_system.require_auth()
        
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{31 if month in [1,3,5,7,8,10,12] else 30}"
        
        try:
            # Category breakdown
            categories = self.db_manager.fetch_all('''
                SELECT c.category_name, c.category_type, SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE t.transaction_date BETWEEN ? AND ? AND t.status = 'approved'
                GROUP BY c.category_id, c.category_name, c.category_type
                ORDER BY c.category_type, total DESC
            ''', (start_date, end_date))
            
            report = {
                'period': f"{year}-{month:02d}",
                'total_income': 0,
                'total_expenses': 0,
                'category_breakdown': [],
                'transaction_count': 0
            }
            
            for category in categories:
                category_dict = dict(category)
                report['category_breakdown'].append(category_dict)
                if category_dict['category_type'] == 'income':
                    report['total_income'] += category_dict['total']
                else:
                    report['total_expenses'] += category_dict['total']
                report['transaction_count'] += 1
            
            report['net_flow'] = report['total_income'] - report['total_expenses']
            return report
            
        except Exception as e:
            raise e