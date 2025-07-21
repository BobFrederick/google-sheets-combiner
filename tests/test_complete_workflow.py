#!/usr/bin/env python3
"""
Test the complete workflow with cleanup functionality
"""

import subprocess
import sys
import os

def run_complete_workflow():
    """Test the complete workflow with cleanup"""
    
    print("🧪 Testing Complete Workflow with Cleanup")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(r"c:\Users\bfrederick\Dev\dev_sandbox\google_sheet_combiner")
    
    try:
        # Run the main script with conversion and cleanup
        cmd = [
            sys.executable, "main.py",
            "--convert-excel",
            "--cleanup-originals",
            "--output", "output/combined_sheets_with_cleanup.xlsx"
        ]
        
        print("🚀 Running command:")
        print(f"   {' '.join(cmd)}")
        print("\n" + "-" * 50)
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=r"c:\Users\bfrederick\Dev\dev_sandbox\google_sheet_combiner"
        )
        
        # Print output
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ Workflow completed successfully!")
            print("🗂️ Converted Google Sheets should be cleaned up")
            print("📁 Check output/combined_sheets_with_cleanup.xlsx")
        else:
            print("\n❌ Workflow failed!")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        return False

if __name__ == "__main__":
    success = run_complete_workflow()
    
    if success:
        print("\n🎉 Complete workflow test PASSED!")
    else:
        print("\n⚠️ Complete workflow test FAILED!")
