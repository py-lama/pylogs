#!/usr/bin/env python3
"""
Script to update environment variable references from LOGLAMA_ to LOGLAMA_
"""

import os
import re
from pathlib import Path

# Configuration
OLD_PREFIX = "LOGLAMA_"
NEW_PREFIX = "LOGLAMA_"
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


def update_env_variables(file_path):
    """Update environment variable references in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if file contains any references to the old prefix
        if OLD_PREFIX not in content:
            return False
        
        # Replace environment variable references
        updated_content = re.sub(
            rf"\b{OLD_PREFIX}([A-Z_]+)\b", 
            f"{NEW_PREFIX}\\1", 
            content
        )
        
        # Replace string references to the prefix itself
        updated_content = updated_content.replace(f'"{OLD_PREFIX}', f'"{NEW_PREFIX}')
        updated_content = updated_content.replace(f"'{OLD_PREFIX}", f"'{NEW_PREFIX}")
        
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
    """Main function to update environment variable references."""
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
                if update_env_variables(file_path):
                    files_updated += 1
                    print(f"Updated: {file_path}")
    
    print(f"\nSummary:\n  Files processed: {files_processed}\n  Files updated: {files_updated}")


if __name__ == "__main__":
    main()
