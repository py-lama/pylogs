#!/usr/bin/env python3
"""
Script to update remaining references from 'loglama' to 'loglama'
"""

import os
import re
from pathlib import Path

# Configuration
OLD_NAME = "loglama"
NEW_NAME = "loglama"
OLD_NAME_CAMEL = "LogLama"
NEW_NAME_CAMEL = "LogLama"
PROJECT_DIR = "/home/tom/github/py-lama/loglama"

# Files to exclude from processing
EXCLUDE_EXTENSIONS = [".pyc", ".pyo", ".so", ".o", ".a", ".lib", ".dll", ".exe", ".bin"]
EXCLUDE_DIRS = [".git", ".idea", "__pycache__", "venv", ".pytest_cache"]


def should_process_file(file_path):
    """Determine if a file should be processed based on extension and path."""
    file_path = str(file_path)
    
    # Check excluded extensions
    if any(file_path.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
        return False
    
    # Check excluded directories
    if any(f"/{exclude_dir}/" in file_path for exclude_dir in EXCLUDE_DIRS):
        return False
    
    return True


def update_references(file_path):
    """Update references in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if file contains any references to the old names
        if OLD_NAME not in content.lower() and OLD_NAME_CAMEL not in content:
            return False
        
        # Replace references
        updated_content = content
        
        # Replace camelCase version first (LogLama -> LogLama)
        updated_content = updated_content.replace(OLD_NAME_CAMEL, NEW_NAME_CAMEL)
        
        # Replace lowercase version with word boundaries
        updated_content = re.sub(
            rf"\b{OLD_NAME}\b", 
            NEW_NAME, 
            updated_content,
            flags=re.IGNORECASE
        )
        
        # Only write if changes were made
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        
        return False
    except UnicodeDecodeError:
        # Skip binary files
        return False


def main():
    """Main function to update references."""
    files_updated = 0
    files_processed = 0
    
    # Walk through the project directory
    for root, dirs, files in os.walk(PROJECT_DIR):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Process each file
        for file in files:
            file_path = os.path.join(root, file)
            
            if should_process_file(file_path):
                files_processed += 1
                if update_references(file_path):
                    files_updated += 1
                    print(f"Updated: {file_path}")
    
    print(f"\nSummary:\n  Files processed: {files_processed}\n  Files updated: {files_updated}")


if __name__ == "__main__":
    main()
