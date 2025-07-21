#!/usr/bin/env python3
"""
Quota Monitor for Google APIs
Tracks API usage to stay within free tier limits
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
from src.config import Config


@dataclass
class QuotaUsage:
    """Track quota usage for different API endpoints"""
    drive_requests: int = 0
    sheets_requests: int = 0
    drive_queries: int = 0
    start_time: float = 0
    daily_drive_quota: int = 0
    last_reset: datetime = None

    def __post_init__(self):
        if self.start_time == 0:
            self.start_time = time.time()
        if self.last_reset is None:
            self.last_reset = datetime.now()


class QuotaMonitor:
    """Monitor and enforce Google API quota limits"""
    
    def __init__(self):
        self.usage = QuotaUsage()
        self.minute_start = time.time()
        self.hundred_second_start = time.time()
        
    def log_drive_request(self, operation_type: str = "read") -> None:
        """Log a Drive API request"""
        self.usage.drive_requests += 1
        
        # Estimate quota units (rough approximation)
        quota_units = self._estimate_quota_units(operation_type)
        self.usage.daily_drive_quota += quota_units
        
        self._check_limits()
        self._print_progress("Drive", self.usage.drive_requests)
        
    def log_sheets_request(self, operation_type: str = "read") -> None:
        """Log a Sheets API request"""
        self.usage.sheets_requests += 1
        self._check_limits()
        self._print_progress("Sheets", self.usage.sheets_requests)
        
    def log_drive_query(self) -> None:
        """Log a Drive API query (search operation)"""
        self.usage.drive_queries += 1
        self._check_limits()
        
    def _estimate_quota_units(self, operation_type: str) -> int:
        """Estimate quota units for different operations"""
        quota_map = {
            "read": 1,
            "write": 10,
            "create": 100,
            "copy": 100,
            "convert": 200,
            "delete": 100,
        }
        return quota_map.get(operation_type, 1)
        
    def _check_limits(self) -> None:
        """Check if approaching any quota limits"""
        current_time = time.time()
        
        # Check per-minute limits (Sheets API)
        if current_time - self.minute_start >= 60:
            if self.usage.sheets_requests > 280:
                print("⚠️  WARNING: Approaching Sheets API limit "
                      f"({self.usage.sheets_requests}/300 per minute)")
            self._reset_minute_counters()
            
        # Check per-100-second limits (Drive API)
        if current_time - self.hundred_second_start >= 100:
            if self.usage.drive_requests > 950:
                print("⚠️  WARNING: Approaching Drive API request limit "
                      f"({self.usage.drive_requests}/1000 per 100s)")
            if self.usage.drive_queries > 19000:
                print("⚠️  WARNING: Approaching Drive API query limit "
                      f"({self.usage.drive_queries}/20000 per 100s)")
            self._reset_hundred_second_counters()
            
        # Check daily limits
        if self._is_new_day():
            self._reset_daily_counters()
            
        if self.usage.daily_drive_quota > 900000000:  # 90% of daily limit
            print("⚠️  WARNING: Approaching daily Drive API quota "
                  f"({self.usage.daily_drive_quota:,}/1,000,000,000)")
    
    def _reset_minute_counters(self) -> None:
        """Reset per-minute counters"""
        if self.usage.sheets_requests > 0:
            print(f"📊 Last minute: {self.usage.sheets_requests} "
                  "Sheets API requests")
        self.usage.sheets_requests = 0
        self.minute_start = time.time()
        
    def _reset_hundred_second_counters(self) -> None:
        """Reset per-100-second counters"""
        if self.usage.drive_requests > 0 or self.usage.drive_queries > 0:
            print(f"📊 Last 100s: {self.usage.drive_requests} "
                  f"Drive requests, {self.usage.drive_queries} queries")
        self.usage.drive_requests = 0
        self.usage.drive_queries = 0
        self.hundred_second_start = time.time()
        
    def _reset_daily_counters(self) -> None:
        """Reset daily counters"""
        print(f"📅 Daily reset: Used {self.usage.daily_drive_quota:,} "
              "Drive API quota units yesterday")
        self.usage.daily_drive_quota = 0
        self.usage.last_reset = datetime.now()
        
    def _is_new_day(self) -> bool:
        """Check if it's a new day since last reset"""
        return datetime.now().date() > self.usage.last_reset.date()
        
    def _print_progress(self, api_name: str, count: int) -> None:
        """Print progress for API requests"""
        if count % 10 == 0:  # Print every 10 requests
            print(f"📊 {api_name} API: {count} requests processed")
            
    def get_status(self) -> Dict:
        """Get current quota usage status"""
        elapsed_minutes = (time.time() - self.minute_start) / 60
        elapsed_100s = (time.time() - self.hundred_second_start) / 100
        
        return {
            'drive_requests_per_100s': self.usage.drive_requests,
            'sheets_requests_per_minute': self.usage.sheets_requests,
            'drive_queries_per_100s': self.usage.drive_queries,
            'daily_drive_quota_used': self.usage.daily_drive_quota,
            'time_in_current_minute': elapsed_minutes,
            'time_in_current_100s': elapsed_100s,
            'limits': Config.QUOTA_LIMITS
        }
        
    def enforce_rate_limit(self, api_type: str) -> None:
        """Enforce rate limiting with delays if needed"""
        if api_type == "drive":
            rate_limit = Config.DRIVE_API_RATE_LIMIT
            if self.usage.drive_requests >= rate_limit:
                sleep_time = 1.0 / rate_limit
                print(f"⏱️  Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
                
        elif api_type == "sheets":
            rate_limit = Config.SHEETS_API_RATE_LIMIT
            if self.usage.sheets_requests >= rate_limit:
                sleep_time = 1.0 / rate_limit
                print(f"⏱️  Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
                
    def should_pause_for_quota(self) -> Optional[int]:
        """Check if we should pause to avoid hitting quota limits"""
        current_time = time.time()
        
        # If approaching Sheets API limit, pause until next minute
        if self.usage.sheets_requests > 280:
            time_until_reset = 60 - (current_time - self.minute_start)
            if time_until_reset > 0:
                return int(time_until_reset) + 1
                
        # If approaching Drive API limit, pause until next 100s period
        if self.usage.drive_requests > 950:
            time_until_reset = 100 - (current_time - self.hundred_second_start)
            if time_until_reset > 0:
                return int(time_until_reset) + 1
                
        return None
        
    def print_summary(self) -> None:
        """Print a summary of quota usage"""
        status = self.get_status()
        print("\n" + "="*50)
        print("📊 QUOTA USAGE SUMMARY")
        print("="*50)
        print(f"Drive API requests (per 100s): "
              f"{status['drive_requests_per_100s']}/1000")
        print(f"Sheets API requests (per minute): "
              f"{status['sheets_requests_per_minute']}/300")
        print(f"Drive queries (per 100s): "
              f"{status['drive_queries_per_100s']}/20000")
        print(f"Daily Drive quota used: "
              f"{status['daily_drive_quota_used']:,}/1,000,000,000")
        print("="*50)


# Global quota monitor instance
quota_monitor = QuotaMonitor()
