"""
Batch Financial Report Processing for VAs - Part 1: Extraction (Linux)
Generic reference implementation for teaching purposes.

This tool demonstrates a repeatable pattern for:
  - Extracting password-protected archives in bulk, across multiple formats:
    RAR, ZIP, 7Z, TAR, TAR.GZ, and GZ (choose one format or search all at once)
  - Recursively finding target files inside extracted content
  - Saving everything into one flat destination folder
  - Handling duplicates, logging, and progress tracking

The file naming pattern to search for, and the archive format to search for,
are both set inside the app itself (Configuration tab), not in this code, so
no editing of this script is ever required to use it with a new client.
"""

import os
import sys
import shutil
import glob
import subprocess
import zipfile
import tarfile
import gzip
from datetime import datetime
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from queue import Queue
import traceback

try:
    import py7zr
    PY7ZR_AVAILABLE = True
except ImportError:
    PY7ZR_AVAILABLE = False

# =========================================================
# CONFIG: only change this if you want a different default
# starting value. The actual value used during a run always
# comes from the Configuration tab in the app, not from here.
# =========================================================
DEFAULT_TARGET_FILE_PREFIX = "REPORT_"
DEFAULT_TARGET_FILE_EXTENSIONS = ".txt"
DEFAULT_ARCHIVE_TYPE = "ALL Supported"
DEFAULT_FILTER_EXTENSIONS = False
ARCHIVE_TYPE_OPTIONS = ["ALL Supported", "RAR", "ZIP", "7Z", "TAR", "TAR.GZ", "GZ"]
APP_TITLE = "Batch Financial Report Processing for VAs - Part 1: Extraction"
# =========================================================


class ArchiveBatchExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')

        try:
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass

        # Variables - three distinct roles, kept separate on purpose
        self.source_path = tk.StringVar()   # Where archive files are located (searched recursively)
        self.dest_path = tk.StringVar()     # Flat folder where all extracted target files land
        self.temp_path = tk.StringVar()     # Temporary extraction working directory
        self.archive_password = tk.StringVar(value="")  # Leave blank; set per client
        self.target_prefix = tk.StringVar(value=DEFAULT_TARGET_FILE_PREFIX)
        self.target_extensions = tk.StringVar(value=DEFAULT_TARGET_FILE_EXTENSIONS)
        self.archive_type = tk.StringVar(value=DEFAULT_ARCHIVE_TYPE)  # Which archive format(s) to search for
        self.filter_extensions = tk.BooleanVar(value=DEFAULT_FILTER_EXTENSIONS)  # Whether extension list is enforced
        self.processing = False
        self.stop_flag = False
        self.log_queue = Queue()

        self.setup_gui()
        self.process_log_queue()

    def setup_gui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#3498db')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Info.TLabel', foreground='#3498db')

        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Configuration")
        self.setup_config_tab()

        self.processing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.processing_tab, text="Processing")
        self.setup_processing_tab()

        self.logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_tab, text="Logs")
        self.setup_logs_tab()

        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="Help & About")
        self.setup_help_tab()

    def browse_source_path(self):
        path = filedialog.askdirectory(title="Select SOURCE Directory with archive files")
        if path:
            self.source_path.set(path)
            self.log_message(f"Source directory set to: {path}", "INFO")

    def browse_dest_path(self):
        path = filedialog.askdirectory(title="Select DESTINATION Directory for extracted files")
        if path:
            self.dest_path.set(path)
            os.makedirs(path, exist_ok=True)
            self.log_message(f"Destination directory set to: {path}", "INFO")

    def browse_temp_path(self):
        path = filedialog.askdirectory(title="Select Temporary Extraction Directory")
        if path:
            self.temp_path.set(path)
            self.log_message(f"Temp directory set to: {path}", "INFO")

    def create_default_folders(self):
        """One-click setup for VAs who find manually browsing to three separate
        folders confusing. Given ONE parent folder, this creates Source,
        Destination, and Temp subfolders inside it (if they don't already
        exist) and fills in all three Configuration tab fields automatically."""
        parent = filedialog.askdirectory(
            title="Choose (or create) ONE parent folder — Source, Destination, and Temp will go inside it")
        if not parent:
            return

        try:
            source_folder = os.path.join(parent, "Source")
            dest_folder = os.path.join(parent, "Destination")
            temp_folder = os.path.join(parent, "Temp")

            os.makedirs(source_folder, exist_ok=True)
            os.makedirs(dest_folder, exist_ok=True)
            os.makedirs(temp_folder, exist_ok=True)

            self.source_path.set(source_folder)
            self.dest_path.set(dest_folder)
            self.temp_path.set(temp_folder)

            self.log_message(f"Default folders created under: {parent}", "SUCCESS")
            self.log_message(f"  Source: {source_folder}", "INFO")
            self.log_message(f"  Destination: {dest_folder}", "INFO")
            self.log_message(f"  Temp: {temp_folder}", "INFO")

            messagebox.showinfo(
                "Folders Ready",
                f"Three folders were created (or already existed) inside:\n{parent}\n\n"
                "  • Source — put your client's archive files here\n"
                "  • Destination — extracted target files will land here\n"
                "  • Temp — used internally while processing, safe to ignore\n\n"
                "All three fields above have been filled in for you. Just drop the "
                "archive files into the Source folder and you're ready to process."
            )
        except Exception as e:
            self.log_message(f"Error creating default folders: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Could not create default folders: {str(e)}")

    def setup_config_tab(self):
        main_frame = ttk.Frame(self.config_tab, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Archive Extraction Configuration", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        sys_frame = ttk.LabelFrame(main_frame, text="System Information", padding="10")
        sys_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(sys_frame, text=f"Operating System: {platform.system()} {platform.release()}",
                  font=('Arial', 10)).pack(anchor=tk.W)

        if platform.system() == "Linux":
            unrar_path = shutil.which('unrar')
            if unrar_path:
                ttk.Label(sys_frame, text=f"✅ unrar found: {unrar_path}",
                          foreground='green').pack(anchor=tk.W)
            else:
                ttk.Label(sys_frame, text="❌ unrar NOT installed! Install with: sudo dnf install unrar (or apt install unrar)",
                          foreground='red').pack(anchor=tk.W)
        elif platform.system() == "Windows":
            seven_zip_path = self.find_7zip_path()
            if seven_zip_path:
                ttk.Label(sys_frame, text=f"✅ 7-Zip found: {seven_zip_path}",
                          foreground='green').pack(anchor=tk.W)
            else:
                ttk.Label(sys_frame, text="❌ 7-Zip NOT installed! Run install_setup.bat first.",
                          foreground='red').pack(anchor=tk.W)

        path_frame = ttk.LabelFrame(main_frame, text="File Locations", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(path_frame, text="SOURCE Directory (archive files location, searched recursively):",
                  foreground='blue').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.source_path, width=60).grid(row=0, column=1, padx=(10, 10), pady=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_source_path).grid(row=0, column=2, pady=5)

        ttk.Label(path_frame, text="DESTINATION Directory (flat folder for all extracted files):",
                  foreground='green').grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.dest_path, width=60).grid(row=1, column=1, padx=(10, 10), pady=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_dest_path).grid(row=1, column=2, pady=5)

        ttk.Label(path_frame, text="Temporary Extraction Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.temp_path, width=60).grid(row=2, column=1, padx=(10, 10), pady=5)
        ttk.Button(path_frame, text="Browse...", command=self.browse_temp_path).grid(row=2, column=2, pady=5)

        ttk.Separator(path_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky='ew', pady=(10, 8))

        ttk.Button(path_frame, text="Create Default Folders...",
                   command=self.create_default_folders).grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(path_frame,
                  text="New here? Click this once to auto-create Source, Destination, and Temp folders\n"
                       "inside a parent folder you choose, and fill in the three fields above automatically.",
                  font=('Arial', 8, 'italic'), foreground='#555555').grid(
            row=4, column=1, columnspan=2, sticky=tk.W, pady=5)

        security_frame = ttk.LabelFrame(main_frame, text="Security Settings", padding="10")
        security_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(security_frame, text="Archive Password (enter client's real password here):").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(security_frame, textvariable=self.archive_password, width=30, show="*")
        password_entry.grid(row=0, column=1, padx=(10, 10), pady=5)

        self.show_password = tk.BooleanVar(value=False)

        def toggle_password():
            password_entry.config(show="" if self.show_password.get() else "*")

        ttk.Checkbutton(security_frame, text="Show Password", variable=self.show_password,
                         command=toggle_password).grid(row=0, column=2, pady=5)

        archive_frame = ttk.LabelFrame(main_frame, text="Archive Type", padding="10")
        archive_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(archive_frame, text="Which archive format(s) should be searched for?").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        archive_type_combo = ttk.Combobox(archive_frame, textvariable=self.archive_type,
                                           values=ARCHIVE_TYPE_OPTIONS, state='readonly', width=20)
        archive_type_combo.grid(row=0, column=1, padx=(10, 10), pady=5, sticky=tk.W)
        ttk.Label(archive_frame, text="\"ALL Supported\" searches every format below in one pass.",
                  font=('Arial', 8, 'italic')).grid(row=0, column=2, pady=5, sticky=tk.W)

        if not PY7ZR_AVAILABLE:
            ttk.Label(archive_frame,
                      text="⚠ py7zr not installed: 7Z archives will be skipped. Install with: pip install py7zr",
                      foreground='#e67e22').grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        target_frame = ttk.LabelFrame(main_frame, text="Target File Name", padding="10")
        target_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(target_frame, text="What do the files you're looking for start with?").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(target_frame, textvariable=self.target_prefix, width=30).grid(
            row=0, column=1, padx=(10, 10), pady=5)
        ttk.Label(target_frame, text=f"Example: {DEFAULT_TARGET_FILE_PREFIX}",
                  font=('Arial', 8, 'italic')).grid(row=0, column=2, pady=5, sticky=tk.W)

        self.filter_ext_checkbox = ttk.Checkbutton(
            target_frame, text="Filter by file extension", variable=self.filter_extensions,
            command=self.toggle_extensions_field)
        self.filter_ext_checkbox.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.target_extensions_entry = ttk.Entry(target_frame, textvariable=self.target_extensions, width=30)
        self.target_extensions_entry.grid(row=1, column=1, padx=(10, 10), pady=5)
        ttk.Label(target_frame, text="Example: .txt or .txt, .csv (only used if the checkbox above is checked)",
                  font=('Arial', 8, 'italic')).grid(row=1, column=2, pady=5, sticky=tk.W)

        ttk.Label(target_frame,
                  text="Ask your client if you're not sure. Get this from them, don't guess.",
                  foreground='#8a6d00').grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))

        self.toggle_extensions_field()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Save Configuration", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Configuration", command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Defaults", command=self.reset_config).pack(side=tk.LEFT, padx=5)

    def toggle_extensions_field(self):
        """Enable the extensions textbox only when 'Filter by file extension' is checked.
        When unchecked, target file matching ignores file extension entirely."""
        if self.filter_extensions.get():
            self.target_extensions_entry.config(state='normal')
        else:
            self.target_extensions_entry.config(state='disabled')

    def setup_processing_tab(self):
        main_frame = ttk.Frame(self.processing_tab, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Process Archives", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 15))

        self.status_label = ttk.Label(status_frame, text="Ready to process", font=('Arial', 10))
        self.status_label.pack()

        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))

        stats_frame = ttk.LabelFrame(main_frame, text="Processing Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 15))

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack()

        self.total_archives_var = tk.StringVar(value="0")
        self.extracted_var = tk.StringVar(value="0")
        self.failed_var = tk.StringVar(value="0")
        self.errors_var = tk.StringVar(value="0")

        stats = [
            ("Total Archive Files Found:", self.total_archives_var),
            ("Target Files Extracted:", self.extracted_var),
            ("Failed Extractions:", self.failed_var),
            ("Errors Encountered:", self.errors_var)
        ]

        for i, (label, var) in enumerate(stats):
            ttk.Label(stats_grid, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=5)
            ttk.Label(stats_grid, textvariable=var, font=('Arial', 12), foreground='#3498db').grid(
                row=i, column=1, sticky=tk.W, pady=5, padx=20)

        current_frame = ttk.LabelFrame(main_frame, text="Currently Processing", padding="10")
        current_frame.pack(fill=tk.X, pady=(0, 15))

        self.current_file_label = ttk.Label(current_frame, text="None", font=('Arial', 9))
        self.current_file_label.pack()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_button = ttk.Button(button_frame, text="Start Processing", command=self.start_processing, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop Processing", command=self.stop_processing, width=20, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Clear Statistics", command=self.clear_stats, width=20).pack(side=tk.LEFT, padx=5)

    def setup_logs_tab(self):
        main_frame = ttk.Frame(self.logs_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=100, height=40,
                                                    font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config('INFO', foreground='#3498db')
        self.log_text.tag_config('SUCCESS', foreground='#27ae60')
        self.log_text.tag_config('ERROR', foreground='#e74c3c')
        self.log_text.tag_config('WARNING', foreground='#f39c12')
        self.log_text.tag_config('DEBUG', foreground='#95a5a6')

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_log).pack(side=tk.LEFT, padx=5)

    def setup_help_tab(self):
        main_frame = ttk.Frame(self.help_tab, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        help_text = f"""
        Batch Financial Report Processing for VAs - Part 1: Extraction (Linux Version)
        ========================================

        System Information:
        ------------------
        Operating System: {platform.system()} {platform.release()}
        Python Version: {sys.version.split()[0]}

        System Requirements:
        -------------------
        - Linux Operating System (Fedora, Ubuntu, etc.)
        - unrar installed (for RAR extraction)
        - py7zr installed (for 7Z extraction) - pip install py7zr
        - ZIP, TAR, TAR.GZ, and GZ extraction use Python's built-in
          libraries, no extra installation needed
        - Python 3.7 or higher
        - tkinter (usually included with Python)

        Installation Instructions:
        --------------------------
        Fedora: sudo dnf install unrar
        Ubuntu/Debian: sudo apt install unrar
        py7zr (any Linux distro): pip install py7zr

        How to Use:
        -----------
        1. Set the SOURCE directory containing your client's archive files.
           This is searched recursively, so archives can live in any
           subfolder underneath it. No specific structure is required.
        2. Set the DESTINATION directory. All extracted target files land
           here in one flat folder (duplicates get a timestamp suffix).
        3. Set a temporary extraction directory (e.g. /tmp/extract_temp)
        4. Enter the archive password provided by your client
        5. In the Archive Type section, choose which archive format to
           search for (or leave it on "ALL Supported" to search every
           format at once: RAR, ZIP, 7Z, TAR, TAR.GZ, GZ).
        6. In the Target File Name section, enter what the files you want
           start with. Check "Filter by file extension" only if your
           client also wants matching restricted to specific file types.
           Get this from your client, don't guess.
        7. Click "Start Processing" to begin

        File Structure Expected:
        ------------------------
        None. SOURCE_PATH can contain archives directly, or nested inside
        any number of subfolders. The tool walks the whole tree and finds
        every matching archive file it contains. This is intentionally
        simple: you don't need to reorganize a client's folders before
        running it.

        Features:
        ---------
        - Automatic archive file detection and extraction (recursive)
        - Supports RAR, ZIP, 7Z, TAR, TAR.GZ, and GZ archive formats
        - Handles multi-part RAR archives
        - Password-protected archive support (RAR, ZIP, 7Z)
        - Optional filter-by-extension for target file matching
        - Progress tracking and logging
        - Error handling and recovery
        - Configuration save/load
        - Flat destination output with automatic duplicate handling

        Troubleshooting:
        ----------------
        - Ensure unrar is installed: which unrar
        - Ensure py7zr is installed (for 7Z files): pip show py7zr
        - Check that the archive password is correct
        - Verify folder permissions for extraction
        - Check available disk space for temporary files
        """

        help_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=30,
                                                  font=('Arial', 10))
        help_display.insert('1.0', help_text)
        help_display.config(state='disabled')
        help_display.pack(fill=tk.BOTH, expand=True)

    def save_config(self):
        """Save configuration to file. NOTE: for a real client deployment,
        avoid writing the password in plaintext. This is simplified for teaching."""
        try:
            config_file = os.path.expanduser("~/archive_extractor_config.txt")
            with open(config_file, 'w') as f:
                f.write(f"SOURCE_PATH={self.source_path.get()}\n")
                f.write(f"DEST_PATH={self.dest_path.get()}\n")
                f.write(f"TEMP_PATH={self.temp_path.get()}\n")
                f.write(f"TARGET_PREFIX={self.target_prefix.get()}\n")
                f.write(f"TARGET_EXTENSIONS={self.target_extensions.get()}\n")
                f.write(f"ARCHIVE_TYPE={self.archive_type.get()}\n")
                f.write(f"FILTER_EXTENSIONS={self.filter_extensions.get()}\n")
                # Password intentionally NOT saved to disk in plaintext.
            self.log_message(f"Configuration saved to {config_file}", "SUCCESS")
            messagebox.showinfo("Success", "Configuration saved successfully! (Password not saved for security.)")
        except Exception as e:
            self.log_message(f"Error saving config: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        try:
            config_file = os.path.expanduser("~/archive_extractor_config.txt")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == "SOURCE_PATH":
                                self.source_path.set(value)
                            elif key == "DEST_PATH":
                                self.dest_path.set(value)
                            elif key == "TEMP_PATH":
                                self.temp_path.set(value)
                            elif key == "TARGET_PREFIX":
                                self.target_prefix.set(value)
                            elif key == "TARGET_EXTENSIONS":
                                self.target_extensions.set(value)
                            elif key == "ARCHIVE_TYPE":
                                if value in ARCHIVE_TYPE_OPTIONS:
                                    self.archive_type.set(value)
                            elif key == "FILTER_EXTENSIONS":
                                self.filter_extensions.set(value.strip().lower() == "true")
                self.toggle_extensions_field()
                self.log_message("Configuration loaded successfully", "SUCCESS")
                messagebox.showinfo("Success", "Configuration loaded! Re-enter password.")
            else:
                messagebox.showwarning("Not Found", "No saved configuration found.")
        except Exception as e:
            self.log_message(f"Error loading config: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def reset_config(self):
        self.source_path.set("")
        self.dest_path.set("")
        self.temp_path.set("/tmp/archive_extract_temp")
        self.archive_password.set("")
        self.target_prefix.set(DEFAULT_TARGET_FILE_PREFIX)
        self.target_extensions.set(DEFAULT_TARGET_FILE_EXTENSIONS)
        self.archive_type.set(DEFAULT_ARCHIVE_TYPE)
        self.filter_extensions.set(DEFAULT_FILTER_EXTENSIONS)
        self.toggle_extensions_field()
        self.log_message("Configuration reset to defaults", "INFO")
        messagebox.showinfo("Reset", "Configuration reset to default values.")

    def clear_stats(self):
        self.total_archives_var.set("0")
        self.extracted_var.set("0")
        self.failed_var.set("0")
        self.errors_var.set("0")
        self.log_message("Statistics cleared", "INFO")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def save_log(self):
        try:
            log_content = self.log_text.get(1.0, tk.END)
            log_file = f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            self.log_message(f"Log saved to {log_file}", "SUCCESS")
            messagebox.showinfo("Success", f"Log saved to {log_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {str(e)}")

    def copy_log(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_text.get(1.0, tk.END))
        self.log_message("Log copied to clipboard", "INFO")

    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_queue.put((log_entry, level))
        print(log_entry)

    def process_log_queue(self):
        try:
            while not self.log_queue.empty():
                log_entry, level = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, log_entry + "\n", level)
                self.log_text.see(tk.END)
        except Exception:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

    def start_processing(self):
        if not self.source_path.get():
            messagebox.showerror("Error", "Please select the SOURCE directory first!")
            return
        if not self.dest_path.get():
            messagebox.showerror("Error", "Please select the DESTINATION directory first!")
            return
        if not self.temp_path.get():
            messagebox.showerror("Error", "Please select the TEMPORARY directory first!")
            return
        if not os.path.exists(self.source_path.get()):
            messagebox.showerror("Error", f"Source directory does not exist!\n{self.source_path.get()}")
            return
        if not self.archive_password.get():
            response = messagebox.askyesno("No Password Set", "No archive password entered. Continue anyway?")
            if not response:
                return

        if platform.system() == "Linux" and not shutil.which('unrar'):
            response = messagebox.askyesno(
                "Missing Dependency",
                "unrar is not installed!\n\n"
                "This is required to extract RAR files.\n\n"
                "Install it with: sudo dnf install unrar (or apt install unrar)\n\n"
                "Do you want to continue anyway?"
            )
            if not response:
                return

        if platform.system() == "Windows" and not self.find_7zip_path():
            response = messagebox.askyesno(
                "Missing Dependency",
                "7-Zip is not installed!\n\n"
                "This is required to extract RAR files.\n\n"
                "Please run install_setup.bat first.\n\n"
                "Do you want to continue anyway?"
            )
            if not response:
                return

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.processing = True
        self.stop_flag = False

        self.progress_bar.start(10)
        self.clear_stats()

        processing_thread = threading.Thread(target=self.run_processing)
        processing_thread.daemon = True
        processing_thread.start()

    def stop_processing(self):
        self.stop_flag = True
        self.log_message("Stop request received. Finishing current operation...", "WARNING")

    def run_processing(self):
        """Main processing logic (runs in separate thread).
        Flat model: recursively find every archive under SOURCE, extract each,
        and copy any matching target files straight into DEST (no subfolders)."""
        try:
            self.log_message("=" * 50, "INFO")
            self.log_message("ARCHIVE PROCESSING - STARTED", "SUCCESS")
            self.log_message(f"Source: {self.source_path.get()}", "INFO")
            self.log_message(f"Destination: {self.dest_path.get()}", "INFO")
            self.log_message("=" * 50, "INFO")

            os.makedirs(self.temp_path.get(), exist_ok=True)
            os.makedirs(self.dest_path.get(), exist_ok=True)

            archive_count, extracted_count, failed_count = self.process_source_folder(
                self.source_path.get(), self.dest_path.get()
            )

            self.log_message(f"\n{'=' * 50}", "SUCCESS")
            self.log_message("PROCESSING COMPLETE", "SUCCESS")
            self.log_message(f"{'=' * 50}", "SUCCESS")
            self.log_message(f"TOTAL ARCHIVE FILES PROCESSED: {archive_count}", "INFO")
            self.log_message(f"TOTAL TARGET FILES EXTRACTED: {extracted_count}", "SUCCESS")
            self.log_message(f"FAILED EXTRACTIONS: {failed_count}", "ERROR" if failed_count > 0 else "INFO")

        except Exception as e:
            self.log_message(f"Unexpected error: {str(e)}", "ERROR")
            self.log_message(traceback.format_exc(), "ERROR")
        finally:
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            self.root.after(0, lambda: self.progress_bar.stop())
            self.processing = False

            if self.stop_flag:
                self.log_message("\nProcessing stopped by user", "WARNING")
                messagebox.showwarning("Stopped", "Processing was stopped by user.")
            else:
                messagebox.showinfo("Complete", "Processing completed successfully!")

    def process_source_folder(self, source_folder, dest_folder):
        """Find every archive anywhere under source_folder (recursively),
        extract each, and copy matching target files into the flat dest_folder."""
        self.root.after(0, lambda: self.status_label.config(text=f"Processing: {source_folder}"))

        archive_files = self.find_archive_files(source_folder)
        extracted_count = 0
        archive_count = len(archive_files)
        failed_count = 0

        if not archive_files:
            self.log_message("No archive files found under source directory", "INFO")
            return 0, 0, 0

        self.log_message(f"Found {len(archive_files)} archive file(s) to extract", "INFO")

        for archive_file in archive_files:
            if self.stop_flag:
                break

            archive_name = os.path.basename(archive_file)
            self.root.after(0, lambda n=archive_name: self.current_file_label.config(text=f"Extracting: {n}"))
            self.log_message(f"Extracting: {archive_name}", "INFO")

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            extract_subfolder = os.path.join(self.temp_path.get(), f"extract_{timestamp}")
            os.makedirs(extract_subfolder, exist_ok=True)

            if self.extract_archive_file(archive_file, extract_subfolder):
                self.log_message(f"Successfully extracted: {archive_name}", "SUCCESS")

                extracted_targets = self.find_target_files(extract_subfolder)

                if extracted_targets:
                    self.log_message(f"Found {len(extracted_targets)} target file(s) in archive", "SUCCESS")
                    extracted_count += len(extracted_targets)

                    for target_file in extracted_targets:
                        dest_path = os.path.join(dest_folder, os.path.basename(target_file))

                        if os.path.exists(dest_path):
                            timestamp2 = datetime.now().strftime('%Y%m%d_%H%M%S')
                            name, ext = os.path.splitext(os.path.basename(target_file))
                            new_filename = f"{name}_{timestamp2}{ext}"
                            dest_path = os.path.join(dest_folder, new_filename)
                            self.log_message(f"File exists, saving as: {new_filename}", "WARNING")

                        shutil.copy2(target_file, dest_path)
                        self.log_message(f"Copied to: {dest_path}", "SUCCESS")
                else:
                    self.log_message("No target files found in the extracted archive", "WARNING")
            else:
                self.log_message(f"Failed to extract: {archive_name}", "ERROR")
                failed_count += 1

            if os.path.exists(extract_subfolder):
                shutil.rmtree(extract_subfolder, ignore_errors=True)

            self.root.after(0, lambda: self.progress_bar.step(1))
            self.root.after(0, lambda r=archive_count: self.total_archives_var.set(str(r)))
            self.root.after(0, lambda e=extracted_count: self.extracted_var.set(str(e)))
            self.root.after(0, lambda f=failed_count: self.failed_var.set(str(f)))

        return archive_count, extracted_count, failed_count

    def _archive_extension_matches(self, filename):
        """Return True if filename's extension matches the currently selected
        Archive Type (ALL Supported, RAR, ZIP, 7Z, TAR, TAR.GZ, or GZ)."""
        name_lower = filename.lower()
        selected = self.archive_type.get()

        is_rar = name_lower.endswith(".rar")
        is_zip = name_lower.endswith(".zip")
        is_7z = name_lower.endswith(".7z")
        is_targz = name_lower.endswith(".tar.gz") or name_lower.endswith(".tgz")
        is_tar = name_lower.endswith(".tar") and not is_targz
        # Plain .gz that is NOT a .tar.gz (a single compressed file, e.g. report.txt.gz)
        is_gz = name_lower.endswith(".gz") and not is_targz

        if selected == "ALL Supported":
            return is_rar or is_zip or is_7z or is_targz or is_tar or is_gz
        elif selected == "RAR":
            return is_rar
        elif selected == "ZIP":
            return is_zip
        elif selected == "7Z":
            return is_7z
        elif selected == "TAR":
            return is_tar
        elif selected == "TAR.GZ":
            return is_targz
        elif selected == "GZ":
            return is_gz
        return False

    def find_archive_files(self, folder_path):
        """Recursively find all archive files anywhere under folder_path that
        match the Archive Type selected in the Configuration tab (ALL Supported,
        RAR, ZIP, 7Z, TAR, TAR.GZ, or GZ)."""
        archive_files = []

        for root_dir, dirs, files in os.walk(folder_path):
            for file in files:
                if self._archive_extension_matches(file):
                    full_path = os.path.join(root_dir, file)
                    if full_path not in archive_files:
                        archive_files.append(full_path)

        return archive_files

    def find_target_files(self, folder_path):
        """Recursively find files matching the pattern entered in the
        Target File Settings section of the Configuration tab.

        Matching rule:
          - Always require the filename to start with the target prefix.
          - If 'Filter by file extension' is UNCHECKED: extension is ignored
            entirely, any file type matching the prefix counts.
          - If it IS checked: the file must also end with one of the
            extensions listed in the Target File Name section.
        """
        target_files = []

        prefix = self.target_prefix.get().strip().upper()
        filter_on = self.filter_extensions.get()
        extensions = ('',)

        if filter_on:
            raw_extensions = self.target_extensions.get().strip()
            extensions = tuple(
                e.strip().lower() if e.strip().startswith('.') else '.' + e.strip().lower()
                for e in raw_extensions.split(',') if e.strip()
            )
            if not extensions:
                extensions = ('',)  # nothing entered: fall back to matching any extension

        for root_dir, dirs, files in os.walk(folder_path):
            for file in files:
                if not file.upper().startswith(prefix):
                    continue
                if filter_on and not file.lower().endswith(extensions):
                    continue
                full_path = os.path.join(root_dir, file)
                target_files.append(full_path)
                self.log_message(f"Found target file: {os.path.relpath(full_path, folder_path)}", "DEBUG")

        return target_files

    def extract_archive_with_linux_tool(self, archive_path, extract_to):
        if not shutil.which('unrar'):
            self.log_message("unrar not found! Install with: sudo dnf install unrar (or apt install unrar)", "ERROR")
            return False

        try:
            cmd = ['unrar', 'x', f'-p{self.archive_password.get()}', '-y', archive_path, f'{extract_to}/']

            self.log_message(f"Running: unrar x -p[PASSWORD] -y {os.path.basename(archive_path)}", "DEBUG")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                return True
            else:
                if "password" in result.stderr.lower() or "CRC" in result.stderr:
                    self.log_message("Password incorrect or archive corrupted", "ERROR")
                else:
                    self.log_message(f"Exit code: {result.returncode}", "ERROR")
                    if result.stderr:
                        self.log_message(f"Error: {result.stderr[:200]}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log_message("Extraction timeout (5 minutes)", "ERROR")
            return False
        except Exception as e:
            self.log_message(f"Extraction error: {str(e)}", "ERROR")
            return False

    def find_7zip_path(self):
        """Locate 7z.exe, checking PATH first, then the standard install location."""
        found = shutil.which('7z')
        if found:
            return found
        default_path = r"C:\Program Files\7-Zip\7z.exe"
        if os.path.exists(default_path):
            return default_path
        return None

    def extract_archive_with_windows_tool(self, archive_path, extract_to):
        """Extract a RAR archive on Windows using 7-Zip's command line (7z.exe).
        Requires 7-Zip to be installed. See install_setup.bat."""
        seven_zip = self.find_7zip_path()
        if not seven_zip:
            self.log_message("7-Zip not found! Please run install_setup.bat first.", "ERROR")
            return False

        try:
            cmd = [seven_zip, 'x', f'-p{self.archive_password.get()}', '-y',
                   archive_path, f'-o{extract_to}']

            self.log_message(f"Running: 7z x -p[PASSWORD] -y {os.path.basename(archive_path)}", "DEBUG")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                return True
            else:
                combined_output = (result.stdout or "") + (result.stderr or "")
                if "wrong password" in combined_output.lower() or "data error" in combined_output.lower():
                    self.log_message("Password incorrect or archive corrupted", "ERROR")
                else:
                    self.log_message(f"Exit code: {result.returncode}", "ERROR")
                    if combined_output:
                        self.log_message(f"Error: {combined_output[:200]}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log_message("Extraction timeout (5 minutes)", "ERROR")
            return False
        except Exception as e:
            self.log_message(f"Extraction error: {str(e)}", "ERROR")
            return False

    def extract_zip_file(self, archive_path, extract_to):
        """Extract a .zip archive, using the password if one was provided."""
        try:
            pwd = self.archive_password.get()
            pwd_bytes = pwd.encode('utf-8') if pwd else None
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(path=extract_to, pwd=pwd_bytes)
            return True
        except RuntimeError as e:
            if "password" in str(e).lower() or "Bad password" in str(e):
                self.log_message("Password incorrect for ZIP archive", "ERROR")
            else:
                self.log_message(f"ZIP extraction error: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log_message(f"ZIP extraction error: {str(e)}", "ERROR")
            return False

    def extract_7z_file(self, archive_path, extract_to):
        """Extract a .7z archive using py7zr, using the password if one was provided."""
        if not PY7ZR_AVAILABLE:
            self.log_message("py7zr is not installed. Install it with: pip install py7zr", "ERROR")
            return False
        try:
            pwd = self.archive_password.get() or None
            with py7zr.SevenZipFile(archive_path, mode='r', password=pwd) as archive:
                archive.extractall(path=extract_to)
            return True
        except Exception as e:
            if "password" in str(e).lower():
                self.log_message("Password incorrect for 7Z archive", "ERROR")
            else:
                self.log_message(f"7Z extraction error: {str(e)}", "ERROR")
            return False

    def extract_tar_file(self, archive_path, extract_to):
        """Extract a .tar, .tar.gz, or .tgz archive. Tar-family archives are not
        password-protected by the format itself, so no password is applied."""
        try:
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(path=extract_to)
            return True
        except Exception as e:
            self.log_message(f"TAR extraction error: {str(e)}", "ERROR")
            return False

    def extract_gz_file(self, archive_path, extract_to):
        """Decompress a single-file .gz archive (not a .tar.gz) into extract_to,
        keeping the original filename minus the .gz suffix."""
        try:
            base_name = os.path.basename(archive_path)
            out_name = base_name[:-3] if base_name.lower().endswith('.gz') else base_name + '.out'
            out_path = os.path.join(extract_to, out_name)
            with gzip.open(archive_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            return True
        except Exception as e:
            self.log_message(f"GZ extraction error: {str(e)}", "ERROR")
            return False

    def extract_archive_file(self, archive_path, extract_to):
        """Format-dispatched extraction wrapper.
        RAR -> unrar (Linux) / 7-Zip (Windows)
        ZIP -> zipfile
        7Z  -> py7zr
        TAR / TAR.GZ / TGZ -> tarfile
        GZ (single file, not tar.gz) -> gzip
        """
        name_lower = archive_path.lower()

        if name_lower.endswith(".rar"):
            system = platform.system()
            if system == "Windows":
                return self.extract_archive_with_windows_tool(archive_path, extract_to)
            elif system == "Linux":
                return self.extract_archive_with_linux_tool(archive_path, extract_to)
            else:
                self.log_message(f"Unsupported operating system: {system}", "ERROR")
                return False
        elif name_lower.endswith(".zip"):
            return self.extract_zip_file(archive_path, extract_to)
        elif name_lower.endswith(".7z"):
            return self.extract_7z_file(archive_path, extract_to)
        elif name_lower.endswith(".tar.gz") or name_lower.endswith(".tgz") or name_lower.endswith(".tar"):
            return self.extract_tar_file(archive_path, extract_to)
        elif name_lower.endswith(".gz"):
            return self.extract_gz_file(archive_path, extract_to)
        else:
            self.log_message(f"Unrecognized archive format: {os.path.basename(archive_path)}", "ERROR")
            return False


def main():
    root = tk.Tk()
    app = ArchiveBatchExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
