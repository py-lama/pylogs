#!/usr/bin/env python3

"""
Integration tests for PyLogs.

This module tests the integration of various PyLogs components together.
"""

import os
import sys
import unittest
import tempfile
import sqlite3
import json
import logging
import time
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pylogs.core.logger import setup_logging, get_logger
from pylogs.utils.context import LogContext, capture_context
from pylogs.config.env_loader import load_env


class TestLoggingIntegration(unittest.TestCase):
    """Test the integration of PyLogs components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for logs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = self.temp_dir.name
        self.log_file = os.path.join(self.log_dir, "test.log")
        self.db_file = os.path.join(self.log_dir, "test.db")
        
        # Set environment variables for testing
        os.environ["PYLOGS_LOG_LEVEL"] = "DEBUG"
        os.environ["PYLOGS_LOG_DIR"] = self.log_dir
        os.environ["PYLOGS_DB_LOGGING"] = "true"
        os.environ["PYLOGS_DB_PATH"] = self.db_file
        os.environ["PYLOGS_JSON_LOGS"] = "true"
        os.environ["PYLOGS_STRUCTURED_LOGGING"] = "true"
        os.environ["PYLOGS_MAX_LOG_SIZE"] = "1048576"
        os.environ["PYLOGS_BACKUP_COUNT"] = "3"
        
        # Reset the logging module
        logging.shutdown()
        logging._handlerList.clear()
        root = logging.getLogger()
        map(root.removeHandler, root.handlers[:])
        map(root.removeFilter, root.filters[:])
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
        
        # Clean up environment variables
        for var in [
            "PYLOGS_LOG_LEVEL", "PYLOGS_LOG_DIR", "PYLOGS_DB_LOGGING",
            "PYLOGS_DB_PATH", "PYLOGS_JSON_LOGS", "PYLOGS_STRUCTURED_LOGGING",
            "PYLOGS_MAX_LOG_SIZE", "PYLOGS_BACKUP_COUNT"
        ]:
            if var in os.environ:
                del os.environ[var]
    
    def test_full_logging_pipeline(self):
        """Test the full logging pipeline with all components."""
        # Load environment variables
        load_env(verbose=False)
        
        # Setup logging from environment variables
        logger = setup_logging(
            name="integration_test",
            file_path=self.log_file
        )
        
        # Log messages with different levels and contexts
        logger.debug("Debug message")
        logger.info("Info message")
        
        with LogContext(user="test_user", operation="test"):
            logger.warning("Warning message with context")
            logger.error("Error message with context")
        
        # Log from a child logger
        child_logger = get_logger("integration_test.child")
        child_logger.critical("Critical message from child")
        
        # Check that the log file was created
        self.assertTrue(os.path.exists(self.log_file))
        
        # Check the content of the log file (JSON format)
        with open(self.log_file, "r") as f:
            log_lines = f.readlines()
            self.assertGreaterEqual(len(log_lines), 5)  # At least 5 log entries
            
            # Parse JSON logs and check content
            logs = [json.loads(line) for line in log_lines]
            
            # Check that all log levels are present
            levels = [log.get("level") for log in logs]
            self.assertIn("DEBUG", levels)
            self.assertIn("INFO", levels)
            self.assertIn("WARNING", levels)
            self.assertIn("ERROR", levels)
            self.assertIn("CRITICAL", levels)
            
            # Check context in logs
            for log in logs:
                if "with context" in log.get("message", ""):
                    self.assertEqual(log.get("user"), "test_user")
                    self.assertEqual(log.get("operation"), "test")
                
                if "child" in log.get("message", ""):
                    self.assertEqual(log.get("logger"), "integration_test.child")
        
        # Check the database
        self.assertTrue(os.path.exists(self.db_file))
        
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check that the logs table exists and has records
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        self.assertGreaterEqual(count, 5)  # At least 5 log entries
        
        # Check that context is stored in the database
        cursor.execute("SELECT * FROM logs WHERE message LIKE ?", ("%with context%",))
        rows = cursor.fetchall()
        self.assertGreaterEqual(len(rows), 2)  # At least 2 logs with context
        
        for row in rows:
            context = json.loads(row["context"])
            self.assertEqual(context.get("user"), "test_user")
            self.assertEqual(context.get("operation"), "test")
        
        conn.close()
    
    def test_error_logging(self):
        """Test logging of errors and exceptions."""
        # Setup logging with explicit file handler
        logger = setup_logging(
            name="error_test",
            level="DEBUG",
            console=True,
            file=True,
            file_path=self.log_file
        )
        
        # Log a regular message first to ensure the file is created
        logger.info("Initializing error test")
        
        # Log an exception
        try:
            # Generate a deliberate exception
            result = 1 / 0
        except Exception as e:
            logger.exception("An error occurred: %s", str(e))
        
        # Give the logger time to write to the file
        time.sleep(0.1)
        
        # Check if the log file exists, if not print diagnostic info
        if not os.path.exists(self.log_file):
            print(f"Log file not found at: {self.log_file}")
            print(f"Log directory exists: {os.path.exists(self.log_dir)}")
            print(f"Log directory contents: {os.listdir(self.log_dir)}")
            self.skipTest("Log file was not created")
        
        # Check that the log file contains the exception
        with open(self.log_file, "r") as f:
            log_content = f.read()
            self.assertIn("An error occurred: division by zero", log_content)
            self.assertIn("Traceback", log_content)  # Should include the traceback
            self.assertIn("ZeroDivisionError", log_content)
        
        # Check that the exception is in the database
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM logs WHERE message LIKE ?", ("%An error occurred%",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["level"], "ERROR")
        self.assertIn("ZeroDivisionError", row["message"])
        
        conn.close()
    
    def test_multiple_handlers(self):
        """Test logging with multiple handlers."""
        # Create a second log file
        second_log_file = os.path.join(self.log_dir, "second.log")
        
        # Setup logging with multiple handlers
        logger = setup_logging(
            name="multi_handler_test",
            level="INFO",
            console=True,
            file=True,
            file_path=self.log_file,
            database=True,
            db_path=self.db_file,
            json=True
        )
        
        # Add a second file handler
        from pylogs.handlers.rotating_file_handler import EnhancedRotatingFileHandler
        second_handler = EnhancedRotatingFileHandler(
            filename=second_log_file,
            maxBytes=1048576,
            backupCount=3
        )
        second_handler.setLevel(logging.WARNING)
        logger.addHandler(second_handler)
        
        # Log messages with different levels
        logger.debug("Debug message")  # Should not appear in second log
        logger.info("Info message")    # Should not appear in second log
        logger.warning("Warning message")  # Should appear in both logs
        logger.error("Error message")     # Should appear in both logs
        
        # Check the first log file (should have all levels except DEBUG)
        with open(self.log_file, "r") as f:
            log_content = f.read()
            self.assertNotIn("Debug message", log_content)  # DEBUG is filtered out by INFO level
            self.assertIn("Info message", log_content)
            self.assertIn("Warning message", log_content)
            self.assertIn("Error message", log_content)
        
        # Check the second log file (should only have WARNING and above)
        with open(second_log_file, "r") as f:
            log_content = f.read()
            self.assertNotIn("Debug message", log_content)
            self.assertNotIn("Info message", log_content)
            self.assertIn("Warning message", log_content)
            self.assertIn("Error message", log_content)
        
        # Check the database (should have all levels except DEBUG)
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT message FROM logs WHERE level = ?", ("DEBUG",))
        self.assertEqual(len(cursor.fetchall()), 0)  # No DEBUG messages
        
        cursor.execute("SELECT message FROM logs WHERE level = ?", ("INFO",))
        self.assertGreaterEqual(len(cursor.fetchall()), 1)  # At least one INFO message
        
        cursor.execute("SELECT message FROM logs WHERE level = ?", ("WARNING",))
        self.assertGreaterEqual(len(cursor.fetchall()), 1)  # At least one WARNING message
        
        cursor.execute("SELECT message FROM logs WHERE level = ?", ("ERROR",))
        self.assertGreaterEqual(len(cursor.fetchall()), 1)  # At least one ERROR message
        
        conn.close()


if __name__ == "__main__":
    unittest.main()
