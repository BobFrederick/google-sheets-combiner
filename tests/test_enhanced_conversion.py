#!/usr/bin/env python3
"""
Test script for enhanced Excel to Google Sheets conversion
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.drive_converter import DriveFileConverter

def test_enhanced_conversion():
    """Test the enhanced conversion capability"""
    
    print("🧪 Testing Enhanced Conversion System")
    print("=" * 50)
    
    # Initialize the converter
    try:
        converter = DriveFileConverter()
        print("✅ DriveFileConverter initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize DriveConverter: {e}")
        return False
    
    # Test with the problematic file ID
    problematic_file_id = "15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m"
    
    print(f"\n🔄 Testing conversion of problematic file: {problematic_file_id}")
    
    try:
        # Try to get file info first
        file_info = converter.drive_service.files().get(
            fileId=problematic_file_id,
            fields='id,name,size,mimeType',
            supportsAllDrives=True
        ).execute()
        
        print(f"📄 File info:")
        print(f"   Name: {file_info.get('name', 'Unknown')}")
        print(f"   Size: {int(file_info.get('size', 0)) / (1024*1024):.1f} MB")
        print(f"   MIME Type: {file_info.get('mimeType', 'Unknown')}")
        
        file_name = file_info.get('name', 'Unknown')
        
        # Try conversion
        result = converter.convert_excel_to_google_sheet(
            problematic_file_id, 
            file_name,
            cleanup_original=False  # Don't delete original for testing
        )
        
        if result:
            print(f"\n✅ Conversion successful!")
            print(f"🔗 New Google Sheet URL: https://docs.google.com/spreadsheets/d/{result}/edit")
            
            # Add to URLs file
            with open('config/urls.txt', 'a') as f:
                f.write(f"https://docs.google.com/spreadsheets/d/{result}/edit\n")
            print("📝 Added URL to config/urls.txt")
            
            return True
        else:
            print("❌ Conversion failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion test: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_conversion()
    
    if success:
        print("\n🎉 Enhanced conversion test PASSED!")
        print("The system can now handle large Excel files with binary data.")
    else:
        print("\n⚠️ Enhanced conversion test FAILED!")
        print("Check the error messages above for debugging information.")
