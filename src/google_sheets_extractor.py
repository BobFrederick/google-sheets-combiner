import os
import time
import re
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from .config import Config
from .rate_limiter import quota_aware_api_call
from .quota_monitor import quota_monitor


class GoogleSheetsExtractor:
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        creds = None
        
        # Check if token file exists
        if os.path.exists(Config.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(Config.TOKEN_FILE, Config.SCOPES)
        
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
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    @quota_aware_api_call(api_type="sheets", operation_type="read")
    def get_sheet_metadata(self, sheet_id: str) -> Dict[str, Any]:
        """Get metadata about a Google Sheet"""
        try:
            metadata = self.service.spreadsheets().get(
                spreadsheetId=sheet_id
            ).execute()
            return metadata
        except HttpError as error:
            print(f"Error getting sheet metadata for {sheet_id}: {error}")
            return {}
    
    def get_sheet_title(self, sheet_id: str) -> str:
        """Get the title of a Google Sheet"""
        metadata = self.get_sheet_metadata(sheet_id)
        return metadata.get('properties', {}).get('title', f'Sheet_{sheet_id[:8]}')
    
    def get_worksheets(self, sheet_id: str) -> List[Dict[str, Any]]:
        """Get list of worksheets in a Google Sheet"""
        metadata = self.get_sheet_metadata(sheet_id)
        sheets = metadata.get('sheets', [])
        
        worksheets = []
        for sheet in sheets:
            props = sheet.get('properties', {})
            worksheets.append({
                'id': props.get('sheetId'),
                'title': props.get('title', 'Untitled'),
                'row_count': props.get('gridProperties', {}).get('rowCount', 0),
                'column_count': props.get('gridProperties', {}).get('columnCount', 0)
            })
        
        return worksheets
    
    @quota_aware_api_call(api_type="sheets", operation_type="read")
    def extract_worksheet_data(self, sheet_id: str, 
                             worksheet_title: str) -> Optional[pd.DataFrame]:
        """Extract data from a specific worksheet"""
        try:
            # Get the data
            range_name = f"'{worksheet_title}'"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id, 
                range=range_name,
                valueRenderOption='UNFORMATTED_VALUE',
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f"No data found in worksheet '{worksheet_title}'")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(values)
            
            # Use first row as headers if it looks like headers
            if len(df) > 1:
                # Check if first row contains mostly strings (likely headers)
                first_row_str_count = sum(1 for val in df.iloc[0] if isinstance(val, str))
                if first_row_str_count > len(df.columns) * 0.5:
                    df.columns = df.iloc[0]
                    df = df.drop(df.index[0]).reset_index(drop=True)
            
            # Remove completely empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            return df if not df.empty else None
            
        except HttpError as error:
            print(f"Error extracting data from '{worksheet_title}': {error}")
            return None
        except Exception as e:
            print(f"Unexpected error extracting '{worksheet_title}': {e}")
            return None
    
    def extract_all_data(self, sheet_urls: List[str]) -> Dict[str, pd.DataFrame]:
        """Extract data from all sheets and worksheets"""
        all_data = {}
        
        for url in sheet_urls:
            try:
                sheet_id = Config.extract_sheet_id(url)
                sheet_title = self.get_sheet_title(sheet_id)
                
                print(f"Processing: {sheet_title}")
                
                worksheets = self.get_worksheets(sheet_id)
                
                if len(worksheets) > Config.MAX_TABS_PER_SHEET:
                    print(f"Warning: Sheet has {len(worksheets)} tabs, limiting to {Config.MAX_TABS_PER_SHEET}")
                    worksheets = worksheets[:Config.MAX_TABS_PER_SHEET]
                
                for worksheet in worksheets:
                    worksheet_title = worksheet['title']
                    print(f"  Extracting: {worksheet_title}")
                    
                    df = self.extract_worksheet_data(sheet_id, worksheet_title)
                    
                    if df is not None and not df.empty:
                        # Create unique tab name using abbreviated sheet title
                        abbreviated_sheet_title = self._extract_abbreviated_title(sheet_title)
                        safe_sheet_title = self._make_safe_filename(abbreviated_sheet_title)
                        safe_worksheet_title = self._make_safe_filename(worksheet_title)
                        tab_name = f"{safe_sheet_title}_{safe_worksheet_title}"
                        
                        # Debug output to show the transformation
                        if abbreviated_sheet_title != sheet_title:
                            print(f"    Title abbreviated: '{sheet_title}' → '{abbreviated_sheet_title}'")
                        
                        # Ensure tab name is not too long (Excel limit is 31 characters)
                        if len(tab_name) > 31:
                            tab_name = tab_name[:28] + "..."
                        
                        # Handle duplicate tab names
                        original_tab_name = tab_name
                        counter = 1
                        while tab_name in all_data:
                            tab_name = f"{original_tab_name[:26]}_{counter:02d}"
                            counter += 1
                        
                        all_data[tab_name] = df
                        print(f"    Added as: {tab_name}")
                    else:
                        print(f"    Skipped (empty): {worksheet_title}")
                    
                    # Rate limiting
                    time.sleep(60 / Config.REQUESTS_PER_MINUTE)
                
            except Exception as e:
                print(f"Error processing sheet {url}: {e}")
                continue
        
        return all_data
    
    def _extract_abbreviated_title(self, full_title: str) -> str:
        """Extract numeric sequence + first word/acronym from sheet title"""
        # Remove file extensions and common prefixes/suffixes
        title = full_title.replace('.xlsx', '').replace('.xls', '')
        title = re.sub(r'_SHARED.*$', '', title)  # Remove "_SHARED..." suffix
        title = re.sub(r'\[([^\]]+)\]', r'\1', title)  # Remove brackets: [1820 Tahoe] -> 1820 Tahoe
        
        # Find numeric sequence at the beginning
        numeric_match = re.match(r'^(\d+)', title.strip())
        numeric_part = numeric_match.group(1) if numeric_match else ""
        
        # Find the first word/acronym after the number
        if numeric_part:
            # Look for word after the number
            remaining = title[len(numeric_part):].strip()
            word_match = re.match(r'^[\s\-_]*([A-Za-z]+)', remaining)
            word_part = word_match.group(1) if word_match else ""
        else:
            # If no number, just take the first word
            word_match = re.match(r'^([A-Za-z]+)', title.strip())
            word_part = word_match.group(1) if word_match else ""
        
        # Combine numeric and word parts
        if numeric_part and word_part:
            abbreviated = f"{numeric_part} {word_part}"
        elif numeric_part:
            abbreviated = numeric_part
        elif word_part:
            abbreviated = word_part
        else:
            # Fallback to first 10 characters
            abbreviated = title[:10].strip()
        
        return abbreviated if abbreviated else "Sheet"
    
    def _make_safe_filename(self, name: str) -> str:
        """Make a string safe for use as a filename/tab name"""
        # Remove or replace invalid characters
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '[', ']']
        safe_name = name
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        safe_name = safe_name.strip(' .')
        
        return safe_name if safe_name else 'Sheet'
