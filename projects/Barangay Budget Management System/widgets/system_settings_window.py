# widgets/system_settings_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class SystemSettingsWindow:
    def __init__(self, parent, auth_system, db_manager, on_back):
        self.parent = parent
        self.auth_system = auth_system
        self.db_manager = db_manager
        self.on_back = on_back
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="System Settings", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # Back button
        ttk.Button(header_frame, text="← Back to Dashboard", 
                  command=self.on_back).pack(side='right')
        
        # Settings notebook
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # General Settings Tab
        self.general_frame = ttk.Frame(notebook)
        notebook.add(self.general_frame, text="General Settings")
        self.create_general_tab()
        
        # Security Settings Tab
        self.security_frame = ttk.Frame(notebook)
        notebook.add(self.security_frame, text="Security")
        self.create_security_tab()
        
        # Backup & Restore Tab
        self.backup_frame = ttk.Frame(notebook)
        notebook.add(self.backup_frame, text="Backup & Restore")
        self.create_backup_tab()
        
        # System Info Tab
        self.info_frame = ttk.Frame(notebook)
        notebook.add(self.info_frame, text="System Information")
        self.create_info_tab()
    
    def create_general_tab(self):
        """Create general settings tab"""
        # System Name
        ttk.Label(self.general_frame, text="System Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.system_name = tk.StringVar(value="Barangay Budget Management System")
        ttk.Entry(self.general_frame, textvariable=self.system_name, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        # Default Currency
        ttk.Label(self.general_frame, text="Default Currency:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.currency = tk.StringVar(value="PHP")
        currency_combo = ttk.Combobox(self.general_frame, textvariable=self.currency,
                                     values=["PHP", "USD", "EUR"], state="readonly", width=10)
        currency_combo.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        
        # Date Format
        ttk.Label(self.general_frame, text="Date Format:").grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.date_format = tk.StringVar(value="YYYY-MM-DD")
        date_combo = ttk.Combobox(self.general_frame, textvariable=self.date_format,
                                 values=["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"], state="readonly", width=15)
        date_combo.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        
        # Auto-logout timeout
        ttk.Label(self.general_frame, text="Auto-logout (minutes):").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.auto_logout = tk.IntVar(value=30)
        ttk.Spinbox(self.general_frame, from_=5, to=240, textvariable=self.auto_logout, width=10).grid(row=3, column=1, padx=10, pady=10, sticky='w')
        
        # Transaction numbering
        ttk.Label(self.general_frame, text="Transaction Number Prefix:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.trans_prefix = tk.StringVar(value="TRX")
        ttk.Entry(self.general_frame, textvariable=self.trans_prefix, width=10).grid(row=4, column=1, padx=10, pady=10, sticky='w')
        
        # Save button
        ttk.Button(self.general_frame, text="Save General Settings", 
                  command=self.save_general_settings).grid(row=5, column=0, columnspan=2, pady=20)
    
    def create_security_tab(self):
        """Create security settings tab"""
        # Password policy
        policy_frame = ttk.LabelFrame(self.security_frame, text="Password Policy", padding="10")
        policy_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.min_password_length = tk.IntVar(value=8)
        ttk.Checkbutton(policy_frame, text="Enforce minimum password length:", 
                       variable=tk.BooleanVar(value=True)).grid(row=0, column=0, sticky='w')
        ttk.Spinbox(policy_frame, from_=6, to=20, textvariable=self.min_password_length, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(policy_frame, text="characters").grid(row=0, column=2, sticky='w')
        
        self.require_special_char = tk.BooleanVar(value=True)
        ttk.Checkbutton(policy_frame, text="Require special characters", 
                       variable=self.require_special_char).grid(row=1, column=0, columnspan=2, sticky='w')
        
        self.require_numbers = tk.BooleanVar(value=True)
        ttk.Checkbutton(policy_frame, text="Require numbers", 
                       variable=self.require_numbers).grid(row=2, column=0, columnspan=2, sticky='w')
        
        # Session settings
        session_frame = ttk.LabelFrame(self.security_frame, text="Session Settings", padding="10")
        session_frame.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        self.max_login_attempts = tk.IntVar(value=5)
        ttk.Label(session_frame, text="Max login attempts:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(session_frame, from_=3, to=10, textvariable=self.max_login_attempts, width=5).grid(row=0, column=1, padx=5)
        
        self.lockout_duration = tk.IntVar(value=30)
        ttk.Label(session_frame, text="Lockout duration (minutes):").grid(row=1, column=0, sticky='w')
        ttk.Spinbox(session_frame, from_=5, to=240, textvariable=self.lockout_duration, width=5).grid(row=1, column=1, padx=5)
        
        # Save button
        ttk.Button(self.security_frame, text="Save Security Settings", 
                  command=self.save_security_settings).grid(row=2, column=0, pady=20)
    
    def create_backup_tab(self):
        """Create backup and restore tab"""
        # Backup settings
        backup_frame = ttk.LabelFrame(self.backup_frame, text="Backup Settings", padding="10")
        backup_frame.pack(fill='x', padx=10, pady=10)
        
        self.auto_backup = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="Enable automatic daily backups", 
                       variable=self.auto_backup).pack(anchor='w')
        
        ttk.Label(backup_frame, text="Backup retention (days):").pack(anchor='w', pady=5)
        self.backup_retention = tk.IntVar(value=30)
        ttk.Spinbox(backup_frame, from_=7, to=365, textvariable=self.backup_retention, width=5).pack(anchor='w')
        
        # Backup actions
        action_frame = ttk.LabelFrame(self.backup_frame, text="Actions", padding="10")
        action_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(action_frame, text="Create Backup Now", 
                  command=self.create_backup).pack(pady=5)
        ttk.Button(action_frame, text="Restore from Backup", 
                  command=self.restore_backup).pack(pady=5)
        ttk.Button(action_frame, text="Download Backup", 
                  command=self.download_backup).pack(pady=5)
    
    def create_info_tab(self):
        """Create system information tab"""
        info_frame = ttk.Frame(self.info_frame)
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # System information
        system_info = [
            ("System Version", "1.0.0"),
            ("Database Version", "1.0.0"),
            ("Last Backup", "2024-01-15 14:30:00"),
            ("Total Users", "3"),
            ("Total Transactions", "156"),
            ("Database Size", "2.4 MB"),
        ]
        
        for i, (label, value) in enumerate(system_info):
            ttk.Label(info_frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
                row=i, column=0, padx=10, pady=5, sticky='w')
            ttk.Label(info_frame, text=value).grid(
                row=i, column=1, padx=10, pady=5, sticky='w')
        
        # System actions
        action_frame = ttk.LabelFrame(self.info_frame, text="System Maintenance", padding="10")
        action_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(action_frame, text="Optimize Database", 
                  command=self.optimize_database).pack(pady=5)
        ttk.Button(action_frame, text="Clear Cache", 
                  command=self.clear_cache).pack(pady=5)
        ttk.Button(action_frame, text="Check for Updates", 
                  command=self.check_updates).pack(pady=5)
    
    def load_current_settings(self):
        """Load current system settings"""
        # This would load actual settings from database or config file
        # For now, we're using the default values set in the UI creation
        pass
    
    def save_general_settings(self):
        """Save general system settings"""
        try:
            # Validate inputs
            if not self.system_name.get().strip():
                messagebox.showerror("Error", "System name cannot be empty")
                return
            
            # Save settings (simulated)
            settings = {
                'system_name': self.system_name.get(),
                'currency': self.currency.get(),
                'date_format': self.date_format.get(),
                'auto_logout': self.auto_logout.get(),
                'trans_prefix': self.trans_prefix.get()
            }
            
            messagebox.showinfo("Success", "General settings saved successfully!\n\nNote: This is a simulation.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def save_security_settings(self):
        """Save security settings"""
        try:
            settings = {
                'min_password_length': self.min_password_length.get(),
                'require_special_char': self.require_special_char.get(),
                'require_numbers': self.require_numbers.get(),
                'max_login_attempts': self.max_login_attempts.get(),
                'lockout_duration': self.lockout_duration.get()
            }
            
            messagebox.showinfo("Success", "Security settings saved successfully!\n\nNote: This is a simulation.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save security settings: {e}")
    
    def create_backup(self):
        """Create system backup"""
        if messagebox.askyesno("Create Backup", "Create a new system backup?"):
            # Simulated backup creation
            messagebox.showinfo("Backup Created", 
                              "System backup created successfully!\n\nNote: This is a simulation.")
    
    def restore_backup(self):
        """Restore from backup"""
        messagebox.showinfo("Restore Backup", 
                          "This feature would allow you to restore from a previous backup.\n\nNote: This is a simulation.")
    
    def download_backup(self):
        """Download backup file"""
        messagebox.showinfo("Download Backup", 
                          "Backup file would be downloaded to your computer.\n\nNote: This is a simulation.")
    
    def optimize_database(self):
        """Optimize database performance"""
        if messagebox.askyesno("Optimize Database", "Optimize database for better performance?"):
            # Simulated optimization
            messagebox.showinfo("Optimization Complete", 
                              "Database optimization completed successfully!\n\nNote: This is a simulation.")
    
    def clear_cache(self):
        """Clear system cache"""
        if messagebox.askyesno("Clear Cache", "Clear system cache?"):
            # Simulated cache clear
            messagebox.showinfo("Cache Cleared", 
                              "System cache cleared successfully!\n\nNote: This is a simulation.")
    
    def check_updates(self):
        """Check for system updates"""
        messagebox.showinfo("Check Updates", 
                          "Your system is up to date!\n\nNote: This is a simulation.")
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
    
    def hide(self):
        self.frame.pack_forget()