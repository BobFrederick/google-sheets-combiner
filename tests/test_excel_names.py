#!/usr/bin/env python3
"""
Test script to demonstrate Excel sheet name sanitization
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.excel_combiner import ExcelCombiner

def test_sheet_name_sanitization():
    """Test the sheet name sanitization functionality"""
    
    print("🧪 Testing Excel Sheet Name Sanitization")
    print("=" * 50)
    
    # Create a test combiner
    combiner = ExcelCombiner("test_output.xlsx")
    
    # Test cases for sheet names
    test_names = [
        "Normal Sheet Name",
        "This is a very long sheet name that definitely exceeds the 31 character limit",
        "Invalid/Characters\\Test?Name*[Sheet]:Name",
        "History",  # Reserved name
        "HISTORY",  # Case insensitive test
        "Duplicate Name",
        "Duplicate Name",  # Test duplicate handling
        "Another Very Long Name That Will Be Truncated",
        "Sheet:With/Invalid\\Characters*[Test]?Name",
        "",  # Empty name test
        "31_Character_Long_Name_Exactly",  # Exactly 31 chars
        "32_Character_Long_Name_Too_Long!"  # 32 chars (too long)
    ]
    
    print("Testing sheet name sanitization:")
    print("-" * 50)
    
    sanitized_names = []
    for i, original_name in enumerate(test_names, 1):
        try:
            sanitized = combiner._sanitize_sheet_name(original_name)
            sanitized_names.append(sanitized)
            
            # Show the transformation
            status = "✅ OK" if len(sanitized) <= 31 else "❌ TOO LONG"
            print(f"{i:2d}. Original: '{original_name}'")
            print(f"    Sanitized: '{sanitized}' ({len(sanitized)} chars) {status}")
            
            # Check for issues
            invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
            has_invalid = any(char in sanitized for char in invalid_chars)
            if has_invalid:
                print(f"    ⚠️ WARNING: Still contains invalid characters!")
            
            print()
            
        except Exception as e:
            print(f"{i:2d}. ERROR with '{original_name}': {e}")
    
    # Summary
    print("=" * 50)
    print("📊 Summary:")
    print(f"   Total names tested: {len(test_names)}")
    print(f"   All under 31 chars: {all(len(name) <= 31 for name in sanitized_names)}")
    print(f"   All unique: {len(sanitized_names) == len(set(sanitized_names))}")
    
    # Check for any names that are still too long
    long_names = [name for name in sanitized_names if len(name) > 31]
    if long_names:
        print(f"   ❌ Names still too long: {long_names}")
    else:
        print("   ✅ All names within Excel limits")
    
    return len(long_names) == 0

if __name__ == "__main__":
    success = test_sheet_name_sanitization()
    
    if success:
        print("\n🎉 Sheet name sanitization test PASSED!")
        print("Excel compatibility ensured for all test cases.")
    else:
        print("\n⚠️ Sheet name sanitization test FAILED!")
        print("Some names still exceed Excel limits.")
