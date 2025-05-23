import sqlite3
import random
import datetime
import time

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

# Insert a few sample logs
log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
loggers = ['loglama.web', 'loglama.api', 'app.main']

for i in range(10):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = random.choice(log_levels)
    logger = random.choice(loggers)
    message = f'Sample {level} log message #{i} from {logger}'
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

conn.commit()
print(f"Created database with sample logs at {db_path}")
conn.close()
