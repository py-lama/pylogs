#!/usr/bin/env python3
"""
Script to rename the LogLama project to LogLama.

This script will:
1. Create the new directory structure
2. Copy and rename files with updated content
3. Update import statements and references
"""

import os
import re
import shutil
from pathlib import Path

# Configuration
OLD_NAME = "loglama"
NEW_NAME = "loglama"
OLD_PROJECT_DIR = "/home/tom/github/py-lama/loglama"
NEW_PROJECT_DIR = "/home/tom/github/py-lama/loglama"

# Files to exclude from processing (binary files, etc.)
EXCLUDE_EXTENSIONS = [".pyc", ".pyo", ".so", ".o", ".a", ".lib", ".dll", ".exe", ".bin"]
EXCLUDE_DIRS = [".git", ".idea", "__pycache__", "venv", ".pytest_cache"]

# Files that need special handling
SPECIAL_FILES = ["pyproject.toml", "Makefile", "README.md"]


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


def update_file_content(content, old_name=OLD_NAME, new_name=NEW_NAME):
    """Update file content by replacing old project name with new name."""
    # Replace import statements
    content = re.sub(
        rf"from {old_name}(\.|\s)", 
        f"from {new_name}\\1", 
        content
    )
    content = re.sub(
        rf"import {old_name}(\.|\s)", 
        f"import {new_name}\\1", 
        content
    )
    
    # Replace other references to the old name
    content = re.sub(
        rf"\b{old_name}\b", 
        new_name, 
        content
    )
    
    # Replace capitalized versions (LogLama -> LogLama)
    content = content.replace("LogLama", "LogLama")
    
    return content


def process_special_file(file_path, new_file_path):
    """Process files that need special handling."""
    file_name = os.path.basename(file_path)
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if file_name == "pyproject.toml":
        # Update package name in pyproject.toml
        content = re.sub(
            r'name = "[^"]*"', 
            f'name = "{NEW_NAME}"', 
            content
        )
    
    elif file_name == "README.md":
        # Update project name and references in README
        content = content.replace("LogLama", "LogLama")
        content = content.replace("loglama", "loglama")
    
    elif file_name == "Makefile":
        # Update references in Makefile
        content = content.replace("loglama", "loglama")
    
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def copy_and_process_file(src_file, dest_file):
    """Copy a file and process its content if needed."""
    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    
    # Check if this is a special file
    if os.path.basename(src_file) in SPECIAL_FILES:
        process_special_file(src_file, dest_file)
        return
    
    # For text files, update content
    if should_process_file(src_file):
        try:
            with open(src_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            updated_content = update_file_content(content)
            
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        except UnicodeDecodeError:
            # If we can't decode as text, just copy the file
            shutil.copy2(src_file, dest_file)
    else:
        # For binary or excluded files, just copy
        shutil.copy2(src_file, dest_file)


def rename_project():
    """Main function to rename the project."""
    # Create the new project directory if it doesn't exist
    os.makedirs(NEW_PROJECT_DIR, exist_ok=True)
    
    # Walk through the old project directory
    for root, dirs, files in os.walk(OLD_PROJECT_DIR):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Process each file
        for file in files:
            src_file = os.path.join(root, file)
            
            # Determine the new file path
            rel_path = os.path.relpath(src_file, OLD_PROJECT_DIR)
            
            # Replace 'loglama' directory with 'loglama' in the path
            if rel_path.startswith(OLD_NAME + os.sep):
                rel_path = NEW_NAME + os.sep + rel_path[len(OLD_NAME) + 1:]
            
            dest_file = os.path.join(NEW_PROJECT_DIR, rel_path)
            
            # Copy and process the file
            copy_and_process_file(src_file, dest_file)
    
    print(f"Project renamed from {OLD_NAME} to {NEW_NAME}")
    print(f"New project directory: {NEW_PROJECT_DIR}")


if __name__ == "__main__":
    rename_project()
