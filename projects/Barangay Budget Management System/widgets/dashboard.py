# widgets/dashboard.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class Dashboard:
    def __init__(self, parent, auth_system, db_manager, cash_manager, on_logout, on_navigate):
        self.parent = parent
        self.auth_system = auth_system
        self.db_manager = db_manager
        self.cash_manager = cash_manager
        self.on_logout = on_logout
        self.on_navigate = on_navigate
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.update_stats()
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        # Welcome message
        welcome_text = f"Welcome, {self.auth_system.current_user['full_name']}"
        ttk.Label(header_frame, text=welcome_text, 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # User info
        user_info = f"Position: {self.auth_system.current_user['position']} | Access: {self.auth_system.current_user['access_level']}"
        ttk.Label(header_frame, text=user_info, 
                 font=('Arial', 10)).pack(side='left', padx=20)
        
        # Logout button
        logout_btn = ttk.Button(header_frame, text="Logout", 
                               command=self.on_logout)
        logout_btn.pack(side='right')
        
        # Date display
        current_date = datetime.now().strftime("%B %d, %Y")
        date_label = ttk.Label(header_frame, text=current_date, 
                              font=('Arial', 10), foreground='gray')
        date_label.pack(side='right', padx=20)
        
        # Quick stats frame
        self.create_stats_section()
        
        # Main buttons frame
        self.create_buttons_section()
    
    def create_stats_section(self):
        stats_frame = ttk.LabelFrame(self.frame, text="Quick Overview", padding="15")
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # Cash Balance
        self.cash_balance_label = ttk.Label(stats_frame, text="Cash on Hand: Loading...", 
                                       font=('Arial', 10, 'bold'))
        self.cash_balance_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        # Today's transactions
        self.today_trans_label = ttk.Label(stats_frame, text="Today's Transactions: Loading...", 
                                          font=('Arial', 10))
        self.today_trans_label.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        
        # Monthly income
        self.month_income_label = ttk.Label(stats_frame, text="Monthly Income: Loading...", 
                                           font=('Arial', 10))
        self.month_income_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        
        # Monthly expenses
        self.month_expense_label = ttk.Label(stats_frame, text="Monthly Expenses: Loading...", 
                                            font=('Arial', 10))
        self.month_expense_label.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        # Pending approvals
        self.pending_label = ttk.Label(stats_frame, text="Pending Approvals: Loading...", 
                                      font=('Arial', 10))
        self.pending_label.grid(row=1, column=2, padx=20, pady=5, sticky='w')
        
        # NEW: Active users count (admin only)
        if self.auth_system.current_user['access_level'] == 'admin':
            self.active_users_label = ttk.Label(stats_frame, text="Active Users: Loading...", 
                                              font=('Arial', 10))
            self.active_users_label.grid(row=0, column=2, padx=20, pady=5, sticky='w')
        
        # Configure grid
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
    
    def create_buttons_section(self):
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Row 1 - Core Functions (Available to all users including kagawad)
        add_trans_btn = ttk.Button(buttons_frame, text="➕ Add Transaction", 
                                command=lambda: self.on_navigate('add_transaction'), 
                                width=25)
        add_trans_btn.grid(row=0, column=0, padx=15, pady=15, ipady=10)

        view_trans_btn = ttk.Button(buttons_frame, text="📋 View Transactions", 
                                command=lambda: self.on_navigate('view_transactions'), 
                                width=25)
        view_trans_btn.grid(row=0, column=1, padx=15, pady=15, ipady=10)

        daily_report_btn = ttk.Button(buttons_frame, text="📊 Daily Report", 
                                    command=lambda: self.on_navigate('daily_report'), 
                                    width=25)
        daily_report_btn.grid(row=0, column=2, padx=15, pady=15, ipady=10)

        # Row 2 - Kagawad and above functions
        if self.auth_system.current_user['access_level'] in ['admin', 'treasurer', 'kagawad']:
            monthly_report_btn = ttk.Button(buttons_frame, text="📈 Monthly Report", 
                                        command=lambda: self.on_navigate('monthly_report'), 
                                        width=25)
            monthly_report_btn.grid(row=1, column=0, padx=15, pady=15, ipady=10)

        # Row 2 continued - Treasurer and Admin only functions
        if self.auth_system.current_user['access_level'] in ['admin', 'treasurer']:
            cash_btn = ttk.Button(buttons_frame, text="💰 Cash Management", 
                                command=lambda: self.on_navigate('cash_management'), 
                                width=25)
            cash_btn.grid(row=1, column=1, padx=15, pady=15, ipady=10)
            
            approve_btn = ttk.Button(buttons_frame, text="✅ Approve Transactions", 
                                    command=lambda: self.on_navigate('approve_transactions'), 
                                    width=25)
            approve_btn.grid(row=1, column=2, padx=15, pady=15, ipady=10)

        # Row 3 - Admin Only Functions
        if self.auth_system.current_user['access_level'] == 'admin':
            # User Management Button
            user_btn = ttk.Button(buttons_frame, text="👥 User Management", 
                                command=lambda: self.on_navigate('user_management'), 
                                width=25)
            user_btn.grid(row=2, column=0, padx=15, pady=15, ipady=10)
            
            settings_btn = ttk.Button(buttons_frame, text="⚙️ System Settings", 
                                    command=lambda: self.on_navigate('system_settings'), 
                                    width=25)
            settings_btn.grid(row=2, column=1, padx=15, pady=15, ipady=10)
            
            budget_btn = ttk.Button(buttons_frame, text="📋 Budget Allocation", 
                                command=lambda: self.on_navigate('budget_allocation'), 
                                width=25)
            budget_btn.grid(row=2, column=2, padx=15, pady=15, ipady=10)

        # Row 4 - Additional Admin Functions
        if self.auth_system.current_user['access_level'] == 'admin':
            # User Reports Button
            user_reports_btn = ttk.Button(buttons_frame, text="📊 User Activity Reports", 
                                        command=lambda: self.on_navigate('user_reports'), 
                                        width=25)
            user_reports_btn.grid(row=3, column=0, padx=15, pady=15, ipady=10)
            
            # Audit Log Button
            audit_log_btn = ttk.Button(buttons_frame, text="📋 System Audit Log", 
                                    command=lambda: self.on_navigate('audit_log'), 
                                    width=25)
            audit_log_btn.grid(row=3, column=1, padx=15, pady=15, ipady=10)

        # Configure grid weights for centering
        for i in range(3):
            buttons_frame.columnconfigure(i, weight=1)
        for i in range(4):  # Increased to 4 rows to accommodate new admin functions
            buttons_frame.rowconfigure(i, weight=1)
    
    def update_stats(self):
        """Update the dashboard statistics"""
        try:
            # Get database connection
            conn = self.db_manager.get_connection()
            
            # Today's transactions count (only regular transactions)
            today = datetime.now().date().isoformat()
            today_count = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE transaction_date = ? AND transaction_type = 'regular'",
                (today,)
            ).fetchone()[0]
            
            # Monthly totals - ONLY REGULAR TRANSACTIONS
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Monthly Income: Only approved regular income transactions
            monthly_income_result = conn.execute('''
                SELECT COALESCE(SUM(t.amount), 0) as total_income 
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE strftime('%Y', t.transaction_date) = ? 
                AND strftime('%m', t.transaction_date) = ?
                AND c.category_type = 'income' 
                AND t.status = 'approved'
                AND t.transaction_type = 'regular'  -- EXCLUDE CASH ADJUSTMENTS
            ''', (str(current_year), f"{current_month:02d}")).fetchone()
            monthly_income = monthly_income_result['total_income'] if monthly_income_result else 0
            
            # Monthly Expenses: Only approved regular expense transactions
            monthly_expense_result = conn.execute('''
                SELECT COALESCE(SUM(t.amount), 0) as total_expense 
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE strftime('%Y', t.transaction_date) = ? 
                AND strftime('%m', t.transaction_date) = ?
                AND c.category_type = 'expense' 
                AND t.status = 'approved'
                AND t.transaction_type = 'regular'  -- EXCLUDE CASH ADJUSTMENTS
            ''', (str(current_year), f"{current_month:02d}")).fetchone()
            monthly_expense = monthly_expense_result['total_expense'] if monthly_expense_result else 0
            
            # Pending approvals (only regular transactions)
            pending_count = conn.execute(
                "SELECT COUNT(*) FROM transactions WHERE status = 'pending' AND transaction_type = 'regular'"
            ).fetchone()[0]
            
            # NEW: Active users count (for admin only)
            if self.auth_system.current_user['access_level'] == 'admin':
                active_users_count = self.db_manager.get_active_users_count()
            
            # Update labels
            self.today_trans_label.config(text=f"Today's Transactions: {today_count}")
            self.month_income_label.config(text=f"Monthly Income: ₱{monthly_income:,.2f}")
            self.month_expense_label.config(text=f"Monthly Expenses: ₱{monthly_expense:,.2f}")
            self.pending_label.config(text=f"Pending Approvals: {pending_count}")
            
            # NEW: Update active users count for admin
            if self.auth_system.current_user['access_level'] == 'admin':
                self.active_users_label.config(text=f"Active Users: {active_users_count}")
            
            # Update cash balance - THIS INCLUDES BOTH REGULAR TRANSACTIONS AND CASH ADJUSTMENTS
            if self.cash_manager:
                cash_balance = self.cash_manager.get_current_balance()
                self.cash_balance_label.config(text=f"Cash on Hand: ₱{cash_balance:,.2f}")
                
                # Color code cash balance
                if cash_balance > 0:
                    self.cash_balance_label.config(foreground='green')
                elif cash_balance < 0:
                    self.cash_balance_label.config(foreground='red')
                else:
                    self.cash_balance_label.config(foreground='black')
            
            # Debug information
            print(f"=== DASHBOARD STATS ===")
            print(f"Monthly Income (Regular): ₱{monthly_income:,.2f}")
            print(f"Monthly Expense (Regular): ₱{monthly_expense:,.2f}")
            print(f"Cash Balance (Total): ₱{cash_balance if self.cash_manager else 'N/A':,.2f}")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            # Set default values on error
            self.today_trans_label.config(text="Today's Transactions: Error")
            self.month_income_label.config(text="Monthly Income: Error")
            self.month_expense_label.config(text="Monthly Expenses: Error")
            self.pending_label.config(text="Pending Approvals: Error")
            self.cash_balance_label.config(text="Cash on Hand: Error", foreground='red')
            
            if self.auth_system.current_user['access_level'] == 'admin':
                self.active_users_label.config(text="Active Users: Error")
    
    def refresh_dashboard(self):
        """Public method to refresh dashboard data"""
        self.update_stats()
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
        self.update_stats()  # Refresh stats when shown
    
    def hide(self):
        self.frame.pack_forget()