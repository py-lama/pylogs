#!/usr/bin/env python3

"""
Test database logging in the PyLama ecosystem.

This script tests that logs are properly saved to the database and can be viewed in the LogLama web interface.
"""

import os
import sys
import time
import sqlite3
from pathlib import Path

# Add the parent directory to the path so we can import loglama
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import LogLama modules
from loglama.config.env_loader import load_env, get_env
from loglama.core.simple_logger import setup_logging, info, warning, error, exception


def ensure_db_exists(db_path):
    """Ensure the database exists and has the necessary tables."""
    # Create the directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}")

    # Connect to the database and create the table if it doesn't exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the log records table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS log_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        level_number INTEGER NOT NULL,
        logger_name TEXT NOT NULL,
        message TEXT NOT NULL,
        file_path TEXT,
        line_number INTEGER,
        function TEXT,
        module TEXT,
        process_id INTEGER,
        process_name TEXT,
        thread_id INTEGER,
        thread_name TEXT,
        exception_info TEXT,
        context TEXT
    )
    """)
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_records_timestamp ON log_records (timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_log_records_level ON log_records (level_number)")
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")


def check_logs_in_db(db_path):
    """Check if logs are being saved to the database."""
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM log_records")
        count = cursor.fetchone()[0]
        print(f"Total logs in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT timestamp, level, logger_name, message FROM log_records ORDER BY timestamp DESC LIMIT 5")
            print("\nRecent logs:")
            for row in cursor.fetchall():
                print(row)
        
        conn.close()
        return count > 0
    except Exception as e:
        print(f"Error checking logs: {str(e)}")
        conn.close()
        return False


def generate_test_logs():
    """Generate test logs to verify database logging."""
    info("Starting database logging test", logger_name="test_db_logging")
    warning("This is a warning message", logger_name="test_db_logging")
    error("This is an error message", logger_name="test_db_logging")
    
    # Test logging with context
    info("Log with context", logger_name="test_db_logging", user="test_user", action="test_action")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        exception("Exception occurred", logger_name="test_db_logging")
    
    info("Database logging test completed", logger_name="test_db_logging")


def main():
    """Main function to test database logging."""
    # Load environment variables
    load_env(verbose=True)
    
    # Get database path from environment
    db_path = get_env("LOGLAMA_DB_PATH", "./logs/loglama.db")
    db_path = os.path.abspath(db_path)
    print(f"Using database path: {db_path}")
    
    # Ensure database exists and has the necessary tables
    ensure_db_exists(db_path)
    
    # Setup logging with database handler
    setup_logging(
        name="test_db_logging",
        level="INFO",
        console=True,
        file=True,
        database=True,
        db_path=db_path
    )
    
    # Generate test logs
    generate_test_logs()
    
    # Wait a moment for logs to be written
    time.sleep(1)
    
    # Check if logs are in the database
    logs_saved = check_logs_in_db(db_path)
    
    if logs_saved:
        print("\n✅ Test passed: Logs are being saved to the database!")
        print(f"\nYou can view the logs using the LogLama web interface:")
        print(f"  python -m loglama.cli.main web --db {db_path}")
    else:
        print("\n❌ Test failed: Logs are not being saved to the database.")


if __name__ == "__main__":
    main()
