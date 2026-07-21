import os
from PIL import Image
import glob
import tkinter as tk
from tkinter import filedialog

def select_images_gui():
    """Open file dialog to select multiple images"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    image_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp"),
            ("All files", "*.*")
        ]
    )
    root.destroy()
    return list(image_paths)

def select_folder_gui():
    """Open folder dialog to select directory"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(title="Select Folder Containing Images")
    root.destroy()
    return folder_path

def select_save_pdf_gui():
    """Open save dialog for PDF file"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    save_path = filedialog.asksaveasfilename(
        title="Save PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    root.destroy()
    return save_path

def get_images_and_output():
    """Get images and output path from user"""
    print("=" * 60)
    print("Image to PDF Converter")
    print("=" * 60)
    print("\nHow would you like to select images?")
    print("1. Select individual images (GUI)")
    print("2. Select folder containing images (GUI)")
    print("3. Enter folder path manually")
    print("4. Enter image paths manually (comma-separated)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    image_paths = []
    
    if choice == '1':
        image_paths = select_images_gui()
        if not image_paths:
            print("No images selected.")
            return None, None
            
    elif choice == '2':
        folder = select_folder_gui()
        if not folder:
            print("No folder selected.")
            return None, None
        
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.gif', '*.webp']
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(folder, ext)))
            image_paths.extend(glob.glob(os.path.join(folder, ext.upper())))
        
        if not image_paths:
            print(f"No images found in: {folder}")
            return None, None
        
        image_paths.sort()
        print(f"Found {len(image_paths)} images")
        
    elif choice == '3':
        folder = input("Enter folder path: ").strip()
        folder = folder.strip('"').strip("'")
        
        if not os.path.exists(folder):
            print(f"Folder not found: {folder}")
            return None, None
        
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.gif', '*.webp']
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(folder, ext)))
            image_paths.extend(glob.glob(os.path.join(folder, ext.upper())))
        
        if not image_paths:
            print(f"No images found in: {folder}")
            return None, None
        
        image_paths.sort()
        print(f"Found {len(image_paths)} images")
        
    elif choice == '4':
        paths_input = input("Enter image paths (comma-separated): ").strip()
        paths_list = [p.strip().strip('"').strip("'") for p in paths_input.split(',')]
        
        for path in paths_list:
            if os.path.exists(path):
                image_paths.append(path)
            else:
                print(f"Warning: File not found - {path}")
        
        if not image_paths:
            print("No valid image paths provided.")
            return None, None
    
    else:
        print("Invalid choice!")
        return None, None
    
    print("\nHow would you like to specify the output PDF location?")
    print("1. Browse to save location (GUI)")
    print("2. Enter path manually")
    
    save_choice = input("\nEnter choice (1 or 2): ").strip()
    
    if save_choice == '1':
        output_path = select_save_pdf_gui()
    else:
        output_path = input("Enter output PDF file path: ").strip()
        output_path = output_path.strip('"').strip("'")
        if not output_path.endswith('.pdf'):
            output_path += '.pdf'
    
    if not output_path:
        print("No output location specified.")
        return None, None
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    return image_paths, output_path

def images_to_pdf(image_paths, output_path):
    """Convert multiple images to a single PDF"""
    try:
        print(f"\nConverting {len(image_paths)} images to PDF...")
        images = []
        
        for i, img_path in enumerate(image_paths, 1):
            print(f"  Processing {i}/{len(image_paths)}: {os.path.basename(img_path)}")
            img = Image.open(img_path)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            images.append(img)
        
        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            print(f"\n✓ Successfully created PDF: {output_path}")
            
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  File size: {file_size:.2f} MB")
            return True
        else:
            print("No images to convert!")
            return False
            
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("Image to PDF Converter")
    print("=" * 60)
    
    image_paths, output_path = get_images_and_output()
    
    if not image_paths or not output_path:
        print("\nOperation cancelled.")
        return
    
    print("\n" + "-" * 40)
    print(f"Number of images: {len(image_paths)}")
    print(f"Output PDF: {output_path}")
    
    confirm = input("\nProceed with conversion? (y/n): ").strip().lower()
    
    if confirm == 'y':
        images_to_pdf(image_paths, output_path)
    else:
        print("Conversion cancelled.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()