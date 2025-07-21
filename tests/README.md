# Test Suite

This directory contains various test scripts for the Google Sheets Combiner project.

## Test Categories

### **Core Functionality Tests**
- `test_auth.py` - Google API authentication testing
- `test_enhanced_conversion.py` - Enhanced large file conversion testing
- `test_complete_workflow.py` - End-to-end workflow testing

### **Conversion & Processing Tests**
- `test_converter.py` - Drive converter functionality
- `test_excel_file.py` - Excel file processing tests
- `test_direct_access.py` - Direct file access testing
- `test_shared_drive.py` - Shared Drive access testing
- `test_working_file.py` - Working file validation

### **Naming & Formatting Tests**
- `test_title_abbreviation.py` - Smart title abbreviation logic
- `test_title_logic.py` - Standalone title processing tests
- `test_excel_names.py` - Excel sheet name sanitization

### **Utility Tests**
- `test_owned_files.py` - File ownership testing
- `test_retry_conversion.py` - Retry mechanism testing
- `test.py` - General utility tests

## Running Tests

### **Individual Tests:**
```bash
# Test authentication
python tests/test_auth.py

# Test enhanced conversion
python tests/test_enhanced_conversion.py

# Test title abbreviation
python tests/test_title_abbreviation.py
```

### **Core Workflow Tests:**
```bash
# Test complete end-to-end workflow
python tests/test_complete_workflow.py

# Test enhanced large file processing
python tests/test_enhanced_conversion.py
```

### **Diagnostic Tests:**
```bash
# Test file access permissions
python tests/test_direct_access.py

# Test shared drive functionality
python tests/test_shared_drive.py
```

## Test Data

Most tests use:
- Real Google Sheets URLs from `config/urls.txt`
- Test file ID: `15aSwFR7Ci9bXDdPSB59qUgAvlZtW370m` (Large Tahoe file)
- Various synthetic test cases for edge conditions

## Notes

- Tests require valid Google API credentials
- Some tests modify Google Drive contents (use with caution)
- Enhanced conversion tests work with large files (55MB+)
- Title abbreviation tests are standalone and don't require API access
