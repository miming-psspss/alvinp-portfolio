# widgets/cash_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class CashWindow:
    def __init__(self, parent, auth_system, cash_manager, on_back):
        self.parent = parent
        self.auth_system = auth_system
        self.cash_manager = cash_manager
        self.on_back = on_back
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(header_frame, text="← Back to Dashboard", 
                  command=self.on_back).pack(side='left')
        
        ttk.Label(header_frame, text="Cash Management", 
                 font=('Arial', 16, 'bold')).pack(side='left', padx=20)
        
        # Refresh button
        ttk.Button(header_frame, text="Refresh", 
                  command=self.update_display).pack(side='right')
        
        # Main content
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Current Balance Card
        balance_frame = ttk.LabelFrame(main_frame, text="Current Cash on Hand", padding="20")
        balance_frame.pack(fill='x', pady=10)
        
        self.balance_label = ttk.Label(balance_frame, text="Loading...", 
                                      font=('Arial', 24, 'bold'))
        self.balance_label.pack(pady=10)
        
        # Financial Summary Frame
        summary_frame = ttk.LabelFrame(main_frame, text="Financial Summary", padding="15")
        summary_frame.pack(fill='x', pady=10)
        
        # Summary labels
        self.summary_labels = {}
        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill='x')
        
        summaries = [
            ("Monthly Income:", "monthly_income"),
            ("Monthly Expenses:", "monthly_expenses"), 
            ("Cash Adjustments:", "cash_adjustments"),
            ("Net Cash Flow:", "net_cash_flow")
        ]
        
        for i, (label, key) in enumerate(summaries):
            ttk.Label(summary_grid, text=label, font=('Arial', 9)).grid(
                row=i//2, column=(i%2)*2, padx=10, pady=5, sticky='w')
            self.summary_labels[key] = ttk.Label(summary_grid, text="Loading...", 
                                               font=('Arial', 9, 'bold'))
            self.summary_labels[key].grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5, sticky='w')
        
        # Quick Actions Frame (Admin only)
        if self.auth_system.current_user['access_level'] in ['admin', 'treasurer']:
            actions_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding="15")
            actions_frame.pack(fill='x', pady=10)
            
            # Adjustment buttons
            adj_frame = ttk.Frame(actions_frame)
            adj_frame.pack(fill='x', pady=5)
            
            ttk.Button(adj_frame, text="➕ Add Cash Adjustment", 
                      command=self.show_add_cash_dialog, width=18).pack(side='left', padx=5)
            
            ttk.Button(adj_frame, text="➖ Remove Cash Adjustment", 
                      command=self.show_remove_cash_dialog, width=20).pack(side='left', padx=5)
            
            ttk.Button(adj_frame, text="🔄 Recalculate Balance", 
                      command=self.recalculate_balance, width=18).pack(side='left', padx=5)
        
        # Balance History Frame
        history_frame = ttk.LabelFrame(main_frame, text="Balance History (Last 30 Days)", padding="10")
        history_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview for history
        columns = ('date', 'balance', 'change')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.history_tree.heading('date', text='Date & Time')
        self.history_tree.heading('balance', text='Balance')
        self.history_tree.heading('change', text='Change')
        
        # Configure columns
        self.history_tree.column('date', width=200)
        self.history_tree.column('balance', width=150)
        self.history_tree.column('change', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def update_display(self):
        """Update the cash balance display and history"""
        try:
            # Update current balance
            current_balance = self.cash_manager.get_current_balance()
            self.balance_label.config(text=f"₱{current_balance:,.2f}")
            
            # Color code based on balance
            if current_balance > 0:
                self.balance_label.config(foreground='green')
            elif current_balance < 0:
                self.balance_label.config(foreground='red')
            else:
                self.balance_label.config(foreground='black')
            
            # Update financial summary
            self.update_financial_summary()
            
            # Update history
            self.update_history()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update cash display: {str(e)}")
    
    def update_financial_summary(self):
        """Update the financial summary labels"""
        try:
            summary = self.cash_manager.get_financial_summary()
            
            self.summary_labels['monthly_income'].config(text=f"₱{summary['monthly_income']:,.2f}")
            self.summary_labels['monthly_expenses'].config(text=f"₱{summary['monthly_expenses']:,.2f}")
            self.summary_labels['cash_adjustments'].config(text=f"₱{summary['cash_adjustments']:,.2f}")
            self.summary_labels['net_cash_flow'].config(text=f"₱{summary['net_cash_flow']:,.2f}")
            
            # Color code net cash flow
            if summary['net_cash_flow'] > 0:
                self.summary_labels['net_cash_flow'].config(foreground='green')
            elif summary['net_cash_flow'] < 0:
                self.summary_labels['net_cash_flow'].config(foreground='red')
            else:
                self.summary_labels['net_cash_flow'].config(foreground='black')
                
        except Exception as e:
            print(f"Error updating financial summary: {e}")
    
    def update_history(self):
        """Update the balance history treeview"""
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            history = self.cash_manager.get_balance_history(30)
            
            if not history:
                self.history_tree.insert('', 'end', values=(
                    'No history available', '', ''
                ))
                return
            
            # Populate treeview
            previous_balance = None
            for record in history:
                balance = record['current_balance']
                date_str = record['last_updated']
                
                # Calculate change
                if previous_balance is not None:
                    change = balance - previous_balance
                    change_str = f"₱{change:+,.2f}"
                else:
                    change_str = "-"
                
                previous_balance = balance
                
                # Format date
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%b %d, %Y %I:%M %p')
                except:
                    formatted_date = date_str
                
                self.history_tree.insert('', 'end', values=(
                    formatted_date,
                    f"₱{balance:,.2f}",
                    change_str
                ))
                
        except Exception as e:
            print(f"Error updating history: {e}")
    
    def show_add_cash_dialog(self):
        """Show dialog to add cash adjustment"""
        self.show_adjustment_dialog("income")
    
    def show_remove_cash_dialog(self):
        """Show dialog to remove cash adjustment"""
        self.show_adjustment_dialog("expense")
    
    def show_adjustment_dialog(self, adjustment_type):
        """Show cash adjustment dialog"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(f"{'Add' if adjustment_type == 'income' else 'Remove'} Cash Adjustment")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Create form frame
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(expand=True, fill='both')
        
        # Amount
        ttk.Label(form_frame, text="Amount:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=10)
        amount_entry = ttk.Entry(form_frame, font=('Arial', 12))
        amount_entry.grid(row=0, column=1, sticky='ew', pady=10, padx=10)
        
        # Reason
        ttk.Label(form_frame, text="Reason/Description:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=10)
        reason_entry = ttk.Entry(form_frame, font=('Arial', 12))
        reason_entry.grid(row=1, column=1, sticky='ew', pady=10, padx=10)
        
        # Info text
        info_text = f"""
This cash adjustment will {'increase' if adjustment_type == 'income' else 'decrease'} 
the cash balance but will NOT affect monthly income/expense reports.
        """
        info_label = ttk.Label(form_frame, text=info_text, font=('Arial', 9),
                              foreground='blue', justify='left')
        info_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=10)
        
        # Current balance
        current_balance = self.cash_manager.get_current_balance()
        ttk.Label(form_frame, text=f"Current Balance: ₱{current_balance:,.2f}",
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def submit_adjustment():
            try:
                amount = float(amount_entry.get())
                reason = reason_entry.get().strip()
                
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be positive", parent=dialog)
                    return
                
                if not reason:
                    messagebox.showerror("Error", "Please enter a reason/description", parent=dialog)
                    return
                
                # Get current user ID
                user_id = self.auth_system.current_user['user_id']
                
                # Add cash adjustment
                if adjustment_type == 'income':
                    transaction_number = self.cash_manager.add_income_adjustment(amount, reason, user_id)
                else:
                    transaction_number = self.cash_manager.add_expense_adjustment(amount, reason, user_id)
                
                # Get new balance
                new_balance = self.cash_manager.get_current_balance()
                
                messagebox.showinfo("Success", 
                                  f"Cash adjustment recorded successfully!\n"
                                  f"Transaction: {transaction_number}\n"
                                  f"New balance: ₱{new_balance:,.2f}", 
                                  parent=dialog)
                dialog.destroy()
                self.update_display()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to record cash adjustment: {str(e)}", parent=dialog)
        
        ttk.Button(button_frame, text="Submit Adjustment", 
                  command=submit_adjustment).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=dialog.destroy).pack(side='left', padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        amount_entry.focus()
    
    def recalculate_balance(self):
        """Recalculate balance from all transactions"""
        try:
            # This method now recalculates from both regular transactions AND cash adjustments
            with self.cash_manager.db_manager.get_connection() as conn:
                # Calculate total cash income (regular + adjustments)
                total_income = conn.execute('''
                    SELECT COALESCE(SUM(amount), 0) FROM transactions 
                    WHERE status = 'approved' 
                    AND category_id IN (SELECT category_id FROM categories WHERE category_type = 'income')
                ''').fetchone()[0]
                
                # Calculate total cash expenses (regular + adjustments)
                total_expenses = conn.execute('''
                    SELECT COALESCE(SUM(amount), 0) FROM transactions 
                    WHERE status = 'approved' 
                    AND category_id IN (SELECT category_id FROM categories WHERE category_type = 'expense')
                ''').fetchone()[0]
                
                # Calculate net cash
                net_cash = total_income - total_expenses
                
                # Update balance
                conn.execute(
                    "INSERT INTO cash_balance (current_balance) VALUES (?)",
                    (net_cash,)
                )
                
            messagebox.showinfo("Success", 
                              f"Balance recalculated from all transactions!\n"
                              f"Total Cash Income: ₱{total_income:,.2f}\n"
                              f"Total Cash Expenses: ₱{total_expenses:,.2f}\n"
                              f"Calculated Balance: ₱{net_cash:,.2f}")
            self.update_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to recalculate balance: {str(e)}")
    
    def show(self):
        self.frame.pack(expand=True, fill='both')
        self.update_display()
    
    def hide(self):
        self.frame.pack_forget()