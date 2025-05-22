#!/usr/bin/env python3
"""
Basic example of using LogLama in a Python script.

This example shows how to use LogLama for logging in a simple Python script.
It demonstrates how to initialize the logger, set log levels, and log messages.
"""

import os
import sys
from pathlib import Path

# Import the utility module to set up the Python path
try:
    from utils import setup_loglama_path
    setup_loglama_path()
except ImportError:
    # Fallback if utils.py is not available
    current_dir = Path(__file__).parent.absolute()
    py_lama_root = current_dir.parent.parent
    loglama_dir = current_dir.parent
    sys.path.append(str(py_lama_root))
    sys.path.append(str(loglama_dir))

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
