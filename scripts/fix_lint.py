#!/usr/bin/env python3

'''
Script to automatically fix common linting issues in the LogLama codebase.

This script addresses the following issues:
1. Unused imports (using autoflake)
2. Lines exceeding 79 characters (using black with line-length=79)
3. Blank lines with whitespace (using black)
4. F-strings missing placeholders (manual fix)
5. Indentation issues (using black)
6. Spacing between functions (using black)
7. Trailing whitespace (using black)

Requires: autoflake, black, isort
'''

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and print its output."""
    print(f"\n{description}...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def fix_f_strings(file_path):
    """Fix f-strings that are missing placeholders."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace f-strings without placeholders with regular strings
    if 'f"' in content or "f'" in content:
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            if 'f"' in line and '{' not in line:
                line = line.replace('f"', '"')
            if "f'" in line and '{' not in line:
                line = line.replace("f'", "'")
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        if fixed_content != content:
            with open(file_path, 'w') as file:
                file.write(fixed_content)
            return True
    return False


def main():
    # Get the root directory of the project
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Make sure we're in the right directory
    os.chdir(project_root)
    print(f"Working in directory: {project_root}")
    
    # Find all Python files in the project
    python_files = list(project_root.glob('loglama/**/*.py'))
    
    # Fix unused imports with autoflake
    autoflake_cmd = f"autoflake --remove-all-unused-imports --recursive --in-place {' '.join(str(f) for f in python_files)}"
    run_command(autoflake_cmd, "Removing unused imports")
    
    # Fix f-strings
    print("\nFixing f-strings missing placeholders...")
    fixed_files = 0
    for file in python_files:
        if fix_f_strings(file):
            fixed_files += 1
    print(f"Fixed f-strings in {fixed_files} files")
    
    # Run isort to organize imports
    isort_cmd = "isort loglama/"
    run_command(isort_cmd, "Organizing imports with isort")
    
    # Run black to fix formatting issues
    black_cmd = "black --line-length 79 loglama/"
    run_command(black_cmd, "Formatting code with black")
    
    # Run flake8 to check if there are any remaining issues
    flake8_cmd = "flake8 loglama/"
    result = subprocess.run(flake8_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ All linting issues have been fixed!")
        return 0
    else:
        print("\n⚠️ Some linting issues remain:")
        print(result.stdout)
        print("\nYou may need to fix these issues manually.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
