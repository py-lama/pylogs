#!/usr/bin/env python3

import logging
import sqlite3
import os
import re
import time
from datetime import datetime
import random

# Configure the database path
DB_PATH = '/logs/loglama.db'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('web_log_monitor')

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
            random.randint(100, 500),  # Random line number for variety
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

def generate_realistic_web_logs():
    """Generate realistic web logs with various HTTP methods, paths, and status codes."""
    now = datetime.now()
    timestamp = now.strftime('%m/%d/%Y, %I:%M:%S %p')
    
    # Sample API endpoints with weights (more common endpoints have higher weights)
    endpoints = [
        ('/api/logs', 0.25),
        ('/api/stats', 0.15),
        ('/api/levels', 0.1),
        ('/api/components', 0.1),
        ('/', 0.25),
        ('/services', 0.05),
        ('/export', 0.05),
        ('/api/logs/clear', 0.02),
        ('/api/logs/filter', 0.03)
    ]
    
    # Sample HTTP methods with weights
    methods = [
        ('GET', 0.8),
        ('POST', 0.15),
        ('PUT', 0.03),
        ('DELETE', 0.02)
    ]
    
    # Sample status codes with weights
    statuses = [
        ('200', 0.85),  # OK
        ('201', 0.05),  # Created
        ('400', 0.03),  # Bad Request
        ('401', 0.01),  # Unauthorized
        ('403', 0.01),  # Forbidden
        ('404', 0.03),  # Not Found
        ('500', 0.02)   # Internal Server Error
    ]
    
    # Sample log levels with weights
    levels = [
        ('INFO', 0.7),
        ('WARNING', 0.15),
        ('ERROR', 0.1),
        ('DEBUG', 0.05)
    ]
    
    # Generate logs
    logs_generated = 0
    num_logs = random.randint(3, 10)  # Generate a random number of logs each time
    
    for _ in range(num_logs):
        # Select endpoint, method, status, and level based on weights
        endpoint = random.choices([e[0] for e in endpoints], weights=[e[1] for e in endpoints])[0]
        method = random.choices([m[0] for m in methods], weights=[m[1] for m in methods])[0]
        status = random.choices([s[0] for s in statuses], weights=[s[1] for s in statuses])[0]
        level = random.choices([l[0] for l in levels], weights=[l[1] for l in levels])[0]
        
        # Skip invalid combinations
        if method != 'GET' and endpoint in ['/', '/services'] and random.random() < 0.9:
            continue
        
        # Add query parameters for some GET requests
        if method == 'GET' and endpoint.startswith('/api/') and random.random() < 0.3:
            endpoint += f"?page={random.randint(1, 5)}&limit={random.choice([10, 20, 50, 100])}"
        
        # Create log message
        ip = f"172.17.0.{random.randint(1, 10)}"  # Random IP in Docker network
        message = f"{ip} - {method} {endpoint} {status}"
        
        # Insert log with appropriate level
        if status.startswith('4'):
            level = 'WARNING'  # Client errors are warnings
        elif status.startswith('5'):
            level = 'ERROR'    # Server errors are errors
        
        if insert_log(timestamp, level, 'loglama_web', message):
            logs_generated += 1
    
    logger.info(f"Generated {logs_generated} realistic web logs")
    return logs_generated

def main():
    """Main function to continuously monitor and generate web logs."""
    # Ensure database schema
    ensure_db_schema()
    
    logger.info("Starting web log monitoring...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            # Generate realistic web logs
            generate_realistic_web_logs()
            
            # Sleep for a random interval (1-5 seconds)
            sleep_time = random.uniform(1, 5)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.info("Web log monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error in web log monitoring: {e}")
    
    logger.info("Web log monitoring completed")

if __name__ == "__main__":
    main()
