#!/usr/bin/env python3

import logging
import random
import time
from datetime import datetime, timedelta
import sqlite3
import os

class SQLiteHandler(logging.Handler):
    def __init__(self, db_path):
        logging.Handler.__init__(self)
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()
    
    def emit(self, record):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO log_records (timestamp, level, level_number, logger_name, message, file_path, line_number, function, module)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.fromtimestamp(record.created).isoformat(),
            record.levelname,
            record.levelno,
            record.name,
            record.getMessage(),
            record.pathname if hasattr(record, 'pathname') else '',
            record.lineno if hasattr(record, 'lineno') else 0,
            record.funcName if hasattr(record, 'funcName') else '',
            record.module if hasattr(record, 'module') else ''
        ))
        
        conn.commit()
        conn.close()

# Configure logging
db_path = '/logs/loglama.db'
handler = SQLiteHandler(db_path)
logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Add console handler for debugging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Define log data
levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
loggers = ['app.api', 'app.database', 'app.auth', 'app.ui', 'app.network', 'system']

messages = [
    'User login successful',
    'User login failed',
    'Database query executed',
    'API request processed',
    'File upload completed',
    'Authentication token expired',
    'Data validation error',
    'Network connection timeout',
    'Cache miss',
    'Background job started',
    'Background job completed',
    'Configuration loaded',
    'Memory usage high',
    'CPU usage spike detected',
    'Disk space running low'
]

# Generate logs with timestamps spread over the last few hours
print(f"Generating logs in {db_path}...")

num_logs = 200
now = datetime.now()

for i in range(num_logs):
    # Select random components
    level_idx = random.choices([0, 1, 2, 3, 4], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
    level = levels[level_idx]
    logger_name = random.choice(loggers)
    message = random.choice(messages)
    
    # Add some context to the message
    if 'login' in message:
        message += f" for user user_{random.randint(1000, 9999)}"
    elif 'query' in message:
        message += f" in {random.choice(['users', 'orders', 'products', 'settings'])} table"
    elif 'API' in message:
        message += f" for endpoint /{random.choice(['users', 'orders', 'products', 'auth'])}"
    
    # Create a log record
    record = logging.LogRecord(
        name=logger_name,
        level=level,
        pathname=__file__,
        lineno=random.randint(10, 500),
        msg=message,
        args=(),
        exc_info=None
    )
    
    # Set a timestamp within the last 6 hours
    time_offset = timedelta(seconds=random.randint(0, 6 * 60 * 60))
    record.created = (now - time_offset).timestamp()
    
    # Emit the record
    handler.emit(record)
    
    # Print progress
    if (i + 1) % 20 == 0:
        print(f"Generated {i + 1}/{num_logs} logs")
    
    # Small delay to avoid overwhelming the database
    time.sleep(0.05)

print(f"Successfully generated {num_logs} logs in {db_path}")
