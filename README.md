# Google Sheets Combiner

Extract data from multiple Google Sheets and combine them into a single Excel file with properly named tabs.

## Quick Start

1. **Setup Google API credentials** (see `docs/GOOGLE_API_SETUP.md`)
2. **Configure your URLs:**
   ```bash
   cp config/urls.txt.template config/urls.txt
   # Edit config/urls.txt and add your Google Sheets URLs
   ```
3. **Run the application:**
   ```bash
   python main.py --convert-excel
   ```

## ✨ New Features

### 🏷️ **Smart Tab Naming**
Automatically abbreviates long sheet titles for cleaner Excel tabs:
- `[1820 Tahoe] SHARED Work Progress List.xlsx` → `1820 Tahoe_Construction Items`
- `5109 OFW_SHARED Work Progress List` → `5109 OFW_Design Items`

### 🚀 **Enhanced Large File Processing**
Two-tier conversion system handles files of any size:
- **Standard Conversion**: Fast Google Drive API conversion for normal files
- **Enhanced Processing**: Local processing for large files (50MB+) with binary data
- **Automatic Cleanup**: Removes intermediate Google Sheets after successful combination

### 📊 **Quota Monitoring & Rate Limiting**
Comprehensive API management for free tier compliance:
- **Real-time Quota Tracking**: Monitor Drive API (1B units/day) and Sheets API (300/minute) usage
- **Smart Rate Limiting**: Automatic throttling with exponential backoff and retry logic
- **Usage Reporting**: Detailed summary of API calls and quota consumption
- **Free Tier Compliance**: Built-in limits ensure you stay within Google's free quotas

## Features

- **Extracts all tabs** from multiple Google Sheets
- **Auto-converts Excel files** to Google Sheets format (handles files up to 55MB+)
- **Smart tab naming** with project number + name abbreviation
- **Enhanced error handling** with automatic fallback for large/complex files
- **Binary data cleanup** removes problematic image columns automatically
- **Prevents naming conflicts** with intelligent duplicate handling
- **Beautiful Excel formatting** with headers and auto-sized columns
- **Automatic cleanup** of intermediate files
- **Quota monitoring** with real-time API usage tracking and free tier compliance
- **Smart rate limiting** with automatic retry and exponential backoff
- **Configurable limits** for safety and performance


## Project Structure

See the [STRUCTURE.md](./docs/STRUCTURE.md) file for a detailed overview of the project structure.


## Usage

### **Recommended Usage:**
```bash
# Convert Excel files and combine with automatic cleanup
python main.py --convert-excel
```

### **Advanced Options:**
```bash
# Keep intermediate Google Sheets for review
python main.py --convert-excel --keep-converted

# Custom output filename
python main.py --convert-excel --output "my_combined_data.xlsx"

# Save to UNC network drive
python main.py --convert-excel --unc-path "\\\\server\\share\\reports\\combined.xlsx"

# Show current path configuration
python main.py --show-path-config

# Process without conversion (Google Sheets only)
python main.py
```

### **Command Line Options:**
- `--convert-excel` - Auto-convert Excel files to Google Sheets
- `--output filename.xlsx` - Specify custom output filename
- `--unc-path "\\\\server\\path"` - Save to UNC network path (overrides config)
- `--show-path-config` - Display current output path configuration
- `--max-tabs N` - Limit tabs per sheet (default: 10)
- `--keep-converted` - Keep intermediate Google Sheets after combination
- `--cleanup-originals` - Delete original Excel files after conversion

### **Legacy Batch Files:**
```bash
run.bat                    # Simple run
run_with_conversion.bat    # Interactive options
```

## How It Works

### **1. File Processing Pipeline**
```
Excel Files → Standard Conversion → Enhanced Processing → Google Sheets → Combined Excel
     ↓              ↓                      ↓                    ↓            ↓
  Large/Complex?  Failed?           Download & Clean        Extract Data   Final Output
```

### **2. Smart Title Abbreviation**
- Extracts project numbers and key identifiers
- Removes file extensions and common suffixes (`_SHARED`, etc.)
- Creates clean, consistent tab names

### **3. Enhanced Large File Support**
- **Standard**: Uses Google Drive API for fast conversion
- **Enhanced**: Downloads files locally, removes binary/image data, creates clean Google Sheets
- **Automatic**: Seamlessly falls back when standard conversion fails

### **4. Excel Compatibility**
- Tab names limited to 31 characters (Excel requirement)
- Invalid characters automatically sanitized
- Duplicate names handled with numbered suffixes

## Configuration

Edit `src/config.py` to customize:
- `OUTPUT_FILENAME` - Output Excel file path (default: `output/combined_sheets.xlsx`)
- `MAX_TABS_PER_SHEET` - Limit tabs per Google Sheet (default: 10)
- `QUOTA_LIMITS` - Google API quota limits for free tier compliance

