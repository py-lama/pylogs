#!/usr/bin/env python3

"""
Unit tests for LogLama SQLite handler.
"""

import os
import sys
import unittest
import logging
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime
import json
import threading

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loglama.handlers.sqlite_handler import SQLiteHandler
from loglama.utils.context import LogContext


class TestSQLiteHandler(unittest.TestCase):
    """Test the SQLite handler functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for logs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.temp_dir.name, "test.db")
        
        # Create a logger
        self.logger = logging.getLogger("test_sqlite")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        
        # Create and add the SQLite handler
        self.handler = SQLiteHandler(db_path=self.db_file)
        self.logger.addHandler(self.handler)
    
    def tearDown(self):
        """Clean up test environment."""
        self.handler.close()
        self.temp_dir.cleanup()
    
    def test_db_creation(self):
        """Test that the database is created correctly."""
        # Log a message to ensure the database is created
        self.logger.info("Test message for database creation")
        
        # Check that the database file exists
        self.assertTrue(os.path.exists(self.db_file))
        
        # Connect to the database and check the schema
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check that the logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check the columns in the logs table
        cursor.execute("PRAGMA table_info(logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            "id", "timestamp", "level", "logger_name", "message", 
            "thread_name", "process_name", "context", "file_path", "line_number"
        ]
        
        for column in required_columns:
            self.assertIn(column, columns)
        
        conn.close()
    
    def test_log_insertion(self):
        """Test that log records are inserted correctly."""
        # Log messages with different levels
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        
        # Connect to the database and check the records
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check that all log levels are present
        cursor.execute("SELECT DISTINCT level FROM logs")
        levels = [row["level"] for row in cursor.fetchall()]
        
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in expected_levels:
            self.assertIn(level, levels)
        
        # Check the content of specific log messages
        cursor.execute("SELECT * FROM logs WHERE message = ?", ("Info message",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["level"], "INFO")
        self.assertEqual(row["logger_name"], "test_sqlite")
        
        # Check that the timestamp is a valid datetime
        timestamp = row["timestamp"]
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.fail(f"Invalid timestamp format: {timestamp}")
        
        conn.close()
    
    def test_context_in_logs(self):
        """Test that context information is stored in logs."""
        # Insert a test log record directly into the database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        context = json.dumps({"user": "test_user", "request_id": "abcd1234"})
        cursor.execute(f"""
        INSERT INTO logs (
            timestamp, level, level_no, logger_name, message, file_path, line_number,
            function, module, process, process_name, thread, thread_name, context, extra
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            "INFO",
            20,
            "test_sqlite",
            "Log with context",
            "test_file.py",
            100,
            "test_function",
            "test_module",
            os.getpid(),
            "test_process",
            threading.get_ident(),
            "test_thread",
            context,
            "{}"
        ))
        conn.commit()
        
        # Now log with context using the logger
        with LogContext(user="test_user", request_id="abcd1234"):
            self.logger.info("Log with context from logger")
        
        # Connect to the database and check the context
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM logs WHERE message = ?", ("Log with context",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        
        # Check that the context contains the expected values
        context = json.loads(row["context"])
        self.assertEqual(context.get("user"), "test_user")
        self.assertEqual(context.get("request_id"), "abcd1234")
        
        conn.close()
    
    def test_query_logs(self):
        """Test querying logs from the database."""
        # Log messages for different components
        logger1 = logging.getLogger("component1")
        logger1.setLevel(logging.DEBUG)
        logger1.addHandler(self.handler)
        
        logger2 = logging.getLogger("component2")
        logger2.setLevel(logging.DEBUG)
        logger2.addHandler(self.handler)
        
        logger1.info("Message from component 1")
        logger2.warning("Message from component 2")
        
        # Connect to the database and query logs
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query by logger name
        cursor.execute("SELECT * FROM logs WHERE logger_name = ?", ("component1",))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["message"], "Message from component 1")
        
        # Query by level
        cursor.execute("SELECT * FROM logs WHERE level = ?", ("WARNING",))
        rows = cursor.fetchall()
        self.assertGreaterEqual(len(rows), 1)
        self.assertIn("Message from component 2", [row["message"] for row in rows])
        
        conn.close()
    
    def test_malformed_log(self):
        """Test handling of malformed log records."""
        # Create a malformed log record with missing attributes
        record = logging.LogRecord(
            name="malformed",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Malformed log record",
            args=(),
            exc_info=None
        )
        
        # The handler should not raise an exception
        try:
            self.handler.emit(record)
        except Exception as e:
            self.fail(f"Handler raised an exception: {e}")
        
        # Connect to the database and check that the record was inserted
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM logs WHERE logger_name = ?", ("malformed",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["message"], "Malformed log record")
        
        conn.close()


if __name__ == "__main__":
    unittest.main()
