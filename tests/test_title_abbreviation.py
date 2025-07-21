#!/usr/bin/env python3
"""
Test script for the abbreviated title extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.google_sheets_extractor import GoogleSheetsExtractor

def test_title_abbreviation():
    """Test the title abbreviation functionality"""
    
    print("🧪 Testing Title Abbreviation Logic")
    print("=" * 60)
    
    # Create extractor instance (we just need the method)
    extractor = GoogleSheetsExtractor()
    
    # Test cases
    test_cases = [
        "[1820 Tahoe] SHARED Work Progress List.xlsx",
        "5109 OFW_SHARED Work Progress List",
        "1234 ProjectName Something Else",
        "9876 ABC_SHARED Random Text",
        "[2023 NewProject] Status Report.xlsx",
        "555 X_SHARED Whatever",
        "NoNumber ProjectName Only",
        "123",
        "ABC Only Letters",
        "Really Long Sheet Name Without Numbers",
        "",
        "777 VeryLongProjectNameHere_SHARED",
        "[8888 Short]_SHARED End"
    ]
    
    print("Testing title abbreviation:")
    print("-" * 60)
    
    for i, original_title in enumerate(test_cases, 1):
        try:
            abbreviated = extractor._extract_abbreviated_title(original_title)
            
            print(f"{i:2d}. Original:    '{original_title}'")
            print(f"    Abbreviated: '{abbreviated}'")
            print()
            
        except Exception as e:
            print(f"{i:2d}. ERROR with '{original_title}': {e}")
            print()
    
    print("=" * 60)
    print("✅ Title abbreviation test completed!")
    
    # Test with your specific examples
    print("\n🎯 Specific Examples:")
    examples = [
        "[1820 Tahoe] SHARED Work Progress List.xlsx",
        "5109 OFW_SHARED Work Progress List"
    ]
    
    for example in examples:
        result = extractor._extract_abbreviated_title(example)
        print(f"'{example}' → '{result}'")

if __name__ == "__main__":
    test_title_abbreviation()
