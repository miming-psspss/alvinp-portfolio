"""
PDF Extractor Diagnostic Tool
Run this to check what's preventing text extraction
"""

import os
import sys

print("="*60)
print("PDF EXTRACTOR DIAGNOSTIC TOOL")
print("="*60)

# Check 1: PDF file exists
print("\n[1] Checking PDF file...")
pdf_path = r'C:\Path\To\Your\Combined_Ledgers.pdf'  # update to your PDF's location
if os.path.exists(pdf_path):
    print(f"   ✓ PDF found: {pdf_path}")
    print(f"   File size: {os.path.getsize(pdf_path):,} bytes")
else:
    print(f"   ✗ PDF NOT found at: {pdf_path}")
    print("   Please update the PDF path")

# Check 2: Python packages
print("\n[2] Checking Python packages...")
packages = {
    'pandas': 'pd',
    'pdf2image': 'pdf2image',
    'pytesseract': 'pytesseract',
    'PIL': 'PIL'
}

for package, import_name in packages.items():
    try:
        __import__(import_name)
        print(f"   ✓ {package} installed")
    except ImportError:
        print(f"   ✗ {package} NOT installed")

# Check 3: Tesseract OCR
print("\n[3] Checking Tesseract OCR...")
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
]

tesseract_found = False
for path in tesseract_paths:
    if os.path.exists(path):
        print(f"   ✓ Tesseract found at: {path}")
        tesseract_found = True
        break

if not tesseract_found:
    print("   ✗ Tesseract NOT found in common locations")
    print("\n   To install Tesseract:")
    print("   1. Go to: https://github.com/UB-Mannheim/tesseract/releases")
    print("   2. Download: tesseract-ocr-w64-setup-5.3.3.20231005.exe")
    print("   3. Run installer as Administrator")
    print("   4. IMPORTANT: Check 'Add to PATH' during installation")
    print("   5. Restart your computer")

# Check 4: Poppler (for pdf2image)
print("\n[4] Checking Poppler...")
try:
    from pdf2image import convert_from_path
    # Try a simple test - this will fail if poppler is missing
    print("   Testing pdf2image...")
    # Don't actually convert, just check if poppler is available
    print("   ✓ pdf2image module loaded")
    print("   ⚠ Note: Poppler needs to be installed separately")
except Exception as e:
    print(f"   ✗ Issue with pdf2image: {str(e)[:100]}")

# Check 5: Try direct text extraction (if PDF has selectable text)
print("\n[5] Trying direct text extraction (no OCR)...")
try:
    import PyPDF2
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        if len(reader.pages) > 0:
            first_page = reader.pages[0]
            text = first_page.extract_text()
            if text and len(text.strip()) > 50:
                print(f"   ✓ PDF has selectable text! Found {len(text)} characters")
                print(f"   Sample: {text[:200]}...")
                print("\n   💡 TIP: Your PDF has selectable text! You don't need OCR.")
                print("   Use the alternative script below that uses PyPDF2 instead.")
            else:
                print("   ✗ PDF appears to be scanned images (no selectable text)")
                print("   OCR is required for this PDF")
except ImportError:
    print("   PyPDF2 not installed (optional for testing)")
except Exception as e:
    print(f"   Could not read PDF: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
input("\nPress Enter to exit...")