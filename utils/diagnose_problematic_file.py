#!/usr/bin/env python3
"""
Diagnose the problematic Excel file and provide alternative solutions
"""
import sys
import os
import time

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.drive_converter import DriveFileConverter
from googleapiclient.errors import HttpError


def diagnose_problematic_file():
    """Thoroughly diagnose the problematic file"""
    file_id = "15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m"
    
    converter = DriveFileConverter()
    
    print("🔍 COMPREHENSIVE DIAGNOSTIC")
    print("=" * 50)
    print(f"File ID: {file_id}")
    
    # Test 1: Basic file info
    print("\n📋 Test 1: Basic File Information")
    try:
        file_info = converter.drive_service.files().get(
            fileId=file_id,
            fields='id,name,mimeType,size,owners,createdTime,modifiedTime,'
                   'capabilities,driveId,teamDriveId',
            supportsAllDrives=True
        ).execute()
        
        print(f"✅ Name: {file_info.get('name', 'Unknown')}")
        print(f"✅ MIME Type: {file_info.get('mimeType', 'Unknown')}")
        print(f"✅ Size: {file_info.get('size', 'Unknown')} bytes")
        print(f"✅ Created: {file_info.get('createdTime', 'Unknown')}")
        print(f"✅ Modified: {file_info.get('modifiedTime', 'Unknown')}")
        print(f"✅ Drive ID: {file_info.get('driveId', 'My Drive')}")
        
        # Check capabilities
        capabilities = file_info.get('capabilities', {})
        print(f"✅ Can Copy: {capabilities.get('canCopy', False)}")
        print(f"✅ Can Download: {capabilities.get('canDownload', False)}")
        print(f"✅ Can Edit: {capabilities.get('canEdit', False)}")
        
    except Exception as e:
        print(f"❌ Failed to get basic info: {e}")
        return
    
    # Test 2: Download capability
    print("\n📥 Test 2: Download Test")
    try:
        content = converter.drive_service.files().get_media(
            fileId=file_id,
            supportsAllDrives=True
        ).execute()
        
        print(f"✅ Download successful: {len(content)} bytes")
        
        # Check if it's a valid Excel file
        if content[:2] == b'PK':  # ZIP signature (Excel files are ZIP)
            print("✅ File appears to be a valid ZIP/Excel format")
        else:
            print("⚠️ File doesn't have ZIP signature - may not be Excel")
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
    
    # Test 3: Alternative conversion methods
    print("\n🔄 Test 3: Alternative Conversion Methods")
    
    # Method 1: Try without supportsAllDrives
    print("   Method 1: Convert without Shared Drive flags")
    try:
        copied_file = converter.drive_service.files().copy(
            fileId=file_id,
            body={'name': '[1820 Tahoe] SHARED Work Progress List',
                  'mimeType': 'application/vnd.google-apps.spreadsheet'},
            fields='id,name,mimeType'
        ).execute()
        
        new_id = copied_file['id']
        print(f"✅ SUCCESS! Converted without Shared Drive flags")
        print(f"   New ID: {new_id}")
        print(f"   URL: https://docs.google.com/spreadsheets/d/{new_id}/edit")
        
        # Update URLs file
        update_urls_with_success(new_id)
        return new_id
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Try creating a copy first, then convert
    print("   Method 2: Copy to My Drive first, then convert")
    try:
        # First, copy to My Drive
        copied_file = converter.drive_service.files().copy(
            fileId=file_id,
            body={'name': '[1820 Tahoe] COPY - Work Progress List.xlsx'},
            fields='id,name,mimeType',
            supportsAllDrives=True
        ).execute()
        
        copy_id = copied_file['id']
        print(f"✅ Step 1: Created copy with ID: {copy_id}")
        
        # Wait a moment
        time.sleep(5)
        
        # Now try to convert the copy
        converted_file = converter.drive_service.files().copy(
            fileId=copy_id,
            body={'name': '[1820 Tahoe] SHARED Work Progress List',
                  'mimeType': 'application/vnd.google-apps.spreadsheet'},
            fields='id,name,mimeType'
        ).execute()
        
        new_id = converted_file['id']
        print(f"✅ SUCCESS! Converted via copy method")
        print(f"   New ID: {new_id}")
        print(f"   URL: https://docs.google.com/spreadsheets/d/{new_id}/edit")
        
        # Clean up the intermediate copy
        try:
            converter.drive_service.files().delete(fileId=copy_id).execute()
            print("✅ Cleaned up intermediate copy")
        except:
            print("⚠️ Could not clean up intermediate copy")
        
        # Update URLs file
        update_urls_with_success(new_id)
        return new_id
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # If all methods fail, provide manual instructions
    print("\n❌ ALL AUTOMATIC METHODS FAILED")
    print("📋 MANUAL CONVERSION REQUIRED")
    print("=" * 50)
    print("1. Open Google Drive in your web browser")
    print("2. Navigate to the file: [1820 Tahoe] SHARED Work Progress List.xlsx")
    print("3. Right-click → 'Open with' → 'Google Sheets'")
    print("4. Once open, go to File → Save as Google Sheets")
    print("5. Copy the new URL and add it to config/urls.txt")
    print("")
    print("Alternative:")
    print("1. Download the Excel file")
    print("2. Upload it to your own Google Drive")
    print("3. Convert it there")
    
    return None


def update_urls_with_success(new_id):
    """Update URLs file with successful conversion"""
    urls_file = "config/urls.txt"
    new_url = f"https://docs.google.com/spreadsheets/d/{new_id}/edit"
    
    try:
        with open(urls_file, 'r') as f:
            content = f.read()
        
        # Replace the note with the actual URL
        updated_content = content.replace(
            "# Note: File 15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m failed conversion"
            " - need to retry or handle manually",
            new_url
        )
        
        with open(urls_file, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {urls_file} with new URL")
        
    except Exception as e:
        print(f"⚠️ Could not update URLs file: {e}")
        print(f"   Please manually add: {new_url}")


if __name__ == "__main__":
    diagnose_problematic_file()
