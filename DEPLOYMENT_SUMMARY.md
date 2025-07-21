# 🚀 Google Sheets Combiner - Deployment Summary

## ✅ Completed Setup Steps

### 1. **Environment Setup**
- ✅ Virtual environment created: `venv/`
- ✅ Dependencies installed from `requirements.txt`
- ✅ Configuration files created from templates

### 2. **Scripts Created**
- ✅ `run_sheets_combiner.sh` - Main cron job script
- ✅ `setup_cron.sh` - Interactive cron job setup tool
- ✅ `SETUP_CREDENTIALS.md` - Google API setup guide
- ✅ `logrotate.conf` - Log rotation configuration

### 3. **Directory Structure**
```
/home/desops/google-sheets-combiner/
├── venv/                          # Virtual environment
├── config/
│   ├── urls.txt                   # ⚠️ EDIT: Add your Google Sheets URLs
│   └── output_config.json         # Output configuration
├── logs/                          # Log files (created automatically)
├── output/                        # Excel output files
├── run_sheets_combiner.sh         # Cron job script
├── setup_cron.sh                  # Cron setup tool
├── SETUP_CREDENTIALS.md           # Credential setup guide
└── logrotate.conf                 # Log rotation config
```

## ⚠️ Required Next Steps

### 1. **Set up Google API Credentials**
```bash
# You need to create and upload credentials.json
# See SETUP_CREDENTIALS.md for detailed instructions
nano credentials.json  # Paste your Google API JSON credentials
chmod 600 credentials.json
```

### 2. **Configure Your Google Sheets URLs**
```bash
# Edit the URLs file and add your actual Google Sheets
nano config/urls.txt

# Example content:
# https://docs.google.com/spreadsheets/d/1ABC123.../edit
# https://docs.google.com/spreadsheets/d/2DEF456.../edit
```

### 3. **Test the Setup**
```bash
# Run the interactive setup tool
./setup_cron.sh

# Or test manually
source venv/bin/activate
python main.py --help
python main.py --show-path-config
```

## 🕐 Cron Job Setup

### Interactive Setup
```bash
./setup_cron.sh
```

### Manual Setup
```bash
# Edit crontab
crontab -e

# Add a line like this (daily at 6 AM):
0 6 * * * /home/desops/google-sheets-combiner/run_sheets_combiner.sh
```

### Common Schedules
- **Daily at 6 AM**: `0 6 * * *`
- **Weekdays at 9 AM**: `0 9 * * 1-5`
- **Every 4 hours**: `0 */4 * * *`
- **Weekly on Monday**: `0 8 * * 1`

## 📊 Monitoring & Logs

### View Logs
```bash
# Recent activity
tail -f logs/cron.log

# All logs
cat logs/cron.log

# System cron logs
sudo tail -f /var/log/syslog | grep CRON
```

### Log Rotation (Optional)
```bash
# Install log rotation
sudo cp logrotate.conf /etc/logrotate.d/sheets-combiner
```

## 🔧 Configuration Options

### Output Paths
Edit `config/output_config.json` to configure:
- Local output directory
- Network drive paths (for shared storage)
- Backup options
- Security settings

### Application Options
The cron script runs with these default options:
```bash
python main.py --convert-excel
```

You can modify `run_sheets_combiner.sh` to use different options:
- `--unc-path "/shared/reports"` - Save to network drive
- `--output "custom_name.xlsx"` - Custom filename
- `--max-tabs 20` - Increase tab limit
- `--keep-converted` - Keep intermediate files

## 🚨 Troubleshooting

### Common Issues
1. **No credentials.json**: Follow SETUP_CREDENTIALS.md
2. **No URLs configured**: Edit config/urls.txt
3. **Permission denied**: Check file permissions
4. **Cron not running**: Check cron service and logs

### Test Commands
```bash
# Test application
source venv/bin/activate && python main.py --help

# Test cron script
./run_sheets_combiner.sh

# Check cron jobs
crontab -l

# Check system cron
sudo systemctl status cron
```

## 📝 Next Steps

1. **Set up credentials** (see SETUP_CREDENTIALS.md)
2. **Configure URLs** (edit config/urls.txt)
3. **Test manually** (run ./setup_cron.sh)
4. **Install cron job** (use ./setup_cron.sh)
5. **Monitor logs** (tail -f logs/cron.log)

## 🎯 Quick Start Commands

```bash
# 1. Setup credentials and URLs (manual step)
nano credentials.json  # Paste your Google API credentials
nano config/urls.txt   # Add your Google Sheets URLs

# 2. Test the setup
./setup_cron.sh

# 3. Install cron job for daily 6 AM execution
echo "0 6 * * * /home/desops/google-sheets-combiner/run_sheets_combiner.sh" | crontab -

# 4. Monitor
tail -f logs/cron.log
```

Your Google Sheets Combiner is ready for deployment! 🎉
