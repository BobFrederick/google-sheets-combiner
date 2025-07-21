#!/usr/bin/env python3
"""
Standalone test for title abbreviation logic (no dependencies)
"""

import re

def extract_abbreviated_title(full_title: str) -> str:
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

def test_title_abbreviation():
    """Test the title abbreviation functionality"""
    
    print("🧪 Testing Title Abbreviation Logic")
    print("=" * 60)
    
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
            abbreviated = extract_abbreviated_title(original_title)
            
            print(f"{i:2d}. Original:    '{original_title}'")
            print(f"    Abbreviated: '{abbreviated}'")
            print()
            
        except Exception as e:
            print(f"{i:2d}. ERROR with '{original_title}': {e}")
            print()
    
    print("=" * 60)
    print("✅ Title abbreviation test completed!")
    
    # Test with your specific examples
    print("\n🎯 Your Specific Examples:")
    examples = [
        "[1820 Tahoe] SHARED Work Progress List.xlsx",
        "5109 OFW_SHARED Work Progress List"
    ]
    
    for example in examples:
        result = extract_abbreviated_title(example)
        print(f"'{example}' → '{result}'")

if __name__ == "__main__":
    test_title_abbreviation()
