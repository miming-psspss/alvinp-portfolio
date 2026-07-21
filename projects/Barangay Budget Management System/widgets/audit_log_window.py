# widgets/audit_log_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3

class AuditLogWindow:
    def __init__(self, parent, auth_system, db_manager, on_back):
        self.parent = parent
        self.auth_system = auth_system
        self.db_manager = db_manager
        self.on_back = on_back
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_audit_logs()
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="System Audit Log", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # Back button
        ttk.Button(header_frame, text="← Back to Dashboard", 
                  command=self.on_back).pack(side='right')
        
        # Controls frame
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        # Severity filter
        ttk.Label(controls_frame, text="Severity:").pack(side='left', padx=5)
        self.severity_var = tk.StringVar(value="All")
        severity_combo = ttk.Combobox(controls_frame, textvariable=self.severity_var,
                                     values=["All", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                     width=10, state="readonly")
        severity_combo.pack(side='left', padx=5)
        
        # Module filter
        ttk.Label(controls_frame, text="Module:").pack(side='left', padx=5)
        self.module_var = tk.StringVar(value="All")
        module_combo = ttk.Combobox(controls_frame, textvariable=self.module_var,
                                   values=["All", "Authentication", "Transactions", "Users", "System", "Reports"],
                                   width=12, state="readonly")
        module_combo.pack(side='left', padx=5)
        
        # Date filter
        ttk.Label(controls_frame, text="Date:").pack(side='left', padx=5)
        self.date_var = tk.StringVar(value="Last 7 days")
        date_combo = ttk.Combobox(controls_frame, textvariable=self.date_var,
                                 values=["Last 24 hours", "Last 7 days", "Last 30 days", "All time"],
                                 width=12, state="readonly")
        date_combo.pack(side='left', padx=5)
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh", 
                  command=self.load_audit_logs).pack(side='left', padx=10)
        
        # Clear logs button
        ttk.Button(controls_frame, text="Clear Old Logs", 
                  command=self.clear_old_logs).pack(side='left', padx=5)
        
        # Export button
        ttk.Button(controls_frame, text="Export Logs", 
                  command=self.export_logs).pack(side='left', padx=5)
        
        # Audit log treeview
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ("Timestamp", "Severity", "Module", "User", "Action", "Details", "IP Address")
        self.audit_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        self.audit_tree.column("Timestamp", width=150)
        self.audit_tree.column("Severity", width=80)
        self.audit_tree.column("Module", width=100)
        self.audit_tree.column("User", width=100)
        self.audit_tree.column("Action", width=150)
        self.audit_tree.column("Details", width=200)
        self.audit_tree.column("IP Address", width=120)
        
        for col in columns:
            self.audit_tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.audit_tree.yview)
        self.audit_tree.configure(yscrollcommand=scrollbar.set)
        
        self.audit_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to show details
        self.audit_tree.bind("<Double-1>", self.show_log_details)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.frame, text="Log Statistics", padding="10")
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.stats_labels = {}
        stats = [
            ("Total Logs", "total_logs"),
            ("Today", "today"),
            ("Warnings", "warnings"),
            ("Errors", "errors")
        ]
        
        for i, (label, key) in enumerate(stats):
            ttk.Label(stats_frame, text=f"{label}:").grid(row=0, column=i*2, padx=10, pady=5, sticky='w')
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
            self.stats_labels[key].grid(row=0, column=i*2+1, padx=5, pady=5, sticky='w')
    
    def load_audit_logs(self):
        """Load audit logs based on filters"""
        try:
            # Clear existing data
            for item in self.audit_tree.get_children():
                self.audit_tree.delete(item)
            
            # Get filter values
            severity = self.severity_var.get()
            module = self.module_var.get()
            date_range = self.date_var.get()
            
            # Get audit logs (simulated data)
            audit_logs = self.get_audit_logs(severity, module, date_range)
            
            # Populate treeview
            for log in audit_logs:
                item_id = self.audit_tree.insert("", "end", values=log)
                
                # Color code by severity
                if log[1] == "ERROR":
                    self.audit_tree.set(item_id, "Severity", log[1])
                elif log[1] == "WARNING":
                    self.audit_tree.set(item_id, "Severity", log[1])
                elif log[1] == "CRITICAL":
                    self.audit_tree.set(item_id, "Severity", log[1])
            
            # Update statistics
            self.update_statistics(audit_logs)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audit logs: {e}")
    
    def get_audit_logs(self, severity, module, date_range):
        """Get filtered audit logs (simulated data)"""
        # Calculate date range
        if date_range == "Last 24 hours":
            start_date = datetime.now() - timedelta(hours=24)
        elif date_range == "Last 7 days":
            start_date = datetime.now() - timedelta(days=7)
        elif date_range == "Last 30 days":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.min
        
        # Simulated audit log data
        logs = [
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "INFO", "Authentication", "admin", 
             "User login", "Successful login from 192.168.1.1", "192.168.1.1"),
            ((datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), "INFO", "Transactions", "admin", 
             "Transaction created", "Created transaction TRX-001 for ₱1,000.00", "192.168.1.1"),
            ((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "WARNING", "System", "system", 
             "Database backup", "Automatic backup completed", "127.0.0.1"),
            ((datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), "INFO", "Users", "admin", 
             "User created", "Created new user: treasurer", "192.168.1.1"),
            ((datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), "ERROR", "Transactions", "treasurer", 
             "Transaction failed", "Insufficient funds for transaction TRX-002", "192.168.1.2"),
            ((datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), "CRITICAL", "System", "system", 
             "System restart", "Application restarted after update", "127.0.0.1"),
        ]
        
        # Apply filters
        filtered_logs = []
        for log in logs:
            log_date = datetime.strptime(log[0], '%Y-%m-%d %H:%M:%S')
            
            # Date filter
            if log_date < start_date:
                continue
            
            # Severity filter
            if severity != "All" and log[1] != severity:
                continue
            
            # Module filter
            if module != "All" and log[2] != module:
                continue
            
            filtered_logs.append(log)
        
        return filtered_logs
    
    def update_statistics(self, logs):
        """Update log statistics"""
        total = len(logs)
        today_count = sum(1 for log in logs if log[0].startswith(datetime.now().strftime('%Y-%m-%d')))
        warnings = sum(1 for log in logs if log[1] == "WARNING")
        errors = sum(1 for log in logs if log[1] in ["ERROR", "CRITICAL"])
        
        self.stats_labels["total_logs"].config(text=str(total))
        self.stats_labels["today"].config(text=str(today_count))
        self.stats_labels["warnings"].config(text=str(warnings))
        self.stats_labels["errors"].config(text=str(errors))
    
    def show_log_details(self, event):
        """Show detailed view of selected log entry"""
        selection = self.audit_tree.selection()
        if not selection:
            return
        
        item = self.audit_tree.item(selection[0])
        values = item['values']
        
        details_window = tk.Toplevel(self.parent)
        details_window.title("Audit Log Details")
        details_window.geometry("500x300")
        details_window.transient(self.parent)
        details_window.grab_set()
        
        # Create details frame
        details_frame = ttk.Frame(details_window, padding="20")
        details_frame.pack(fill='both', expand=True)
        
        fields = [
            ("Timestamp", values[0]),
            ("Severity", values[1]),
            ("Module", values[2]),
            ("User", values[3]),
            ("Action", values[4]),
            ("Details", values[5]),
            ("IP Address", values[6])
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(details_frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
                row=i, column=0, padx=5, pady=5, sticky='w')
            ttk.Label(details_frame, text=value, font=('Arial', 10)).grid(
                row=i, column=1, padx=5, pady=5, sticky='w')
    
    def clear_old_logs(self):
        """Clear logs older than 30 days"""
        if messagebox.askyesno("Confirm Clear", 
                             "This will delete audit logs older than 30 days. Continue?"):
            # Simulated clear operation
            messagebox.showinfo("Success", "Old audit logs cleared successfully.\n\nNote: This is a simulation.")
            self.load_audit_logs()
    
    def export_logs(self):
        """Export audit logs to file"""
        try:
            filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            # Simulated export operation
            messagebox.showinfo("Export Successful", 
                              f"Audit logs exported to {filename}\n\nNote: This is a simulation.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export logs: {e}")
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
    
    def hide(self):
        self.frame.pack_forget()