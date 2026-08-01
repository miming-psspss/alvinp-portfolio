#!/usr/bin/env python3
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

def get_g2_value(df, sheet_name):
    """Extract G2 value from dataframe"""
    if len(df) > 1 and df.shape[1] > 6:
        val = df.iloc[1, 6]
        try:
            return float(val)
        except (ValueError, TypeError):
            return str(val) if pd.notna(val) else None
    return None

def determine_excel_engine(file_path):
    """Determine which Excel engine to use based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.xls':
        return 'xlrd'
    elif ext in ['.xlsx', '.xlsm']:
        return 'openpyxl'
    else:
        return None

def process_excel_file(file_path):
    """
    Process a single Excel file - extract G2 from sheet "12-29-25" only
    """
    try:
        # Get file info
        stats = os.stat(file_path)
        modified_date = datetime.fromtimestamp(stats.st_mtime)
        modified_year = modified_date.year
        
        # Determine engine
        engine = determine_excel_engine(file_path)
        if not engine:
            return None
        
        # Load Excel file
        excel_file = pd.ExcelFile(file_path, engine=engine)
        all_sheets = excel_file.sheet_names
        
        print(f"\n📁 File: {os.path.basename(file_path)}")
        print(f"   Sheets: {', '.join(all_sheets)}")
        
        # Initialize result
        result = {
            'ACCOUNT': os.path.basename(file_path),
            'sheet_12_29_25_exists': 'NO',
            'sheet_12_29_25_value': None,
            'file_modified_year': modified_year,
            'all_sheets': ', '.join(all_sheets)
        }
        
        # Check if 12-29-25 exists
        if '12-29-25' in all_sheets:
            result['sheet_12_29_25_exists'] = 'YES'
            print(f"   ✅ Found sheet: 12-29-25")
            
            # Read the sheet and extract G2
            df = pd.read_excel(file_path, sheet_name='12-29-25', engine=engine)
            value = get_g2_value(df, '12-29-25')
            
            if value is not None:
                result['sheet_12_29_25_value'] = value
                print(f"   ✅ G2 value: {value}")
            else:
                print(f"   ⚠️ Could not extract G2 value")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            'ACCOUNT': os.path.basename(file_path),
            'sheet_12_29_25_exists': 'ERROR',
            'sheet_12_29_25_value': None,
            'file_modified_year': 0,
            'all_sheets': 'ERROR'
        }

def main():
    print("\n" + "="*80)
    print("📊 EXCEL SHEET EXTRACTOR - 12-29-25 ONLY")
    print("="*80)
    print("\n📋 WHAT THIS DOES:")
    print("   • Scans Excel files in a folder")
    print("   • Looks for sheet named '12-29-25'")
    print("   • Extracts G2 value (row 2, column G)")
    print("   • No compounding, no calculations")
    print("   • Simple CSV output")
    
    # Ask for directory
    print("\n📁 Enter directory path (or press Enter for default):")
    default = "C:/Users/SAMCO/Desktop/SD/CLIENT SD QRTLY COMP 1"
    
    user_input = input("\n📝 Path: ").strip()
    
    if user_input == "":
        dir_path = default
        print(f"Using default: {dir_path}")
    else:
        dir_path = user_input.strip().strip('"').strip("'")
    
    dir_path = Path(dir_path)
    
    if not dir_path.exists():
        print(f"\n❌ Directory not found: {dir_path}")
        return
    
    # Find Excel files
    excel_files = []
    for ext in ['*.xlsx', '*.xls', '*.xlsm']:
        excel_files.extend(dir_path.glob(ext))
    
    if not excel_files:
        print(f"\n❌ No Excel files found")
        return
    
    print(f"\n📁 Found {len(excel_files)} Excel file(s)")
    
    # Ask how many to process
    print(f"\n📋 Options:")
    print(f"1. Process ALL files ({len(excel_files)})")
    print(f"2. Process first N files")
    
    choice = input("\nChoice (1-2, default 1): ").strip()
    
    files_to_process = excel_files
    if choice == "2":
        try:
            n = int(input("How many files? "))
            files_to_process = excel_files[:n]
        except:
            print("Invalid, processing all")
    
    # Process files
    print(f"\n📊 Processing {len(files_to_process)} file(s)...")
    
    all_results = []
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n[{i}/{len(files_to_process)}]", end="")
        result = process_excel_file(file_path)
        if result:
            all_results.append(result)
        
        # Progress indicator
        if i % 100 == 0:
            print(f"\n   Progress: {i}/{len(files_to_process)} files processed")
    
    # Create and save CSV
    if all_results:
        df = pd.DataFrame(all_results)
        
        # Define columns
        cols = ['ACCOUNT', 'sheet_12_29_25_exists', 'sheet_12_29_25_value', 
                'file_modified_year', 'all_sheets']
        
        # Keep only existing columns
        cols = [c for c in cols if c in df.columns]
        df = df[cols]
        
        # Save CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = dir_path / f"extract_12_29_25_{timestamp}.csv"
        df.to_csv(output, index=False)
        
        print(f"\n{'='*80}")
        print(f"✅ CSV saved to: {output}")
        print(f"{'='*80}")
        
        # Show summary
        print(f"\n📊 SUMMARY:")
        if 'sheet_12_29_25_exists' in df.columns:
            found = (df['sheet_12_29_25_exists'] == 'YES').sum()
            print(f"   • Files with 12-29-25 sheet: {found}/{len(df)}")
        
        if 'sheet_12_29_25_value' in df.columns:
            with_values = df['sheet_12_29_25_value'].notna().sum()
            print(f"   • Files with G2 values: {with_values}/{len(df)}")
        
        # Show sample
        print(f"\n📈 FIRST 10 RESULTS:")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df.head(10).to_string())
        
    else:
        print(f"\n❌ No files were successfully processed")

if __name__ == "__main__":
    # Check packages
    try:
        import pandas as pd
        import openpyxl
        import xlrd
    except ImportError as e:
        print(f"\n❌ Missing package: {e}")
        print("Run: pip install pandas openpyxl xlrd")
        sys.exit(1)
    
    main()