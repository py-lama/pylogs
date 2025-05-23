#!/usr/bin/env python3

"""
Script to build and publish LogLama Docker image to Docker Hub.

This script:
1. Reads the current version from pyproject.toml
2. Builds a Docker image with the current version tag
3. Logs in to Docker Hub using provided credentials
4. Pushes the image to Docker Hub
5. Optionally creates and pushes a 'latest' tag

Usage:
    python publish_docker.py [--no-latest]
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Get the project root directory
project_dir = Path(__file__).parent.parent
os.chdir(project_dir)

# Default Docker Hub repository
DEFAULT_REPO = "loglama/loglama"

def get_version():
    """Get the current version from pyproject.toml"""
    try:
        result = subprocess.run(["poetry", "version", "-s"], 
                              check=True, capture_output=True, text=True)
        version = result.stdout.strip()
        return version
    except subprocess.CalledProcessError as e:
        print(f"Error getting version: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def docker_login():
    """Log in to Docker Hub"""
    print("\n=== Logging in to Docker Hub ===")
    username = input("Docker Hub username: ").strip()
    password = input("Docker Hub password (will be visible): ").strip()
    
    if not username or not password:
        print("Error: Username and password are required")
        sys.exit(1)
    
    try:
        # Use subprocess.run with input parameter to provide password
        result = subprocess.run(["docker", "login", "--username", username],
                               input=password, text=True, capture_output=True)
        
        if result.returncode != 0:
            print(f"Error logging in to Docker Hub: {result.stderr}")
            sys.exit(1)
        
        print("Successfully logged in to Docker Hub")
    except Exception as e:
        print(f"Error logging in to Docker Hub: {e}")
        sys.exit(1)

def build_image(repo, version):
    """Build Docker image with version tag"""
    print(f"\n=== Building Docker image {repo}:{version} ===")
    try:
        subprocess.run(["docker", "build", "-t", f"{repo}:{version}", "."], check=True)
        print(f"Successfully built image {repo}:{version}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image: {e}")
        return False

def push_image(repo, version):
    """Push Docker image to Docker Hub"""
    print(f"\n=== Pushing Docker image {repo}:{version} to Docker Hub ===")
    try:
        subprocess.run(["docker", "push", f"{repo}:{version}"], check=True)
        print(f"Successfully pushed {repo}:{version} to Docker Hub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pushing Docker image: {e}")
        return False

def tag_latest(repo, version):
    """Create and push a 'latest' tag"""
    print(f"\n=== Tagging and pushing {repo}:latest ===")
    try:
        # Tag the version as latest
        subprocess.run(["docker", "tag", f"{repo}:{version}", f"{repo}:latest"], check=True)
        print(f"Tagged {repo}:{version} as {repo}:latest")
        
        # Push the latest tag
        subprocess.run(["docker", "push", f"{repo}:latest"], check=True)
        print(f"Successfully pushed {repo}:latest to Docker Hub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error tagging or pushing latest: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Build and publish LogLama Docker image to Docker Hub")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"Docker Hub repository (default: {DEFAULT_REPO})")
    parser.add_argument("--no-latest", action="store_true", help="Don't create and push a 'latest' tag")
    args = parser.parse_args()
    
    # Get the current version
    version = get_version()
    print(f"Current LogLama version: {version}")
    
    # Confirm with the user
    print(f"\nThis will build and push Docker image {args.repo}:{version} to Docker Hub.")
    if not args.no_latest:
        print(f"It will also create and push {args.repo}:latest.")
    
    confirm = input("\nDo you want to continue? (y/N): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        sys.exit(0)
    
    # Log in to Docker Hub
    docker_login()
    
    # Build the image
    if not build_image(args.repo, version):
        sys.exit(1)
    
    # Push the image
    if not push_image(args.repo, version):
        sys.exit(1)
    
    # Create and push a 'latest' tag if requested
    if not args.no_latest:
        if not tag_latest(args.repo, version):
            sys.exit(1)
    
    print("\n=== Docker image publishing completed successfully ===")
    print(f"Image {args.repo}:{version} is now available on Docker Hub")
    if not args.no_latest:
        print(f"Image {args.repo}:latest is also available")
    print("\nYou can pull it with:")
    print(f"  docker pull {args.repo}:{version}")
    if not args.no_latest:
        print(f"  docker pull {args.repo}:latest")

if __name__ == "__main__":
    main()
