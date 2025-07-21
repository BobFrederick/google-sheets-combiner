#!/usr/bin/env python3
"""
Setup script for Google Sheets Combiner
Helps with initial configuration and testing
"""

import os
import sys
import webbrowser
from config import Config


def check_credentials():
    """Check if Google API credentials exist"""
    if os.path.exists(Config.CREDENTIALS_FILE):
        print("✓ Google API credentials found")
        return True
    else:
        print("✗ Google API credentials not found")
        print(f"  Please download credentials.json from Google Cloud Console")
        return False


def check_urls():
    """Check if URLs are configured"""
    urls = Config.get_sheet_urls()
    if urls:
        print(f"✓ Found {len(urls)} Google Sheets URL(s)")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url[:50]}...")
        return True
    else:
        print("✗ No Google Sheets URLs configured")
        print("  Please add URLs to urls.txt or .env file")
        return False


def open_google_cloud_console():
    """Open Google Cloud Console for setup"""
    print("Opening Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")
    print("\\nGoogle Cloud Console Setup Steps:")
    print("1. Create a new project or select existing one")
    print("2. Enable the Google Sheets API")
    print("3. Go to 'Credentials' in the left sidebar")
    print("4. Click 'Create Credentials' > 'OAuth client ID'")
    print("5. Choose 'Desktop application'")
    print("6. Download the JSON file")
    print("7. Save it as 'credentials.json' in this directory")


def test_connection():
    """Test the Google Sheets connection"""
    try:
        from google_sheets_extractor import GoogleSheetsExtractor
        print("Testing Google Sheets connection...")
        extractor = GoogleSheetsExtractor()
        print("✓ Google Sheets API connection successful")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def main():
    print("Google Sheets Combiner Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7+ required")
        return 1
    else:
        print(f"✓ Python {sys.version.split()[0]}")
    
    # Check dependencies
    try:
        import google.auth
        import pandas
        import openpyxl
        print("✓ All dependencies installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return 1
    
    # Check configuration
    print("\\nConfiguration Check:")
    print("-" * 20)
    
    has_credentials = check_credentials()
    has_urls = check_urls()
    
    if not has_credentials:
        response = input("\\nOpen Google Cloud Console for setup? (y/n): ")
        if response.lower() == 'y':
            open_google_cloud_console()
        return 1
    
    if not has_urls:
        print("\\nPlease add Google Sheets URLs to urls.txt")
        print("Example URL format:")
        print("https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0")
        return 1
    
    # Test connection
    print("\\nConnection Test:")
    print("-" * 15)
    if test_connection():
        print("\\n✓ Setup complete! You can now run:")
        print("  python main.py")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
