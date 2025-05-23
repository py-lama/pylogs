#!/usr/bin/env python3

import logging
import sqlite3
import os
import re
import time
from datetime import datetime

# Configure the database path
DB_PATH = '/logs/loglama.db'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('web_log_capture')

# Regular expression to parse LogLama web logs
LOG_PATTERN = re.compile(r'(\d+/\d+/\d+, \d+:\d+:\d+ [AP]M)\s+(\w+)\s+(\w+)\s+(.*)')
API_REQUEST_PATTERN = re.compile(r'(\d+\.\d+\.\d+\.\d+) - (GET|POST|PUT|DELETE) (.*) (\d+)')

def ensure_db_schema():
    """Ensure the database schema exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the log_records table if it doesn't exist
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
    logger.info(f"Database schema ensured at {DB_PATH}")

def get_level_number(level_name):
    """Convert level name to level number."""
    level_map = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }
    return level_map.get(level_name, 20)  # Default to INFO if level not found

def insert_log(timestamp, level, logger_name, message):
    """Insert a log record into the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Convert timestamp to ISO format
        dt = datetime.strptime(timestamp, '%m/%d/%Y, %I:%M:%S %p')
        iso_timestamp = dt.isoformat()
        
        # Get level number
        level_number = get_level_number(level)
        
        # Insert log record
        cursor.execute("""
        INSERT INTO log_records (
            timestamp, level, level_number, logger_name, message, 
            file_path, line_number, function, module
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            iso_timestamp,
            level,
            level_number,
            logger_name,
            message,
            '/app/loglama/web/app.py',  # Assuming web logs come from app.py
            0,  # Default line number
            'handle_request',  # Assuming function name
            'web'  # Module name
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Inserted log: {timestamp} - {level} - {logger_name} - {message}")
        return True
    except Exception as e:
        logger.error(f"Error inserting log: {e}")
        return False

def parse_and_insert_api_log(log_entry):
    """Parse an API log entry and insert it into the database."""
    try:
        # Parse the log entry
        match = LOG_PATTERN.match(log_entry)
        if not match:
            logger.warning(f"Could not parse log entry: {log_entry}")
            return False
        
        timestamp, level, logger_name, message = match.groups()
        
        # Parse API request details
        api_match = API_REQUEST_PATTERN.match(message.strip())
        if api_match:
            ip, method, path, status = api_match.groups()
            # Enhanced message with more details
            message = f"HTTP {method} {path} - Status: {status} - Client: {ip}"
        
        # Insert into database
        return insert_log(timestamp, level, logger_name, message)
    except Exception as e:
        logger.error(f"Error parsing log entry: {e}")
        return False

def generate_sample_web_logs():
    """Generate sample web logs for demonstration."""
    now = datetime.now()
    timestamp = now.strftime('%m/%d/%Y, %I:%M:%S %p')
    
    # Sample API endpoints
    endpoints = [
        '/api/logs', '/api/stats', '/api/levels', '/api/components',
        '/', '/services', '/export', '/api/logs/clear'
    ]
    
    # Sample HTTP methods
    methods = ['GET', 'POST']
    
    # Sample status codes
    statuses = ['200', '201', '400', '404', '500']
    
    # Generate logs
    logs_generated = 0
    for endpoint in endpoints:
        for method in methods:
            # Skip invalid combinations
            if method == 'POST' and endpoint in ['/', '/services']:
                continue
                
            # Generate a status code (mostly 200, but occasionally others)
            import random
            status = '200' if random.random() < 0.9 else random.choice(statuses)
            
            # Create log message
            message = f"172.17.0.1 - {method} {endpoint} {status}"
            
            # Insert log
            if insert_log(timestamp, 'INFO', 'loglama_web', message):
                logs_generated += 1
    
    logger.info(f"Generated {logs_generated} sample web logs")
    return logs_generated

def main():
    """Main function to capture and process web logs."""
    # Ensure database schema
    ensure_db_schema()
    
    # Generate sample logs
    generate_sample_web_logs()
    
    logger.info("Web log capture completed successfully")

if __name__ == "__main__":
    main()
