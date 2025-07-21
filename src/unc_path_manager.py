#!/usr/bin/env python3
"""
UNC Path Manager for handling network drive operations
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path, PurePath
from typing import Dict, Optional, List, Union
import re


class UNCPathManager:
    """Manages UNC drive paths and network file operations"""
    
    def __init__(self, config_file: str = "config/output_config.json"):
        """Initialize with configuration file"""
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Return default configuration if file doesn't exist
                return self._get_default_config()
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️  Warning: Could not load output config: {e}")
            print("Using default local output settings")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration when config file is not available"""
        return {
            "output_paths": {
                "default_local": "output/combined_sheets.xlsx",
                "unc_drive_enabled": False,
                "unc_base_path": "",
                "unc_filename_template": "combined_sheets_{timestamp}.xlsx",
                "backup_to_local": True,
                "create_subdirectories": True
            },
            "fallback_options": {
                "use_local_on_unc_failure": True,
                "create_missing_directories": True,
                "verify_path_accessibility": True,
                "retry_attempts": 3
            }
        }
    
    def is_unc_enabled(self) -> bool:
        """Check if UNC drive output is enabled"""
        return self.config.get("output_paths", {}).get("unc_drive_enabled", False)
    
    def validate_unc_path(self, unc_path: str) -> bool:
        """Validate UNC path format and security"""
        if not unc_path.startswith("\\\\"):
            return False
        
        # Check against allowed patterns if security is configured
        security_config = self.config.get("security", {})
        if security_config.get("validate_unc_path", False):
            allowed_patterns = security_config.get("allowed_unc_patterns", [])
            if allowed_patterns:
                for pattern in allowed_patterns:
                    # Convert glob pattern to regex
                    regex_pattern = pattern.replace("\\", "\\\\").replace("*", ".*")
                    if re.match(regex_pattern, unc_path, re.IGNORECASE):
                        return True
                return False
        
        return True
    
    def check_unc_accessibility(self, unc_path: str) -> bool:
        """Check if UNC path is accessible and writable"""
        try:
            # Extract directory from full path
            unc_dir = os.path.dirname(unc_path)
            
            # Check if directory exists
            if not os.path.exists(unc_dir):
                if self.config.get("fallback_options", {}).get("create_missing_directories", True):
                    try:
                        os.makedirs(unc_dir, exist_ok=True)
                        print(f"✓ Created UNC directory: {unc_dir}")
                    except OSError as e:
                        print(f"❌ Cannot create UNC directory {unc_dir}: {e}")
                        return False
                else:
                    print(f"❌ UNC directory does not exist: {unc_dir}")
                    return False
            
            # Check write permissions by creating a test file
            test_file = os.path.join(unc_dir, ".write_test_temp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                return True
            except (OSError, PermissionError) as e:
                print(f"❌ No write permission to UNC path {unc_dir}: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking UNC accessibility: {e}")
            return False
    
    def get_output_path(self, filename_override: Optional[str] = None, 
                       template_vars: Optional[Dict] = None) -> str:
        """Get the output path based on configuration"""
        output_config = self.config.get("output_paths", {})
        
        # If UNC is not enabled, use local path
        if not self.is_unc_enabled():
            local_path = filename_override or output_config.get("default_local", "output/combined_sheets.xlsx")
            return os.path.abspath(local_path)
        
        # Build UNC path
        unc_base = output_config.get("unc_base_path", "")
        filename_template = output_config.get("unc_filename_template", "combined_sheets_{timestamp}.xlsx")
        
        if not unc_base:
            print("⚠️  UNC enabled but no base path configured, using local path")
            return os.path.abspath(output_config.get("default_local", "output/combined_sheets.xlsx"))
        
        # Process template variables
        if template_vars is None:
            template_vars = {}
        
        # Add default template variables
        now = datetime.now()
        default_vars = {
            "timestamp": now.strftime("%Y%m%d_%H%M%S"),
            "date": now.strftime("%Y-%m-%d"),
            "year": now.strftime("%Y"),
            "month": now.strftime("%m"),
            "day": now.strftime("%d")
        }
        default_vars.update(template_vars)
        
        # Use override filename or format template
        if filename_override:
            filename = filename_override
        else:
            try:
                filename = filename_template.format(**default_vars)
            except KeyError as e:
                print(f"⚠️  Template variable missing: {e}, using default filename")
                filename = f"combined_sheets_{default_vars['timestamp']}.xlsx"
        
        # Construct full UNC path
        unc_path = os.path.join(unc_base, filename).replace("/", "\\")
        
        return unc_path
    
    def save_file_safely(self, source_file: str, target_path: str) -> bool:
        """Save file to target path with fallback options"""
        output_config = self.config.get("output_paths", {})
        fallback_config = self.config.get("fallback_options", {})
        
        # If it's a UNC path, validate and check accessibility
        if target_path.startswith("\\\\"):
            if not self.validate_unc_path(target_path):
                print(f"❌ Invalid UNC path: {target_path}")
                return self._fallback_to_local(source_file, output_config)
            
            if fallback_config.get("verify_path_accessibility", True):
                if not self.check_unc_accessibility(target_path):
                    print(f"❌ UNC path not accessible: {target_path}")
                    return self._fallback_to_local(source_file, output_config)
        
        # Attempt to save file
        retry_attempts = fallback_config.get("retry_attempts", 3)
        
        for attempt in range(retry_attempts):
            try:
                # Ensure target directory exists
                target_dir = os.path.dirname(target_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                # Copy the file
                shutil.copy2(source_file, target_path)
                print(f"✅ File saved successfully: {target_path}")
                
                # Create backup to local if configured
                if (target_path.startswith("\\\\") and 
                    output_config.get("backup_to_local", True)):
                    self._create_local_backup(source_file, output_config)
                
                return True
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed to save to {target_path}: {e}")
                if attempt < retry_attempts - 1:
                    print(f"🔄 Retrying... ({attempt + 2}/{retry_attempts})")
        
        # All attempts failed, try fallback
        print(f"❌ All attempts failed to save to: {target_path}")
        return self._fallback_to_local(source_file, output_config)
    
    def _fallback_to_local(self, source_file: str, output_config: Dict) -> bool:
        """Fallback to local save when UNC fails"""
        if not output_config.get("use_local_on_unc_failure", True):
            print("❌ UNC save failed and local fallback is disabled")
            return False
        
        try:
            local_path = output_config.get("default_local", "output/combined_sheets.xlsx")
            local_path = os.path.abspath(local_path)
            
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            shutil.copy2(source_file, local_path)
            print(f"✅ Fallback: File saved locally: {local_path}")
            return True
            
        except Exception as e:
            print(f"❌ Fallback to local also failed: {e}")
            return False
    
    def _create_local_backup(self, source_file: str, output_config: Dict) -> None:
        """Create a local backup copy of the file"""
        try:
            backup_path = output_config.get("default_local", "output/combined_sheets.xlsx")
            backup_path = os.path.abspath(backup_path)
            
            # Ensure backup directory exists
            backup_dir = os.path.dirname(backup_path)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            shutil.copy2(source_file, backup_path)
            print(f"📋 Local backup created: {backup_path}")
            
        except Exception as e:
            print(f"⚠️  Could not create local backup: {e}")
    
    def get_configuration_summary(self) -> str:
        """Get a summary of current configuration"""
        output_config = self.config.get("output_paths", {})
        fallback_config = self.config.get("fallback_options", {})
        
        summary = []
        summary.append("📁 Output Path Configuration:")
        summary.append(f"  UNC Drive Enabled: {self.is_unc_enabled()}")
        
        if self.is_unc_enabled():
            summary.append(f"  UNC Base Path: {output_config.get('unc_base_path', 'Not configured')}")
            summary.append(f"  Filename Template: {output_config.get('unc_filename_template', 'Default')}")
            summary.append(f"  Create Subdirectories: {output_config.get('create_subdirectories', True)}")
            summary.append(f"  Backup to Local: {output_config.get('backup_to_local', True)}")
        
        summary.append(f"  Default Local Path: {output_config.get('default_local', 'output/combined_sheets.xlsx')}")
        summary.append(f"  Fallback to Local: {fallback_config.get('use_local_on_unc_failure', True)}")
        summary.append(f"  Retry Attempts: {fallback_config.get('retry_attempts', 3)}")
        
        return "\n".join(summary)


# Global instance for easy access
unc_path_manager = UNCPathManager()