URLs are stored in `config/urls.txt` (one URL per line).

## 📊 Quota Monitoring & Rate Limiting

### **Free Tier Compliance**
The application includes comprehensive quota monitoring to stay within Google API free tier limits:
- **Drive API**: 1 billion quota units per day
- **Sheets API**: 300 requests per minute
- **Drive Requests**: 1,000 requests per 100 seconds
- **Drive Queries**: 20,000 queries per 100 seconds

### **Smart Rate Limiting**
All API calls are automatically rate-limited with:
- **@quota_aware_api_call** decorators on all API methods
- **Automatic retry** with exponential backoff on quota errors
- **Real-time monitoring** of quota usage and limits
- **Progress reporting** every 10 requests for visibility

### **Usage Reporting**
At the end of each run, you'll see:
```
📊 API Usage Summary:
Drive API requests: 15
Sheets API requests: 8
Drive quota used: 23 units
Drive quota usage: 0.0% of daily limit
```

### **Rate Limiting Configuration**
The system automatically enforces:
- Minimum 200ms between Drive API calls (5 calls/second)
- Minimum 200ms between Sheets API calls (5 calls/second)
- Automatic backoff when approaching limits
- Warning messages at 90% of quota limits

## 🗂️ UNC Drive Path Configuration

### **Network Drive Support**
Save combined Excel files directly to UNC network drives with enterprise-grade reliability:

```bash
# Configure UNC drive settings
cp config/output_config.json.template config/output_config.json
# Edit config/output_config.json with your network paths
```

### **Configuration Options**
```json
{
    "output_paths": {
        "unc_drive_enabled": true,
        "unc_base_path": "\\\\server\\share\\reports",
        "unc_filename_template": "combined_sheets_{timestamp}.xlsx",
        "backup_to_local": true
    },
    "security": {
        "validate_unc_path": true,
        "allowed_unc_patterns": [
            "\\\\companyserver\\*"
        ]
    }
}
```

### **UNC Features**
- **Automatic Fallback**: Falls back to local save if UNC path fails
- **Path Validation**: Security checks against allowed UNC patterns
- **Directory Creation**: Automatically creates missing network directories
- **Local Backup**: Optional backup copy to local drive
- **Template Variables**: Dynamic filenames with `{timestamp}`, `{date}`, `{year}`, etc.
- **Retry Logic**: Multiple attempts with error handling

### **Template Variables**
Available for dynamic filenames:
- `{timestamp}` - `20250721_143022`
- `{date}` - `2025-07-21`
- `{year}`, `{month}`, `{day}` - Individual date components
- Custom variables via command line

## Requirements

- **Python 3.7+** with virtual environment support
- **Google Cloud API credentials** (Drive + Sheets APIs)
- **Dependencies**: `pandas`, `openpyxl`, `google-api-python-client`, `google-auth`

### **Installation:**
```bash
# Clone/download the project
cd google_sheet_combiner

# Install dependencies (virtual environment recommended)
pip install -r requirements.txt

# Setup Google API credentials
# See docs/GOOGLE_API_SETUP.md for detailed instructions
```

## Usage

### **Basic Operation**
```bash
python main.py
```

### **Command Line Options**
```bash
# Save to UNC network drive
python main.py --unc-path "\\server\share\reports"

# Show UNC path configuration
python main.py --show-path-config

# Combine with other options
python main.py --unc-path "\\server\share" --config custom_config.json
```

### **Configuration Files**
- `config/urls.txt` - Google Sheets URLs (one per line)
- `config/output_config.json` - Output and UNC path settings (optional)
  
**Example urls.txt:**
```
https://docs.google.com/spreadsheets/d/1ABC.../edit
https://docs.google.com/spreadsheets/d/2DEF.../edit
```

### **Project Structure:**
```
📁 google_sheet_combiner/
├── 📁 src/                     # Core application code
│   ├── config.py              # Configuration settings
│   ├── drive_converter.py     # Excel→Sheets conversion with enhanced processing
│   ├── google_sheets_extractor.py  # Data extraction with smart tab naming
│   └── excel_combiner.py      # Excel file creation with sanitization
├── 📁 config/                 # Configuration files
│   └── urls.txt              # Google Sheets URLs (one per line)
├── 📁 tests/                  # Test scripts and validation
│   ├── README.md             # Test documentation
│   ├── test_enhanced_conversion.py    # Large file conversion tests
│   ├── test_title_abbreviation.py    # Title abbreviation tests
│   ├── test_complete_workflow.py     # End-to-end workflow tests
│   └── ...                   # Additional test modules
├── 📁 utils/                  # Utilities and diagnostic tools
│   ├── README.md             # Utility documentation
│   ├── diagnose_access.py    # File access diagnostics
│   ├── process_excel_with_images.py  # Large file processing
│   ├── retry_conversion_with_backoff.py  # Retry utilities
│   └── ...                   # Additional utilities
├── 📁 output/                 # Generated Excel files
├── 📁 docs/                   # Documentation
│   ├── GOOGLE_API_SETUP.md   # Setup instructions
│   └── STRUCTURE.md          # Detailed project structure
├── main.py                   # Main application entry point
├── manual_cleanup.py         # Manual cleanup utility
├── requirements.txt          # Python dependencies
├── run.bat                   # Windows batch file
└── credentials.json          # Google API credentials (user-provided)
```

