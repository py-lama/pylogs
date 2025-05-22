#!/usr/bin/env python3

"""
Debug script for testing context handling in PyLogs.
"""

import os
import json
import tempfile

from pylogs.utils.context import LogContext
from pylogs.core.logger import setup_logging

# Create a temporary file for logs
temp_dir = tempfile.TemporaryDirectory()
log_file = os.path.join(temp_dir.name, "test.log")

# Setup logging with JSON format and context filter
logger = setup_logging(
    name="test_debug",
    level="INFO",
    console=True,
    file=True,
    file_path=log_file,
    json=True,
    context_filter=True
)

# Log without context
logger.info("Message without context")

# Log with context
with LogContext(user="test_user", request_id="12345"):
    logger.info("Message with context")

# Print the content of the log file
print("\nLog file content:")
with open(log_file, "r") as f:
    for line in f:
        print(f"\n{line}")
        if "Message with context" in line:
            log_entry = json.loads(line)
            print(f"\nContext in log entry: {json.dumps(log_entry, indent=2)}")
            print(f"user value: {log_entry.get('user')}")
            print(f"request_id value: {log_entry.get('request_id')}")

# Clean up
temp_dir.cleanup()
