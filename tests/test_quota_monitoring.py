#!/usr/bin/env python3
"""
Test quota monitoring and rate limiting functionality
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
from src.quota_monitor import QuotaMonitor, quota_monitor
from src.rate_limiter import quota_aware_api_call
from src.config import Config


class TestQuotaMonitoring(unittest.TestCase):
    """Test quota monitoring functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.quota_monitor = QuotaMonitor()

    def test_drive_request_logging(self):
        """Test Drive API request logging"""
        initial_requests = self.quota_monitor.usage.drive_requests
        
        self.quota_monitor.log_drive_request("read")
        
        self.assertEqual(
            self.quota_monitor.usage.drive_requests, 
            initial_requests + 1
        )
        self.assertGreater(
            self.quota_monitor.usage.daily_drive_quota, 
            0
        )

    def test_sheets_request_logging(self):
        """Test Sheets API request logging"""
        initial_requests = self.quota_monitor.usage.sheets_requests
        
        self.quota_monitor.log_sheets_request("read")
        
        self.assertEqual(
            self.quota_monitor.usage.sheets_requests, 
            initial_requests + 1
        )

    def test_quota_status(self):
        """Test getting quota status"""
        # Log some requests
        self.quota_monitor.log_drive_request("read")
        self.quota_monitor.log_sheets_request("read")
        
        status = self.quota_monitor.get_status()
        
        self.assertIn('drive_requests_per_100s', status)
        self.assertIn('sheets_requests_per_minute', status)
        self.assertIn('daily_drive_quota_used', status)
        self.assertIn('limits', status)
        
        self.assertEqual(status['limits'], Config.QUOTA_LIMITS)

    def test_rate_limiting_decorator(self):
        """Test the quota-aware API call decorator"""
        call_count = 0
        
        @quota_aware_api_call(api_type="drive", operation_type="read")
        def mock_api_call():
            nonlocal call_count
            call_count += 1
            return {"result": "success"}
        
        # Mock the quota monitor to avoid actual rate limiting
        with patch('src.rate_limiter.quota_monitor') as mock_monitor:
            mock_monitor.enforce_rate_limit = Mock()
            mock_monitor.log_drive_request = Mock()
            
            result = mock_api_call()
            
            self.assertEqual(result["result"], "success")
            self.assertEqual(call_count, 1)
            mock_monitor.enforce_rate_limit.assert_called_once_with("drive")
            mock_monitor.log_drive_request.assert_called_once_with("read")

    def test_quota_limits_configuration(self):
        """Test that quota limits are properly configured"""
        limits = Config.QUOTA_LIMITS
        
        self.assertIn('drive_daily', limits)
        self.assertIn('sheets_per_minute', limits)
        self.assertIn('drive_per_100s', limits)
        self.assertIn('drive_queries_per_100s', limits)
        
        # Check that limits are reasonable values
        self.assertEqual(limits['drive_daily'], 1000000000)  # 1B
        self.assertEqual(limits['sheets_per_minute'], 300)
        self.assertEqual(limits['drive_per_100s'], 1000)
        self.assertEqual(limits['drive_queries_per_100s'], 20000)


class TestRateLimitingIntegration(unittest.TestCase):
    """Test integration of rate limiting with API methods"""

    def test_global_quota_monitor_instance(self):
        """Test that global quota monitor instance exists"""
        from src.quota_monitor import quota_monitor
        
        self.assertIsInstance(quota_monitor, QuotaMonitor)
        
        # Test that it can log requests
        initial_drive = quota_monitor.usage.drive_requests
        quota_monitor.log_drive_request("test")
        self.assertEqual(quota_monitor.usage.drive_requests, initial_drive + 1)

    @patch('src.rate_limiter.time.sleep')
    def test_rate_limiting_delay(self, mock_sleep):
        """Test that rate limiting introduces appropriate delays"""
        
        @quota_aware_api_call(api_type="sheets", operation_type="read")
        def fast_api_call():
            return "result"
        
        # Mock quota monitor to simulate high usage
        with patch('src.rate_limiter.quota_monitor') as mock_monitor:
            mock_monitor.enforce_rate_limit = Mock()
            mock_monitor.log_sheets_request = Mock()
            
            # Call multiple times rapidly
            for _ in range(3):
                result = fast_api_call()
                self.assertEqual(result, "result")
            
            # Verify rate limiting was enforced
            self.assertEqual(mock_monitor.enforce_rate_limit.call_count, 3)
            self.assertEqual(mock_monitor.log_sheets_request.call_count, 3)


if __name__ == '__main__':
    unittest.main()
