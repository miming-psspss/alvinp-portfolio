# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from widgets import LoginWindow, Dashboard, TransactionWindow, ReportWindow, AdminWindow, CashWindow
from database_fixed import DatabaseManager
from auth import AuthSystem
from transaction_manager import TransactionManager
from reporting import ReportGenerator
from cash_manager import CashManager

class BarangayBudgetSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Barangay Budget Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Center the window
        self.center_window()
        
        # Initialize core systems with fixed database
        self.db_manager = DatabaseManager()
        self.auth_system = AuthSystem(self.db_manager)
        self.cash_manager = CashManager(self.db_manager)
        self.transaction_manager = TransactionManager(
            self.db_manager, self.auth_system, self.cash_manager
        )
        self.report_generator = ReportGenerator(self.db_manager, self.auth_system)
        
        # Style configuration
        self.setup_styles()
        
        # Current active window
        self.current_window = None
        
        # Show login screen first
        self.show_login()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Configure custom styles for the application"""
        self.style = ttk.Style()
        
        # Configure styles
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Success.TButton', background='#28a745', foreground='white')
        self.style.configure('Primary.TButton', background='#007bff', foreground='white')
        self.style.configure('Danger.TButton', background='#dc3545', foreground='white')
        
        # Map styles to ensure they work on different platforms
        self.style.map('Success.TButton',
                      background=[('active', '#218838'), ('pressed', '#1e7e34')])
        self.style.map('Primary.TButton',
                      background=[('active', '#0069d9'), ('pressed', '#0062cc')])
        self.style.map('Danger.TButton',
                      background=[('active', '#c82333'), ('pressed', '#bd2130')])
    
    def clear_window(self):
        """Clear all widgets from the root window"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.current_window = None
    
    def show_window(self, window_class, *args, **kwargs):
        """Show a specific window class"""
        self.clear_window()
        self.current_window = window_class(self.root, *args, **kwargs)
        self.current_window.show()
    
    def show_login(self):
        """Show the login window"""
        self.show_window(
            LoginWindow,
            auth_system=self.auth_system,
            on_login_success=self.show_dashboard
        )
    
    def show_dashboard(self):
        """Show the main dashboard"""
        if not self.auth_system.is_logged_in():
            messagebox.showerror("Error", "Please login first")
            self.show_login()
            return
        
        self.show_window(
            Dashboard,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            cash_manager=self.cash_manager,  # Pass cash_manager to dashboard
            on_logout=self.logout,
            on_navigate=self.navigate_to
        )
    
    def show_add_transaction(self):
        """Show the add transaction window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        self.show_window(
            TransactionWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            transaction_manager=self.transaction_manager,
            on_back=self.show_dashboard
        )
        # Set to add mode
        self.current_window.set_mode("add")
    
    def show_view_transactions(self):
        """Show the view transactions window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        self.show_window(
            TransactionWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            transaction_manager=self.transaction_manager,
            on_back=self.show_dashboard
        )
        # Set to view mode
        self.current_window.set_mode("view")
    
    def show_daily_report(self):
        """Show the daily report window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        self.show_window(
            ReportWindow,
            auth_system=self.auth_system,
            report_generator=self.report_generator,
            on_back=self.show_dashboard
        )
        # Set to daily report mode
        self.current_window.report_type_var.set("daily")
        self.current_window.switch_report_type()
    
    def show_monthly_report(self):
        """Show the monthly report window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        self.show_window(
            ReportWindow,
            auth_system=self.auth_system,
            report_generator=self.report_generator,
            on_back=self.show_dashboard
        )
        # Set to monthly report mode
        self.current_window.report_type_var.set("monthly")
        self.current_window.switch_report_type()
    
    def show_approve_transactions(self):
        """Show the admin approval window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        # Check if user has permission
        if self.auth_system.current_user['access_level'] not in ['admin', 'treasurer']:
            messagebox.showerror("Access Denied", 
                               "You need admin or treasurer privileges to access this feature.")
            return
        
        self.show_window(
            AdminWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            transaction_manager=self.transaction_manager,
            on_back=self.show_dashboard
        )
    
    def show_cash_management(self):
        """Show cash management window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        self.show_window(
            CashWindow,
            auth_system=self.auth_system,
            cash_manager=self.cash_manager,
            on_back=self.show_dashboard
        )
    
    def show_budget_allocation(self):
        """Show budget allocation window (placeholder)"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        messagebox.showinfo("Coming Soon", 
                          "Budget Allocation feature will be implemented in the next version.")
    
    def show_user_management(self):
        """Show user management window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        # Check if user has admin permission
        if self.auth_system.current_user['access_level'] != 'admin':
            messagebox.showerror("Access Denied", 
                               "You need admin privileges to access this feature.")
            return
        
        # Import here to avoid circular imports
        from widgets.user_management_window import UserManagementWindow
        
        self.show_window(
            UserManagementWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            on_back=self.show_dashboard
        )
    
    def show_user_reports(self):
        """Show user activity reports window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        # Check if user has admin permission
        if self.auth_system.current_user['access_level'] != 'admin':
            messagebox.showerror("Access Denied", 
                               "You need admin privileges to access this feature.")
            return
        
        # Import here to avoid circular imports
        from widgets.user_reports_window import UserReportsWindow
        
        self.show_window(
            UserReportsWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            on_back=self.show_dashboard
        )
    
    def show_audit_log(self):
        """Show system audit log window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        # Check if user has admin permission
        if self.auth_system.current_user['access_level'] != 'admin':
            messagebox.showerror("Access Denied", 
                               "You need admin privileges to access this feature.")
            return
        
        # Import here to avoid circular imports
        from widgets.audit_log_window import AuditLogWindow
        
        self.show_window(
            AuditLogWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            on_back=self.show_dashboard
        )
    
    def show_system_settings(self):
        """Show system settings window"""
        if not self.auth_system.is_logged_in():
            self.show_login()
            return
        
        # Check if user has admin permission
        if self.auth_system.current_user['access_level'] != 'admin':
            messagebox.showerror("Access Denied", 
                               "You need admin privileges to access this feature.")
            return
        
        # Import here to avoid circular imports
        from widgets.system_settings_window import SystemSettingsWindow
        
        self.show_window(
            SystemSettingsWindow,
            auth_system=self.auth_system,
            db_manager=self.db_manager,
            on_back=self.show_dashboard
        )
    
    def navigate_to(self, destination):
        """Navigate to different sections of the application"""
        navigation_map = {
            'add_transaction': self.show_add_transaction,
            'view_transactions': self.show_view_transactions,
            'daily_report': self.show_daily_report,
            'monthly_report': self.show_monthly_report,
            'approve_transactions': self.show_approve_transactions,
            'budget_allocation': self.show_budget_allocation,
            'user_management': self.show_user_management,
            'system_settings': self.show_system_settings,
            'cash_management': self.show_cash_management,
            'user_reports': self.show_user_reports,  # NEW
            'audit_log': self.show_audit_log         # NEW
        }
        
        if destination in navigation_map:
            navigation_map[destination]()
        else:
            messagebox.showerror("Error", f"Unknown destination: {destination}")
    
    def logout(self):
        """Logout the current user"""
        self.auth_system.logout()
        messagebox.showinfo("Logged Out", "You have been successfully logged out.")
        self.show_login()
    
    def on_closing(self):
        """Handle application closing - IMPORTANT: Close database connection"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Close database connection properly
            if hasattr(self, 'db_manager'):
                self.db_manager.close_connection()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BarangayBudgetSystemGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()