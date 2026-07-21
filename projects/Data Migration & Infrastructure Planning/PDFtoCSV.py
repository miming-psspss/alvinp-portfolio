"""
PDF TO CSV EXTRACTOR - FAST VERSION
Optimized for speed with progress tracking
"""

import os
import re
import time
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# ============================================
# CONFIGURATION
# ============================================

POPPLER_PATH = r'C:\poppler\Library\bin'
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Speed settings (adjust based on your needs)
DPI = 150  # Lower DPI = faster (150 is good balance, 200 is slower but clearer)
THREADS = multiprocessing.cpu_count()  # Use all CPU cores

# ============================================
# FILE SELECTION
# ============================================

def select_pdf_file():
    """Open dialog to select PDF file"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    pdf_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    return pdf_path

def select_csv_location():
    """Open dialog to select CSV save location"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    csv_path = filedialog.asksaveasfilename(title="Save CSV As", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    root.destroy()
    return csv_path

# ============================================
# FAST PDF PROCESSING
# ============================================

def process_single_page(args):
    """Process a single page (for parallel processing)"""
    page_num, image = args
    
    try:
        # Convert to grayscale (faster processing)
        image = image.convert('L')
        
        # OCR with optimized settings
        text = pytesseract.image_to_string(
            image,
            config='--oem 3 --psm 6'  # OEM 3 = Default, PSM 6 = Uniform block of text
        )
        
        return {
            'page_number': page_num,
            'text': text,
            'success': True
        }
    except Exception as e:
        return {
            'page_number': page_num,
            'text': '',
            'success': False,
            'error': str(e)
        }

def extract_text_from_pdf_fast(pdf_path):
    """Fast parallel PDF to text extraction"""
    
    # Set Tesseract path
    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    else:
        raise Exception(f"Tesseract not found at: {TESSERACT_PATH}")
    
    print(f"\n📄 Converting PDF to images (DPI={DPI})...")
    start_time = time.time()
    
    # Convert PDF to images
    images = convert_from_path(
        pdf_path, 
        dpi=DPI,
        poppler_path=POPPLER_PATH
    )
    
    convert_time = time.time() - start_time
    total_pages = len(images)
    print(f"   ✅ Converted {total_pages} pages in {convert_time:.1f} seconds")
    
    print(f"\n🔍 Extracting text from {total_pages} pages using {THREADS} threads...")
    start_time = time.time()
    
    # Prepare arguments for parallel processing
    args_list = [(i+1, img) for i, img in enumerate(images)]
    
    # Process pages in parallel
    all_text = []
    completed = 0
    
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        # Submit all tasks
        futures = {executor.submit(process_single_page, args): args[0] for args in args_list}
        
        # Process results as they complete
        for future in as_completed(futures):
            result = future.result()
            all_text.append(result)
            completed += 1
            
            # Show progress
            if completed % 5 == 0 or completed == total_pages:
                print(f"   Progress: {completed}/{total_pages} pages ({int(completed/total_pages*100)}%)")
    
    # Sort by page number
    all_text.sort(key=lambda x: x['page_number'])
    
    extract_time = time.time() - start_time
    print(f"   ✅ Text extraction completed in {extract_time:.1f} seconds")
    
    return all_text

# ============================================
# FAST DATA EXTRACTION
# ============================================

