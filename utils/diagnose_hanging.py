#!/usr/bin/env python3
"""
Diagnostic script to test where main.py might be hanging
"""

import sys
import os
import traceback

# Add parent directory to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    try:
        from src.config import Config
        print("✅ Config import successful")
        
        from src.google_sheets_extractor import GoogleSheetsExtractor
        print("✅ GoogleSheetsExtractor import successful")
        
        from src.excel_combiner import ExcelCombiner
        print("✅ ExcelCombiner import successful")
        
        from src.drive_converter import DriveFileConverter
        print("✅ DriveFileConverter import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_config():
    """Test configuration validation"""
    print("\n🔍 Testing configuration...")
    try:
        from src.config import Config
        Config.validate_config()
        print("✅ Configuration validation successful")
        
        sheet_urls = Config.get_sheet_urls()
        print(f"✅ Found {len(sheet_urls)} URLs in config")
        for i, url in enumerate(sheet_urls[:3], 1):  # Show first 3
            print(f"   {i}. {url[:50]}...")
        
        return True, sheet_urls
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        traceback.print_exc()
        return False, []

def test_converter_init():
    """Test DriveFileConverter initialization"""
    print("\n🔍 Testing DriveFileConverter initialization...")
    try:
        from src.drive_converter import DriveFileConverter
        converter = DriveFileConverter()
        print("✅ DriveFileConverter initialization successful")
        return True, converter
    except Exception as e:
        print(f"❌ DriveFileConverter initialization error: {e}")
        traceback.print_exc()
        return False, None

def test_credentials():
    """Test if credentials files exist"""
    print("\n🔍 Testing credentials...")
    
    creds_file = "credentials.json"
    token_file = "token.json"
    
    if os.path.exists(creds_file):
        print(f"✅ {creds_file} exists")
    else:
        print(f"❌ {creds_file} not found")
        
    if os.path.exists(token_file):
        print(f"✅ {token_file} exists")
    else:
        print(f"⚠️ {token_file} not found (will be created on first auth)")

def main():
    print("=" * 60)
    print("🔧 Google Sheets Combiner - Diagnostic Tool")
    print("=" * 60)
    
    # Test credentials
    test_credentials()
    
    # Test imports
    if not test_imports():
        print("\n❌ Cannot proceed - import errors found")
        return 1
    
    # Test configuration
    success, urls = test_config()
    if not success:
        print("\n❌ Cannot proceed - configuration errors found")
        return 1
    
    if not urls:
        print("\n❌ No URLs found in config/urls.txt")
        return 1
    
    # Test converter initialization (this is where it might hang)
    print("\n⚠️ About to test DriveFileConverter initialization...")
    print("   (This is where your script might be hanging)")
    print("   If this hangs, it's likely an authentication issue...")
    
    success, converter = test_converter_init()
    if not success:
        print("\n❌ DriveFileConverter initialization failed")
        return 1
    
    print("\n✅ All diagnostic tests passed!")
    print("🎯 Your main.py should work now.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
