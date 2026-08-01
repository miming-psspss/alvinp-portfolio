#!/usr/bin/env python3
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

def get_g2_value(df, sheet_name):
    """Extract G2 value from dataframe"""
    print(f"      🔍 Reading G2 from {sheet_name}:")
    
    if len(df) > 1 and df.shape[1] > 6:
        val = df.iloc[1, 6]
        print(f"         G2 value: {val}")
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    return None

def get_column_b_last(df, sheet_name):
    """Extract last value in Column B"""
    print(f"      🔍 Reading Column B from {sheet_name}:")
    
    if df.shape[1] >= 2:
        col_b = df.iloc[:, 1]
        non_null = col_b.dropna()
        if len(non_null) > 0:
            last_val = non_null.iloc[-1]
            print(f"         Last Column B: {last_val}")
            return last_val
    return None

def compound_to_target(start_value, start_quarter, all_quarters, target_quarter='12-29-25'):
    """
    Compound a value forward from start_quarter to target_quarter
    """
    if start_value is None:
        return None
    
    if start_quarter not in all_quarters:
        return start_value
    
    start_idx = all_quarters.index(start_quarter)
    target_idx = all_quarters.index(target_quarter)
    
    if start_idx >= target_idx:
        return start_value
    
    current = start_value
    rate = 0.0075  # 0.75%
    
    print(f"      🔄 Compounding from {start_quarter} ({start_value}) to {target_quarter}")
    
    for i in range(start_idx + 1, target_idx + 1):
        current_quarter = all_quarters[i]
        interest = current * rate
        compounded = current + interest
        print(f"         → {current_quarter}: {current:.4f} + {interest:.4f} = {compounded:.4f}")
        current = compounded
    
    return current

def determine_excel_engine(file_path):
    """Determine which Excel engine to use based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.xls':
        return 'xlrd'
    elif ext == '.xlsx':
        return 'openpyxl'
    elif ext == '.xlsm':
        return 'openpyxl'
    else:
        return None

def process_excel_file(file_path, target_year=2025):
    """
    Process a single Excel file:
    - Special sheets: 3-31-26 (Column B), 12-29-25 (G2)
    - Other sheets: Use the FIRST sheet in the file (not the last)
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
        try:
            excel_file = pd.ExcelFile(file_path, engine=engine)
            all_sheets = excel_file.sheet_names
        except:
            try:
                if engine == 'xlrd':
                    excel_file = pd.ExcelFile(file_path, engine='openpyxl')
                else:
                    excel_file = pd.ExcelFile(file_path, engine='xlrd')
                all_sheets = excel_file.sheet_names
            except:
                print(f"   ❌ Cannot read file")
                return None
        
        total_sheets = len(all_sheets)
        
        print(f"\n{'='*60}")
        print(f"📁 File: {os.path.basename(file_path)}")
        print(f"   Sheets: {', '.join(all_sheets)}")
        
        # Quarter order for compounding
        quarters = [
            '6-29-22', '9-28-22', '12-29-22', '3-31-23',
            '6-29-23', '9-28-23', '12-29-23', '3-31-24',
            '6-29-24', '9-28-24', '12-29-24', '3-31-25',
            '6-29-25', '9-28-25', '12-29-25', '3-31-26'
        ]
        
        # Initialize result
        result = {
            'ACCOUNT': os.path.basename(file_path),
            'sheet_used': None,
            'total_sheets': total_sheets,
            'file_modified_year': modified_year,
            'edited_in_target_year': 'YES' if modified_year == target_year else 'NO',
            'TOTAL SAVINGS': None,
            'extraction_method': None,
            'raw_value': None,
            'start_quarter': None,
            'all_sheets_found': ', '.join(all_sheets)
        }
        
        # Check for SPECIAL SHEETS first (these take priority)
        print(f"\n   🔍 Checking for special sheets...")
        
        # Check if 3-31-26 exists
        if '3-31-26' in all_sheets:
            print(f"   ✅ Found special sheet: 3-31-26")
            df = pd.read_excel(file_path, sheet_name='3-31-26', engine=engine)
            value = get_column_b_last(df, '3-31-26')
            if value is not None:
                result['sheet_used'] = '3-31-26'
                result['raw_value'] = value
                result['TOTAL SAVINGS'] = value
                result['extraction_method'] = 'Column B (direct)'
                result['start_quarter'] = '3-31-26'
                print(f"   ✅ Using 3-31-26 Column B: {value}")
                return result
        
        # Check if 12-29-25 exists
        if '12-29-25' in all_sheets:
            print(f"   ✅ Found special sheet: 12-29-25")
            df = pd.read_excel(file_path, sheet_name='12-29-25', engine=engine)
            value = get_g2_value(df, '12-29-25')
            if value is not None:
                result['sheet_used'] = '12-29-25'
                result['raw_value'] = value
                result['TOTAL SAVINGS'] = value
                result['extraction_method'] = 'G2 (direct)'
                result['start_quarter'] = '12-29-25'
                print(f"   ✅ Using 12-29-25 G2: {value}")
                return result
        
        # No special sheets found - use the FIRST sheet in the file
        print(f"\n   🔍 No special sheets found, using FIRST sheet...")
        
        if all_sheets:
            first_sheet = all_sheets[0]  # Take the FIRST sheet, not the last
            print(f"   📍 First sheet: '{first_sheet}'")
            
            df = pd.read_excel(file_path, sheet_name=first_sheet, engine=engine)
            value = get_g2_value(df, first_sheet)
            
            if value is not None:
                result['sheet_used'] = first_sheet
                result['raw_value'] = value
                
                # Check if this sheet is in quarter list for compounding
                if first_sheet in quarters:
                    print(f"   🔄 Sheet is in quarter list, compounding...")
                    compounded = compound_to_target(value, first_sheet, quarters, '12-29-25')
                    result['TOTAL SAVINGS'] = compounded
                    result['extraction_method'] = f'Compounded from {first_sheet}'
                    result['start_quarter'] = first_sheet
                    print(f"   ✅ Final: {value} → {compounded:.4f}")
                else:
                    print(f"   ⚠️ Not in quarter list, using raw value")
                    result['TOTAL SAVINGS'] = value
                    result['extraction_method'] = f'Raw from {first_sheet}'
                    result['start_quarter'] = first_sheet
            else:
                print(f"   ⚠️ No G2 value found in first sheet")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            'ACCOUNT': os.path.basename(file_path),
            'sheet_used': 'ERROR',
            'total_sheets': 0,
            'file_modified_year': 0,
            'edited_in_target_year': 'NO',
            'TOTAL SAVINGS': None,
            'extraction_method': f'ERROR: {str(e)}',
            'raw_value': None,
            'start_quarter': None,
            'all_sheets_found': 'ERROR'
        }

