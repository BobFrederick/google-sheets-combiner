#!/bin/bash

# Cron Job Setup Script for Google Sheets Combiner
# This script helps you set up automated execution

echo "🚀 Google Sheets Combiner - Cron Job Setup"
echo "=========================================="

# Function to show cron job examples
show_cron_examples() {
    echo ""
    echo "📅 Cron Schedule Examples:"
    echo "------------------------"
    echo "Every day at 6:00 AM:"
    echo "0 6 * * * /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
    echo ""
    echo "Every Monday at 8:00 AM:"
    echo "0 8 * * 1 /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
    echo ""
    echo "Every hour during business hours (9 AM - 5 PM, Mon-Fri):"
    echo "0 9-17 * * 1-5 /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
    echo ""
    echo "Every 15 minutes (for testing):"
    echo "*/15 * * * * /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
    echo ""
    echo "Every 4 hours:"
    echo "0 */4 * * * /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
    echo ""
    echo "First day of every month at midnight:"
    echo "0 0 1 * * /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
}

# Function to test the setup
test_setup() {
    echo ""
    echo "🧪 Testing Setup..."
    echo "-------------------"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Run setup first."
        return 1
    fi
    
    # Check if credentials exist
    if [ ! -f "credentials.json" ]; then
        echo "⚠️  credentials.json not found. You need to set up Google API credentials."
        echo "   See SETUP_CREDENTIALS.md for instructions."
    else
        echo "✅ credentials.json found"
    fi
    
    # Check if URLs are configured
    if [ ! -f "config/urls.txt" ] || [ ! -s "config/urls.txt" ] || grep -q "^#" config/urls.txt; then
        echo "⚠️  No URLs configured in config/urls.txt"
        echo "   Edit config/urls.txt and add your Google Sheets URLs"
    else
        echo "✅ URLs configured"
    fi
    
    # Test script execution
    echo ""
    echo "Testing script execution..."
    if [ -x "run_sheets_combiner.sh" ]; then
        echo "✅ run_sheets_combiner.sh is executable"
    else
        echo "❌ run_sheets_combiner.sh is not executable"
        chmod +x run_sheets_combiner.sh
        echo "✅ Fixed permissions"
    fi
    
    # Test basic application
    echo ""
    echo "Testing application..."
    source venv/bin/activate
    if python main.py --help > /dev/null 2>&1; then
        echo "✅ Application runs successfully"
    else
        echo "❌ Application has issues"
    fi
    deactivate
}

# Function to install cron job
install_cron() {
    echo ""
    read -p "Enter cron schedule (e.g., '0 6 * * *' for daily 6 AM): " schedule
    
    if [ -z "$schedule" ]; then
        echo "❌ No schedule provided"
        return 1
    fi
    
    cron_line="$schedule /home/desops/google-sheets-combiner/run_sheets_combiner.sh"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "run_sheets_combiner.sh"; then
        echo "⚠️  Cron job already exists. Remove it first with option 4."
        return 1
    fi
    
    # Add cron job
    (crontab -l 2>/dev/null; echo "$cron_line") | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job installed successfully:"
        echo "   $cron_line"
    else
        echo "❌ Failed to install cron job"
    fi
}

# Function to remove cron job
remove_cron() {
    echo ""
    echo "Removing existing cron jobs..."
    
    # Remove lines containing run_sheets_combiner.sh
    crontab -l 2>/dev/null | grep -v "run_sheets_combiner.sh" | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job removed successfully"
    else
        echo "❌ Failed to remove cron job"
    fi
}

# Function to show current cron jobs
show_current_cron() {
    echo ""
    echo "📋 Current Cron Jobs:"
    echo "--------------------"
    
    if crontab -l 2>/dev/null | grep -q "run_sheets_combiner.sh"; then
        echo "Active Google Sheets Combiner jobs:"
        crontab -l 2>/dev/null | grep "run_sheets_combiner.sh"
    else
        echo "No Google Sheets Combiner cron jobs found"
    fi
    
    echo ""
    echo "All cron jobs:"
    crontab -l 2>/dev/null || echo "No cron jobs configured"
}

# Function to show logs
show_logs() {
    echo ""
    echo "📊 Recent Logs:"
    echo "--------------"
    
    if [ -f "logs/cron.log" ]; then
        echo "Last 20 lines of cron.log:"
        tail -20 logs/cron.log
    else
        echo "No logs found yet. Logs will appear in logs/cron.log after first run."
    fi
}

# Main menu
while true; do
    echo ""
    echo "Choose an option:"
    echo "1. Show cron schedule examples"
    echo "2. Test setup"
    echo "3. Install cron job"
    echo "4. Remove cron job"
    echo "5. Show current cron jobs"
    echo "6. Show logs"
    echo "7. Manual test run"
    echo "8. Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1)
            show_cron_examples
            ;;
        2)
            test_setup
            ;;
        3)
            install_cron
            ;;
        4)
            remove_cron
            ;;
        5)
            show_current_cron
            ;;
        6)
            show_logs
            ;;
        7)
            echo ""
            echo "🔄 Running manual test..."
            ./run_sheets_combiner.sh
            echo "✅ Manual test complete. Check logs/cron.log for output."
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter 1-8."
            ;;
    esac
done
