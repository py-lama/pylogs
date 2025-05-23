#!/usr/bin/env python3

"""
Simplified script to publish LogLama package to PyPI with automatic version bump.

This script:
1. Increments the version number (patch version)
2. Uses the existing Poetry token configuration
3. Builds and publishes the package

Usage:
    python simple_publish.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Get the project root directory
project_dir = Path(__file__).parent.parent
os.chdir(project_dir)

print("=== LogLama Simple Publishing Tool ===\n")

# Bump the version number
print("=== Bumping version number ===")
try:
    result = subprocess.run(["poetry", "version", "patch"], 
                          check=True, capture_output=True, text=True)
    new_version = result.stdout.strip()
    print(f"Version bumped to: {new_version}")
except subprocess.CalledProcessError as e:
    print(f"Error bumping version: {e}")
    print(f"Error output: {e.stderr}")
    sys.exit(1)

# Build the package
print("\n=== Building package ===")
try:
    subprocess.run(["poetry", "build"], check=True)
    print("Package built successfully")
except subprocess.CalledProcessError as e:
    print(f"Error building package: {e}")
    sys.exit(1)

# Publish the package
print("\n=== Publishing to PyPI ===")
print("Publishing automatically using configured token...")
try:
    result = subprocess.run(["poetry", "publish"], check=True, 
                          capture_output=True, text=True)
    print(result.stdout)
    print("\n=== Package published successfully ===")
    print(f"Version {new_version} is now available on PyPI")
    print("Install with: pip install loglama")
except subprocess.CalledProcessError as e:
    print(f"Error publishing package: {e}")
    print(f"Error output: {e.stderr}")
    sys.exit(1)
