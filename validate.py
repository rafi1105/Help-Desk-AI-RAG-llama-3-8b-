#!/usr/bin/env python3
"""
Validation script for Help Desk AI project structure.
Tests the project without requiring external dependencies.
"""
import os
import sys
import json

def validate_project_structure():
    """Validate that all required files and directories exist."""
    print("🔍 Validating project structure...")
    
    required_files = [
        "requirements.txt",
        "README.md",
        ".gitignore",
        ".env.example",
        "setup.py",
        "cli.py",
        "src/__init__.py",
        "src/helpdesk_ai/__init__.py",
        "src/helpdesk_ai/core/__init__.py",
        "src/helpdesk_ai/core/config.py",
        "src/helpdesk_ai/core/knowledge_base.py",
        "src/helpdesk_ai/core/automation.py",
        "src/helpdesk_ai/models/__init__.py",
        "src/helpdesk_ai/models/chatbot.py",
        "src/helpdesk_ai/utils/__init__.py",
        "src/helpdesk_ai/utils/helpers.py",
        "src/helpdesk_ai/api/__init__.py",
        "src/helpdesk_ai/api/main.py",
        "src/helpdesk_ai/ui/__init__.py",
        "src/helpdesk_ai/ui/streamlit_app.py",
        "knowledge_base/sample_faq.json"
    ]
    
    required_dirs = [
        "src",
        "src/helpdesk_ai",
        "src/helpdesk_ai/core",
        "src/helpdesk_ai/models",
        "src/helpdesk_ai/utils",
        "src/helpdesk_ai/api",
        "src/helpdesk_ai/ui",
        "knowledge_base"
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check directories
    for directory in required_dirs:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
        else:
            print(f"✓ Directory: {directory}")
    
    # Check files
    for file_path in required_files:
        if not os.path.isfile(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ File: {file_path}")
    
    if missing_dirs:
        print("\n❌ Missing directories:")
        for directory in missing_dirs:
            print(f"  - {directory}")
    
    if missing_files:
        print("\n❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
    
    if not missing_dirs and not missing_files:
        print("\n✅ All required files and directories are present!")
        return True
    else:
        print(f"\n❌ Missing {len(missing_dirs)} directories and {len(missing_files)} files")
        return False

def validate_json_files():
    """Validate JSON files are properly formatted."""
    print("\n🔍 Validating JSON files...")
    
    json_files = [
        "knowledge_base/sample_faq.json"
    ]
    
    valid_json = True
    
    for json_file in json_files:
        if os.path.isfile(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                print(f"✓ Valid JSON: {json_file} ({len(data)} items)")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {json_file} - {e}")
                valid_json = False
        else:
            print(f"⚠ Missing JSON file: {json_file}")
    
    return valid_json

def validate_dependencies():
    """Check if dependencies file is valid."""
    print("\n🔍 Validating dependencies...")
    
    if os.path.isfile("requirements.txt"):
        with open("requirements.txt", 'r') as f:
            deps = f.read().strip().split('\n')
        
        print(f"✓ Found {len(deps)} dependencies in requirements.txt")
        
        # Check for critical dependencies
        critical_deps = [
            "torch", "transformers", "sentence-transformers", 
            "faiss-cpu", "streamlit", "fastapi", "pydantic"
        ]
        
        found_deps = []
        for dep in deps:
            dep_name = dep.split('>=')[0].split('==')[0].strip()
            if dep_name in critical_deps:
                found_deps.append(dep_name)
        
        missing_critical = set(critical_deps) - set(found_deps)
        
        if missing_critical:
            print(f"⚠ Missing critical dependencies: {missing_critical}")
        else:
            print("✅ All critical dependencies found!")
        
        return len(missing_critical) == 0
    else:
        print("❌ requirements.txt not found")
        return False

def check_file_sizes():
    """Check file sizes for reasonableness."""
    print("\n🔍 Checking file sizes...")
    
    important_files = [
        "src/helpdesk_ai/models/chatbot.py",
        "src/helpdesk_ai/core/knowledge_base.py",
        "src/helpdesk_ai/core/automation.py",
        "src/helpdesk_ai/ui/streamlit_app.py",
        "src/helpdesk_ai/api/main.py",
        "README.md"
    ]
    
    all_good = True
    for file_path in important_files:
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            if size > 1000:  # At least 1KB for substantial files
                print(f"✓ {file_path}: {size} bytes")
            else:
                print(f"⚠ {file_path}: {size} bytes (seems small)")
                all_good = False
        else:
            print(f"❌ Missing: {file_path}")
            all_good = False
    
    return all_good

def validate_readme():
    """Validate README content."""
    print("\n🔍 Validating README...")
    
    if os.path.isfile("README.md"):
        with open("README.md", 'r') as f:
            content = f.read()
        
        required_sections = [
            "# Help Desk AI RAG Chat-Bot",
            "Features",
            "Quick Start",
            "Configuration",
            "Usage",
            "Architecture"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
            else:
                print(f"✓ Found section: {section}")
        
        if missing_sections:
            print(f"⚠ Missing README sections: {missing_sections}")
        else:
            print("✅ README has all required sections!")
        
        return len(missing_sections) == 0
    else:
        print("❌ README.md not found")
        return False

def main():
    """Main validation function."""
    print("🚀 Help Desk AI RAG Project Validation")
    print("=" * 50)
    
    validations = [
        ("Project Structure", validate_project_structure),
        ("JSON Files", validate_json_files),
        ("Dependencies", validate_dependencies),
        ("File Sizes", check_file_sizes),
        ("README", validate_readme)
    ]
    
    results = []
    
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error validating {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} validations passed")
    
    if passed == len(results):
        print("\n🎉 Project validation successful!")
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and configure")
        print("3. Run setup: python setup.py")
        print("4. Start the system: streamlit run src/helpdesk_ai/ui/streamlit_app.py")
    else:
        print(f"\n⚠ {len(results) - passed} validation(s) failed")
        print("Please fix the issues before proceeding")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)