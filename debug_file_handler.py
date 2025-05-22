#!/usr/bin/env python3

"""
Debug script specifically for testing file handler and JSON formatting.
"""

import os
import json
import logging
import tempfile
import time

from loglama.utils.context import LogContext
from loglama.core.logger import JSONFormatter

# Create a temporary file for logs
temp_dir = tempfile.TemporaryDirectory()
log_file = os.path.join(temp_dir.name, "test.log")
print(f"Log file path: {log_file}")

# Create a logger directly without using setup_logging
logger = logging.getLogger("test_direct")
logger.setLevel(logging.INFO)

# Remove any existing handlers
for handler in logger.handlers:
    logger.removeHandler(handler)

# Create a file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a JSON formatter
json_formatter = JSONFormatter()
file_handler.setFormatter(json_formatter)

# Add a context filter
class ContextFilter(logging.Filter):
    def filter(self, record):
        context = LogContext.get_context()
        record.context = context
        for key, value in context.items():
            setattr(record, key, value)
        return True

context_filter = ContextFilter()
logger.addFilter(context_filter)

# Add the handler to the logger
logger.addHandler(file_handler)

# Add a console handler for debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Log without context
logger.info("Message without context")

# Log with context
with LogContext(user="test_user", request_id="12345"):
    logger.info("Message with context")

# Force flush the handler
file_handler.flush()

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
                    print(f"user value: {log_entry.get('user')}")
                    print(f"request_id value: {log_entry.get('request_id')}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
        else:
            print("Log file is empty!")
except Exception as e:
    print(f"Error reading log file: {e}")

# Clean up
temp_dir.cleanup()
