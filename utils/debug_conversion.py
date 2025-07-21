#!/usr/bin/env python3
"""
Debug conversion process step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drive_converter import DriveFileConverter
from config import Config

def debug_conversion():
    """Debug the conversion process step by step"""
    
    print("🔍 Debug: Testing conversion process...")
    
    # Get URLs
    sheet_urls = Config.get_sheet_urls()
    print(f"Found {len(sheet_urls)} URLs to test")
    
    # Initialize converter
    try:
        converter = DriveFileConverter()
        print("✅ Drive converter initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize converter: {e}")
        return
    
    # Test each URL
    for i, url in enumerate(sheet_urls, 1):
        print(f"\n--- Testing URL {i} ---")
        print(f"URL: {url}")
        
        # Extract file ID
        try:
            file_id = url.split('/d/')[1].split('/')[0]
            print(f"File ID: {file_id}")
        except Exception as e:
            print(f"❌ Failed to extract file ID: {e}")
            continue
        
        # Get file info
        print("Attempting to get file info...")
        file_info = converter.get_file_info(file_id)
        
        if file_info:
            print(f"✅ File found!")
            print(f"  Name: {file_info.get('name', 'Unknown')}")
            print(f"  MIME Type: {file_info.get('mimeType', 'Unknown')}")
            print(f"  Is Excel: {converter.is_excel_file(file_info)}")
            print(f"  Is Google Sheet: {converter.is_google_sheet(file_info)}")
            
            # Try conversion if it's Excel
            if converter.is_excel_file(file_info):
                print("  🔄 Attempting conversion...")
                try:
                    new_url, converted = converter.process_url(url, cleanup_originals=False)
                    if converted:
                        print(f"  ✅ Conversion successful: {new_url}")
                    else:
                        print(f"  ℹ️  No conversion needed: {new_url}")
                except Exception as e:
                    print(f"  ❌ Conversion failed: {e}")
            
        else:
            print("❌ File not accessible or not found")
    
    print("\n--- Debug Summary ---")
    print("If files are not accessible, it might be due to:")
    print("1. Insufficient Drive API permissions in your credentials")
    print("2. Files need to be explicitly shared with your email")
    print("3. Files are in a different sharing context")

if __name__ == "__main__":
    debug_conversion()
