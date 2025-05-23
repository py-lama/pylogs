#!/usr/bin/env python3

"""
Script to publish LogLama package to PyPI with automatic version bump.

This script:
1. Increments the version number (patch version)
2. Opens a browser to the PyPI token creation page
3. Waits for you to paste the token (shows it visibly)
4. Publishes the package automatically

Usage:
    python publish_with_version_bump.py
"""

import os
import subprocess
import sys
import webbrowser
import time
from pathlib import Path

# Get the project root directory
project_dir = Path(__file__).parent.parent
os.chdir(project_dir)

print("=== LogLama Publishing Tool with Version Bump ===\n")

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

# Open the PyPI token creation page
print("\nOpening browser to create a PyPI token...")
print("URL: https://pypi.org/manage/account/token/")
print("\nInstructions:")
print("1. Log in to PyPI if prompted")
print("2. Set 'Token name' to 'loglama-publish'")
print("3. Select 'Entire account (all projects)' scope")
print("4. Click 'Create token'")
print("5. Copy the generated token (it will only be shown once!)")

webbrowser.open("https://pypi.org/manage/account/token/")

# Give the user time to create and copy the token
time.sleep(2)

# Get the token from the user
print("\nWaiting for token...")
token = input("Paste the token here (it will be visible): ").strip()

if not token:
    print("Error: No token provided. Exiting.")
    sys.exit(1)

print(f"\nToken received: {token}")
print(f"Token length: {len(token)} characters")

# Configure Poetry with the token
print("\n=== Configuring Poetry with token ===")
try:
    # Use subprocess.run with arguments as a list to avoid shell escaping issues
    result = subprocess.run(["poetry", "config", "pypi-token.pypi", token], 
                           check=True, capture_output=True, text=True)
    print("Token configured successfully")
except subprocess.CalledProcessError as e:
    print(f"Error configuring token: {e}")
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
print("Publishing automatically...")
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
