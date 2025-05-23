#!/usr/bin/env python3

"""
Smart script to publish LogLama package to PyPI with automatic version bump and token reuse.

This script:
1. Increments the version number (patch version)
2. Checks for PyPI token in environment variable PYPI_TOKEN
3. If no environment variable, checks for a saved token in .pypi_token file
4. Only asks for a new token if no saved token is found
5. Saves the token for future use
6. Publishes the package automatically

Usage:
    python publish_with_saved_token.py
    
    # With token in environment variable:
    PYPI_TOKEN=your_token python publish_with_saved_token.py
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

# Path to the saved token file
TOKEN_FILE = project_dir / ".pypi_token"

print("=== LogLama Publishing Tool with Token Reuse ===\n")

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

# Check for PyPI token in environment variable
env_token = os.environ.get("PYPI_TOKEN")
if env_token:
    print("\n=== Using PyPI token from environment variable ===")
    token = env_token
    print(f"Token found (length: {len(token)} characters)")
    
    # Save the token for future use
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    os.chmod(TOKEN_FILE, 0o600)  # Make the file readable only by the owner
    print(f"Token saved to {TOKEN_FILE} for future use")
else:
    # Check for saved token
    print("\n=== Checking for saved PyPI token ===")
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        
        if token:
            print(f"Found saved token (length: {len(token)} characters)")
            print(f"Using token from {TOKEN_FILE}")
        else:
            token = None
            print("Saved token file exists but is empty")
    else:
        token = None
        print("No saved token found")
    
    # If no saved token, ask for one
    if not token:
        print("You'll need to provide a PyPI token.")
        
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
        
        # Save the token for future use
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        os.chmod(TOKEN_FILE, 0o600)  # Make the file readable only by the owner
        print(f"Token saved to {TOKEN_FILE} for future use")

# Configure Poetry with the token
print("\n=== Configuring Poetry with token ===")
try:
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
    
    # Provide hint for future publishing
    print("\nTIP: Your token has been saved for future use.")
    print("Next time you run this script, it will use the saved token automatically.")
    print("You can also set the PYPI_TOKEN environment variable to override the saved token:")
    print("PYPI_TOKEN=your_token make publish")
except subprocess.CalledProcessError as e:
    print(f"Error publishing package: {e}")
    print(f"Error output: {e.stderr}")
    sys.exit(1)
