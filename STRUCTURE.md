# 📁 Project Structure Guide

This project has been reorganized for better maintainability and development workflow.

## 📂 Folder Structure

```
google_sheet_combiner/
├── src/                    # 🔧 Core source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── drive_converter.py # Excel to Sheets conversion
│   ├── excel_combiner.py  # Excel output generation
│   └── google_sheets_extractor.py # Google Sheets data extraction
├── tests/                  # 🧪 Test files
│   ├── __init__.py
│   ├── test_auth.py       # Authentication tests
│   ├── test_converter.py  # Conversion tests
│   ├── test_direct_access.py # Direct file access tests
│   ├── test_excel_file.py # Excel file analysis
│   ├── test_owned_files.py # Owned files tests
│   ├── test_shared_drive.py # Shared drive tests
│   └── test_working_file.py # Working file tests
├── utils/                  # 🛠️ Utility scripts and tools
│   ├── check_access.py    # File access checker
│   ├── check_file_types.py # File type validator
│   ├── copy_shared_files.py # Shared file copier
│   ├── debug_conversion.py # Conversion debugger
│   ├── debug_urls.py      # URL debugger
│   ├── diagnose_access.py # Access diagnostics
│   ├── setup.py           # Utility setup script
│   └── 1235 SMD_SHARED Work Progress List.xlsx # Sample file
├── config/                 # ⚙️ Configuration files
│   └── urls.txt           # Google Sheets URLs
├── docs/                   # 📚 Documentation
│   └── GOOGLE_API_SETUP.md
├── output/                 # 📊 Generated output files
│   └── combined_sheets.xlsx
├── main.py                 # 🚀 Main entry point
├── requirements.txt        # 📦 Dependencies
├── run.bat                 # 🏃‍♂️ Windows runner script
└── README.md              # 📖 Project documentation
```

## 🎯 Key Benefits

### 1. **Organized Code Structure**
- All core functionality in `src/` folder
- Clear separation of concerns
- Easy to navigate and maintain

### 2. **Dedicated Testing**
- All tests in `tests/` folder
- Comprehensive test coverage
- Easy to run and maintain tests

### 3. **Utility Scripts**
- Debug and diagnostic tools in `utils/`
- Sample files for testing
- Helper scripts for development

### 4. **Configuration Management**
- All config files in `config/` folder
- URLs separated from code
- Easy to manage different environments

## 🚀 Usage

The main entry point remains the same:

```bash
# Run from project root
python main.py

# Or use the batch file
run.bat
```

## 🧪 Running Tests

```bash
# Run individual tests
python tests/test_auth.py
python tests/test_direct_access.py

# Run specific diagnostic tests
python tests/test_shared_drive.py
```

## 🛠️ Development

### Adding New Features
1. Add core functionality to `src/`
2. Add tests to `tests/`
3. Add utilities to `utils/` if needed
4. Update configuration in `config/`

### File Imports
- Use relative imports within `src/` package: `from .config import Config`
- Import from `src` in main.py: `from src.config import Config`

## 📝 Migration Notes

- **URLs file moved**: `urls.txt` → `config/urls.txt`
- **Source code moved**: Root files → `src/` folder
- **Tests organized**: All test files → `tests/` folder
- **Utilities consolidated**: Debug scripts → `utils/` folder

This structure follows Python best practices and makes the project more scalable and maintainable.
