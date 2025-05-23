#!/usr/bin/env python3

"""
Publish LogLama package to PyPI with automatic token handling.

This script:
1. Checks if a PyPI token exists
2. If not, opens a browser to the PyPI token creation page
3. Prompts you to paste the token
4. Configures Poetry with the token
5. Publishes the package

Usage:
    python publish_with_token.py [--test]

Options:
    --test  Publish to TestPyPI instead of PyPI
"""

import argparse
import os
import subprocess
import sys
import webbrowser
from pathlib import Path


def run_command(cmd, cwd=None, check=True, capture_output=True):
    """Run a shell command and return the output."""
    print(f"Running: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                universal_newlines=True)
            print(result.stdout)
        else:
            result = subprocess.run(cmd, shell=True, check=check, cwd=cwd)
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            print(f"Command failed with exit code {e.returncode}")
            print(e.output)
        if check:
            raise
        return e


def check_token_exists(is_test=False):
    """Check if a PyPI token exists in Poetry configuration."""
    repo = "testpypi" if is_test else "pypi"
    result = run_command(f"poetry config pypi-token.{repo}", check=False)
    return result.returncode == 0 and result.stdout.strip() != ""


def open_token_page(is_test=False):
    """Open the PyPI token creation page in a browser."""
    project_name = "loglama"
    if is_test:
        url = f"https://test.pypi.org/manage/account/token/"
    else:
        url = f"https://pypi.org/manage/account/token/"
    
    print(f"\nOpening browser to create a PyPI token...")
    print(f"URL: {url}")
    print("\nInstructions:")
    print("1. Log in to PyPI if prompted")
    print("2. Set 'Token name' to 'loglama-publish'")
    print("3. Select 'Entire account (all projects)' scope")
    print("4. Click 'Create token'")
    print("5. Copy the generated token (it will only be shown once!)")
    
    webbrowser.open(url)
    
    return input("\nPaste the token here (input will be hidden): ")


def configure_token(token, is_test=False):
    """Configure Poetry with the PyPI token."""
    repo = "testpypi" if is_test else "pypi"
    run_command(f"poetry config pypi-token.{repo} {token}")
    print(f"Token configured for {'TestPyPI' if is_test else 'PyPI'}")


def build_package():
    """Build the package with Poetry."""
    print("\n=== Building package ===")
    run_command("poetry build")


def publish_package(is_test=False):
    """Publish the package to PyPI or TestPyPI."""
    repo = "-r testpypi" if is_test else ""
    print(f"\n=== Publishing to {'TestPyPI' if is_test else 'PyPI'} ===")
    run_command(f"poetry publish {repo}")


def main():
    """Run the publishing workflow."""
    parser = argparse.ArgumentParser(description="Publish LogLama package to PyPI with token handling")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI instead of PyPI")
    args = parser.parse_args()
    
    # Get the project root directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    print("=== LogLama Publishing Tool with Token Handling ===")
    
    # Check if token exists
    if not check_token_exists(args.test):
        print(f"No {'TestPyPI' if args.test else 'PyPI'} token found in Poetry configuration")
        token = open_token_page(args.test)
        configure_token(token, args.test)
    else:
        print(f"{'TestPyPI' if args.test else 'PyPI'} token found in Poetry configuration")
    
    # Build the package
    build_package()
    
    # Confirm publishing
    print("\n=== Publishing to PyPI ===")
    print("WARNING: This will publish to PyPI. This action cannot be undone.")
    response = input("Are you sure you want to continue? (y/N): ").lower().strip()
    if response != 'y':
        print("Aborted.")
        return 1
    
    # Publish to PyPI
    publish_package(args.test)
    
    print("\n=== Package published successfully ===")
    print(f"Install with: pip install {'--index-url https://test.pypi.org/simple/ ' if args.test else ''}loglama")
    return 0


if __name__ == "__main__":
    sys.exit(main())
