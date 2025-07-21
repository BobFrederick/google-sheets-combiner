import os
import re
import time
import io
import pandas as pd
from typing import List, Dict, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from .config import Config
from .rate_limiter import quota_aware_api_call
from .quota_monitor import quota_monitor


class DriveFileConverter:
    def __init__(self):
        self.drive_service = None
        self.sheets_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive and Sheets APIs"""
        required_scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        
        # Check if we have all required scopes
        missing_scopes = []
        for scope in required_scopes:
            if scope not in Config.SCOPES:
                missing_scopes.append(scope)
        
        if missing_scopes:
            print("⚠️ Missing required scopes:")
            for scope in missing_scopes:
                print(f"  - {scope}")
            print("Please update Config.SCOPES and delete token.json to re-authenticate")
            # Don't return here - continue with current scopes for now
            print("Continuing with available scopes...")
        
        creds = None
        
        # Check if token file exists
        if os.path.exists(Config.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(
                Config.TOKEN_FILE, Config.SCOPES
            )
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.CREDENTIALS_FILE, Config.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(Config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.sheets_service = build('sheets', 'v4', credentials=creds)
    
    def extract_file_id(self, url: str) -> str:
        """Extract Google Drive file ID from various URL formats"""
        # Debug print
        print(f"Extracting file ID from URL: {url}")
        
        # Remove any trailing parameters and get the base URL
        base_url = url.split('?')[0]
        
        # Remove trailing slashes
        base_url = base_url.rstrip('/')
        
        # Handle Excel export URLs
        if '/export' in base_url:
            base_url = base_url.split('/export')[0]
        
        # Extract ID using the last component after /d/
        if '/d/' in base_url:
            file_id = base_url.split('/d/')[1].split('/')[0]
            print(f"Extracted file ID: {file_id}")
            return file_id
            
        # Handle spreadsheets direct URLs
        if '/spreadsheets/d/' in base_url:
            file_id = base_url.split('/spreadsheets/d/')[1].split('/')[0]
            print(f"Extracted file ID: {file_id}")
            return file_id
        
        raise ValueError(f"Could not extract file ID from URL: {url}")

    @quota_aware_api_call(api_type="drive", operation_type="read")
    def get_file_info(self, file_id: str) -> Dict:
        """Get file information from Google Drive"""
        try:
            # Debug print
            print(f"Requesting file info for ID: {file_id}")
            
            # Try Drive API first to get the actual file type
            try:
                file_info = self.drive_service.files().get(
                    fileId=file_id,
                    fields='id,name,mimeType,parents,createdTime,capabilities,'
                           'driveId',
                    supportsAllDrives=True
                ).execute()
                
                file_name = file_info.get('name', 'Unknown')
                print(f"✅ Accessed via Drive API: {file_name}")
                print(f"   MIME type: {file_info.get('mimeType', 'Unknown')}")
                return file_info
                
            except HttpError as drive_error:
                print(f"Drive API failed: {drive_error}")
                
                # Try Sheets API as fallback (for already converted files)
                try:
                    sheets_info = self.sheets_service.spreadsheets().get(
                        spreadsheetId=file_id,
                        fields='spreadsheetId,properties'
                    ).execute()
                    
                    print(f"✅ Accessed via Sheets API: {sheets_info.get('properties', {}).get('title', 'Unknown')}")
                    # Create a mock file_info compatible with our code
                    return {
                        'id': file_id,
                        'name': sheets_info.get('properties', {}).get('title', 'Unknown'),
                        'mimeType': 'application/vnd.google-apps.spreadsheet',
                        'parents': [],
                        'createdTime': '',
                        'capabilities': {}
                    }
                except HttpError as sheets_error:
                    print(f"Sheets API also failed: {sheets_error}")
                    
                    # Both APIs failed
                    print("⚠️ Neither Sheets nor Drive API could access the file")
                    print("This suggests:")
                    print("  1. The file may not exist or be accessible")
                    print("  2. The file may be in a format that's not supported")
                    print("  3. There may be permission issues")
                    return {}
            
        except Exception as error:
            print(f"Unexpected error getting file info for {file_id}: {error}")
            return {}
    
    def is_excel_file(self, file_info: Dict) -> bool:
        """Check if file is an Excel file"""
        excel_mime_types = [
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
        return file_info.get('mimeType', '') in excel_mime_types
    
    def is_google_sheet(self, file_info: Dict) -> bool:
        """Check if file is a native Google Sheet"""
        return file_info.get('mimeType', '') == \
            'application/vnd.google-apps.spreadsheet'
    
    @quota_aware_api_call(api_type="drive", operation_type="query")
    def find_existing_conversion(self, original_name: str, 
                               parent_folder: str = None) -> Optional[str]:
        """Find existing Google Sheet conversion of an Excel file"""
        # Search for files with similar name and Google Sheets MIME type
        query_parts = [
            f"name contains '{original_name.replace('.xlsx', '')}'",
            "mimeType='application/vnd.google-apps.spreadsheet'",
            "trashed=false"
        ]
        
        if parent_folder:
            query_parts.append(f"'{parent_folder}' in parents")
        
        query = " and ".join(query_parts)
        
        try:
            results = self.drive_service.files().list(
                q=query,
                fields="files(id,name,createdTime)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            if files:
                # Return the most recently created one
                files.sort(key=lambda x: x.get('createdTime', ''), reverse=True)
                return files[0]['id']
        except HttpError as error:
            print(f"Error searching for existing conversion: {error}")
        
        return None
    
    @quota_aware_api_call(api_type="drive", operation_type="convert")
    def convert_excel_to_google_sheet(self, file_id: str, 
                                    original_name: str,
                                    cleanup_original: bool = True) -> \
                                        Optional[str]:
        """Convert Excel file to Google Sheet using Drive API v3 with enhanced error handling"""
        try:
            print(f"Converting {original_name} to Google Sheets...")
            
            # First, try the standard conversion
            converted_id = self._try_standard_conversion(file_id, original_name)
            if converted_id:
                if cleanup_original:
                    self._cleanup_original_file(file_id, original_name)
                return converted_id
            
            # If standard conversion fails, try enhanced processing for large files
            print("🔄 Standard conversion failed, trying enhanced processing...")
            converted_id = self._try_enhanced_conversion(file_id, original_name)
            if converted_id:
                if cleanup_original:
                    self._cleanup_original_file(file_id, original_name)
                return converted_id
            
            return None
            
        except Exception as error:
            print(f"Unexpected error in conversion: {error}")
            return None
            
        except HttpError as error:
            print(f"Error converting Excel file to Google Sheets: {error}")
            
            # Check for rate limit errors
            if "rate limit" in str(error).lower() or "quota" in str(error).lower():
                print("⚠️ RATE LIMIT ERROR - Too many API requests")
                print("   Solutions:")
                print("   1. Wait 5-10 minutes and try again")
                print("   2. Use the retry script: python utils/retry_conversion_with_backoff.py")
                print("   3. Convert manually in Google Drive web interface")
            else:
                print("This might happen if:")
            print("  1. The file is not actually an Excel file")
            print("  2. The file is corrupted")
            print("  3. You don't have permission to create files in Drive")
            return None
    
    def process_url(self, url: str, cleanup_originals: bool = True) -> \
                        Tuple[str, bool]:
        """
        Process a URL - convert if needed, return Google Sheets URL
        Returns: (new_url, was_converted)
        """
        try:
            file_id = self.extract_file_id(url)
            file_info = self.get_file_info(file_id)
            
            if not file_info:
                print(f"Could not get file info for {url}")
                print("⚠️ Skipping conversion - assuming it's already a Google Sheet")
                return url, False
            
            file_name = file_info.get('name', 'Unknown')
            
            # If it's already a Google Sheet, return as-is
            if self.is_google_sheet(file_info):
                print(f"✓ {file_name} is already a Google Sheet")
                return url, False
            
            # If it's an Excel file, convert it
            if self.is_excel_file(file_info):
                print(f"📋 Found Excel file: {file_name}")
                
                # Check if conversion already exists
                parent_folder = file_info.get('parents', [None])[0]
                existing_id = self.find_existing_conversion(
                    file_name, parent_folder
                )
                
                if existing_id and not cleanup_originals:
                    print(f"✓ Using existing conversion: {existing_id}")
                    new_url = f"https://docs.google.com/spreadsheets/d/" \
                             f"{existing_id}/edit"
                    return new_url, False
                
                # Convert the file
                new_file_id = self.convert_excel_to_google_sheet(
                    file_id, file_name, cleanup_originals
                )
                
                if new_file_id:
                    new_url = f"https://docs.google.com/spreadsheets/d/" \
                             f"{new_file_id}/edit"
                    return new_url, True
                else:
                    print(f"✗ Conversion failed for {file_name}")
                    return url, False
            
            else:
                print(f"⚠️  {file_name} is not an Excel file or Google Sheet")
                return url, False
                
        except Exception as e:
            print(f"Error processing {url}: {e}")
            print("⚠️ Assuming it's already a Google Sheet and continuing...")
            return url, False
    
    def convert_all_urls(self, urls: List[str], 
                        cleanup_originals: bool = True) -> List[str]:
        """Convert all URLs, handling Excel files automatically"""
        converted_urls = []
        conversion_count = 0
        
        print("🔄 Processing URLs for conversion...")
        print("-" * 50)
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url[:60]}...")
            
            new_url, was_converted = self.process_url(url, cleanup_originals)
            converted_urls.append(new_url)
            
            if was_converted:
                conversion_count += 1
            
            # Rate limiting
            time.sleep(1)
        
        print(f"\n✅ Conversion complete!")
        print(f"   Converted: {conversion_count} files")
        print(f"   Total URLs: {len(converted_urls)}")
        print("-" * 50)
        
        return converted_urls
    
    def _try_standard_conversion(self, file_id: str, original_name: str) -> Optional[str]:
        """Try standard Google Drive API conversion"""
        try:
            # Create metadata for the new Google Sheets file
            copy_metadata = {
                'name': f"{original_name.replace('.xlsx', '').replace('.xls', '')}",
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
            
            # Use the copy method to convert Excel to Google Sheets
            copied_file = self.drive_service.files().copy(
                fileId=file_id,
                body=copy_metadata,
                fields='id,name,mimeType',
                supportsAllDrives=True
            ).execute()
            
            new_file_id = copied_file['id']
            new_file_name = copied_file.get('name', 'Unknown')
            print(f"✓ Standard conversion successful: {new_file_name}")
            print(f"   New file ID: {new_file_id}")
            
            return new_file_id
            
        except HttpError as error:
            print(f"Standard conversion failed: {error}")
            
            # Check for specific error types
            if "rate limit" in str(error).lower() or "quota" in str(error).lower():
                print("⚠️ RATE LIMIT ERROR - Too many API requests")
                return None
            elif "internal" in str(error).lower() or "500" in str(error):
                print("⚠️ INTERNAL ERROR - File may be too large or complex")
                return None
            else:
                print("⚠️ Other conversion error")
                return None
    
    def _try_enhanced_conversion(self, file_id: str, original_name: str) -> Optional[str]:
        """Enhanced conversion for large files with binary data"""
        try:
            print("📥 Downloading Excel file for local processing...")
            
            # Download the file
            content = self.drive_service.files().get_media(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            
            file_size_mb = len(content) / (1024 * 1024)
            print(f"✅ Downloaded {file_size_mb:.1f} MB")
            
            # Process the Excel file locally
            processed_sheets = self._process_excel_locally(content, original_name)
            
            if not processed_sheets:
                print("❌ Failed to process Excel file locally")
                return None
            
            # Create a new Google Sheet and upload the processed data
            return self._create_google_sheet_from_data(processed_sheets, original_name)
            
        except Exception as error:
            print(f"Enhanced conversion failed: {error}")
            return None
    
    def _process_excel_locally(self, content: bytes, file_name: str) -> Optional[Dict]:
        """Process Excel file locally, removing binary/image columns"""
        try:
            print("📊 Processing Excel sheets locally...")
            file_buffer = io.BytesIO(content)
            
            # Get all sheet names
            excel_file = pd.ExcelFile(file_buffer)
            sheet_names = excel_file.sheet_names
            print(f"Found {len(sheet_names)} sheets: {sheet_names}")
            
            processed_data = {}
            
            for sheet_name in sheet_names:
                print(f"   🔄 Processing: {sheet_name}")
                
                try:
                    # Read the sheet
                    df = pd.read_excel(file_buffer, sheet_name=sheet_name)
                    print(f"      Original: {df.shape[0]} rows, {df.shape[1]} columns")
                    
                    # Remove problematic columns
                    cleaned_df = self._clean_dataframe(df)
                    print(f"      Cleaned: {cleaned_df.shape[0]} rows, {cleaned_df.shape[1]} columns")
                    
                    processed_data[sheet_name] = cleaned_df
                    
                except Exception as e:
                    print(f"      ❌ Failed to process {sheet_name}: {e}")
                    continue
            
            return processed_data if processed_data else None
            
        except Exception as error:
            print(f"Failed to process Excel locally: {error}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove columns with binary data or images"""
        columns_to_drop = []
        
        for col in df.columns:
            # Check column name for image-related keywords
            col_str = str(col).lower()
            if (col_str in ['photos', 'photo', 'image', 'images', 'picture', 'pictures'] or
                col_str.startswith('photo') or
                col == 'L'):  # Specific problematic column
                
                columns_to_drop.append(col)
                continue
            
            # Check for binary data in the column
            try:
                sample_data = df[col].dropna().head(5)
                for value in sample_data:
                    if isinstance(value, bytes):
                        columns_to_drop.append(col)
                        break
                    elif isinstance(value, str) and len(value) > 1000:
                        # Check if it contains non-printable characters (likely binary)
                        if any(ord(c) > 127 for c in value[:100]):
                            columns_to_drop.append(col)
                            break
            except:
                # If we can't analyze the column, it's safer to drop it
                columns_to_drop.append(col)
        
        # Drop problematic columns
        if columns_to_drop:
            print(f"         🗑️ Removing columns: {columns_to_drop}")
            df = df.drop(columns=columns_to_drop)
        
        return df
    
    @quota_aware_api_call(api_type="drive", operation_type="delete")
    def _cleanup_original_file(self, file_id: str, original_name: str):
        """Clean up the original Excel file"""
        try:
            self.drive_service.files().delete(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            print(f"✓ Cleaned up original Excel file: {original_name}")
        except HttpError as e:
            print(f"Warning: Could not delete original file: {e}")
    
    @quota_aware_api_call(api_type="sheets", operation_type="create")
    def _create_google_sheet_from_data(self, processed_sheets: Dict, 
                                     original_name: str) -> Optional[str]:
        """Create a new Google Sheet and populate it with processed data"""
        try:
            print("📝 Creating new Google Sheet...")
            
            # Create a new Google Sheet
            sheet_name = f"{original_name.replace('.xlsx', '').replace('.xls', '')}_processed"
            spreadsheet_body = {
                'properties': {
                    'title': sheet_name
                }
            }
            
            sheet = self.sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = sheet['spreadsheetId']
            print(f"✓ Created Google Sheet: {sheet_name}")
            print(f"   Spreadsheet ID: {spreadsheet_id}")
            
            # Clear the default sheet and add our sheets
            sheet_requests = []
            
            # First, rename the default sheet to our first sheet
            sheet_names = list(processed_sheets.keys())
            if sheet_names:
                first_sheet_name = sheet_names[0]
                sheet_requests.append({
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': 0,
                            'title': first_sheet_name
                        },
                        'fields': 'title'
                    }
                })
                
                # Add additional sheets for remaining data
                for i, sheet_name in enumerate(sheet_names[1:], 1):
                    sheet_requests.append({
                        'addSheet': {
                            'properties': {
                                'title': sheet_name
                            }
                        }
                    })
            
            # Execute sheet creation requests
            if sheet_requests:
                self.sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={'requests': sheet_requests}
                ).execute()
            
            # Now populate each sheet with data
            for sheet_name, df in processed_sheets.items():
                try:
                    print(f"   📊 Uploading data to sheet: {sheet_name}")
                    
                    # Convert DataFrame to values
                    values = [df.columns.tolist()]  # Header row
                    values.extend(df.fillna('').astype(str).values.tolist())
                    
                    # Update the sheet
                    range_name = f"'{sheet_name}'!A1"
                    value_input_option = 'RAW'
                    
                    body = {
                        'values': values
                    }
                    
                    self.sheets_service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_name,
                        valueInputOption=value_input_option,
                        body=body
                    ).execute()
                    
                    print(f"      ✓ Uploaded {len(values)-1} rows to {sheet_name}")
                    
                except Exception as e:
                    print(f"      ❌ Failed to upload {sheet_name}: {e}")
                    continue
            
            return spreadsheet_id
            
        except Exception as error:
            print(f"Failed to create Google Sheet: {error}")
            return None
    
    @quota_aware_api_call(api_type="drive", operation_type="delete")
    def cleanup_converted_sheets(self, urls: List[str], 
                               keep_converted_sheets: bool = False) -> None:
        """Clean up intermediate Google Sheets after successful combination"""
        if keep_converted_sheets:
            print("🗂️ Keeping converted Google Sheets (cleanup disabled)")
            return
        
        print("\n🧹 Cleaning up intermediate Google Sheets...")
        
        deleted_count = 0
        failed_count = 0
        
        for url in urls:
            try:
                # Extract file ID from URL
                file_id = self.extract_file_id(url)
                
                # Get file info to check if it's a converted file
                file_info = self.get_file_info(file_id)
                if not file_info:
                    continue
                
                file_name = file_info.get('name', 'Unknown')
                
                # Only delete files that look like our converted sheets
                # (either end with '_processed' or are Google Sheets)
                is_converted = (
                    '_processed' in file_name or 
                    self.is_google_sheet(file_info)
                )
                
                if is_converted:
                    print(f"   🗑️ Deleting: {file_name}")
                    
                    self.drive_service.files().delete(
                        fileId=file_id,
                        supportsAllDrives=True
                    ).execute()
                    
                    deleted_count += 1
                    print(f"      ✅ Deleted successfully")
                else:
                    print(f"   ⏭️ Skipping: {file_name} (not a converted file)")
                    
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed to delete {url}: {e}")
                continue
        
        print(f"\n✅ Cleanup complete:")
        print(f"   Deleted: {deleted_count} files")
        if failed_count > 0:
            print(f"   Failed: {failed_count} files")
        print("   Your original Excel files are preserved")
