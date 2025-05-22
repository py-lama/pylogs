#!/usr/bin/env python3

"""
Debug script for testing SQLiteHandler context handling in LogLama.
"""

import os
import json
import sqlite3
import tempfile
import logging

from loglama.utils.context import LogContext
from loglama.handlers.sqlite_handler import SQLiteHandler

# Create a temporary directory for the database
temp_dir = tempfile.TemporaryDirectory()
db_file = os.path.join(temp_dir.name, "test.db")

# Create a logger
logger = logging.getLogger("test_sqlite")
logger.setLevel(logging.DEBUG)

# Remove any existing handlers
for handler in logger.handlers:
    logger.removeHandler(handler)

# Create and add the SQLite handler
handler = SQLiteHandler(db_path=db_file)
logger.addHandler(handler)

# Add a console handler for debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Log without context
logger.info("Message without context")

# Log with context
with LogContext(user="test_user", request_id="abcd1234"):
    logger.info("Log with context")

# Connect to the database and check the logs
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check logs without context
cursor.execute("SELECT * FROM logs WHERE message = ?", ("Message without context",))
row = cursor.fetchone()
if row:
    print("\nLog without context:")
    for key in row.keys():
        print(f"{key}: {row[key]}")
    
    if row["context"]:
        context = json.loads(row["context"])
        print(f"\nParsed context: {json.dumps(context, indent=2)}")
else:
    print("No log without context found")

# Check logs with context
cursor.execute("SELECT * FROM logs WHERE message = ?", ("Log with context",))
row = cursor.fetchone()
if row:
    print("\nLog with context:")
    for key in row.keys():
        print(f"{key}: {row[key]}")
    
    if row["context"]:
        context = json.loads(row["context"])
        print(f"\nParsed context: {json.dumps(context, indent=2)}")
        print(f"user value: {context.get('user')}")
        print(f"request_id value: {context.get('request_id')}")
else:
    print("No log with context found")

# Check the schema of the logs table
cursor.execute("PRAGMA table_info(logs)")
columns = cursor.fetchall()
print("\nTable schema:")
for column in columns:
    print(f"{column[1]}: {column[2]}")

conn.close()

# Clean up
temp_dir.cleanup()
