# widgets/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    def __init__(self, parent, auth_system, on_login_success):
        self.parent = parent
        self.auth_system = auth_system
        self.on_login_success = on_login_success
        
        self.frame = ttk.Frame(parent, padding="20")
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.frame, text="BARANGAY BUDGET MANAGEMENT SYSTEM", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Login frame
        login_frame = ttk.LabelFrame(self.frame, text="Login", padding="20")
        login_frame.pack(pady=20, padx=100, fill='x')
        
        # Username
        ttk.Label(login_frame, text="Username:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=8)
        self.username_entry = ttk.Entry(login_frame, width=30, font=('Arial', 10))
        self.username_entry.grid(row=0, column=1, pady=8, padx=10, sticky='ew')
        
        # Password
        ttk.Label(login_frame, text="Password:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=8)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*", font=('Arial', 10))
        self.password_entry.grid(row=1, column=1, pady=8, padx=10, sticky='ew')
        
        # Login button
        login_btn = ttk.Button(login_frame, text="Login", 
                              command=self.handle_login, width=15)
        login_btn.grid(row=2, column=0, columnspan=2, pady=15)
        
        # Configure grid weights
        login_frame.columnconfigure(1, weight=1)
        
        # Default credentials hint
        hint_label = ttk.Label(self.frame, text="Default: admin / admin123", 
                              font=('Arial', 9), foreground='gray')
        hint_label.pack(pady=10)
        
        # Bind Enter key to login
        self.parent.bind('<Return>', lambda e: self.handle_login())
        
        self.username_entry.focus()
    
    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if self.auth_system.login(username, password):
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
    
    def hide(self):
        self.frame.pack_forget()