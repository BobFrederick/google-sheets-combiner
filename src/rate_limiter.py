#!/usr/bin/env python3
"""
Rate limiting decorators for Google APIs
"""

import time
import functools
from typing import Callable, Any
from googleapiclient.errors import HttpError


def rate_limit(calls_per_second: float = 10) -> Callable:
    """
    Decorator to rate limit API calls
    
    Args:
        calls_per_second: Maximum number of calls per second
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


def retry_on_quota_error(max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Decorator to retry API calls on quota/rate limit errors
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except HttpError as e:
                    last_exception = e
                    
                    if e.resp.status == 429:  # Rate limit exceeded
                        wait_time = backoff_factor ** attempt
                        print(f"⚠️  Rate limit hit (attempt {attempt + 1}/"
                              f"{max_retries + 1}) - waiting {wait_time:.1f}s")
                        time.sleep(wait_time)
                        continue
                        
                    elif e.resp.status in [500, 502, 503, 504]:  # Server errors
                        wait_time = backoff_factor ** attempt
                        print(f"⚠️  Server error (attempt {attempt + 1}/"
                              f"{max_retries + 1}) - waiting {wait_time:.1f}s")
                        time.sleep(wait_time)
                        continue
                        
                    else:
                        # Not a retryable error
                        raise
                        
                except Exception as e:
                    # Non-HTTP errors, don't retry
                    raise
                    
            # All retries exhausted
            print(f"❌ All {max_retries + 1} attempts failed")
            raise last_exception
            
        return wrapper
    return decorator


def quota_aware_api_call(api_type: str = "drive", operation_type: str = "read"):
    """
    Decorator that combines rate limiting, quota monitoring, and retry logic
    
    Args:
        api_type: Type of API ('drive' or 'sheets')
        operation_type: Type of operation for quota estimation
    """
    from src.quota_monitor import quota_monitor
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        @retry_on_quota_error(max_retries=3, backoff_factor=2.0)
        @rate_limit(calls_per_second=10 if api_type == "drive" else 5)
        def wrapper(*args, **kwargs) -> Any:
            # Check if we should pause for quota limits
            pause_time = quota_monitor.should_pause_for_quota()
            if pause_time:
                print(f"⏸️  Pausing {pause_time}s to avoid quota limits...")
                time.sleep(pause_time)
            
            # Enforce additional rate limiting
            quota_monitor.enforce_rate_limit(api_type)
            
            # Make the API call
            result = func(*args, **kwargs)
            
            # Log the request for quota tracking
            if api_type == "drive":
                quota_monitor.log_drive_request(operation_type)
            elif api_type == "sheets":
                quota_monitor.log_sheets_request(operation_type)
                
            return result
            
        return wrapper
    return decorator
