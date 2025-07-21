#!/usr/bin/env python3
"""
Google Sheets Combiner
Extract data from multiple Google Sheets and combine into a single Excel file.
"""

import argparse
import os
import sys
from src.config import Config
from src.google_sheets_extractor import GoogleSheetsExtractor
from src.excel_combiner import ExcelCombiner
from src.drive_converter import DriveFileConverter
from src.quota_monitor import quota_monitor
from src.unc_path_manager import unc_path_manager


def create_urls_file():
    """Create a sample urls.txt file if it doesn't exist"""
    urls_file = 'config/urls.txt'
    if not os.path.exists(urls_file):
        with open(urls_file, 'w') as f:
            f.write("""# Add your Google Sheets URLs here (one per line)
# Example:
# https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit#gid=0
# https://docs.google.com/spreadsheets/d/1XYZ789UVW012/edit#gid=0

""")
        print(f"Created sample {urls_file} file. Please add your Google Sheets URLs.")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description='Combine Google Sheets into Excel')
    parser.add_argument('--output', '-o', 
                       help='Output Excel filename', 
                       default=Config.OUTPUT_FILENAME)
    parser.add_argument('--max-tabs', '-m', 
                       type=int,
                       help='Maximum tabs per sheet', 
                       default=Config.MAX_TABS_PER_SHEET)
    parser.add_argument('--urls-file', '-u',
                       help='File containing Google Sheets URLs',
                       default='config/urls.txt')
    parser.add_argument('--convert-excel', '-c',
                       action='store_true',
                       help='Auto-convert Excel files to Google Sheets')
    parser.add_argument('--cleanup-originals',
                       action='store_true',
                       help='Delete original Excel files after conversion')
    parser.add_argument('--keep-converted',
                       action='store_true',
                       help='Keep intermediate Google Sheets after combination')
    parser.add_argument('--unc-path',
                       help='Save to UNC network path (overrides config)')
    parser.add_argument('--show-path-config',
                       action='store_true',
                       help='Show current output path configuration')
    
    args = parser.parse_args()
    
    try:
        # Show path configuration if requested
        if args.show_path_config:
            print(unc_path_manager.get_configuration_summary())
            return 0
        
        # Validate configuration
        Config.validate_config()
        
        # Get URLs
        sheet_urls = Config.get_sheet_urls()
        if not sheet_urls:
            if not create_urls_file():
                return 1
            print("Please add Google Sheets URLs to config/urls.txt and run again.")
            return 1
        
        # Determine output path
        if args.unc_path:
            output_path = args.unc_path
            print(f"Using UNC path override: {output_path}")
        else:
            output_path = unc_path_manager.get_output_path(args.output)
            if unc_path_manager.is_unc_enabled():
                print(f"Using configured UNC path: {output_path}")
            else:
                print(f"Using local path: {output_path}")
        
        print(f"Found {len(sheet_urls)} Google Sheets to process")
        
        # Initialize converter for potential cleanup
        converter = None
        
        # Convert Excel files if requested
        if args.convert_excel:
            print("\n🔄 Converting Excel files to Google Sheets...")
            converter = DriveFileConverter()
            sheet_urls = converter.convert_all_urls(
                sheet_urls, 
                cleanup_originals=args.cleanup_originals
            )
        
        print("-" * 50)
        
        # Extract data from Google Sheets
        extractor = GoogleSheetsExtractor()
        all_data = extractor.extract_all_data(sheet_urls)
        
        if not all_data:
            print("No data extracted from any sheets!")
            return 1
        
        print(f"\nExtracted data from {len(all_data)} worksheets")
        print("-" * 50)
        
        # Combine into Excel
        combiner = ExcelCombiner()
        
        for tab_name, df in all_data.items():
            print(f"Adding to Excel: {tab_name} ({len(df)} rows)")
            combiner.add_dataframe(df, tab_name)
        
        # Save the file
        print("-" * 50)
        if combiner.save(output_path):
            summary = combiner.get_sheet_summary()
            print("\nSummary:")
            for sheet, row_count in summary.items():
                print(f"  {sheet}: {row_count} rows")
            print(f"\nTotal worksheets: {len(summary)}")
            
            # Clean up intermediate Google Sheets if conversion was used
            if args.convert_excel and converter and not args.keep_converted:
                converter.cleanup_converted_sheets(
                    sheet_urls, 
                    keep_converted_sheets=args.keep_converted
                )
            
            # Report quota usage
            print("\n" + "=" * 50)
            print("📊 API Usage Summary:")
            status = quota_monitor.get_status()
            print(f"Drive API requests: {status['drive_requests_per_100s']}")
            print(f"Sheets API requests: {status['sheets_requests_per_minute']}")
            print(f"Drive quota used: {status['daily_drive_quota_used']:,} units")
            if status['daily_drive_quota_used'] > 0:
                daily_quota = Config.QUOTA_LIMITS['drive_daily']
                usage_pct = (status['daily_drive_quota_used'] / daily_quota) * 100
                print(f"Drive quota usage: {usage_pct:.1f}% of daily limit")
            print("=" * 50)
            
            return 0
        else:
            return 1
            
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        print("\nSetup instructions:")
        print("1. Go to Google Cloud Console")
        print("2. Enable Google Sheets API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download and save as 'credentials.json'")
        return 1
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
