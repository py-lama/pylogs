#!/usr/bin/env python3

"""
Debug script for testing JSON formatting in LogLama.
"""

import os
import json
import tempfile
import logging

from loglama.utils.context import LogContext, capture_context
from loglama.core.logger import setup_logging, JSONFormatter, ContextFilter

# Create a temporary file for logs
temp_dir = tempfile.TemporaryDirectory()
log_file = os.path.join(temp_dir.name, "test.log")

# Setup logging with JSON format and context filter
logger = setup_logging(
    name="test_json",
    level="INFO",
    console=True,
    file=True,
    file_path=log_file,
    json=True,
    context_filter=True
)

# Test the capture_context decorator
@capture_context(request_id="function_context")
def function_with_context():
    logger = setup_logging(
        name="test_capture",
        level="INFO",
        console=True,
        file=True,
        file_path=log_file,
        json=True,
        context_filter=True
    )
    logger.info("Function with captured context")

# Call the function
function_with_context()

# Print the content of the log file
print("\nLog file content:")
with open(log_file, "r") as f:
    for line in f:
        print(f"\nRaw line: {line}")
        try:
            log_entry = json.loads(line)
            print(f"Parsed JSON: {json.dumps(log_entry, indent=2)}")
            print(f"request_id value: {log_entry.get('request_id')}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

# Clean up
temp_dir.cleanup()
