# widgets/user_management_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

class UserManagementWindow:
    def __init__(self, parent, auth_system, db_manager, on_back):
        self.parent = parent
        self.auth_system = auth_system
        self.db_manager = db_manager
        self.on_back = on_back
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_users()
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="User Management", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # Back button
        ttk.Button(header_frame, text="← Back to Dashboard", 
                  command=self.on_back).pack(side='right')
        
        # Controls frame
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        # Add user button
        ttk.Button(controls_frame, text="➕ Add New User", 
                  command=self.add_user).pack(side='left', padx=5)
        
        # Refresh button
        ttk.Button(controls_frame, text="🔄 Refresh", 
                  command=self.load_users).pack(side='left', padx=5)
        
        # Search frame
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(side='right')
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # Users table frame
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create treeview
        columns = ("ID", "Username", "Full Name", "Position", "Access Level", "Status", "Created")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.column("ID", width=50)
        self.tree.column("Username", width=120)
        self.tree.column("Full Name", width=150)
        self.tree.column("Position", width=120)
        self.tree.column("Access Level", width=100)
        self.tree.column("Status", width=80)
        self.tree.column("Created", width=120)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons frame
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(action_frame, text="Edit User", 
                  command=self.edit_user).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Reset Password", 
                  command=self.reset_password).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Activate/Deactivate", 
                  command=self.toggle_user_status).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Delete User", 
                  command=self.delete_user).pack(side='left', padx=5)
    
    def load_users(self):
        """Load all users from database"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            users = self.db_manager.get_all_users()
            
            for user in users:
                status = "Active" if user['is_active'] else "Inactive"
                created_date = user['created_at'][:10] if user['created_at'] else "N/A"
                
                self.tree.insert("", "end", values=(
                    user['user_id'],
                    user['username'],
                    user['full_name'],
                    user['position'],
                    user['access_level'],
                    status,
                    created_date
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {e}")
    
    def on_search(self, event=None):
        """Filter users based on search text"""
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            # Search in username, full name, position, and access level
            if (search_text in str(values[1]).lower() or 
                search_text in str(values[2]).lower() or 
                search_text in str(values[3]).lower() or 
                search_text in str(values[4]).lower()):
                self.tree.item(item, tags=('match',))
                self.tree.set(item, column='#0', value='')
            else:
                self.tree.item(item, tags=('no_match',))
                self.tree.set(item, column='#0', value='')
        
        # Hide non-matching items
        self.tree.tag_configure('no_match', foreground='gray')
    
    def add_user(self):
        """Open add user dialog"""
        dialog = UserDialog(self.parent, self.db_manager, None)
        self.parent.wait_window(dialog.dialog)
        self.load_users()
    
    def edit_user(self):
        """Edit selected user"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        dialog = UserDialog(self.parent, self.db_manager, user_id)
        self.parent.wait_window(dialog.dialog)
        self.load_users()
    
    def reset_password(self):
        """Reset password for selected user"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        username = self.tree.item(selected[0])['values'][1]
        
        new_password = simpledialog.askstring("Reset Password", 
                                            f"Enter new password for {username}:",
                                            show='*')
        if new_password:
            if len(new_password) < 6:
                messagebox.showwarning("Warning", "Password must be at least 6 characters long")
                return
            
            success = self.db_manager.reset_password(user_id, new_password)
            if success:
                messagebox.showinfo("Success", "Password reset successfully")
            else:
                messagebox.showerror("Error", "Failed to reset password")
    
    def toggle_user_status(self):
        """Activate or deactivate selected user"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        username = self.tree.item(selected[0])['values'][1]
        current_status = self.tree.item(selected[0])['values'][5]
        
        if current_status == "Active":
            if messagebox.askyesno("Confirm Deactivation", 
                                 f"Are you sure you want to deactivate user {username}?"):
                success, message = self.db_manager.deactivate_user(user_id)
                if success:
                    messagebox.showinfo("Success", message)
                    self.load_users()
                else:
                    messagebox.showerror("Error", message)
        else:
            if messagebox.askyesno("Confirm Activation", 
                                 f"Are you sure you want to activate user {username}?"):
                success, message = self.db_manager.activate_user(user_id)
                if success:
                    messagebox.showinfo("Success", message)
                    self.load_users()
                else:
                    messagebox.showerror("Error", message)
    
    def delete_user(self):
        """Delete selected user"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        username = self.tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to permanently delete user {username}?\n\nThis action cannot be undone."):
            success, message = self.db_manager.delete_user(user_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_users()
            else:
                messagebox.showerror("Error", message)
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
    
    def hide(self):
        self.frame.pack_forget()


class UserDialog:
    def __init__(self, parent, db_manager, user_id=None):
        self.parent = parent
        self.db_manager = db_manager
        self.user_id = user_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add User" if not user_id else "Edit User")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        if user_id:
            self.load_user_data()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Username
        ttk.Label(main_frame, text="Username:*").grid(row=0, column=0, padx=5, pady=8, sticky='w')
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=8, sticky='w')
        
        # Password (only for new users)
        if not self.user_id:
            ttk.Label(main_frame, text="Password:*").grid(row=1, column=0, padx=5, pady=8, sticky='w')
            self.password_var = tk.StringVar()
            self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=25)
            self.password_entry.grid(row=1, column=1, padx=5, pady=8, sticky='w')
        
        # Full Name
        ttk.Label(main_frame, text="Full Name:*").grid(row=2, column=0, padx=5, pady=8, sticky='w')
        self.fullname_var = tk.StringVar()
        self.fullname_entry = ttk.Entry(main_frame, textvariable=self.fullname_var, width=25)
        self.fullname_entry.grid(row=2, column=1, padx=5, pady=8, sticky='w')
        
        # Position
        ttk.Label(main_frame, text="Position:*").grid(row=3, column=0, padx=5, pady=8, sticky='w')
        self.position_var = tk.StringVar()
        self.position_entry = ttk.Entry(main_frame, textvariable=self.position_var, width=25)
        self.position_entry.grid(row=3, column=1, padx=5, pady=8, sticky='w')
        
        # Access Level - INCLUDES KAGAWAD
        ttk.Label(main_frame, text="Access Level:*").grid(row=4, column=0, padx=5, pady=8, sticky='w')
        self.access_var = tk.StringVar(value="kagawad")
        access_combo = ttk.Combobox(main_frame, textvariable=self.access_var,
                                   values=["admin", "treasurer", "kagawad", "viewer"], 
                                   state="readonly", width=22)
        access_combo.grid(row=4, column=1, padx=5, pady=8, sticky='w')
        
        # Active status (for editing existing users)
        if self.user_id:
            self.active_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(main_frame, text="Active User", 
                           variable=self.active_var).grid(row=5, column=1, padx=5, pady=8, sticky='w')
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", 
                  command=self.save_user, width=12).pack(side='left', padx=10)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.dialog.destroy, width=12).pack(side='left', padx=10)
    
    def load_user_data(self):
        """Load existing user data for editing"""
        try:
            user = self.db_manager.get_user_by_id(self.user_id)
            if user:
                self.username_var.set(user['username'])
                self.fullname_var.set(user['full_name'])
                self.position_var.set(user['position'])
                self.access_var.set(user['access_level'])
                if hasattr(self, 'active_var'):
                    self.active_var.set(bool(user['is_active']))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {e}")
    
    def save_user(self):
        """Save user data"""
        try:
            # Validate required fields
            if not all([self.username_var.get().strip(), 
                       self.fullname_var.get().strip(), 
                       self.position_var.get().strip()]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
            
            if not self.user_id and not self.password_var.get():
                messagebox.showwarning("Warning", "Please enter a password for the new user")
                return
            
            # Validate access level
            allowed_access_levels = ["admin", "treasurer", "kagawad", "viewer"]
            if self.access_var.get() not in allowed_access_levels:
                messagebox.showerror("Error", f"Invalid access level. Must be one of: {', '.join(allowed_access_levels)}")
                return
            
            if self.user_id:
                # Update existing user
                success = self.db_manager.update_user(
                    self.user_id,
                    self.username_var.get(),
                    self.fullname_var.get(),
                    self.position_var.get(),
                    self.access_var.get(),
                    self.active_var.get() if hasattr(self, 'active_var') else True
                )
                if success:
                    messagebox.showinfo("Success", "User updated successfully")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update user. Please check if the username already exists.")
            else:
                # Add new user
                success = self.db_manager.add_user(
                    self.username_var.get(),
                    self.password_var.get(),
                    self.fullname_var.get(),
                    self.position_var.get(),
                    self.access_var.get()
                )
                if success:
                    messagebox.showinfo("Success", "User added successfully")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "Username already exists or failed to add user")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {str(e)}")