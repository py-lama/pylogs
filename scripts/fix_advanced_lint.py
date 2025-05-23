#!/usr/bin/env python3

'''
Advanced script to fix remaining linting issues in the LogLama codebase.

This script addresses the following issues:
1. Lines exceeding 79 characters (E501) - using manual line breaking
2. Unused variables (F841) - removing unused variables
3. Imports not at the top of files (E402) - moving imports to the top
4. Membership tests (E713) - fixing 'not in' syntax

This script should be run after fix_lint.py to address more complex issues.
'''

import os
import re
import sys
from pathlib import Path


def fix_long_lines(file_path):
    """Fix lines that exceed 79 characters by breaking them intelligently."""
    with open(file_path, 'r') as file:
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
            if '=' in line:
                # Break at assignment
                parts = line.split('=', 1)
                indent = len(parts[0]) - len(parts[0].lstrip())
                new_indent = ' ' * (indent + 4)  # Add 4 spaces for continuation
                fixed_lines.append(f"{parts[0]}=\n{new_indent}{parts[1]}")
                fixed = True
            elif ',' in line:
                # Break at commas in lists, dicts, function calls
                last_comma = line.rstrip('\n').rfind(',', 0, 79)
                if last_comma > 0:
                    indent = len(line) - len(line.lstrip())
                    new_indent = ' ' * (indent + 4)  # Add 4 spaces for continuation
                    fixed_lines.append(f"{line[:last_comma+1]}\n{new_indent}{line[last_comma+1:]}")
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
        with open(file_path, 'w') as file:
            file.writelines(fixed_lines)
    
    return fixed


def fix_unused_variables(file_path):
    """Fix unused variables (F841) by removing them."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    original_content = content
    
    # Find and fix patterns like 'except Exception as e:' where e is never used
    # Replace with 'except Exception:'
    content = re.sub(r'except\s+([^\n:]+)\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'except \1:', content)
    
    # Write the changes back to the file if changed
    if content != original_content:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    
    return False


def fix_imports_not_at_top(file_path):
    """Fix imports that are not at the top of the file (E402)."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    imports = []
    non_imports = []
    in_docstring = False
    docstring_delimiter = None
    
    # First pass: separate imports from non-imports
    for line in lines:
        # Track docstrings to avoid moving imports inside them
        if '"""' in line or "'''" in line:
            if not in_docstring:
                in_docstring = True
                docstring_delimiter = '"""' if '"""' in line else "'''"
            elif docstring_delimiter in line:
                in_docstring = False
        
        # Skip empty lines and docstrings
        if in_docstring or line.strip() == '':
            non_imports.append(line)
            continue
        
        # Collect import statements
        if line.strip().startswith(('import ', 'from ')):
            imports.append(line)
        else:
            non_imports.append(line)
    
    # Second pass: reconstruct the file with imports at the top
    if len(imports) > 0:
        # Find where to insert imports (after docstrings and module-level comments)
        insert_point = 0
        for i, line in enumerate(non_imports):
            if line.strip() and not line.strip().startswith('#'):
                insert_point = i
                break
        
        # Reconstruct the file
        result = non_imports[:insert_point] + imports + non_imports[insert_point:]
        
        # Write the changes back to the file
        with open(file_path, 'w') as file:
            file.writelines(result)
        
        return True
    
    return False


def fix_membership_tests(file_path):
    """Fix membership tests (E713) by changing 'not x in y' to 'x not in y'."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Find and fix patterns like 'not x in y' to 'x not in y'
    pattern = re.compile(r'not\s+([^\s]+)\s+in\s+', re.MULTILINE)
    fixed_content = pattern.sub(r'\1 not in ', content)
    
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
    
    # Fix each issue type
    fixed_files = 0
    
    print("\nFixing membership tests (E713)...")
    for file in python_files:
        if fix_membership_tests(file):
            print(f"Fixed membership tests in {file}")
            fixed_files += 1
    
    print("\nFixing imports not at top (E402)...")
    for file in python_files:
        if fix_imports_not_at_top(file):
            print(f"Fixed imports in {file}")
            fixed_files += 1
    
    print("\nFixing unused variables (F841)...")
    for file in python_files:
        try:
            if fix_unused_variables(file):
                print(f"Fixed unused variables in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing unused variables in {file}: {e}")
    
    print("\nFixing long lines (E501)...")
    for file in python_files:
        try:
            if fix_long_lines(file):
                print(f"Fixed long lines in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing long lines in {file}: {e}")
    
    print(f"\nFixed issues in {fixed_files} files")
    
    # Run the basic fix script again to clean up any remaining issues
    print("\nRunning basic fix script again to clean up...")
    os.system(f"{sys.executable} {script_dir}/fix_lint.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