def extract_loan_data_fast(text_data):
    """Optimized data extraction"""
    
    print(f"\n📊 Extracting loan data...")
    start_time = time.time()
    
    # Compile patterns once for speed
    patterns = {
        'NAME': re.compile(r'(?:NAME|BORROWER)[:\s]+([^\n]+)', re.IGNORECASE),
        'ADDRESS': re.compile(r'(?:ADDRESS|ADD)[:\s]+([^\n]+)', re.IGNORECASE),
        'KIND OF LOAN': re.compile(r'(?:KIND OF LOAN|LOAN TYPE)[:\s]+([^\n]+)', re.IGNORECASE),
        'DATE GRANTED': re.compile(r'(?:DATE GRANTED|GRANTED DATE)[:\s]+([^\n]+)', re.IGNORECASE),
        'MATURITY DATE': re.compile(r'(?:MATURITY DATE|DUE DATE)[:\s]+([^\n]+)', re.IGNORECASE),
        'LOAN TERM': re.compile(r'(?:LOAN TERM|TERM)[:\s]+([^\n]+)', re.IGNORECASE),
        'DATE': re.compile(r'\bDATE[:\s]+([^\n]+)', re.IGNORECASE),
        'CC/CV NO.': re.compile(r'(?:CC/CV NO|CC NO|CV NO)[:\s.]+([^\n]+)', re.IGNORECASE),
        'PRINCIPAL': re.compile(r'PRINCIPAL[:\s]*[PHP₱\$]?\s*([\d,\.]+)', re.IGNORECASE),
        'INTEREST': re.compile(r'INTEREST[:\s]*[PHP₱\$]?\s*([\d,\.]+)', re.IGNORECASE),
        'SERVICE FEE': re.compile(r'SERVICE FEE[:\s]*[PHP₱\$]?\s*([\d,\.]+)', re.IGNORECASE),
        'PROCEEDS': re.compile(r'PROCEEDS[:\s]*[PHP₱\$]?\s*([\d,\.]+)', re.IGNORECASE)
    }
    
    all_records = []
    pages_with_data = 0
    
    for page in text_data:
        if not page['success']:
            continue
            
        record = {'page_number': page['page_number']}
        text = page['text']
        
        has_data = False
        for field, pattern in patterns.items():
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                record[field] = value
                has_data = True
            else:
                record[field] = ''
        
        all_records.append(record)
        if has_data:
            pages_with_data += 1
    
    extract_time = time.time() - start_time
    print(f"   ✅ Extracted data from {pages_with_data}/{len(text_data)} pages in {extract_time:.1f} seconds")
    
    return all_records

# ============================================
# SAVE TO CSV
# ============================================

def save_to_csv(records, csv_path):
    """Save to CSV"""
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    file_size = os.path.getsize(csv_path) / 1024
    print(f"\n💾 Saved to: {csv_path}")
    print(f"   File size: {file_size:.1f} KB")
    print(f"   Records: {len(records)}")
    
    return df

# ============================================
# PROGRESS BAR
# ============================================

def print_header():
    """Print nice header"""
    print("\n" + "="*60)
    print("   PDF TO CSV EXTRACTOR - FAST VERSION")
    print("="*60)
    print(f"\n⚙️  Settings:")
    print(f"   • Poppler: {POPPLER_PATH}")
    print(f"   • DPI: {DPI} (lower = faster)")
    print(f"   • Threads: {THREADS} (CPU cores)")
    print("="*60)

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print_header()
    
    # Select files
    pdf_path = select_pdf_file()
    if not pdf_path:
        print("\n❌ No PDF selected. Exiting.")
        return
    
    csv_path = select_csv_location()
    if not csv_path:
        print("\n❌ No save location selected. Exiting.")
        return
    
    # Get file size
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"\n📁 Input: {os.path.basename(pdf_path)} ({file_size_mb:.1f} MB)")
    
    # Process PDF
    total_start = time.time()
    
    text_data = extract_text_from_pdf_fast(pdf_path)
    
    if not text_data:
        print("\n❌ Failed to extract text from PDF.")
        return
    
    records = extract_loan_data_fast(text_data)
    df = save_to_csv(records, csv_path)
    
    total_time = time.time() - total_start
    print(f"\n⏱️  Total processing time: {total_time:.1f} seconds")
    
    # Preview
    print("\n📋 Preview (first 3 records):")
    print(df.head(3).to_string())
    
    # Ask to open
    open_file = input("\n📂 Open CSV file? (y/n): ").strip().lower()
    if open_file == 'y':
        os.startfile(csv_path)
    
    print("\n✅ Done!")

# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    main()