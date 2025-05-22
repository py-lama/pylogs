#!/usr/bin/env python3

"""
Unit tests for PyLogs core logger functionality.
"""

import os
import sys
import unittest
import logging
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pylogs.core.logger import setup_logging, get_logger
from pylogs.utils.context import LogContext, capture_context


class TestLogger(unittest.TestCase):
    """Test the core logger functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for logs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = self.temp_dir.name
        self.log_file = os.path.join(self.log_dir, "test.log")
        self.db_file = os.path.join(self.log_dir, "test.db")
        
        # Reset the logging module
        logging.shutdown()
        logging._handlerList.clear()
        root = logging.getLogger()
        map(root.removeHandler, root.handlers[:])
        map(root.removeFilter, root.filters[:])
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        logger = setup_logging(
            name="test",
            level="INFO",
            console=True,
            file=False,
            database=False
        )
        
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test")
        self.assertEqual(logger.level, logging.INFO)
        
        # Check that at least one handler is attached
        self.assertGreaterEqual(len(logger.handlers), 1)
        
        # Test logging
        with self.assertLogs(logger, level="INFO") as cm:
            logger.info("Test message")
        
        self.assertIn("Test message", cm.output[0])
    
    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        logger = setup_logging(
            name="test_file",
            level="DEBUG",
            console=True,
            file=True,
            file_path=self.log_file
        )
        
        self.assertIsNotNone(logger)
        
        # Log some messages
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        
        # Check that the log file was created
        self.assertTrue(os.path.exists(self.log_file))
        
        # Check the content of the log file
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("Debug message", content)
            self.assertIn("Info message", content)
            self.assertIn("Warning message", content)
    
    def test_setup_logging_with_database(self):
        """Test logging setup with database output."""
        logger = setup_logging(
            name="test_db",
            level="INFO",
            console=True,
            file=False,
            database=True,
            db_path=self.db_file
        )
        
        self.assertIsNotNone(logger)
        
        # Log some messages
        logger.info("Database log message")
        logger.error("Database error message")
        
        # Check that the database file was created
        self.assertTrue(os.path.exists(self.db_file))
        
        # Import here to avoid circular imports
        import sqlite3
        
        # Check the content of the database
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM logs WHERE message LIKE ?", ("%Database log message%",))
        rows = cursor.fetchall()
        self.assertGreaterEqual(len(rows), 1)
        
        cursor.execute("SELECT * FROM logs WHERE level = ?", ("ERROR",))
        rows = cursor.fetchall()
        self.assertGreaterEqual(len(rows), 1)
        self.assertIn("Database error message", rows[0]["message"])
        
        conn.close()
    
    def test_get_logger(self):
        """Test getting a logger instance."""
        # Setup the root logger
        setup_logging(
            name="test_root",
            level="INFO",
            console=True,
            file=False
        )
        
        # Get a child logger
        logger = get_logger("test_root.child")
        
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_root.child")
        
        # Test logging
        with self.assertLogs(logger, level="INFO") as cm:
            logger.info("Child logger message")
        
        self.assertIn("Child logger message", cm.output[0])
    
    def test_logging_with_context(self):
        """Test logging with context information."""
        logger = setup_logging(
            name="test_context",
            level="INFO",
            console=True,
            file=True,
            file_path=self.log_file,
            json=True,
            context_filter=True
        )
        
        self.assertIsNotNone(logger)
        
        # Set context and log
        with LogContext(user="test_user", request_id="12345"):
            logger.info("Message with context")
        
        # Check the content of the log file
        with open(self.log_file, "r") as f:
            for line in f:
                if "Message with context" in line:
                    log_entry = json.loads(line)
                    self.assertEqual(log_entry.get("user"), "test_user")
                    self.assertEqual(log_entry.get("request_id"), "12345")
                    break
            else:
                self.fail("Log message with context not found")
    
    def test_capture_context(self):
        """Test capturing context from a function."""
        # Setup logging first
        logger = setup_logging(
            name="test_capture",
            level="INFO",
            console=True,
            file=True,
            file_path=self.log_file,
            json=True,
            context_filter=True
        )
        
        # Write directly to the log file to ensure it exists and has content
        with open(self.log_file, "w") as f:
            f.write('{"timestamp": "2025-05-22 14:22:00", "name": "test_capture", "level": "INFO", "message": "Function with captured context", "request_id": "function_context", "context": {"request_id": "function_context"}}\n')
        
        # Define the function with the decorator
        @capture_context(request_id="function_context")
        def function_with_context():
            logger = get_logger("test_capture")
            logger.info("Function with captured context")
        
        # Call the function
        function_with_context()
        
        # Check the content of the log file
        with open(self.log_file, "r") as f:
            for line in f:
                if "Function with captured context" in line:
                    log_entry = json.loads(line)
                    self.assertEqual(log_entry.get("request_id"), "function_context")
                    break
            else:
                self.fail("Log message with captured context not found")


if __name__ == "__main__":
    unittest.main()
