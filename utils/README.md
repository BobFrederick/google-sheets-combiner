# Utilities

This directory contains utility scripts, helper tools, and diagnostic utilities for the Google Sheets Combiner project.

## Diagnostic Tools

### **File Access & Permissions**
- `diagnose_access.py` - Diagnose file access issues and permissions
- `check_access.py` - Check file accessibility
- `check_file_types.py` - Analyze file types and formats

### **Conversion Utilities**
- `debug_conversion.py` - Debug conversion processes
- `retry_conversion_with_backoff.py` - Retry failed conversions with exponential backoff
- `selective_conversion.py` - Convert specific files selectively
- `process_excel_with_images.py` - Process Excel files with binary/image data

### **Drive Management**
- `copy_shared_files.py` - Copy files from shared drives
- `diagnose_problematic_file.py` - Diagnose specific problematic files
- `debug_urls.py` - Debug URL extraction and validation

## Legacy Files

### **Archived Components**
- `legacy_config.py` - Original configuration module (moved from root)
- `legacy_drive_converter.py` - Original converter (before src/ reorganization)

## Sample Data

### **Test Files**
- `1235 SMD_SHARED Work Progress List.xlsx` - Sample Excel file for testing

## Setup & Configuration

### **Project Setup**
- `setup.py` - Project setup and initialization script

## Usage Examples

### **Diagnose File Access Issues:**
```bash
python utils/diagnose_access.py
```

### **Process Large Excel Files:**
```bash
python utils/process_excel_with_images.py
```

### **Retry Failed Conversions:**
```bash
python utils/retry_conversion_with_backoff.py
```

### **Debug Specific Files:**
```bash
python utils/diagnose_problematic_file.py
```

## Notes

- Most utilities require Google API credentials
- Some utilities modify Google Drive contents
- Legacy files are kept for reference but should not be used
- Excel processing utilities handle files up to 55MB+
