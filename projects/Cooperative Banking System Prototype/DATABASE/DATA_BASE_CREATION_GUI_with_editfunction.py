from cmath import e
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class FinancialRecordsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Records Database")
        self.root.geometry("1400x900")
        
        # Database connection
        self.conn = self.create_connection("financial_records.db")
        self.create_tables()
        self.migrate_account_numbers()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_data_entry_tab()
        self.create_view_records_tab()
        self.create_search_tab()
        
        # Load initial data
        self.load_accounts()
    
    def create_connection(self, db_file):
        """ Create a database connection """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return conn
    
    def create_tables(self):
        """ Create tables if they don't exist with proper TEXT types """
        if self.conn is not None:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        account_number TEXT PRIMARY KEY COLLATE NOCASE,
                        last_name TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        middle_name TEXT,
                        name_suffix TEXT,
                        address TEXT NOT NULL,
                        contact_number TEXT NOT NULL,
                        id_type TEXT NOT NULL,
                        id_number TEXT NOT NULL,
                        account_status TEXT NOT NULL,
                        lq_total_savings REAL DEFAULT 0,
                        savings_quarterly_interest REAL DEFAULT 0,       
                        total_savings REAL DEFAULT 0,
                        cbu_paid REAL DEFAULT 0,
                        dividend REAL DEFAULT 0,
                        patronage_refund REAL DEFAULT 0,
                        total_cbu REAL DEFAULT 0,
                        loan_amount REAL DEFAULT 0,
                        loan_type TEXT,
                        loan_term_months INTEGER,
                        net_proceed REAL,
                        date_released TEXT,
                        date_first_installment TEXT,
                        maturity_date TEXT,
                        service_fee REAL DEFAULT 0,
                        cbu_retention REAL DEFAULT 0,
                        total_interest REAL DEFAULT 0,
                        penalty REAL DEFAULT 0,
                        past_due_interest REAL DEFAULT 0,
                        account_officer TEXT
                    );
                """)
                self.conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Error creating tables: {e}")
    
    def migrate_account_numbers(self):
        """Convert existing numeric account numbers to properly formatted text"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT account_number, typeof(account_number) FROM accounts LIMIT 1")
            result = cursor.fetchone()
            
            if result and result[1] == 'integer':
                if not messagebox.askyesno("Migration Needed", 
                                         "Account numbers need migration to text format. Continue?"):
                    return
                
                cursor.execute("CREATE TABLE accounts_temp AS SELECT * FROM accounts WHERE 1=0")
                cursor.execute("""
                    INSERT INTO accounts_temp 
                    SELECT 
                        printf('%04d', account_number),
                        last_name, first_name, middle_name, name_suffix,
                        address, contact_number, id_type, id_number, account_status,
                        lq_total_savings, savings_quarterly_interest, total_savings, cbu_paid, 
                        dividend, patronage_refund, total_cbu,
                        loan_amount, loan_type, loan_term_months, net_proceed,
                        date_released, date_first_installment, maturity_date,
                        service_fee, cbu_retention, total_interest, penalty,
                        past_due_interest, account_officer
                    FROM accounts
                """)
                cursor.execute("DROP TABLE accounts")
                cursor.execute("ALTER TABLE accounts_temp RENAME TO accounts")
                self.conn.commit()
                messagebox.showinfo("Success", "Account numbers migrated to text format")
                
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Migration Error", str(e))
    
    def format_account_number(self, account_num):
        """Ensure consistent account number formatting"""
        if account_num is None:
            return ""
        if isinstance(account_num, int):
            return f"{account_num:04d}"
        if account_num.replace("-", "").isdigit():
            if "-" in account_num:
                return account_num
            return account_num.zfill(4)
        return str(account_num)
    
    def create_data_entry_tab(self):
        """ Create the data entry tab """
        self.entry_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.entry_tab, text="Data Entry")
        
        # Create scrollable frame
        canvas = tk.Canvas(self.entry_tab)
        scrollbar = ttk.Scrollbar(self.entry_tab, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Personal Information Section
        personal_frame = ttk.LabelFrame(self.scrollable_frame, text="Personal Information", padding=10)
        personal_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Label(personal_frame, text="Account Number:").grid(row=0, column=0, sticky="e")
        self.account_number = ttk.Entry(personal_frame)
        self.account_number.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(personal_frame, text="Last Name:").grid(row=1, column=0, sticky="e")
        self.last_name = ttk.Entry(personal_frame)
        self.last_name.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(personal_frame, text="First Name:").grid(row=2, column=0, sticky="e")
        self.first_name = ttk.Entry(personal_frame)
        self.first_name.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(personal_frame, text="Middle Name:").grid(row=3, column=0, sticky="e")
        self.middle_name = ttk.Entry(personal_frame)
        self.middle_name.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(personal_frame, text="Suffix:").grid(row=4, column=0, sticky="e")
        self.name_suffix = ttk.Entry(personal_frame)
        self.name_suffix.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(personal_frame, text="Address:").grid(row=5, column=0, sticky="e")
        self.address = ttk.Entry(personal_frame, width=40)
        self.address.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(personal_frame, text="Contact Number:").grid(row=6, column=0, sticky="e")
        self.contact_number = ttk.Entry(personal_frame)
        self.contact_number.grid(row=6, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(personal_frame, text="ID Type:").grid(row=7, column=0, sticky="e")
        self.id_type = ttk.Combobox(personal_frame, values=["National ID", "UMID ID", "Passport", "Driver's License", "SSS ID", "GSIS ID", "TIN ID", "Voter's ID", "Other"])
        self.id_type.grid(row=7, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(personal_frame, text="ID Number:").grid(row=8, column=0, sticky="e")
        self.id_number = ttk.Entry(personal_frame)
        self.id_number.grid(row=8, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(personal_frame, text="Account Status:").grid(row=9, column=0, sticky="e")
        self.account_status = ttk.Combobox(personal_frame, values=["ACTIVE", "DORMANT", "CLOSED", "PAST DUE"])
        self.account_status.grid(row=9, column=1, padx=5, pady=2, sticky="w")

        # Savings Information Section
        savings_frame = ttk.LabelFrame(self.scrollable_frame, text="Savings Information", padding=10)
        savings_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(savings_frame, text="LQ Total Savings:").grid(row=0, column=0, sticky="e")
        self.lq_total_savings = ttk.Entry(savings_frame)
        self.lq_total_savings.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.lq_total_savings.insert(0, "0.00")

        ttk.Label(savings_frame, text="Savings Quarterly Interest:").grid(row=1, column=0, sticky="e")
        self.savings_quarterly_interest = ttk.Entry(savings_frame)
        self.savings_quarterly_interest.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        self.savings_quarterly_interest.insert(0, "0.00")

        ttk.Label(savings_frame, text="Total Savings:").grid(row=2, column=0, sticky="e")
        self.total_savings = ttk.Entry(savings_frame)
        self.total_savings.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.total_savings.insert(0, "0.00")

        ttk.Label(savings_frame, text="CBU Paid:").grid(row=3, column=0, sticky="e")
        self.cbu_paid = ttk.Entry(savings_frame)
        self.cbu_paid.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self.cbu_paid.insert(0, "0.00")

        ttk.Label(savings_frame, text="Dividend:").grid(row=4, column=0, sticky="e")
        self.dividend = ttk.Entry(savings_frame)
        self.dividend.grid(row=4, column=1, padx=5, pady=2, sticky="w")
        self.dividend.insert(0, "0.00")

        ttk.Label(savings_frame, text="Patronage Refund:").grid(row=5, column=0, sticky="e")
        self.patronage_refund = ttk.Entry(savings_frame)
        self.patronage_refund.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        self.patronage_refund.insert(0, "0.00")

        ttk.Label(savings_frame, text="Total CBU:").grid(row=6, column=0, sticky="e")
        self.total_cbu = ttk.Entry(savings_frame)
        self.total_cbu.grid(row=6, column=1, padx=5, pady=2, sticky="w")
        self.total_cbu.insert(0, "0.00")
                
        # Loan Information Section
        loan_frame = ttk.LabelFrame(self.scrollable_frame, text="Loan Information", padding=10)
        loan_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Label(loan_frame, text="Loan Amount:").grid(row=0, column=0, sticky="e")
        self.loan_amount = ttk.Entry(loan_frame)
        self.loan_amount.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.loan_amount.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="Type of Loan:").grid(row=1, column=0, sticky="e")
        self.loan_type = ttk.Combobox(loan_frame, values=["Salary Loan", "Small Business Loan", "Emergency Loan", "Honorarium Loan", "Other"])
        self.loan_type.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(loan_frame, text="Loan Term (months):").grid(row=2, column=0, sticky="e")
        self.loan_term = ttk.Entry(loan_frame)
        self.loan_term.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.loan_term.insert(0, "0")
        
        ttk.Label(loan_frame, text="Net Proceed:").grid(row=3, column=0, sticky="e")
        self.net_proceed = ttk.Entry(loan_frame)
        self.net_proceed.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self.net_proceed.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="Date Released (YYYY-MM-DD):").grid(row=4, column=0, sticky="e")
        self.date_released = ttk.Entry(loan_frame)
        self.date_released.grid(row=4, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(loan_frame, text="Date 1st Installment:").grid(row=5, column=0, sticky="e")
        self.date_first_installment = ttk.Entry(loan_frame, state='readonly')
        self.date_first_installment.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(loan_frame, text="Maturity Date:").grid(row=6, column=0, sticky="e")
        self.maturity_date = ttk.Entry(loan_frame, state='readonly')
        self.maturity_date.grid(row=6, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(loan_frame, text="Service Fee:").grid(row=7, column=0, sticky="e")
        self.service_fee = ttk.Entry(loan_frame)
        self.service_fee.grid(row=7, column=1, padx=5, pady=2, sticky="w")
        self.service_fee.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="CBU Retention:").grid(row=8, column=0, sticky="e")
        self.cbu_retention = ttk.Entry(loan_frame)
        self.cbu_retention.grid(row=8, column=1, padx=5, pady=2, sticky="w")
        self.cbu_retention.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="Total Interest:").grid(row=9, column=0, sticky="e")
        self.total_interest = ttk.Entry(loan_frame)
        self.total_interest.grid(row=9, column=1, padx=5, pady=2, sticky="w")
        self.total_interest.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="Penalty:").grid(row=10, column=0, sticky="e")
        self.penalty = ttk.Entry(loan_frame)
        self.penalty.grid(row=10, column=1, padx=5, pady=2, sticky="w")
        self.penalty.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="Past Due Interest:").grid(row=11, column=0, sticky="e")
        self.past_due_interest = ttk.Entry(loan_frame)
        self.past_due_interest.grid(row=11, column=1, padx=5, pady=2, sticky="w")
        self.past_due_interest.insert(0, "0.00")
        
        ttk.Label(loan_frame, text="Account Officer:").grid(row=12, column=0, sticky="e")
        self.account_officer = ttk.Entry(loan_frame)
        self.account_officer.grid(row=12, column=1, padx=5, pady=2, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(button_frame, text="Save Record", command=self.save_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Calculate Dates", command=self.calculate_dates).pack(side="left", padx=5)
    
    def create_view_records_tab(self):
        """ Create the view records tab with all fields """
        self.view_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.view_tab, text="View Records")
        
        # Treeview for displaying records with all columns
        columns = (
            "account_number", "last_name", "first_name", "middle_name", "name_suffix", "address",
            "contact_number", "id_type", "id_number", "account_status", "lq_total_savings", "savings_quarterly_interest", "total_savings",
            "cbu_paid", "dividend", "patronage_refund", "total_cbu", "loan_amount", "loan_type", "loan_term_months",
            "net_proceed", "date_released", "date_first_installment", "maturity_date",
            "service_fee", "cbu_retention", "total_interest", "penalty", "past_due_interest",
            "account_officer"
        )
        
        self.tree = ttk.Treeview(self.view_tab, columns=columns, show='headings')
        
        # Define headings for all columns
        headings = {
            "account_number": "Account No.",
            "last_name": "Last Name",
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "name_suffix": "Suffix",
            "address": "Address",
            "contact_number": "Contact No.",
            "id_type": "ID Type",
            "id_number": "ID Number",
            "account_status": "Account Status",
            "lq_total_savings": "LQ Savings",
            "savings_quarterly_interest": "Quarterly Interest",
            "total_savings": "Total Savings",
            "cbu_paid": "CBU Paid",
            "dividend": "Dividend",
            "patronage_refund": "Patronage Refund",
            "total_cbu": "Total CBU",
            "loan_amount": "Loan Amount",
            "loan_type": "Loan Type",
            "loan_term_months": "Loan Term",
            "net_proceed": "Net Proceed",
            "date_released": "Date Released",
            "date_first_installment": "1st Installment",
            "maturity_date": "Maturity Date",
            "service_fee": "Service Fee",
            "cbu_retention": "CBU Retention",
            "total_interest": "Total Interest",
            "penalty": "Penalty",
            "past_due_interest": "Past Due Interest",
            "account_officer": "Account Officer"
        }
        
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100, stretch=False)
        
        # Adjust widths for specific columns
        self.tree.column("account_number", width=120)
        self.tree.column("last_name", width=120)
        self.tree.column("first_name", width=120)
        self.tree.column("address", width=200)
        self.tree.column("loan_type", width=120)
        self.tree.column("account_officer", width=120)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(self.view_tab, orient="horizontal", command=self.tree.xview)
        v_scrollbar = ttk.Scrollbar(self.view_tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Layout
        self.tree.pack(side="top", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        
        # Double-click to view full record
        self.tree.bind("<Double-1>", self.view_full_record)
        
        # Add delete button
        delete_button = ttk.Button(self.view_tab, text="Delete Selected", command=self.delete_selected_record)
        delete_button.pack(pady=5)
    
    def create_search_tab(self):
        """ Create the search tab with all fields """
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Search Records")
        
        # Search frame
        search_frame = ttk.Frame(self.search_tab, padding=10)
        search_frame.pack(fill="x")
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_records).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left")
        
        # Results treeview with all columns
        columns = (
            "account_number", "last_name", "first_name", "middle_name", "name_suffix", "address",
            "contact_number", "id_type", "id_number", "account_status", "lq_total_savings", "savings_quarterly_interest", "total_savings",
            "cbu_paid", "dividend", "patronage_refund", "total_cbu", "loan_amount", "loan_type", "loan_term_months",
            "net_proceed", "date_released", "date_first_installment", "maturity_date",
            "service_fee", "cbu_retention", "total_interest", "penalty", "past_due_interest",
            "account_officer"
        )
        
        self.search_tree = ttk.Treeview(self.search_tab, columns=columns, show="headings")
        
        # Define headings for all columns (same as view tab)
        headings = {
            "account_number": "Account No.",
            "last_name": "Last Name",
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "name_suffix": "Suffix",
            "address": "Address",
            "contact_number": "Contact No.",
            "id_type": "ID Type",
            "id_number": "ID Number",
            "account_status": "Account Status",
            "lq_total_savings": "LQ Savings",
            "savings_quarterly_interest": "Quarterly Interest",
            "total_savings": "Total Savings",
            "cbu_paid": "CBU Paid",
            "dividend": "Dividend",
            "patronage_refund": "Patronage Refund",
            "total_cbu": "Total CBU",
            "loan_amount": "Loan Amount",
            "loan_type": "Loan Type",
            "loan_term_months": "Loan Term",
            "net_proceed": "Net Proceed",
            "date_released": "Date Released",
            "date_first_installment": "1st Installment",
            "maturity_date": "Maturity Date",
            "service_fee": "Service Fee",
            "cbu_retention": "CBU Retention",
            "total_interest": "Total Interest",
            "penalty": "Penalty",
            "past_due_interest": "Past Due Interest",
            "account_officer": "Account Officer"
        }
        
        for col, text in headings.items():
            self.search_tree.heading(col, text=text)
            self.search_tree.column(col, width=100, stretch=False)
        
        # Adjust widths for specific columns
        self.search_tree.column("account_number", width=120)
        self.search_tree.column("last_name", width=120)
        self.search_tree.column("first_name", width=120)
        self.search_tree.column("address", width=200)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(self.search_tab, orient="horizontal", command=self.search_tree.xview)
        v_scrollbar = ttk.Scrollbar(self.search_tab, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Layout
        self.search_tree.pack(side="top", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        
        # Double-click to view full record
        self.search_tree.bind("<Double-1>", self.view_full_record_from_search)
        
        # Add delete button
        delete_button = ttk.Button(self.search_tab, text="Delete Selected", command=self.delete_selected_search_record)
        delete_button.pack(pady=5)
    
    def calculate_dates(self):
        """ Calculate dates based on release date and loan term """
        date_released = self.date_released.get()
        loan_term = self.loan_term.get()
        
        if not date_released or not loan_term.isdigit():
            messagebox.showwarning("Input Error", "Please enter a valid date and loan term")
            return
        
        try:
            release_date = datetime.strptime(date_released, "%Y-%m-%d")
            loan_months = int(loan_term)
            
            first_installment = release_date + timedelta(days=30)
            maturity_date = release_date + timedelta(days=30*loan_months)
            
            self.date_first_installment.config(state='normal')
            self.date_first_installment.delete(0, tk.END)
            self.date_first_installment.insert(0, first_installment.strftime("%Y-%m-%d"))
            
            self.maturity_date.delete(0, tk.END)
            self.maturity_date.insert(0, maturity_date.strftime("%Y-%m-%d"))
            
            self.date_first_installment.config(state='readonly')
            self.maturity_date.config(state='readonly')
            
        except ValueError:
            messagebox.showerror("Date Error", "Please enter date in YYYY-MM-DD format")

    def _convert_to_float(self, value):
        """Helper method to safely convert to float"""
        if value == "":
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0

    def _convert_to_int(self, value):
        """Helper method to safely convert to integer"""
        if value == "":
            return 0
        try:
            return int(value)
        except ValueError:
            return 0       

    def save_record(self):
        """ Save the record to the database """
        account_num = self.format_account_number(self.account_number.get().strip())
        
        if not account_num:
            messagebox.showerror("Input Error", "Account number is required")
            return
        
        # Validate required fields
        required_fields = {
            "Last Name": self.last_name.get(),
            "First Name": self.first_name.get(),
            "Address": self.address.get(),
            "Contact Number": self.contact_number.get(),
            "ID Type": self.id_type.get(),
            "ID Number": self.id_number.get(),
            "Account Status": self.account_status.get()
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            messagebox.showerror("Input Error", f"These fields are required:\n{', '.join(missing_fields)}")
            return
        
        try:
            cursor = self.conn.cursor()
            account_data = {
                "account_number": account_num,
                "last_name": self.last_name.get(),
                "first_name": self.first_name.get(),
                "middle_name": self.middle_name.get(),
                "name_suffix": self.name_suffix.get(),
                "address": self.address.get(),
                "contact_number": self.contact_number.get(),
                "id_type": self.id_type.get(),
                "id_number": self.id_number.get(),
                "account_status": self.account_status.get(),
                "loan_type": self.loan_type.get(),
                "account_officer": self.account_officer.get(),
                "date_released": self.date_released.get(),
                "date_first_installment": self.date_first_installment.get(),
                "maturity_date": self.maturity_date.get(),
                "lq_total_savings": self._convert_to_float(self.lq_total_savings.get()),
                "savings_quarterly_interest": self._convert_to_float(self.savings_quarterly_interest.get()),
                "total_savings": self._convert_to_float(self.total_savings.get()),
                "cbu_paid": self._convert_to_float(self.cbu_paid.get()),
                "dividend": self._convert_to_float(self.dividend.get()),
                "patronage_refund": self._convert_to_float(self.patronage_refund.get()),
                "total_cbu": self._convert_to_float(self.total_cbu.get()),
                "loan_amount": self._convert_to_float(self.loan_amount.get()),
                "loan_term_months": self._convert_to_int(self.loan_term.get()),
                "net_proceed": self._convert_to_float(self.net_proceed.get()),
                "service_fee": self._convert_to_float(self.service_fee.get()),
                "cbu_retention": self._convert_to_float(self.cbu_retention.get()),
                "total_interest": self._convert_to_float(self.total_interest.get()),
                "penalty": self._convert_to_float(self.penalty.get()),
                "past_due_interest": self._convert_to_float(self.past_due_interest.get())
            }
            
            # Check if account exists
            cursor.execute("SELECT 1 FROM accounts WHERE account_number=?", (account_data["account_number"],))
            
            if cursor.fetchone():
                if not messagebox.askyesno("Confirm Update", 
                                         f"Update account {account_data['account_number']}?"):
                    return
                
                update_sql = """
                UPDATE accounts SET 
                    last_name=?, first_name=?, middle_name=?, name_suffix=?, 
                    address=?, contact_number=?, id_type=?, id_number=?, account_status=?,
                    lq_total_savings=?, savings_quarterly_interest=?, total_savings=?, cbu_paid=?, dividend=?, patronage_refund=?, total_cbu=?,
                    loan_amount=?, loan_type=?, loan_term_months=?, net_proceed=?,
                    date_released=?, date_first_installment=?, maturity_date=?,
                    service_fee=?, cbu_retention=?, total_interest=?, 
                    penalty=?, past_due_interest=?, account_officer=?
                WHERE account_number=?
                """
                cursor.execute(update_sql, (
                    account_data["last_name"], account_data["first_name"], 
                    account_data["middle_name"], account_data["name_suffix"],
                    account_data["address"], account_data["contact_number"], 
                    account_data["id_type"], account_data["id_number"], 
                    account_data["account_status"],
                    account_data["lq_total_savings"], account_data["savings_quarterly_interest"], 
                    account_data["total_savings"], account_data["cbu_paid"], 
                    account_data["dividend"], account_data["patronage_refund"], 
                    account_data["total_cbu"],
                    account_data["loan_amount"], account_data["loan_type"], 
                    account_data["loan_term_months"], account_data["net_proceed"],
                    account_data["date_released"], account_data["date_first_installment"], 
                    account_data["maturity_date"],
                    account_data["service_fee"], account_data["cbu_retention"], 
                    account_data["total_interest"],
                    account_data["penalty"], account_data["past_due_interest"], 
                    account_data["account_officer"],
                    account_data["account_number"]
                ))
                message = "Account updated successfully"
            else:
                if not messagebox.askyesno("Confirm Creation", 
                                         f"Create new account {account_data['account_number']}?"):
                    return
                
                columns = ', '.join(account_data.keys())
                placeholders = ', '.join(['?'] * len(account_data))
                sql = f"INSERT INTO accounts ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(account_data.values()))
                message = "New account added successfully"
            
            self.conn.commit()
            self.load_accounts()
            self.clear_form()
            messagebox.showinfo("Success", message)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error saving record: {e}")
            self.conn.rollback()
        
        except ValueError as e:
            messagebox.showerror("Input Error", f"Please check your numeric inputs: {e}")

    def clear_form(self):
        """ Clear all entry fields """
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Entry) and widget['state'] != 'readonly':
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set('')
        
        # Reset numeric fields to 0
        self.lq_total_savings.insert(0, "0.00")
        self.savings_quarterly_interest.insert(0, "0.00")
        self.total_savings.insert(0, "0.00")
        self.cbu_paid.insert(0, "0.00")
        self.dividend.insert(0, "0.00")
        self.patronage_refund.insert(0, "0.00")
        self.total_cbu.insert(0, "0.00")
        self.loan_amount.insert(0, "0.00")
        self.loan_term.insert(0, "0")
        self.net_proceed.insert(0, "0.00")
        self.service_fee.insert(0, "0.00")
        self.cbu_retention.insert(0, "0.00")
        self.total_interest.insert(0, "0.00")
        self.penalty.insert(0, "0.00")
        self.past_due_interest.insert(0, "0.00")
    
    def load_accounts(self):
        """ Load accounts into the view records treeview """
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM accounts ORDER BY last_name, first_name")
            
            for row in cursor.fetchall():
                # Format numeric values
                formatted_row = list(row)
                for i in range(10, 25):  # Format numeric fields
                    if formatted_row[i] is None:
                        formatted_row[i] = "0.00"
                    else:
                        try:
                            formatted_row[i] = f"{float(formatted_row[i]):,.2f}"
                        except (ValueError, TypeError):
                            formatted_row[i] = "0.00"
                
                self.tree.insert("", "end", values=formatted_row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading accounts: {e}")

    def search_records(self):
        """ Search for records matching the search term """
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Search", "Please enter a search term")
            return
        
        try:
            # Clear existing data
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            cursor = self.conn.cursor()
            
            # Search using exact string matching for account numbers
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE account_number LIKE ? COLLATE NOCASE
                OR last_name LIKE ? COLLATE NOCASE
                OR first_name LIKE ? COLLATE NOCASE
                OR id_number LIKE ? COLLATE NOCASE
                ORDER BY account_number
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            results = cursor.fetchall()
            if not results:
                messagebox.showinfo("Search", "No matching records found")
                return
            
            for row in results:
                formatted_row = list(row)
                # Format numeric fields
                for i in range(10, 25):
                    if formatted_row[i] is None:
                        formatted_row[i] = "0.00"
                    else:
                        try:
                            formatted_row[i] = f"{float(formatted_row[i]):,.2f}"
                        except (ValueError, TypeError):
                            formatted_row[i] = "0.00"
                
                self.search_tree.insert("", "end", values=formatted_row)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error searching records: {e}")

    def clear_search(self):
        """ Clear the search results """
        self.search_entry.delete(0, tk.END)
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
    
    def view_full_record(self, event):
        """ View full record when double-clicked in view tab """
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        account_number = self.tree.item(selected_item)['values'][0]
        self.display_full_record(account_number)
    
    def view_full_record_from_search(self, event):
        """ View full record when double-clicked in search tab """
        selected_item = self.search_tree.focus()
        if not selected_item:
            return
        
        account_number = self.search_tree.item(selected_item)['values'][0]
        self.display_full_record(account_number)
    
    def display_full_record(self, account_number):
        """ Display full record in a new window with improved account number handling """
        try:
            cursor = self.conn.cursor()
            
            # Format the account number consistently before searching
            formatted_account = self.format_account_number(account_number)
            
            # First try exact match with formatted number
            cursor.execute("SELECT * FROM accounts WHERE account_number = ? COLLATE NOCASE", 
                        (formatted_account,))
            record = cursor.fetchone()
            
            if not record:
                # Fallback: try searching without hyphens if present
                if '-' in formatted_account:
                    clean_num = formatted_account.replace("-", "")
                    cursor.execute("SELECT * FROM accounts WHERE REPLACE(account_number, '-', '') = ?", 
                                (clean_num,))
                    record = cursor.fetchone()
                
                if not record:
                    messagebox.showerror("Error", f"Account {formatted_account} not found in database")
                    return
            
            # Create a new window
            record_window = tk.Toplevel(self.root)
            record_window.title(f"Account Details - {formatted_account}")
            record_window.geometry("800x600")
            
            # Create a text widget to display the record
            text_widget = tk.Text(record_window, wrap="word")
            scrollbar = ttk.Scrollbar(record_window, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side="right", fill="y")
            text_widget.pack(side="left", fill="both", expand=True)
            
            # Get column names
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Format the output with proper alignment
            output = ""
            for col, value in zip(columns, record):
                if col in ["lq_total_savings", "savings_quarterly_interest", "total_savings", 
                        "cbu_paid", "dividend", "patronage_refund", "total_cbu", "loan_amount", 
                        "net_proceed", "service_fee", "cbu_retention", "total_interest", 
                        "penalty", "past_due_interest"] and value is not None:
                    value = f"₱{float(value):,.2f}"
                output += f"{col:25}: {value}\n"
            
            text_widget.insert("1.0", output)
            text_widget.config(state="disabled")
            
            # Add buttons
            button_frame = ttk.Frame(record_window)
            button_frame.pack(pady=10)
            
            ttk.Button(
                button_frame, 
                text="Edit Record", 
                command=lambda: self.edit_record(formatted_account, record_window)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text="Delete Record",
                command=lambda: self.delete_record(formatted_account, record_window)
            ).pack(side="left", padx=5)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving record: {e}")
        
    def edit_record(self, account_number, record_window):
        """ Load record into the form for editing with consistent account number handling """
        try:
            # Format the account number consistently before searching
            formatted_account = self.format_account_number(account_number)
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE account_number = ? COLLATE NOCASE", 
                        (formatted_account,))
            record = cursor.fetchone()
            
            if not record:
                # Fallback: try searching without hyphens if present
                if '-' in formatted_account:
                    clean_num = formatted_account.replace("-", "")
                    cursor.execute("SELECT * FROM accounts WHERE REPLACE(account_number, '-', '') = ?", 
                                (clean_num,))
                    record = cursor.fetchone()
                
                if not record:
                    messagebox.showerror("Error", f"Record {formatted_account} not found")
                    return
            
            # Get column names
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [column[1] for column in cursor.fetchall()]
            record_dict = dict(zip(columns, record))
            
            # Switch to data entry tab
            self.notebook.select(self.entry_tab)
            self.clear_form()
            
            # Helper function to safely set field values
            def set_field(field, value, default=""):
                if value is None:
                    value = default
                if isinstance(field, ttk.Entry):
                    field.delete(0, tk.END)
                    field.insert(0, str(value))
                elif isinstance(field, ttk.Combobox):
                    field.set(value)
            
            # Set all field values
            set_field(self.account_number, record_dict["account_number"])
            set_field(self.last_name, record_dict["last_name"])
            set_field(self.first_name, record_dict["first_name"])
            set_field(self.middle_name, record_dict["middle_name"])
            set_field(self.name_suffix, record_dict["name_suffix"])
            set_field(self.address, record_dict["address"])
            set_field(self.contact_number, record_dict["contact_number"])
            set_field(self.id_type, record_dict["id_type"])
            set_field(self.id_number, record_dict["id_number"])
            set_field(self.account_status, record_dict["account_status"])
            
            # Numeric fields
            set_field(self.lq_total_savings, record_dict["lq_total_savings"], "0.00")
            set_field(self.savings_quarterly_interest, record_dict["savings_quarterly_interest"], "0.00")
            set_field(self.total_savings, record_dict["total_savings"], "0.00")
            set_field(self.cbu_paid, record_dict["cbu_paid"], "0.00")
            set_field(self.dividend, record_dict["dividend"], "0.00")
            set_field(self.patronage_refund, record_dict["patronage_refund"], "0.00")
            set_field(self.total_cbu, record_dict["total_cbu"], "0.00")
            set_field(self.loan_amount, record_dict["loan_amount"], "0.00")
            set_field(self.loan_type, record_dict["loan_type"])
            set_field(self.loan_term, record_dict["loan_term_months"], "0")
            set_field(self.net_proceed, record_dict["net_proceed"], "0.00")
            
            # Date fields
            set_field(self.date_released, record_dict["date_released"])
            
            self.date_first_installment.config(state='normal')
            set_field(self.date_first_installment, record_dict["date_first_installment"])
            self.date_first_installment.config(state='readonly')
            
            self.maturity_date.config(state='normal')
            set_field(self.maturity_date, record_dict["maturity_date"])
            self.maturity_date.config(state='readonly')
            
            # Other numeric fields
            set_field(self.service_fee, record_dict["service_fee"], "0.00")
            set_field(self.cbu_retention, record_dict["cbu_retention"], "0.00")
            set_field(self.total_interest, record_dict["total_interest"], "0.00")
            set_field(self.penalty, record_dict["penalty"], "0.00")
            set_field(self.past_due_interest, record_dict["past_due_interest"], "0.00")
            set_field(self.account_officer, record_dict["account_officer"])
            
            # Close the record window
            record_window.destroy()
            
            # Highlight the form for editing
            self.highlight_editable_fields()
            messagebox.showinfo("Edit Mode", f"Record {account_number} loaded for editing.")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving record: {e}")

    def delete_record(self, account_number, record_window=None):
        """Delete a record from the database"""
        account_number = self.format_account_number(account_number)
        if not messagebox.askyesno("Confirm Delete", f"Delete account {account_number}?"):
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM accounts WHERE account_number = ? COLLATE NOCASE", (account_number,))
            
            if cursor.rowcount == 0:
                messagebox.showwarning("Not Found", f"Account {account_number} not found")
                return
                
            self.conn.commit()
            messagebox.showinfo("Success", f"Account {account_number} deleted")
            
            if record_window:
                record_window.destroy()
            
            self.load_accounts()
            self.clear_search()
            
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error deleting record: {e}")

    def delete_selected_record(self):
        """Delete the selected record from the view tab"""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to delete")
            return
        
        account_number = self.tree.item(selected_item)['values'][0]
        self.delete_record(account_number)

    def delete_selected_search_record(self):
        """Delete the selected record from the search tab"""
        selected_item = self.search_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to delete")
            return
        
        account_number = self.search_tree.item(selected_item)['values'][0]
        self.delete_record(account_number)

    def highlight_editable_fields(self):
        """ Temporarily highlight editable fields """
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Combobox)) and widget['state'] != 'disabled':
                widget.configure(style='Highlight.TEntry')
        
        # Reset the style after 2 seconds
        self.root.after(2000, self.reset_field_styles)

    def reset_field_styles(self):
        """ Reset field styles to default """
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                widget.configure(style='TEntry')

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Highlight.TEntry', background='#ffffcc')
    app = FinancialRecordsApp(root)
    root.mainloop()