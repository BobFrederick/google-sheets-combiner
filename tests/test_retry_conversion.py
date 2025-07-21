#!/usr/bin/env python3
"""
Test script to retry the failed Excel conversion
"""

import sys
sys.path.append('.')
from src.drive_converter import DriveFileConverter

def test_failed_conversion():
    """Test converting the file that failed"""
    
    # File that failed: 15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m
    failed_file_id = "15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m"
    
    print("🔄 Testing failed conversion...")
    print(f"File ID: {failed_file_id}")
    
    converter = DriveFileConverter()
    
    # Get file info
    file_info = converter.get_file_info(failed_file_id)
    if file_info:
        print(f"✅ File accessible: {file_info.get('name', 'Unknown')}")
        print(f"   MIME type: {file_info.get('mimeType', 'Unknown')}")
        
        if converter.is_excel_file(file_info):
            print("📋 File is Excel format - attempting conversion...")
            
            # Try conversion with different approach
            try:
                converted_id = converter.convert_excel_to_google_sheet(
                    file_id=failed_file_id,
                    original_name=file_info.get('name', 'Unknown'),
                    cleanup_original=False  # Don't delete original
                )
                
                if converted_id:
                    print(f"✅ Conversion successful!")
                    print(f"   New file ID: {converted_id}")
                    print(f"   New URL: https://docs.google.com/spreadsheets/d/{converted_id}/edit")
                    
                    # Update URLs file
                    return converted_id
                else:
                    print("❌ Conversion failed")
                    return None
                    
            except Exception as e:
                print(f"❌ Conversion error: {e}")
                return None
        else:
            print("❌ File is not Excel format")
            return None
    else:
        print("❌ Cannot access file")
        return None

if __name__ == "__main__":
    result = test_failed_conversion()
    if result:
        print(f"\n🎉 Success! Add this URL to your config/urls.txt:")
        print(f"https://docs.google.com/spreadsheets/d/{result}/edit")
    else:
        print("\n❌ Conversion failed. File may need manual conversion.")
