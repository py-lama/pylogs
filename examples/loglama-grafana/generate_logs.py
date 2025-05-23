#!/usr/bin/env python3
"""
Generate sample logs for LogLama-Grafana integration.
"""

import sqlite3
import random
import datetime
import time
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Connect to the SQLite database
db_path = "logs/loglama.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create logs table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    level TEXT,
    logger TEXT,
    message TEXT,
    source TEXT,
    line INTEGER,
    function TEXT,
    extra TEXT
)
""")
conn.commit()

# Log levels
log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
loggers = ['loglama.web', 'loglama.api', 'app.main', 'app.auth', 'system']

# Generate historical logs (past 3 days)
print('Generating historical logs...')
now = datetime.datetime.now()
for day in range(3, 0, -1):
    for hour in range(0, 24, 2):  # Every 2 hours to reduce volume
        log_time = now - datetime.timedelta(days=day, hours=24-hour)
        timestamp = log_time.strftime('%Y-%m-%d %H:%M:%S')
        # Generate 5-10 logs per time period
        for _ in range(random.randint(5, 10)):
            level = random.choices(log_levels, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]
            logger = random.choice(loggers)
            message = f'Sample {level} log message from {logger}'
            cursor.execute("""
            INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, 
                level, 
                logger, 
                message, 
                f'{logger}.py', 
                random.randint(10, 100), 
                'process_request', 
                '{}'
            ))

# Generate real-time logs
print('Generating real-time logs...')
for i in range(20):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = random.choices(log_levels, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]
    logger = random.choice(loggers)
    message = f'Real-time {level} log message #{i} from {logger}'
    cursor.execute("""
    INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, 
        level, 
        logger, 
        message, 
        f'{logger}.py', 
        random.randint(10, 100), 
        'process_request', 
        '{}'
    ))
    print(f'  {timestamp} - {level} - {logger}: {message}')
    time.sleep(0.2)

conn.commit()
count = cursor.execute('SELECT COUNT(*) FROM logs').fetchone()[0]
print(f'Generated {count} total log entries')
conn.close()

print(f"\nSample log data has been generated in {db_path}")
print("You can now access LogLama at http://localhost:5000")
print("and set up Grafana at http://localhost:3001 (login: admin/admin)")
