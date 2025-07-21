#!/usr/bin/env python3
"""
Alternative approach: Try to convert specific sheets/ranges that don't contain images
"""
import sys
import os

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.drive_converter import DriveFileConverter
from googleapiclient.errors import HttpError
import time


def selective_sheet_processing():
    """Try to work with the file by processing specific ranges without images"""
    file_id = "15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m"
    
    converter = DriveFileConverter()
    
    print("🎯 SELECTIVE PROCESSING APPROACH")
    print("=" * 50)
    print("Strategy: Try to access specific sheets/ranges that might not have images")
    
    # First, try to create a "clean" copy with a different name
    print("\n🔄 Method 1: Create a duplicate without conversion")
    try:
        # Just copy the file as-is (no conversion)
        copied_file = converter.drive_service.files().copy(
            fileId=file_id,
            body={
                'name': '[1820 Tahoe] DUPLICATE - No Images',
                # Keep original MIME type, don't convert yet
                'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            },
            fields='id,name,mimeType',
            supportsAllDrives=True
        ).execute()
        
        duplicate_id = copied_file['id']
        print(f"✅ Created duplicate: {duplicate_id}")
        
        # Wait a moment
        time.sleep(3)
        
        # Now try to convert the duplicate (sometimes this works better)
        print("🔄 Attempting conversion of duplicate...")
        converted_file = converter.drive_service.files().copy(
            fileId=duplicate_id,
            body={
                'name': '[1820 Tahoe] CONVERTED Work Progress List',
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            },
            fields='id,name,mimeType'
        ).execute()
        
        new_id = converted_file['id']
        new_url = f"https://docs.google.com/spreadsheets/d/{new_id}/edit"
        
        print(f"✅ SUCCESS! Conversion worked!")
        print(f"   New ID: {new_id}")
        print(f"   URL: {new_url}")
        
        # Clean up the intermediate duplicate
        try:
            converter.drive_service.files().delete(fileId=duplicate_id).execute()
            print("✅ Cleaned up duplicate")
        except:
            print("⚠️ Could not clean up duplicate")
        
        # Update URLs file
        update_urls_file(new_url)
        return new_id
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Try to download and re-upload in chunks
    print("\n🔄 Method 2: Download and chunk upload")
    try:
        print("📥 Downloading file...")
        content = converter.drive_service.files().get_media(
            fileId=file_id,
            supportsAllDrives=True
        ).execute()
        
        print(f"✅ Downloaded {len(content)} bytes")
        
        # Save locally temporarily
        temp_file = "temp_tahoe.xlsx"
        with open(temp_file, 'wb') as f:
            f.write(content)
        
        print("📤 Re-uploading to your Drive...")
        
        # Upload to your personal Drive (not shared drive)
        # This sometimes works better for conversion
        
        from googleapiclient.http import MediaFileUpload
        
        media = MediaFileUpload(temp_file, 
                               mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        uploaded_file = converter.drive_service.files().create(
            body={
                'name': '[1820 Tahoe] UPLOADED Work Progress List.xlsx'
            },
            media_body=media,
            fields='id,name'
        ).execute()
        
        uploaded_id = uploaded_file['id']
        print(f"✅ Uploaded to your Drive: {uploaded_id}")
        
        # Clean up temp file
        os.remove(temp_file)
        
        # Now try to convert this version
        time.sleep(5)
        print("🔄 Converting uploaded version...")
        
        converted_file = converter.drive_service.files().copy(
            fileId=uploaded_id,
            body={
                'name': '[1820 Tahoe] FINAL Work Progress List',
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            },
            fields='id,name,mimeType'
        ).execute()
        
        final_id = converted_file['id']
        final_url = f"https://docs.google.com/spreadsheets/d/{final_id}/edit"
        
        print(f"✅ SUCCESS! Final conversion worked!")
        print(f"   Final ID: {final_id}")
        print(f"   URL: {final_url}")
        
        # Clean up uploaded Excel version
        try:
            converter.drive_service.files().delete(fileId=uploaded_id).execute()
            print("✅ Cleaned up uploaded Excel file")
        except:
            print("⚠️ Could not clean up uploaded file")
        
        # Update URLs file
        update_urls_file(final_url)
        return final_id
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    print("\n❌ All methods failed")
    print("🔧 RECOMMENDATION:")
    print("The file is too complex for automatic conversion.")
    print("Manual conversion is the most reliable option:")
    print("1. Open the file in Google Drive web interface")
    print("2. Right-click → 'Open with' → 'Google Sheets'")
    print("3. This will convert it and handle the images properly")
    print("4. Copy the resulting URL")
    
    return None


def update_urls_file(new_url):
    """Update the URLs file with the successful conversion"""
    urls_file = "config/urls.txt"
    
    try:
        with open(urls_file, 'r') as f:
            content = f.read()
        
        # Add the new URL at the end
        updated_content = content + f"\n{new_url}"
        
        with open(urls_file, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Added URL to {urls_file}")
        
    except Exception as e:
        print(f"⚠️ Could not update URLs file: {e}")
        print(f"   Please manually add: {new_url}")


if __name__ == "__main__":
    selective_sheet_processing()