def main():
    print("\n" + "="*80)
    print("📊 EXCEL SHEET COMPOUNDING CALCULATOR")
    print("="*80)
    print("\n📋 PROCESSING ORDER:")
    print("   1. Check for special sheet: 3-31-26 (use Column B)")
    print("   2. Check for special sheet: 12-29-25 (use G2)")
    print("   3. If no special sheets, use the FIRST sheet in the file")
    print("   4. If first sheet is a quarter, compound to 12-29-25")
    print("   5. If not a quarter, use raw G2 value")
    
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
    
    # Process first 3 files for verification
    print(f"\n📊 Processing first 3 files for verification...")
    
    all_results = []
    for i, file_path in enumerate(excel_files[:3], 1):
        print(f"\n{'='*60}")
        print(f"FILE {i}/3")
        print(f"{'='*60}")
        result = process_excel_file(file_path)
        if result:
            all_results.append(result)
    
    # Show results
    if all_results:
        print(f"\n{'='*80}")
        print("📊 VERIFICATION RESULTS")
        print('='*80)
        
        for result in all_results:
            print(f"\n📄 {result['ACCOUNT']}:")
            print(f"   Sheet used: {result['sheet_used']}")
            print(f"   Raw value: {result['raw_value']}")
            print(f"   TOTAL SAVINGS: {result['TOTAL SAVINGS']}")
            print(f"   Method: {result['extraction_method']}")
    
    # Ask to process all
    print(f"\n📋 Process all {len(excel_files)} files?")
    choice = input("(y/n, default n): ").strip().lower()
    
    if choice == 'y':
        print(f"\n📊 Processing all files...")
        
        all_results = []
        for i, file_path in enumerate(excel_files, 1):
            print(f"\n[{i}/{len(excel_files)}]", end="")
            result = process_excel_file(file_path)
            if result:
                all_results.append(result)
        
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Define columns
            cols = ['ACCOUNT', 'sheet_used', 'total_sheets', 
                    'file_modified_year', 'edited_in_target_year', 
                    'TOTAL SAVINGS', 'raw_value', 'start_quarter',
                    'extraction_method', 'all_sheets_found']
            
            cols = [c for c in cols if c in df.columns]
            df = df[cols]
            
            # Save
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = dir_path / f"compounding_results_{timestamp}.csv"
            df.to_csv(output, index=False)
            
            print(f"\n✅ CSV saved to: {output}")
            
            # Show summary
            print(f"\n📊 SUMMARY:")
            if 'extraction_method' in df.columns:
                summary = df['extraction_method'].value_counts()
                for method, count in summary.items():
                    print(f"   • {method}: {count} file(s)")

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