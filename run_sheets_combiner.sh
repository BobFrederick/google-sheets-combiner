#!/bin/bash

# Google Sheets Combiner Cron Job Script
# This script runs the Google Sheets Combiner with proper environment setup

# Set working directory
cd /home/desops/google-sheets-combiner

# Activate virtual environment
source venv/bin/activate

# Set timezone (optional)
export TZ='America/New_York'

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the combiner with logging
# Modify the command line options as needed for your use case
python main.py --convert-excel --output "output/combined_sheets.xlsx" >> logs/cron.log 2>&1

# Check exit status and log it
EXIT_CODE=$?
echo "$(date): Google Sheets Combiner completed with exit code: $EXIT_CODE" >> logs/cron.log

# If successful, copy to Egnyte drive
if [ $EXIT_CODE -eq 0 ] && [ -f "output/combined_sheets.xlsx" ]; then
    echo "$(date): File created successfully: output/combined_sheets.xlsx" >> logs/cron.log
    echo "$(date): Attempting to copy to Egnyte drive..." >> logs/cron.log
    
    # Try to copy to Egnyte
    if cp "output/combined_sheets.xlsx" "/mnt/egnyte/Shared/Administrative/STAFF FOLDERS/Bob Frederick/google_sheet_combiner/mfreeland_projects/combined_sheets.xlsx" 2>>logs/cron.log; then
        echo "$(date): ✅ Successfully copied to Egnyte drive" >> logs/cron.log
    else
        echo "$(date): ⚠️ Failed to copy to Egnyte drive - using local file" >> logs/cron.log
        echo "$(date): 📁 Local file available at: $(pwd)/output/combined_sheets.xlsx" >> logs/cron.log
    fi
else
    echo "$(date): ❌ Script failed or output file not found" >> logs/cron.log
fi

# Deactivate virtual environment
deactivate

exit $EXIT_CODE
