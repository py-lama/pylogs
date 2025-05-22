#!/usr/bin/env python3
"""
Basic example of using LogLama in a Python script.

This example shows how to use LogLama for logging in a simple Python script.
It demonstrates how to initialize the logger, set log levels, and log messages.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import LogLama
sys.path.append(str(Path(__file__).parent.parent.parent))

# For development environment, also add the loglama directory
loglama_path = Path(__file__).parent.parent
sys.path.append(str(loglama_path))

# Import LogLama modules
from loglama.core.logger import get_logger, setup_logging
from loglama.core.env_manager import load_central_env

# Load environment variables from the central .env file
load_central_env()

# Set up logging
setup_logging()

# Get a logger for this script
logger = get_logger("example_script")


def main():
    """Main function that demonstrates LogLama logging."""
    # Log messages at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Log with context
    # Note: 'filename' is a reserved attribute in LogRecord, so we use 'file_name' instead
    logger.info("Processing file", extra={"file_name": "example.txt", "file_size": 1024})
    
    # Log with exception
    try:
        result = 10 / 0
    except Exception as e:
        logger.exception("An error occurred during calculation")
    
    # Log with timing
    with logger.time("operation_time"):
        # Simulate some work
        import time
        time.sleep(1)
        logger.info("Operation completed")


if __name__ == "__main__":
    main()
    print("\nCheck the logs to see the output. You can use the LogLama CLI to view them:")
    print("python -m loglama.cli.main logs")
