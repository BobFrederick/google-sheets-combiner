#!/usr/bin/env python3
"""
Project Structure Maintenance Script
Helps keep the project organized by checking for misplaced files
"""

from pathlib import Path


def check_project_structure():
    """Check for files that might be in the wrong location"""
    
    print("🔍 Checking Project Structure")
    print("=" * 50)
    
    root_dir = Path(".")
    issues = []
    
    # Check for test files in root
    root_test_files = list(root_dir.glob("test_*.py"))
    if root_test_files:
        file_names = [f.name for f in root_test_files]
        issues.append(f"❌ Test files in root: {file_names}")
        print("   → Should be in tests/ directory")
    
    # Check for utility files in root
    utility_patterns = [
        "diagnose_*.py", "debug_*.py", "check_*.py", "*_util.py"
    ]
    for pattern in utility_patterns:
        util_files = list(root_dir.glob(pattern))
        if util_files:
            file_names = [f.name for f in util_files]
            issues.append(f"❌ Utility files in root: {file_names}")
            print("   → Should be in utils/ directory")
    
    # Check for config files in root
    config_files = ["urls.txt", "config.py"]
    for config_file in config_files:
        if (root_dir / config_file).exists():
            issues.append(f"❌ Config file in root: {config_file}")
            print("   → Should be in config/ or src/ directory")
    
    # Check for docs in root
    doc_files = list(root_dir.glob("*.md"))
    excluded_docs = ["README.md", "STRUCTURE.md"]
    misplaced_docs = [f for f in doc_files if f.name not in excluded_docs]
    if misplaced_docs:
        file_names = [f.name for f in misplaced_docs]
        issues.append(f"❌ Documentation in root: {file_names}")
        print("   → Should be in docs/ directory")
    
    # Check for Python cache directories
    cache_dirs = (list(root_dir.glob("*/__pycache__")) +
                  list(root_dir.glob("__pycache__")))
    # Exclude .venv directory
    cache_dirs = [d for d in cache_dirs if not str(d).startswith(".venv")]
    if cache_dirs:
        dir_names = [str(d) for d in cache_dirs]
        issues.append(f"⚠️ Python cache directories found: {dir_names}")
        print("   → Can be safely deleted")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues:
        print("✅ Project structure is clean and organized!")
        print("\n📁 Current structure:")
        print("   ├── src/          # Core application code")
        print("   ├── tests/        # Test scripts")
        print("   ├── utils/        # Utilities and diagnostics")
        print("   ├── config/       # Configuration files")
        print("   ├── docs/         # Documentation")
        print("   ├── output/       # Generated files")
        print("   └── main.py       # Entry point")
    else:
        print(f"⚠️ Found {len(issues)} structural issues:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Run cleanup commands to fix these issues.")
    
    return len(issues) == 0


def cleanup_suggestions():
    """Provide cleanup suggestions"""
    
    print("\n🧹 Cleanup Commands:")
    print("-" * 30)
    print("# Move test files:")
    print("move test_*.py tests\\")
    print("")
    print("# Move utility files:")
    print("move diagnose_*.py utils\\")
    print("move debug_*.py utils\\")
    print("")
    print("# Move config files:")
    print("move urls.txt config\\")
    print("")
    print("# Remove cache:")
    print("rmdir /s /q __pycache__")
    print("rmdir /s /q *\\__pycache__")


if __name__ == "__main__":
    is_clean = check_project_structure()
    
    if not is_clean:
        cleanup_suggestions()
