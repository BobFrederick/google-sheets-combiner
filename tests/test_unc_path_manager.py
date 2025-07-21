#!/usr/bin/env python3
"""
Test UNC Path Manager functionality
"""

import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.unc_path_manager import UNCPathManager


class TestUNCPathManager(unittest.TestCase):
    """Test UNC Path Manager functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock configuration
        self.test_config = {
            "output_paths": {
                "default_local": "output/test_combined.xlsx",
                "unc_drive_enabled": True,
                "unc_base_path": "\\\\testserver\\share\\reports",
                "unc_filename_template": "combined_{timestamp}.xlsx",
                "backup_to_local": True,
                "create_subdirectories": True
            },
            "fallback_options": {
                "use_local_on_unc_failure": True,
                "create_missing_directories": True,
                "verify_path_accessibility": True,
                "retry_attempts": 3
            },
            "security": {
                "validate_unc_path": True,
                "allowed_unc_patterns": [
                    "\\\\testserver\\*"
                ],
                "require_write_permissions": True
            }
        }
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('os.path.exists')
    def test_load_config_success(self, mock_exists, mock_json_load, mock_file):
        """Test successful configuration loading"""
        mock_exists.return_value = True
        mock_json_load.return_value = self.test_config
        
        manager = UNCPathManager("test_config.json")
        
        self.assertTrue(manager.is_unc_enabled())
        self.assertEqual(
            manager.config["output_paths"]["unc_base_path"],
            "\\\\testserver\\share\\reports"
        )
    
    def test_validate_unc_path(self):
        """Test UNC path validation"""
        with patch('builtins.open', mock_open()), \
             patch('json.load', return_value=self.test_config), \
             patch('os.path.exists', return_value=True):
            
            manager = UNCPathManager("test_config.json")
            
            # Valid UNC path
            self.assertTrue(manager.validate_unc_path("\\\\testserver\\share\\file.xlsx"))
            
            # Invalid UNC path (not starting with \\)
            self.assertFalse(manager.validate_unc_path("C:\\local\\path\\file.xlsx"))
            
            # Invalid UNC path (not in allowed patterns)
            self.assertFalse(manager.validate_unc_path("\\\\otherserver\\share\\file.xlsx"))
    
    def test_get_output_path_local(self):
        """Test output path generation for local storage"""
        local_config = {
            "output_paths": {
                "default_local": "output/local_test.xlsx",
                "unc_drive_enabled": False
            }
        }
        
        with patch('builtins.open', mock_open()), \
             patch('json.load', return_value=local_config), \
             patch('os.path.exists', return_value=True):
            
            manager = UNCPathManager("test_config.json")
            path = manager.get_output_path()
            
            self.assertFalse(manager.is_unc_enabled())
            self.assertTrue(path.endswith("local_test.xlsx"))
    
    def test_get_output_path_unc(self):
        """Test output path generation for UNC storage"""
        with patch('builtins.open', mock_open()), \
             patch('json.load', return_value=self.test_config), \
             patch('os.path.exists', return_value=True):
            
            manager = UNCPathManager("test_config.json")
            path = manager.get_output_path()
            
            self.assertTrue(manager.is_unc_enabled())
            self.assertTrue(path.startswith("\\\\testserver\\share\\reports"))
            self.assertTrue(path.endswith(".xlsx"))
    
    def test_get_output_path_with_template_vars(self):
        """Test output path generation with template variables"""
        with patch('builtins.open', mock_open()), \
             patch('json.load', return_value=self.test_config), \
             patch('os.path.exists', return_value=True):
            
            manager = UNCPathManager("test_config.json")
            template_vars = {"project_name": "test_project"}
            path = manager.get_output_path(template_vars=template_vars)
            
            self.assertTrue(path.startswith("\\\\testserver\\share\\reports"))
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_check_unc_accessibility_success(self, mock_file, mock_makedirs, mock_exists):
        """Test successful UNC accessibility check"""
        with patch('json.load', return_value=self.test_config):
            manager = UNCPathManager("test_config.json")
            
            # Mock directory exists and file operations succeed
            mock_exists.return_value = True
            mock_file.return_value.__enter__.return_value.write = MagicMock()
            
            # Mock os.remove to avoid actual file operations
            with patch('os.remove'):
                result = manager.check_unc_accessibility("\\\\testserver\\share\\test.xlsx")
            
            self.assertTrue(result)
    
    def test_configuration_summary(self):
        """Test configuration summary generation"""
        with patch('builtins.open', mock_open()), \
             patch('json.load', return_value=self.test_config), \
             patch('os.path.exists', return_value=True):
            
            manager = UNCPathManager("test_config.json")
            summary = manager.get_configuration_summary()
            
            self.assertIn("Output Path Configuration", summary)
            self.assertIn("UNC Drive Enabled: True", summary)
            self.assertIn("\\\\testserver\\share\\reports", summary)


if __name__ == '__main__':
    # Create a simple test run
    print("🧪 Testing UNC Path Manager...")
    
    # Test default configuration
    manager = UNCPathManager("nonexistent_config.json")
    print(f"Default config loaded: {not manager.is_unc_enabled()}")
    
    # Test path generation
    local_path = manager.get_output_path("test_output.xlsx")
    print(f"Generated path: {local_path}")
    
    # Test configuration summary
    print("\n" + manager.get_configuration_summary())
    
    print("\n✅ Basic UNC Path Manager test completed!")
    
    # Run unit tests if available
    try:
        unittest.main(argv=[''], exit=False, verbosity=2)
    except SystemExit:
        pass
