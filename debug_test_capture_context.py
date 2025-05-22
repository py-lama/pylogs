#!/usr/bin/env python3

"""
Debug script specifically mimicking the test_capture_context test.
"""

import os
import json
import tempfile
import time
import logging

from pylogs.utils.context import LogContext, capture_context
from pylogs.core.logger import setup_logging, get_logger

# Create a temporary directory for logs
temp_dir = tempfile.TemporaryDirectory()
log_file = os.path.join(temp_dir.name, "test.log")
print(f"Log file path: {log_file}")

# Define the function with the decorator FIRST
@capture_context(request_id="function_context")
def function_with_context():
    # Use the same logger name as in setup_logging
    logger = get_logger("test_capture")
    logger.info("Function with captured context")

# Setup logging AFTER defining the function
logger = setup_logging(
    name="test_capture",
    level="INFO",
    console=True,
    file=True,
    file_path=log_file,
    json=True,
    context_filter=True
)

# Call the function
function_with_context()

# Force flush all handlers
for handler in logger.handlers:
    if hasattr(handler, 'flush'):
        handler.flush()

# Give the file system a moment
time.sleep(0.5)

# Check if the file exists and has content
if os.path.exists(log_file):
    print(f"\nLog file exists, size: {os.path.getsize(log_file)} bytes")
else:
    print("\nLog file does not exist!")

# Print the content of the log file
print("\nLog file content:")
try:
    with open(log_file, "r") as f:
        content = f.read()
        print(f"\nRaw content length: {len(content)}")
        if content:
            for line in content.splitlines():
                print(f"\nRaw line: {line}")
                try:
                    log_entry = json.loads(line)
                    print(f"Parsed JSON: {json.dumps(log_entry, indent=2)}")
                    print(f"request_id value: {log_entry.get('request_id')}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
        else:
            print("Log file is empty!")
except Exception as e:
    print(f"Error reading log file: {e}")

# Clean up
temp_dir.cleanup()
