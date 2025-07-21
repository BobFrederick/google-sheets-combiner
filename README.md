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

## 🐧 Linux Deployment & Cron Job Setup

### **Prerequisites**
```bash
# Install Python 3.7+ and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# For CentOS/RHEL/Fedora
sudo yum install python3 python3-pip git
# or
sudo dnf install python3 python3-pip git
```

### **Step 1: Clone and Setup**
```bash
# Clone the repository
git clone https://github.com/BobFrederick/google-sheets-combiner.git
cd google-sheets-combiner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Configuration**
```bash
# Copy configuration templates
cp config/urls.txt.template config/urls.txt
cp config/output_config.json.template config/output_config.json

# Edit URLs file with your Google Sheets
nano config/urls.txt

# Configure output paths (optional for UNC/network drives)
nano config/output_config.json
```

### **Step 3: Google API Credentials**
```bash
# Upload your credentials.json file
# Method 1: SCP from Windows machine
scp /path/to/credentials.json user@linux-server:/path/to/google-sheets-combiner/

# Method 2: Create manually and paste content
nano credentials.json
# Paste your Google API credentials JSON content

# Set proper permissions
chmod 600 credentials.json
```

### **Step 4: Test Manual Execution**
```bash
# Activate virtual environment
source venv/bin/activate

# Test run
python main.py --help

# Test basic functionality
python main.py --show-path-config

# Test with conversion
python main.py --convert-excel
```

### **Step 5: Create Automated Deployment Scripts**
The repository includes automated setup scripts for easy deployment:

```bash
# Interactive cron job setup tool
./setup_cron.sh

# Manual cron job script (created automatically)
./run_sheets_combiner.sh
```

**Example cron script content:**
```bash
#!/bin/bash
cd /home/yourusername/google-sheets-combiner
source venv/bin/activate
export TZ='America/New_York'
mkdir -p logs

# Run with local backup and network drive copy
python main.py --convert-excel --output "output/combined_sheets.xlsx" >> logs/cron.log 2>&1

# Check exit status and copy to network drive if successful
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ] && [ -f "output/combined_sheets.xlsx" ]; then
    # Copy to network drive (update path as needed)
    cp "output/combined_sheets.xlsx" "/mnt/network-drive/path/combined_sheets.xlsx" 2>>logs/cron.log
fi

deactivate
exit $EXIT_CODE
```

### **Step 6: Setup Cron Job**
**Interactive Setup (Recommended):**
```bash
./setup_cron.sh
```

**Manual Setup:**
```bash
# Edit crontab
crontab -e

# Add cron job entries (examples):

# Every 4 hours (recommended)
0 */4 * * * /home/yourusername/google-sheets-combiner/run_sheets_combiner.sh

# Every day at 6:00 AM
0 6 * * * /home/yourusername/google-sheets-combiner/run_sheets_combiner.sh

# Every weekday at 9 AM
0 9 * * 1-5 /home/yourusername/google-sheets-combiner/run_sheets_combiner.sh
```

### **Step 7: Network Drive Configuration**

**For Egnyte Drives:**
```bash
# Check if Egnyte is mounted
mount | grep egnyte

# Typical Egnyte mount location
ls -la /mnt/egnyte/

# Fix permissions for your user (if needed)
sudo chown -R $USER:$USER "/mnt/egnyte/path/to/your/folder"
```

**For SMB/CIFS Network Drives:**
```bash
# Install SMB utilities
sudo apt install cifs-utils

# Create mount point
sudo mkdir -p /mnt/shared-reports

# Mount network drive (temporary)
sudo mount -t cifs //server/share /mnt/shared-reports -o username=youruser

# For permanent mounting, add to /etc/fstab
echo "//server/share /mnt/shared-reports cifs username=youruser,password=yourpass,uid=1000,gid=1000,iocharset=utf8 0 0" | sudo tee -a /etc/fstab
```

### **Step 8: Monitoring & Maintenance**
```bash
# Real-time log monitoring
tail -f logs/cron.log

