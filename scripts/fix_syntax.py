#!/usr/bin/env python3

'''
Script to fix critical syntax errors in the LogLama codebase.

This script addresses specific syntax issues that are preventing the package from being published.
'''

import os
import re
import sys
from pathlib import Path


def fix_syntax_errors(file_path):
    """Fix specific syntax errors in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
        
        original_content = content
        
        # Convert the content to lines for easier processing
        lines = content.split('\n')
        fixed_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            # Fix unmatched parentheses
            open_count = line.count('(')
            close_count = line.count(')')
            
            if open_count > close_count:
                line += ')' * (open_count - close_count)
            elif close_count > open_count and not line.strip().startswith('#'):
                # Remove extra closing parentheses
                for _ in range(close_count - open_count):
                    last_paren = line.rfind(')')
                    if last_paren >= 0:
                        line = line[:last_paren] + line[last_paren + 1:]
            
            # Fix indentation errors
            if i > 0 and lines[i-1].strip().endswith(':') and not line.strip():
                # Add proper indentation after a colon
                indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                line = ' ' * (indent + 4) + 'pass'
            
            # Fix 'expected :' errors
            if re.search(r'\bdef\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*$', line):
                line += ':'
            
            # Fix invalid syntax in except blocks
            if 'except' in line and 'as' in line and ':' in line:
                # Extract the part after the colon
                parts = line.split(':', 1)
                if len(parts) > 1 and parts[1].strip() and not parts[1].strip().startswith('#'):
                    # Move the code after the colon to the next line with proper indentation
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(parts[0] + ':')
                    fixed_lines.append(' ' * (indent + 4) + parts[1].strip())
                    skip_next = False  # Don't skip, we've already handled it
                    continue
            
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Additional fixes for specific patterns
        
        # Fix 'cannot assign to literal' errors
        fixed_content = re.sub(r'(["\'])([^"\']*)\1\s*=', r'var_\2 =', fixed_content)
        
        # Fix unterminated string literals
        fixed_content = re.sub(r'(["\'])([^"\'\\
]*)$', r'\1\2\1', fixed_content, flags=re.MULTILINE)
        
        # Write the changes back to the file if changed
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(fixed_content)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing syntax in {file_path}: {e}")
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
    
    # Fix each file
    fixed_files = 0
    for file in python_files:
        try:
            if fix_syntax_errors(file):
                print(f"Fixed syntax in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    print(f"\nFixed syntax in {fixed_files} files")
    
    # Run isort to organize imports
    print("\nRunning isort to organize imports...")
    os.system("isort loglama/ || true")
    
    # Run flake8 with ignore flags to check if there are any remaining critical issues
    print("\nChecking for remaining critical issues...")
    os.system("flake8 loglama/ --select=E999 --count || true")
    
    print("\nNow try running 'make publish' to see if the package is ready for publishing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
