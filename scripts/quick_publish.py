#!/usr/bin/env python3

"""
Quick script to build and publish the LogLama package to PyPI.

This script assumes all tests and checks have already been run successfully.
It only handles the build and publish steps.

Usage:
    python quick_publish.py [--no-upload] [--no-confirm]

Options:
    --no-upload  Build the package but don't upload to PyPI
    --no-confirm Skip the confirmation prompt (useful for CI/CD)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the output."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, cwd=cwd,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(e.output)
        if check:
            raise
        return e


def confirm(message):
    """Ask for user confirmation."""
    response = input(f"{message} (y/N): ").lower().strip()
    return response == 'y'


def main():
    """Run the publishing workflow."""
    parser = argparse.ArgumentParser(description="Publish LogLama package to PyPI")
    parser.add_argument("--no-upload", action="store_true", help="Build only, don't upload")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompts")
    args = parser.parse_args()
    
    # Get the project root directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    print("=== LogLama Quick Publishing Tool ===")
    
    # Build the package
    print("\n=== Building package ===")
    run_command("poetry build", check=False)
    
    if args.no_upload:
        print("\n=== Package built successfully (skipping upload) ===")
        print(f"Package files are in {project_dir / 'dist'}")
        return 0
    
    # Confirm publishing
    if not args.no_confirm:
        print("\n=== Publishing to PyPI ===")
        print("WARNING: This will publish to PyPI (production). This action cannot be undone.")
        if not confirm("Are you sure you want to continue?"):
            print("Aborted.")
            return 1
    
    # Publish to PyPI
    print("\n=== Publishing to PyPI ===")
    run_command("poetry publish", check=False)
    
    print("\n=== Package published successfully ===")
    print("Install with: pip install loglama")
    return 0


if __name__ == "__main__":
    sys.exit(main())
