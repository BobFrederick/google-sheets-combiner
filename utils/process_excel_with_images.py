#!/usr/bin/env python3
"""
Download and process Excel file locally, skipping image columns
"""
import sys
import os
import pandas as pd
import io

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.drive_converter import DriveFileConverter


def process_excel_with_images():
    """Download Excel file and process it locally, excluding image columns"""
    file_id = "15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m"
    file_name = "[1820 Tahoe] SHARED Work Progress List.xlsx"
    
    converter = DriveFileConverter()
    
    print(f"🔍 Processing Excel file with image data...")
    print(f"File: {file_name}")
    print(f"Strategy: Download → Process locally → Skip image columns")
    
    try:
        # Download the file content
        print("\n📥 Downloading Excel file...")
        content = converter.drive_service.files().get_media(
            fileId=file_id,
            supportsAllDrives=True
        ).execute()
        
        print(f"✅ Downloaded {len(content)} bytes")
        
        # Load into pandas, handling potential issues
        print("\n📊 Processing Excel sheets...")
        file_buffer = io.BytesIO(content)
        
        # Get all sheet names first
        excel_file = pd.ExcelFile(file_buffer)
        sheet_names = excel_file.sheet_names
        print(f"Found {len(sheet_names)} sheets: {sheet_names}")
        
        # Process each sheet
        processed_data = {}
        
        for sheet_name in sheet_names:
            print(f"\n🔄 Processing sheet: {sheet_name}")
            
            try:
                # Read the sheet
                df = pd.read_excel(file_buffer, sheet_name=sheet_name)
                
                print(f"   Original: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Identify and remove image columns
                image_columns = []
                columns_to_drop = []
                
                for col in df.columns:
                    # Check if column contains binary data or is named like an image column
                    if (str(col).lower() in ['photos', 'photo', 'image', 'images', 'picture', 'pictures'] or
                        str(col).lower().startswith('photo') or
                        col == 'L'):  # Specific column mentioned
                        
                        image_columns.append(col)
                        columns_to_drop.append(col)
                        continue
                    
                    # Check if column contains mostly binary/non-text data
                    try:
                        sample_data = df[col].dropna().head(10)
                        if len(sample_data) > 0:
                            # Check if data looks like binary
                            for value in sample_data:
                                if isinstance(value, bytes) or (
                                    isinstance(value, str) and 
                                    len(value) > 1000 and
                                    any(ord(c) > 127 for c in value[:100] if isinstance(c, str))
                                ):
                                    image_columns.append(col)
                                    columns_to_drop.append(col)
                                    break
                    except:
                        # If we can't analyze the column, it might be problematic
                        print(f"   ⚠️ Skipping problematic column: {col}")
                        columns_to_drop.append(col)
                
                # Drop image/binary columns
                if columns_to_drop:
                    print(f"   🗑️ Removing image/binary columns: {columns_to_drop}")
                    df = df.drop(columns=columns_to_drop)
                
                print(f"   Cleaned: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Store the cleaned data
                sheet_key = f"{file_name.replace('.xlsx', '')} - {sheet_name}"
                processed_data[sheet_key] = df
                
            except Exception as e:
                print(f"   ❌ Failed to process sheet {sheet_name}: {e}")
                continue
        
        if processed_data:
            print(f"\n✅ Successfully processed {len(processed_data)} sheets")
            
            # Save as individual CSV files for inspection
            output_dir = "output/tahoe_processed"
            os.makedirs(output_dir, exist_ok=True)
            
            for sheet_name, df in processed_data.items():
                csv_path = os.path.join(output_dir, f"{sheet_name.replace(' ', '_')}.csv")
                df.to_csv(csv_path, index=False)
                print(f"   📄 Saved: {csv_path}")
            
            # Also return the data for further processing
            return processed_data
        else:
            print("❌ No sheets could be processed")
            return None
            
    except Exception as e:
        print(f"❌ Failed to process file: {e}")
        return None


def upload_to_google_sheets(processed_data):
    """Upload the processed data to Google Sheets"""
    if not processed_data:
        return None
    
    converter = DriveFileConverter()
    
    print("\n🔄 Creating Google Sheets from processed data...")
    
    try:
        # For now, let's create CSV files that can be manually uploaded
        # In a future version, we could use the Sheets API to create sheets directly
        
        print("✅ Processed data is ready for manual upload")
        print("\nNext steps:")
        print("1. Check the CSV files in output/tahoe_processed/")
        print("2. Create a new Google Sheet")
        print("3. Import each CSV as a separate tab")
        print("4. Add the new Google Sheets URL to config/urls.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to upload: {e}")
        return None


if __name__ == "__main__":
    processed_data = process_excel_with_images()
    if processed_data:
        upload_to_google_sheets(processed_data)
