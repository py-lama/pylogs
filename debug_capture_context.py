#!/usr/bin/env python3

"""
Debug script specifically for the capture_context test case.
"""

import os
import json
import tempfile
import time

from loglama.utils.context import LogContext, capture_context
from loglama.core.logger import setup_logging, get_logger

# Create a temporary file for logs
temp_dir = tempfile.TemporaryDirectory()
log_file = os.path.join(temp_dir.name, "test.log")
print(f"Log file path: {log_file}")

# Setup logging FIRST
logger = setup_logging(
    name="test_capture",
    level="INFO",
    console=True,
    file=True,
    file_path=log_file,
    json=True,
    context_filter=True
)

# Define the function with the decorator
@capture_context(request_id="function_context")
def function_with_context():
    logger = get_logger("test_capture")
    logger.info("Function with captured context")

# Call the function
function_with_context()

# Give the file system a moment to flush
time.sleep(0.1)

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
