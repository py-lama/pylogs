#!/usr/bin/env python3

'''
Script to fix docstring issues in the LogLama codebase.

This script addresses the following issues:
1. Unterminated docstrings
2. Malformed docstrings with extra quotes
3. Incorrect docstring indentation
'''

import os
import re
import sys
from pathlib import Path


def fix_docstrings(file_path):
    """Fix docstring issues in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Fix incorrect docstring format: """" -> """
        content = re.sub(r'""""', '"""', content)
        content = re.sub(r"''''", "'''", content)
        
        # Fix unterminated docstrings
        # Count occurrences of triple quotes
        double_quotes = content.count('"""')
        single_quotes = content.count("'''")
        
        # If odd number of triple quotes, add a closing one at the end of the docstring
        if double_quotes % 2 == 1:
            # Find the last occurrence of """
            last_pos = content.rfind('"""')
            if last_pos >= 0:
                # Find the next occurrence of a newline after the opening """
                next_newline = content.find('\n', last_pos + 3)
                if next_newline >= 0:
                    # Insert closing quotes after the next newline
                    content = content[:next_newline + 1] + '"""\n' + content[next_newline + 1:]
        
        if single_quotes % 2 == 1:
            # Find the last occurrence of '''
            last_pos = content.rfind("'''")
            if last_pos >= 0:
                # Find the next occurrence of a newline after the opening '''
                next_newline = content.find('\n', last_pos + 3)
                if next_newline >= 0:
                    # Insert closing quotes after the next newline
                    content = content[:next_newline + 1] + "'''\n" + content[next_newline + 1:]
        
        # Fix docstrings with incorrect indentation
        lines = content.split('\n')
        fixed_lines = []
        in_docstring = False
        docstring_start_indent = 0
        docstring_type = None
        
        for i, line in enumerate(lines):
            # Check for docstring start/end
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    # Starting a docstring
                    in_docstring = True
                    docstring_type = '"""' if '"""' in line else "'''"
                    docstring_start_indent = len(line) - len(line.lstrip())
                    fixed_lines.append(line)
                else:
                    # Ending a docstring
                    if docstring_type in line:
                        in_docstring = False
                        docstring_type = None
                        fixed_lines.append(line)
                    else:
                        # Mixed quotes, fix it
                        indent = ' ' * docstring_start_indent
                        fixed_lines.append(f"{indent}{docstring_type}")
                        in_docstring = False
                        docstring_type = None
            else:
                fixed_lines.append(line)
        
        # If we're still in a docstring at the end, close it
        if in_docstring and docstring_type:
            indent = ' ' * docstring_start_indent
            fixed_lines.append(f"{indent}{docstring_type}")
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Write the changes back to the file if changed
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(fixed_content)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing docstrings in {file_path}: {e}")
        return False


def fix_except_blocks(file_path):
    """Fix malformed except blocks."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Fix malformed except blocks like "except Exception as e:tion:"
        content = re.sub(r'except\s+([^\n:]+)\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)', 
                         r'except \1 as \2:', content)
        
        # Write the changes back to the file if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing except blocks in {file_path}: {e}")
        return False


def fix_unmatched_parentheses(file_path):
    """Fix unmatched parentheses in Python files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        # Simple stack-based approach to check for unmatched parentheses
        for line in lines:
            # Skip comments
            if line.strip().startswith('#'):
                fixed_lines.append(line)
                continue
            
            # Count opening and closing parentheses
            open_count = line.count('(')
            close_count = line.count(')')
            
            # If unbalanced, try to fix
            if open_count > close_count:
                # Add missing closing parentheses
                line += ')' * (open_count - close_count)
            elif close_count > open_count:
                # Remove extra closing parentheses
                for _ in range(close_count - open_count):
                    last_paren = line.rfind(')')
                    if last_paren >= 0:
                        line = line[:last_paren] + line[last_paren + 1:]
            
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Write the changes back to the file if changed
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(fixed_content)
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing unmatched parentheses in {file_path}: {e}")
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
    
    print("\nFixing docstring issues...")
    for file in python_files:
        try:
            if fix_docstrings(file):
                print(f"Fixed docstrings in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing docstrings in {file}: {e}")
    
    print("\nFixing except blocks...")
    for file in python_files:
        try:
            if fix_except_blocks(file):
                print(f"Fixed except blocks in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing except blocks in {file}: {e}")
    
    print("\nFixing unmatched parentheses...")
    for file in python_files:
        try:
            if fix_unmatched_parentheses(file):
                print(f"Fixed unmatched parentheses in {file}")
                fixed_files += 1
        except Exception as e:
            print(f"Error fixing unmatched parentheses in {file}: {e}")
    
    print(f"\nFixed issues in {fixed_files} files")
    
    # Run black and isort to clean up formatting
    print("\nRunning black and isort to clean up formatting...")
    os.system("black --line-length 79 loglama/ || true")
    os.system("isort loglama/ || true")
    
    # Run flake8 to check if there are any remaining issues
    print("\nChecking for remaining issues...")
    os.system("flake8 loglama/ --count || true")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
