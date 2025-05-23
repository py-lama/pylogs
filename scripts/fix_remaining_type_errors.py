#!/usr/bin/env python3

"""
Fix remaining type errors in the LogLama codebase.

This script adds # type: ignore comments to lines with specific mypy errors
to allow the package to pass type checking for publication.
"""

import os
import re
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Files with type errors that need to be fixed
FILES_WITH_TYPE_ERRORS = {
    "loglama/cli/commands/diagnostic_commands.py": [
        # Line with import-untyped error for pkg_resources
        (116, "import pkg_resources", "import pkg_resources  # type: ignore[import-untyped]")
    ],
}


def fix_type_errors():
    """Add type: ignore comments to lines with mypy errors."""
    print("Fixing remaining type errors...")
    
    base_dir = Path(__file__).parent.parent
    
    for file_path, errors in FILES_WITH_TYPE_ERRORS.items():
        full_path = base_dir / file_path
        if not full_path.exists():
            print(f"Warning: File {full_path} not found")
            continue
            
        print(f"Processing {file_path}...")
        
        # Read the file content
        with open(full_path, "r") as f:
            lines = f.readlines()
        
        # Apply fixes
        for line_num, old_text, new_text in errors:
            if line_num <= len(lines):
                if old_text in lines[line_num - 1]:
                    lines[line_num - 1] = lines[line_num - 1].replace(old_text, new_text)
                    print(f"  Fixed line {line_num}: {old_text} -> {new_text}")
                else:
                    print(f"  Warning: Expected text not found on line {line_num}")
                    print(f"  Expected: {old_text}")
                    print(f"  Found: {lines[line_num - 1].strip()}")
            else:
                print(f"  Warning: Line {line_num} out of range (file has {len(lines)} lines)")
        
        # Write the modified content back to the file
        with open(full_path, "w") as f:
            f.writelines(lines)
    
    print("Type error fixes complete!")


if __name__ == "__main__":
    fix_type_errors()
