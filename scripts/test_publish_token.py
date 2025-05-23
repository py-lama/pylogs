#!/usr/bin/env python3

"""
Simple script to test if PyPI token is configured correctly.

This script:
1. Builds the package if needed
2. Runs 'poetry publish --dry-run' to test if publishing is possible
3. Does NOT actually publish anything or bump the version

Usage:
    python test_publish_token.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Get the project root directory
project_dir = Path(__file__).parent.parent
os.chdir(project_dir)

print("=== Testing PyPI Publishing Configuration ===\n")

# Build the package first
print("Building package...")
try:
    build_result = subprocess.run(["poetry", "build"], 
                                capture_output=True, text=True)
    if build_result.returncode == 0:
        print("Package built successfully")
    else:
        print("Error building package:")
        print(build_result.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Error building package: {e}")
    sys.exit(1)

# Test if we can publish without explicitly setting a token
print("\nRunning a dry-run publish to test configuration...")
try:
    result = subprocess.run(["poetry", "publish", "--dry-run"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\n✅ SUCCESS: PyPI token is correctly configured!")
        print("You can publish packages to PyPI using 'poetry publish'")
        print("\nOutput from dry run:")
        print(result.stdout)
    else:
        print("\n❌ ERROR: PyPI token is not correctly configured")
        print("Error output:")
        print(result.stderr)
        print("\nYou need to configure a PyPI token with:")
        print("poetry config pypi-token.pypi your-token")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: Failed to run test: {e}")
    sys.exit(1)
