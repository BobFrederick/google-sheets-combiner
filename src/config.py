import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Google API settings
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    # Output settings
    OUTPUT_FILENAME = os.getenv('OUTPUT_FILENAME', 'output/combined_sheets.xlsx')
    MAX_TABS_PER_SHEET = int(os.getenv('MAX_TABS_PER_SHEET', '10'))
    REMOVE_EMPTY_SHEETS = os.getenv('REMOVE_EMPTY_SHEETS', 'true').lower() == 'true'
    
    # Rate limiting and quota settings
    DRIVE_API_RATE_LIMIT = 10  # requests per second
    SHEETS_API_RATE_LIMIT = 5  # requests per second
    REQUEST_DELAY = 0.1        # seconds between requests
    MAX_RETRIES = 3            # max retry attempts
    BACKOFF_FACTOR = 2         # exponential backoff multiplier
    
    # Google API Quota Limits (Free Tier)
    QUOTA_LIMITS = {
        'drive_daily': 1000000000,        # 1B quota units per day
        'sheets_per_minute': 300,         # 300 requests/minute
        'drive_per_100s': 1000,          # 1000 requests/100s per user
        'drive_queries_per_100s': 20000,  # 20K queries/100s
    }
    
    # Legacy rate limiting (deprecated - use new settings above)
    REQUESTS_PER_MINUTE = 100
    
    @staticmethod
    def get_sheet_urls() -> List[str]:
        """Get Google Sheets URLs from environment or file"""
        urls = []
        
        # Try to get from .env file
        env_urls = os.getenv('SHEET_URLS', '')
        if env_urls:
            urls.extend([url.strip() for url in env_urls.split(',') if url.strip()])
        
        # Try to get from synced_urls.txt file (Power Automate output)
        synced_urls_file = 'synced_urls.txt'
        if os.path.exists(synced_urls_file):
            with open(synced_urls_file, 'r') as f:
                synced_urls = [line.strip() for line in f.readlines() 
                             if line.strip() and not line.strip().startswith('#')]
                urls.extend(synced_urls)
        
        # Fallback to urls.txt file
        urls_file = 'config/urls.txt'
        if os.path.exists(urls_file):
            with open(urls_file, 'r') as f:
                file_urls = [line.strip() for line in f.readlines() 
                           if line.strip() and not line.strip().startswith('#')]
                urls.extend(file_urls)
        
        return list(set(urls))  # Remove duplicates
    
    @staticmethod
    def extract_sheet_id(url: str) -> str:
        """Extract Google Sheets ID from URL"""
        if '/spreadsheets/d/' in url:
            return url.split('/spreadsheets/d/')[1].split('/')[0]
        raise ValueError(f"Invalid Google Sheets URL: {url}")
    
    @staticmethod
    def validate_config():
        """Validate configuration"""
        if not os.path.exists(Config.CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Google API credentials file '{Config.CREDENTIALS_FILE}' not found. "
                "Please download it from Google Cloud Console."
            )
        
        urls = Config.get_sheet_urls()
        if not urls:
            raise ValueError(
                "No Google Sheets URLs found. Please add them to .env file or create urls.txt"
            )