## Output

Excel files are saved based on configuration:

### **Local Storage (Default)**
```
📁 output/
  └── combined_sheets.xlsx
```

### **UNC Network Drive**
```bash
# With UNC path configured
\\server\share\reports\combined_sheets_20250721_143022.xlsx

# With local backup enabled (optional)
📁 output/
  └── combined_sheets.xlsx (backup copy)
```

### **Output Features**
- **Smart tab names**: `1820 Tahoe_Construction Items`, `5109 OFW_Design Items`
- **All tabs** from source sheets (up to configured limit)
- **Formatted headers** with bold styling and gray background
- **Auto-sized columns** for optimal readability
- **Clean data** with binary/image columns removed
- **Progress summary** showing row counts and processing details

### **Example Output Structure:**
```
📁 combined_sheets.xlsx
  ├── 1820 Tahoe_Construction Items (44 rows)
  ├── 1820 Tahoe_Design Items (13 rows)
  ├── 1820 Tahoe_FF&E Items (32 rows)
  ├── 5109 OFW_Budget Summary (156 rows)
  └── 5109 OFW_Timeline (89 rows)
```

## Troubleshooting

### **Common Issues:**

**Large File Conversion:**
- ✅ **Automatic**: System automatically handles files up to 55MB+ using enhanced processing
- 🔄 **Fallback**: Standard conversion failures trigger local processing
- 🧹 **Cleanup**: Intermediate files cleaned up after successful combination

**File Access:**
- **"Operation not supported"**: Excel files automatically converted to Google Sheets
- **"File not found"**: Ensure files have proper sharing permissions
- **"Internal Error 500"**: Large files automatically processed with enhanced method

**UNC Network Drive Issues:**
- **Path not accessible**: Check network connectivity and permissions
- **Authentication required**: Ensure Windows authentication for network share
- **Directory creation failed**: Verify write permissions to UNC path
- **Automatic fallback**: System saves locally if UNC path fails

**Authentication:**
- **Token errors**: Delete `token.json` and re-authenticate
- **Permission issues**: Ensure Google Drive and Sheets APIs are enabled
- **Rate limits**: Built-in quota monitoring prevents API exhaustion with automatic rate limiting
- **Quota errors**: System automatically retries with exponential backoff and reports usage

### **Enhanced Processing Details:**
When standard conversion fails (typically for files >10MB or with binary data):
1. 📥 Downloads Excel file locally
2. 🧹 Removes problematic columns (images, binary data)
3. 📊 Processes each sheet separately
4. ☁️ Uploads clean data to new Google Sheets
5. 🗑️ Cleans up intermediate files automatically

## Security Best Practices

### **UNC Drive Configuration**
When using UNC network drives, follow these security guidelines:

1. **Path Validation**: Always enable `validate_unc_path` in configuration
2. **Allowed Patterns**: Restrict access using `allowed_unc_patterns`:
   ```json
   "allowed_unc_patterns": [
       "\\\\companyserver\\reports\\*",
       "\\\\fileserver01\\shared\\projects\\*"
   ]
   ```
3. **Credential Management**: Use Windows integrated authentication when possible
4. **Backup Strategy**: Enable `backup_to_local` for critical data
5. **Access Logging**: Monitor UNC access attempts in application logs

### **Configuration Security**
- Keep `config/output_config.json` out of version control (use `.gitignore`)
- Use configuration templates for team distribution
- Regularly review and update allowed UNC patterns
- Test UNC accessibility before production use

## Project Maintenance

### **Quick Structure Check:**
```bash
# Check if project structure is clean and organized
python utils\check_project_structure.py
```

### **Auto Maintenance:**
```bash
# Run comprehensive maintenance (structure check + cleanup)
maintain.bat
```

### **Manual Cleanup:**
```bash
# Remove Python cache files
rmdir /s /q src\__pycache__
rmdir /s /q tests\__pycache__

# Clean up intermediate Google Sheets
python manual_cleanup.py
```

See `docs/GOOGLE_API_SETUP.md` for detailed setup instructions.
