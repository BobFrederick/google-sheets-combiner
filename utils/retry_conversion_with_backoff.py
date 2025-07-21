#!/usr/bin/env python3
"""
Retry conversion with rate limit handling
"""
import sys
import os
import time

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.drive_converter import DriveFileConverter

def retry_conversion_with_backoff():
    """Retry failed conversion with exponential backoff for rate limits"""
    file_id = "15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m"
    file_name = "[1820 Tahoe] SHARED Work Progress List.xlsx"
    
    converter = DriveFileConverter()
    
    print(f"🔄 Retrying conversion with rate limit handling...")
    print(f"File: {file_name}")
    print(f"ID: {file_id}")
    
    # Wait for rate limit to reset
    print("⏳ Waiting 60 seconds for rate limit to reset...")
    time.sleep(60)
    
    # Retry with exponential backoff
    max_retries = 3
    base_delay = 30
    
    for attempt in range(max_retries):
        try:
            print(f"\n🔄 Attempt {attempt + 1}/{max_retries}")
            
            converted_id = converter.convert_excel_to_google_sheet(
                file_id=file_id,
                original_name=file_name,
                cleanup_original=False  # Don't delete original for safety
            )
            
            if converted_id:
                print(f"✅ SUCCESS! Conversion completed on attempt {attempt + 1}")
                print(f"   New Google Sheets ID: {converted_id}")
                print(f"   New URL: https://docs.google.com/spreadsheets/d/{converted_id}/edit")
                
                # Update the URLs file
                print("\n📝 Updating URLs file...")
                update_urls_file(converted_id)
                return converted_id
            else:
                print(f"❌ Attempt {attempt + 1} failed - no ID returned")
                
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"⏳ Rate limit hit. Waiting {delay} seconds before retry...")
                time.sleep(delay)
            elif attempt < max_retries - 1:
                print(f"⏳ Waiting {base_delay} seconds before retry...")
                time.sleep(base_delay)
    
    print("❌ All retry attempts failed")
    return None

def update_urls_file(new_id):
    """Update the URLs file with the successful conversion"""
    urls_file = "config/urls.txt"
    new_url = f"https://docs.google.com/spreadsheets/d/{new_id}/edit"
    
    try:
        # Read existing content
        with open(urls_file, 'r') as f:
            content = f.read()
        
        # Replace the failed conversion note with the actual URL
        updated_content = content.replace(
            "# Note: File 15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m failed conversion - need to retry or handle manually",
            new_url
        )
        
        # Write back
        with open(urls_file, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {urls_file} with new URL")
        
    except Exception as e:
        print(f"⚠️ Could not update URLs file: {e}")
        print(f"   Please manually add: {new_url}")

if __name__ == "__main__":
    retry_conversion_with_backoff()