# Check cron job status
crontab -l

# View recent activity summary
tail -20 logs/cron.log

# Interactive management
./setup_cron.sh

# Manual test run
./run_sheets_combiner.sh
```

### **Step 9: Log Rotation Setup (Optional)**
```bash
# Install log rotation
sudo cp logrotate.conf /etc/logrotate.d/sheets-combiner

# Or create manually
sudo tee /etc/logrotate.d/sheets-combiner << 'EOF'
/home/yourusername/google-sheets-combiner/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    copytruncate
    create 644 yourusername yourusername
}
EOF
```

### **Deployment Verification**
After setup, verify everything is working:

```bash
# 1. Test the application
source venv/bin/activate
python main.py --help

# 2. Test the cron script
./run_sheets_combiner.sh

# 3. Check output files
ls -la output/
ls -la /mnt/network-drive/path/ # if using network drive

# 4. Verify cron installation
crontab -l

# 5. Monitor first automated run
tail -f logs/cron.log
```

### **Common Cron Schedules**
```bash
# Every 15 minutes (testing)
*/15 * * * * /path/to/run_sheets_combiner.sh

# Every 4 hours (recommended for active projects)
0 */4 * * * /path/to/run_sheets_combiner.sh

# Twice daily (6 AM and 6 PM)
0 6,18 * * * /path/to/run_sheets_combiner.sh

# Business hours only (9 AM - 5 PM, Mon-Fri)
0 9-17 * * 1-5 /path/to/run_sheets_combiner.sh

# Daily at 2:30 AM
30 2 * * * /path/to/run_sheets_combiner.sh

# Weekly on Monday at 8 AM
0 8 * * 1 /path/to/run_sheets_combiner.sh

# First day of every month
0 0 1 * * /path/to/run_sheets_combiner.sh
```

### **Troubleshooting Linux Deployment**

**Permission Issues:**
```bash
# Fix script permissions
chmod +x run_sheets_combiner.sh setup_cron.sh

# Fix network drive permissions
sudo chown -R $USER:$USER "/mnt/network-drive/your-folder"

# Check file creation
ls -la output/
```

**Cron Job Issues:**
```bash
# Check if cron job ran
grep "run_sheets_combiner" /var/log/syslog

# Test cron environment
env -i /bin/bash --noprofile --norc ./run_sheets_combiner.sh

# Check cron service
sudo systemctl status cron
sudo systemctl restart cron
```

**Application Issues:**
```bash
# Check Python environment
source venv/bin/activate
which python
python --version
pip list

# Test Google API credentials
python -c "import json; print('Credentials OK' if 'client_id' in json.load(open('credentials.json')) else 'Invalid credentials')"

# Check configuration
python main.py --show-path-config
```

**Network Drive Issues:**
```bash
# Test network drive access
touch "/mnt/network-drive/test-file.txt"
rm "/mnt/network-drive/test-file.txt"

# Check mount status
mount | grep network-drive
df -h | grep network-drive

# Test Egnyte specifically
mount | grep egnyte
ls -la /mnt/egnyte/
```

**Log Analysis:**
```bash
# Check for errors
grep -i error logs/cron.log

# Check success rate
grep "completed with exit code" logs/cron.log

# Monitor API usage
grep "API Usage Summary" logs/cron.log

# Check file operations
grep -E "(File created|Successfully copied|Failed to copy)" logs/cron.log
```

### **Quick Deployment Commands**
```bash
# Complete setup in one go
git clone https://github.com/BobFrederick/google-sheets-combiner.git
cd google-sheets-combiner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config/*.template config/
chmod +x *.sh

# Edit configuration files
nano config/urls.txt          # Add your Google Sheets URLs
nano credentials.json         # Add your Google API credentials

# Test and deploy
./run_sheets_combiner.sh      # Test run
./setup_cron.sh              # Interactive cron setup
```

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
