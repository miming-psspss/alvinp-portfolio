"""
DATR File Processor with GUI - Enhanced Version
Features: Browse folders, preview data, generate master CSV
Compatible with Tcl 9+ and Python 3.14
"""

import os
import re
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from datetime import datetime
from pathlib import Path
import json

class DATRProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DATR File Processor & Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.processing = False
        self.transactions_data = []
        self.total_files = 0
        self.total_transactions = 0
        
        # Configuration
        self.config_file = os.path.expanduser("~/datr_processor_config.json")
        
        # Setup GUI
        self.setup_styles()
        self.setup_gui()
        self.load_config()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Stats.TLabel', font=('Segoe UI', 11), foreground='#2c3e50')
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        
    def setup_gui(self):
        """Create the main GUI layout"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="DATR File Processor & Analyzer", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create PanedWindow for resizable sections
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_frame = ttk.Frame(paned, width=400)
        paned.add(left_frame, weight=1)
        self.setup_left_panel(left_frame)
        
        # Right panel - Data view
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        self.setup_right_panel(right_frame)
        
        # Bottom status bar
        self.setup_status_bar(main_frame)
        
    def setup_left_panel(self, parent):
        """Setup control panel"""
        
        # Path Selection Frame
        path_frame = ttk.LabelFrame(parent, text="📁 File Locations", padding="15")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Source folder
        ttk.Label(path_frame, text="DATR Files Folder:", 
                 style='Header.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        source_frame = ttk.Frame(path_frame)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_path)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(source_frame, text="Browse", command=self.browse_source,
                  style='Primary.TButton').pack(side=tk.RIGHT)
        
        # Output folder
        ttk.Label(path_frame, text="Output Folder:", 
                 style='Header.TLabel').pack(anchor=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(path_frame)
        output_frame.pack(fill=tk.X)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output,
                  style='Primary.TButton').pack(side=tk.RIGHT)
        
        # Filters Frame
        filter_frame = ttk.LabelFrame(parent, text="🔍 Filters", padding="15")
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Year selection
        ttk.Label(filter_frame, text="Filter by Year:", 
                 style='Header.TLabel').pack(anchor=tk.W)
        
        year_frame = ttk.Frame(filter_frame)
        year_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.year_var = tk.StringVar(value="All")
        years = ["All", "2024", "2025", "2026"]
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, 
                                  values=years, state='readonly', width=10)
        year_combo.pack(side=tk.LEFT)
        
        # Month filter
        ttk.Label(filter_frame, text="Filter by Month:", 
                 style='Header.TLabel').pack(anchor=tk.W, pady=(10, 5))
        
        self.month_var = tk.StringVar(value="All")
        months = ["All", "January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var, 
                                   values=months, state='readonly', width=15)
        month_combo.pack(fill=tk.X)
        
        # Action Buttons Frame
        action_frame = ttk.LabelFrame(parent, text="⚡ Actions", padding="15")
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Load data button
        self.load_btn = ttk.Button(action_frame, text="📂 Load DATR Files", 
                                   command=self.load_datr_files,
                                   style='Primary.TButton')
        self.load_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Generate CSV button
        self.csv_btn = ttk.Button(action_frame, text="📊 Generate Master CSV",
                                 command=self.generate_master_csv,
                                 style='Primary.TButton')
        self.csv_btn.pack(fill=tk.X, pady=(0, 10))
        self.csv_btn.config(state='disabled')
        
        # Clear data button
        ttk.Button(action_frame, text="🗑️ Clear All Data",
                  command=self.clear_data).pack(fill=tk.X)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(parent, text="📈 Progress", padding="15")
        progress_frame.pack(fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="Ready", 
                                      font=('Segoe UI', 9))
        self.status_label.pack()
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(parent, text="📊 Statistics", padding="15")
        stats_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.files_var = tk.StringVar(value="Files: 0")
        self.trans_var = tk.StringVar(value="Transactions: 0")
        
        ttk.Label(stats_frame, textvariable=self.files_var, 
                 style='Stats.TLabel').pack(anchor=tk.W, pady=2)
        ttk.Label(stats_frame, textvariable=self.trans_var, 
                 style='Stats.TLabel').pack(anchor=tk.W, pady=2)
        
    def setup_right_panel(self, parent):
        """Setup data view panel"""
        
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="🔍 Search:", 
                 style='Header.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        # FIXED: Use trace_add instead of deprecated trace_variable
        self.search_var.trace_add('write', self.filter_treeview)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create Treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('Year', 'Month', 'File', 'Date/Time', 'Seq No', 'Trace No',
                  'Tran Code', 'Account No', 'Card No', 'Amount', 'Fee', 'Terminal')
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=y_scroll.set,
                                xscrollcommand=x_scroll.set)
        
        # Configure scrollbars
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Define column headings and widths
        column_widths = {
            'Year': 60, 'Month': 80, 'File': 150, 'Date/Time': 140,
            'Seq No': 80, 'Trace No': 80, 'Tran Code': 80,
            'Account No': 120, 'Card No': 120, 'Amount': 100,
            'Fee': 80, 'Terminal': 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to show details
        self.tree.bind('<Double-Button-1>', self.show_transaction_details)
        
    def setup_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_text = tk.StringVar(value="Ready - Select DATR files folder to begin")
        status_label = ttk.Label(status_frame, textvariable=self.status_text,
                                relief=tk.SUNKEN, anchor=tk.W, padding=(10, 5))
        status_label.pack(fill=tk.X)
        
    def browse_source(self):
        """Browse for source folder"""
        folder = filedialog.askdirectory(title="Select Folder with DATR Files")
        if folder:
            self.source_path.set(folder)
            # Auto-set output folder
            if not self.output_path.get():
                self.output_path.set(os.path.join(folder, "PROCESSED_DATA"))
            self.update_status(f"Source folder set: {folder}")
            
    def browse_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder for CSV")
        if folder:
            self.output_path.set(folder)
            
    def update_status(self, message):
        """Update status bar"""
        self.status_text.set(message)
        
    def load_datr_files(self):
        """Load DATR files in a separate thread"""
        source = self.source_path.get()
        
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Please select a valid source folder!")
            return
            
        # Disable buttons during processing
        self.load_btn.config(state='disabled')
        self.csv_btn.config(state='disabled')
        self.progress_bar.start()
        
        # Start processing thread
        thread = threading.Thread(target=self.process_datr_files, args=(source,))
        thread.daemon = True
        thread.start()
        
    def process_datr_files(self, base_path):
        """Process all DATR files recursively"""
        try:
            self.update_status("Scanning for DATR files...")
            self.transactions_data = []
            self.total_files = 0
            self.total_transactions = 0
            
            # Find all DATR files recursively
            datr_files = []
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.upper().startswith('DATR_') and file.upper().endswith('.TXT'):
                        datr_files.append(os.path.join(root, file))
            
            if not datr_files:
                self.root.after(0, lambda: messagebox.showinfo("Info", 
                    "No DATR files found in the selected folder or its subfolders!"))
                return
                
            # Extract year and month from path for filtering
            year_filter = self.year_var.get()
            month_filter = self.month_var.get()
            
            # Process each file
            for file_path in datr_files:
                # Try to extract year/month from path
                path_parts = Path(file_path).parts
                year = None
                month = None
                
                for part in path_parts:
                    # Look for year pattern (e.g., 2024_EMV)
                    year_match = re.match(r'(\d{4})_EMV', part)
                    if year_match:
                        year = year_match.group(1)
                    
                    # Look for month pattern (e.g., a_January_2024)
                    month_match = re.match(r'[a-l]_(\w+)_\d{4}', part)
                    if month_match:
                        month = month_match.group(1)
                
                # Apply filters
                if year_filter != "All" and year != year_filter:
                    continue
                if month_filter != "All" and month != month_filter:
                    continue
                
                self.process_single_datr(file_path, year or "Unknown", month or "Unknown")
                self.total_files += 1
                
                # Update UI
                self.root.after(0, lambda: self.files_var.set(
                    f"Files: {self.total_files}"))
                self.root.after(0, lambda: self.trans_var.set(
                    f"Transactions: {self.total_transactions}"))
            
            # Update UI after completion
            self.root.after(0, self.update_treeview)
            self.root.after(0, lambda: self.update_status(
                f"Loaded {self.total_files} files, {self.total_transactions} transactions"))
            
            if self.total_files > 0:
                self.root.after(0, lambda: self.csv_btn.config(state='normal'))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.load_btn.config(state='normal'))
            self.root.after(0, lambda: self.progress_bar.stop())
            
    def process_single_datr(self, file_path, year, month):
        """Process a single DATR file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Metadata variables
                current_report_date = None
                current_run_time = None
                current_site_code = None
                current_terminal_id = None
                current_terminal_name = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extract metadata
                    if 'FOR ' in line and not current_report_date:
                        date_match = re.search(r'FOR\s+(\d{1,2}/\d{1,2}/\d{4})', line)
                        if date_match:
                            current_report_date = date_match.group(1)
                    
                    if 'RUN TIME' in line and not current_run_time:
                        time_match = re.search(r'RUN TIME\s+(\d{2}:\d{2}:\d{2})', line)
                        if time_match:
                            current_run_time = time_match.group(1)
                    
                    if 'SITE CODE' in line and 'TERMINAL' not in line:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit() and len(part) >= 4:
                                current_site_code = part
                                break
                    
                    if 'TERMINAL' in line:
                        parts = line.split()
                        for j, part in enumerate(parts):
                            if part == 'TERMINAL' and j + 1 < len(parts):
                                current_terminal_id = parts[j + 1]
                                if j + 2 < len(parts):
                                    current_terminal_name = ' '.join(parts[j + 2:])
                                break
                    
                    # Process transaction lines
                    if re.match(r'\s*\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}', line):
                        parts = re.split(r'\s{2,}', line)
                        
                        if len(parts) >= 9:
                            transaction = {
                                'Year': year,
                                'Month': month,
                                'File': os.path.basename(file_path),
                                'FilePath': file_path,
                                'ReportDate': current_report_date or '',
                                'RunTime': current_run_time or '',
                                'SiteCode': current_site_code or '',
                                'TerminalID': current_terminal_id or '',
                                'TerminalName': current_terminal_name or '',
                                'DateTime': parts[0],
                                'SeqNo': parts[1] if len(parts) > 1 else '',
                                'TraceNo': parts[2] if len(parts) > 2 else '',
                                'ATMTrace': parts[3] if len(parts) > 3 else '',
                                'TranCode': parts[4] if len(parts) > 4 else '',
                                'AccountNo': parts[5] if len(parts) > 5 else '',
                                'CardNo': parts[6] if len(parts) > 6 else '',
                                'TranAmount': parts[7].replace(',', '') if len(parts) > 7 else '',
                                'TranFee': parts[8].replace(',', '') if len(parts) > 8 else ''
                            }
                            
                            self.transactions_data.append(transaction)
                            self.total_transactions += 1
                            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            
    def update_treeview(self):
        """Update the treeview with processed data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add sorted data
        for trans in self.transactions_data:
            values = (
                trans['Year'],
                trans['Month'],
                trans['File'],
                trans['DateTime'],
                trans['SeqNo'],
                trans['TraceNo'],
                trans['TranCode'],
                trans['AccountNo'],
                trans['CardNo'],
                trans['TranAmount'],
                trans['TranFee'],
                trans['TerminalName']
            )
            self.tree.insert('', 'end', values=values)
            
        # Update statistics
        self.files_var.set(f"Files: {self.total_files}")
        self.trans_var.set(f"Transactions: {self.total_transactions}")
        
    def filter_treeview(self, *args):
        """Filter treeview based on search text"""
        search_term = self.search_var.get().lower()
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter and add matching items
        for trans in self.transactions_data:
            if not search_term:
                # Add all if no search term
                values = self.get_transaction_values(trans)
                self.tree.insert('', 'end', values=values)
            else:
                # Check if search term matches any field
                for key, value in trans.items():
                    if search_term in str(value).lower():
                        values = self.get_transaction_values(trans)
                        self.tree.insert('', 'end', values=values)
                        break
                        
    def get_transaction_values(self, trans):
        """Get values tuple for treeview"""
        return (
            trans['Year'],
            trans['Month'],
            trans['File'],
            trans['DateTime'],
            trans['SeqNo'],
            trans['TraceNo'],
            trans['TranCode'],
            trans['AccountNo'],
            trans['CardNo'],
            trans['TranAmount'],
            trans['TranFee'],
            trans['TerminalName']
        )
        
    def sort_treeview(self, col):
        """Sort treeview by column"""
        # Get all items
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Sort items
        items.sort()
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)
            
    def show_transaction_details(self, event):
        """Show detailed view of selected transaction"""
        selection = self.tree.selection()
        if not selection:
            return
            
        # Create popup window
        item = self.tree.item(selection[0])
        values = item['values']
        columns = ['Year', 'Month', 'File', 'Date/Time', 'Seq No', 'Trace No',
                  'Tran Code', 'Account No', 'Card No', 'Amount', 'Fee', 'Terminal']
        
        popup = tk.Toplevel(self.root)
        popup.title("Transaction Details")
        popup.geometry("500x400")
        popup.resizable(False, False)
        
        # Display details
        frame = ttk.Frame(popup, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Transaction Details", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Create scrollable frame for details
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, col in enumerate(columns):
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"{col}:", 
                     font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(row_frame, text=str(values[i]), 
                     font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Button(frame, text="Close", command=popup.destroy).pack(pady=20)
        
    def generate_master_csv(self):
        """Generate master CSV file"""
        if not self.transactions_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
            
        output_dir = self.output_path.get()
        if not output_dir:
            # Ask where to save the file
            output_file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Master CSV As"
            )
            if not output_file:
                return
        else:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f"MASTER_TRANSACTIONS_{timestamp}.csv")
        
        try:
            # Generate CSV
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Year', 'Month', 'Source File', 'Report Date', 'Run Time',
                    'Site Code', 'Terminal ID', 'Terminal Name', 'Date/Time',
                    'Seq No', 'Trace No', 'ATM Trace', 'Tran Code',
                    'Account Number', 'Card Number', 'Transaction Amount',
                    'Transaction Fee'
                ])
                
                # Write data
                for trans in self.transactions_data:
                    writer.writerow([
                        trans['Year'],
                        trans['Month'],
                        trans['File'],
                        trans['ReportDate'],
                        trans['RunTime'],
                        trans['SiteCode'],
                        trans['TerminalID'],
                        trans['TerminalName'],
                        trans['DateTime'],
                        trans['SeqNo'],
                        trans['TraceNo'],
                        trans['ATMTrace'],
                        trans['TranCode'],
                        trans['AccountNo'],
                        trans['CardNo'],
                        trans['TranAmount'],
                        trans['TranFee']
                    ])
            
            self.update_status(f"Master CSV generated: {output_file}")
            messagebox.showinfo("Success", 
                f"Master CSV created successfully!\n\n"
                f"File: {output_file}\n"
                f"Total transactions: {len(self.transactions_data)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate CSV: {str(e)}")
            
    def clear_data(self):
        """Clear all loaded data"""
        if messagebox.askyesno("Confirm", "Clear all loaded data?"):
            self.transactions_data = []
            self.total_files = 0
            self.total_transactions = 0
            
            # Clear treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Reset statistics
            self.files_var.set("Files: 0")
            self.trans_var.set("Transactions: 0")
            self.csv_btn.config(state='disabled')
            
            self.update_status("Data cleared")
            
    def save_config(self):
        """Save configuration to file"""
        config = {
            'source_path': self.source_path.get(),
            'output_path': self.output_path.get(),
            'year_filter': self.year_var.get(),
            'month_filter': self.month_var.get()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except:
            pass
            
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                if config.get('source_path'):
                    self.source_path.set(config['source_path'])
                if config.get('output_path'):
                    self.output_path.set(config['output_path'])
                if config.get('year_filter'):
                    self.year_var.set(config['year_filter'])
                if config.get('month_filter'):
                    self.month_var.set(config['month_filter'])
        except:
            pass
            
    def on_closing(self):
        """Handle window closing"""
        self.save_config()
        self.root.destroy()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = DATRProcessorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()