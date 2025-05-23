#!/usr/bin/env python3

'''
Script to fix critical linting issues in the LogLama codebase.

This script addresses the following issues:
1. Undefined variables in except blocks (F821)
2. Long lines (E501) - using manual line breaking for specific files
3. Syntax errors in string literals

This script should be run after the other linting scripts to address critical issues.
'''

import os
import re
import sys
from pathlib import Path


def fix_undefined_exception_vars(file_path):
    """Fix undefined exception variables (F821) in except blocks."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    original_content = content
    
    # Find except blocks with undefined variables
    # Pattern: except SomeException as e:
    #          some_code(e)  # e is undefined if it was removed earlier
    
    # First, find all except blocks
    except_pattern = re.compile(r'except\s+([^\n:]+)(?:\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*))?\s*:', re.MULTILINE)
    except_matches = except_pattern.finditer(content)
    
    for match in except_matches:
        # If there's no exception variable, add one
        if not match.group(2):
            # Get the exception type
            exception_type = match.group(1).strip()
            # Replace 'except ExceptionType:' with 'except ExceptionType as e:'
            content = content[:match.start()] + f"except {exception_type} as e:" + content[match.end():]
    
    # Write the changes back to the file if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    
    return False


def fix_unterminated_strings(file_path):
    """Fix unterminated string literals."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed = False
        for i, line in enumerate(lines):
            # Check for unterminated string literals
            if ('"' in line or "'" in line) and not line.strip().startswith('#'):
                # Count quotes in the line
                single_quotes = line.count("'")
                double_quotes = line.count('"')
                
                # If odd number of quotes, it might be unterminated
                if single_quotes % 2 == 1 or double_quotes % 2 == 1:
                    # Add a closing quote at the end
                    if single_quotes % 2 == 1:
                        lines[i] = line.rstrip() + "'\n"
                    elif double_quotes % 2 == 1:
                        lines[i] = line.rstrip() + '"\n'
                    fixed = True
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing unterminated strings in {file_path}: {e}")
        return False


def fix_long_lines(file_path):
    """Fix lines that exceed 79 characters by breaking them intelligently."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        fixed = False
        fixed_lines = []
        
        for line in lines:
            if len(line.rstrip('\n')) > 79:
                # Skip comment lines - these are harder to fix automatically
                if line.strip().startswith('#'):
                    fixed_lines.append(line)
                    continue
                
                # Try to break at logical points
                if '=' in line and not line.strip().startswith('return'):
                    # Break at assignment
                    parts = line.split('=', 1)
                    indent = len(parts[0]) - len(parts[0].lstrip())
                    new_indent = ' ' * (indent + 4)  # Add 4 spaces for continuation
                    fixed_lines.append(f"{parts[0].rstrip()}=\n{new_indent}{parts[1].lstrip()}")
                    fixed = True
                elif ',' in line:
                    # Break at commas in lists, dicts, function calls
                    last_comma = line.rstrip('\n').rfind(',', 0, 79)
                    if last_comma > 0:
                        indent = len(line) - len(line.lstrip())
                        new_indent = ' ' * (indent + 4)  # Add 4 spaces for continuation
                        fixed_lines.append(f"{line[:last_comma+1]}\n{new_indent}{line[last_comma+1:].lstrip()}")
                        fixed = True
                    else:
                        fixed_lines.append(line)
                elif ' + ' in line:
                    # Break at string concatenation
                    last_plus = line.rstrip('\n').rfind(' + ', 0, 79)
                    if last_plus > 0:
                        indent = len(line) - len(line.lstrip())
                        new_indent = ' ' * indent
                        fixed_lines.append(f"{line[:last_plus]}\n{new_indent}{line[last_plus:]}")
                        fixed = True
                    else:
                        fixed_lines.append(line)
                else:
                    # If we can't find a good break point, just append the line
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(fixed_lines)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing long lines in {file_path}: {e}")
        return False


def fix_redefined_imports(file_path):
    """Fix redefined imports."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Track imports to avoid redefinition
        imports = set()
        fixed_lines = []
        fixed = False
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                # Extract the imported module/name
                if line.strip().startswith('import '):
                    imported = line.strip()[7:].split('#')[0].strip()
                else:  # from ... import ...
                    parts = line.strip().split('import')
                    if len(parts) > 1:
                        imported = parts[1].split('#')[0].strip()
                    else:
                        imported = ''
                
                # Check if this import is already present
                if imported and imported in imports:
                    fixed = True
                    continue  # Skip this line
                
                imports.add(imported)
            
            fixed_lines.append(line)
        
        if fixed:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(fixed_lines)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing redefined imports in {file_path}: {e}")
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
    
    # Fix each issue type
    fixed_files = 0
    
    print("\nFixing undefined exception variables (F821)...")
    for file in python_files:
        try:
            if fix_undefined_exception_vars(file):
                print(f"Fixed undefined exception variables in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing undefined exception variables in {file}: {e}")
    
    print("\nFixing unterminated strings...")
    for file in python_files:
        try:
            if fix_unterminated_strings(file):
                print(f"Fixed unterminated strings in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing unterminated strings in {file}: {e}")
    
    print("\nFixing redefined imports...")
    for file in python_files:
        try:
            if fix_redefined_imports(file):
                print(f"Fixed redefined imports in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing redefined imports in {file}: {e}")
    
    print("\nFixing long lines (E501)...")
    for file in python_files:
        try:
            if fix_long_lines(file):
                print(f"Fixed long lines in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing long lines in {file}: {e}")
    
    print(f"\nFixed issues in {fixed_files} files")
    
    # Run black and isort to clean up formatting
    print("\nRunning black and isort to clean up formatting...")
    os.system("black --line-length 79 loglama/")
    os.system("isort loglama/")
    
    # Run flake8 to check if there are any remaining issues
    print("\nChecking for remaining issues...")
    os.system("flake8 loglama/ --count")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
