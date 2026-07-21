# widgets/admin_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AdminWindow:
    def __init__(self, parent, auth_system, db_manager, transaction_manager, on_back):
        self.parent = parent
        self.auth_system = auth_system
        self.db_manager = db_manager
        self.transaction_manager = transaction_manager
        self.on_back = on_back
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_pending_transactions()
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(header_frame, text="← Back to Dashboard", 
                  command=self.on_back).pack(side='left')
        
        ttk.Label(header_frame, text="Admin Panel - Approve Transactions", 
                 font=('Arial', 16, 'bold')).pack(side='left', padx=20)
        
        # Refresh button
        ttk.Button(header_frame, text="Refresh", 
                  command=self.load_pending_transactions).pack(side='right')
        
        # Main content
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Pending transactions frame
        pending_frame = ttk.LabelFrame(main_frame, text="Pending Transactions Approval", padding="10")
        pending_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview for pending transactions
        columns = ('id', 'date', 'number', 'type', 'category', 'amount', 'prepared_by', 'description')
        self.pending_tree = ttk.Treeview(pending_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.pending_tree.heading('id', text='ID')
        self.pending_tree.heading('date', text='Date')
        self.pending_tree.heading('number', text='Trans No')
        self.pending_tree.heading('type', text='Type')
        self.pending_tree.heading('category', text='Category')
        self.pending_tree.heading('amount', text='Amount')
        self.pending_tree.heading('prepared_by', text='Prepared By')
        self.pending_tree.heading('description', text='Description')
        
        # Configure columns
        self.pending_tree.column('id', width=50)
        self.pending_tree.column('date', width=100)
        self.pending_tree.column('number', width=120)
        self.pending_tree.column('type', width=80)
        self.pending_tree.column('category', width=120)
        self.pending_tree.column('amount', width=100)
        self.pending_tree.column('prepared_by', width=120)
        self.pending_tree.column('description', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(pending_frame, orient=tk.VERTICAL, command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pending_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click to show details
        self.pending_tree.bind('<Double-1>', self.show_transaction_details)
        
        # Action buttons frame
        action_frame = ttk.Frame(pending_frame)
        action_frame.pack(fill='x', pady=10)
        
        ttk.Button(action_frame, text="Approve Selected", 
                  command=self.approve_selected).pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="Reject Selected", 
                  command=self.reject_selected).pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="View Details", 
                  command=self.show_transaction_details).pack(side='left', padx=5)
    
    def load_pending_transactions(self):
        """Load pending transactions into the treeview"""
        # Clear existing data
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        
        try:
            # Get pending transactions
            transactions = self.transaction_manager.get_transactions(status='pending')
            
            if not transactions:
                self.pending_tree.insert('', 'end', values=(
                    '', '', 'No pending transactions', '', '', '', '', ''
                ))
                return
            
            # Populate treeview
            for trans in transactions:
                trans_type = "INC" if trans['category_type'] == 'income' else "EXP"
                
                self.pending_tree.insert('', 'end', values=(
                    trans['transaction_id'],
                    trans['transaction_date'],
                    trans['transaction_number'],
                    trans_type,
                    trans['category_name'],
                    f"₱{trans['amount']:,.2f}",
                    trans['prepared_by_name'],
                    trans['description']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pending transactions: {str(e)}")
    
    def get_selected_transaction_id(self):
        """Get the selected transaction ID from treeview"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a transaction first")
            return None
        
        item = self.pending_tree.item(selection[0])
        values = item['values']
        
        if not values or not values[0]:  # Check if it's the "no transactions" row
            return None
        
        return values[0]  # transaction_id is in the first column
    
    def approve_selected(self):
        """Approve the selected transaction"""
        trans_id = self.get_selected_transaction_id()
        if not trans_id:
            return
        
        try:
            self.transaction_manager.approve_transaction(trans_id)
            messagebox.showinfo("Success", "Transaction approved successfully!")
            self.load_pending_transactions()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve transaction: {str(e)}")
    
    def reject_selected(self):
        """Reject the selected transaction"""
        trans_id = self.get_selected_transaction_id()
        if not trans_id:
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute(
                    "UPDATE transactions SET status = 'rejected', approved_by = ? WHERE transaction_id = ?",
                    (self.auth_system.current_user['user_id'], trans_id)
                )
            
            messagebox.showinfo("Success", "Transaction rejected successfully!")
            self.load_pending_transactions()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject transaction: {str(e)}")
    
    def show_transaction_details(self, event=None):
        """Show detailed view of selected transaction"""
        trans_id = self.get_selected_transaction_id()
        if not trans_id:
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                transaction = conn.execute('''
                    SELECT t.*, c.category_name, c.category_type, u.full_name as prepared_by_name,
                           u2.full_name as approved_by_name
                    FROM transactions t
                    JOIN categories c ON t.category_id = c.category_id
                    JOIN users u ON t.prepared_by = u.user_id
                    LEFT JOIN users u2 ON t.approved_by = u2.user_id
                    WHERE t.transaction_id = ?
                ''', (trans_id,)).fetchone()
            
            if transaction:
                self.show_detail_dialog(transaction)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transaction details: {str(e)}")
    
    def show_detail_dialog(self, transaction):
        """Show transaction details in a dialog"""
        detail_window = tk.Toplevel(self.parent)
        detail_window.title("Transaction Details")
        detail_window.geometry("500x400")
        detail_window.transient(self.parent)
        detail_window.grab_set()
        
        # Center the window
        detail_window.update_idletasks()
        x = (detail_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (detail_window.winfo_screenheight() // 2) - (400 // 2)
        detail_window.geometry(f"500x400+{x}+{y}")
        
        # Create details frame
        details_frame = ttk.Frame(detail_window, padding="20")
        details_frame.pack(expand=True, fill='both')
        
        # Transaction details
        details = [
            ("Transaction Number:", transaction['transaction_number']),
            ("Date:", transaction['transaction_date']),
            ("Type:", "Income" if transaction['category_type'] == 'income' else "Expense"),
            ("Category:", transaction['category_name']),
            ("Amount:", f"₱{transaction['amount']:,.2f}"),
            ("Description:", transaction['description']),
            ("Payee/Payer:", transaction['payee_payer'] or "N/A"),
            ("Payment Method:", transaction['payment_method'].capitalize()),
            ("Status:", transaction['status'].capitalize()),
            ("Prepared By:", transaction['prepared_by_name']),
            ("Approved By:", transaction['approved_by_name'] or "Pending"),
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(details_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', pady=5, padx=5)
            ttk.Label(details_frame, text=value, font=('Arial', 10)).grid(
                row=i, column=1, sticky='w', pady=5, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.grid(row=len(details), column=0, columnspan=2, pady=20)
        
        if transaction['status'] == 'pending':
            ttk.Button(button_frame, text="Approve", 
                      command=lambda: self.approve_from_detail(transaction['transaction_id'], detail_window)).pack(side='left', padx=5)
            
            ttk.Button(button_frame, text="Reject", 
                      command=lambda: self.reject_from_detail(transaction['transaction_id'], detail_window)).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=detail_window.destroy).pack(side='left', padx=5)
    
    def approve_from_detail(self, trans_id, window):
        """Approve transaction from detail window"""
        try:
            self.transaction_manager.approve_transaction(trans_id)
            messagebox.showinfo("Success", "Transaction approved successfully!", parent=window)
            window.destroy()
            self.load_pending_transactions()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve transaction: {str(e)}", parent=window)
    
    def reject_from_detail(self, trans_id, window):
        """Reject transaction from detail window"""
        try:
            with self.db_manager.get_connection() as conn:
                conn.execute(
                    "UPDATE transactions SET status = 'rejected', approved_by = ? WHERE transaction_id = ?",
                    (self.auth_system.current_user['user_id'], trans_id)
                )
            
            messagebox.showinfo("Success", "Transaction rejected successfully!", parent=window)
            window.destroy()
            self.load_pending_transactions()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject transaction: {str(e)}", parent=window)
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
        self.load_pending_transactions()
    
    def hide(self):
        self.frame.pack_forget()