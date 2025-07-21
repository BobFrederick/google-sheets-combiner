#!/usr/bin/env python3
"""
Manual cleanup script to remove converted Google Sheets after combination
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.drive_converter import DriveFileConverter
from src.config import Config

def cleanup_converted_sheets():
    """Clean up all converted Google Sheets"""
    
    print("🧹 Manual Cleanup of Converted Google Sheets")
    print("=" * 50)
    
    try:
        # Initialize the converter
        converter = DriveFileConverter()
        print("✅ DriveFileConverter initialized successfully")
        
        # Get URLs from config
        sheet_urls = Config.get_sheet_urls()
        if not sheet_urls:
            print("❌ No URLs found in config/urls.txt")
            return False
        
        print(f"📋 Found {len(sheet_urls)} URLs to check for cleanup")
        
        # Ask for confirmation
        print("\n⚠️ WARNING: This will delete the intermediate Google Sheets!")
        print("Your original Excel files will NOT be deleted.")
        response = input("Do you want to continue? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Cleanup cancelled")
            return False
        
        # Perform cleanup
        converter.cleanup_converted_sheets(
            sheet_urls, 
            keep_converted_sheets=False
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_converted_sheets()
    
    if success:
        print("\n🎉 Manual cleanup completed successfully!")
        print("Your Drive should now be clean of intermediate converted files.")
    else:
        print("\n⚠️ Manual cleanup failed or was cancelled.")
