#!/usr/bin/env python3
"""
Generate sample logs for the LogLama-Grafana integration example.
This script creates a variety of log entries to demonstrate the dashboard functionality.
"""

import os
import sys
import time
import random
import sqlite3
import datetime
from pathlib import Path

# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# SQLite database path
db_path = logs_dir / "loglama.db"

# Create or connect to the SQLite database
conn = sqlite3.connect(str(db_path))
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

# Log levels with their probabilities
log_levels = {
    "DEBUG": 0.5,
    "INFO": 0.3,
    "WARNING": 0.15,
    "ERROR": 0.04,
    "CRITICAL": 0.01
}

# Sample loggers
loggers = [
    "app",
    "app.api",
    "app.database",
    "app.auth",
    "app.ui",
    "system",
    "network",
    "loglama.web",
    "loglama.collector"
]

# Sample message templates
message_templates = {
    "DEBUG": [
        "Debug information for {component}",
        "Processing {item} with value {value}",
        "Checking {condition} condition",
        "Variable {name} = {value}",
        "Entering function {function}"
    ],
    "INFO": [
        "Successfully processed {item}",
        "User {user} logged in",
        "Request completed in {time}ms",
        "Started {service} service",
        "Configuration loaded from {source}"
    ],
    "WARNING": [
        "Slow response time: {time}ms",
        "Deprecated function {function} called",
        "High resource usage: {resource} at {percentage}%",
        "Retry attempt {attempt} of {max_attempts}",
        "Missing optional parameter {param}"
    ],
    "ERROR": [
        "Failed to connect to {service}",
        "Exception occurred: {exception}",
        "Could not process {item}: {reason}",
        "Invalid input: {input}",
        "Database query failed: {query}"
    ],
    "CRITICAL": [
        "System shutdown due to {reason}",
        "Data corruption detected in {location}",
        "Security breach detected: {details}",
        "Fatal error in {component}: {error}",
        "Service {service} crashed"
    ]
}

# Sample values for message formatting
sample_values = {
    "component": ["API", "Database", "Auth", "UI", "Network", "Cache"],
    "item": ["request", "user", "file", "transaction", "message", "event"],
    "value": ["42", "true", "active", "pending", "completed", "null"],
    "condition": ["timeout", "valid", "authorized", "available", "enabled"],
    "name": ["count", "index", "status", "flag", "mode", "level"],
    "function": ["process_data", "validate_input", "authenticate_user", "save_record", "load_config"],
    "user": ["admin", "user123", "guest", "system", "api_client"],
    "time": ["50", "120", "200", "500", "1000", "2000"],
    "service": ["database", "api", "auth", "cache", "queue", "worker"],
    "source": ["config.json", "settings.yml", "database", "api", "user input"],
    "resource": ["CPU", "memory", "disk", "network", "database connections"],
    "percentage": ["75", "80", "85", "90", "95"],
    "attempt": ["2", "3", "4", "5"],
    "max_attempts": ["3", "5", "10"],
    "param": ["timeout", "retry_count", "callback", "filter", "sort_order"],
    "exception": ["ValueError", "KeyError", "ConnectionError", "TimeoutError", "AuthenticationError"],
    "reason": ["timeout", "invalid input", "permission denied", "not found", "already exists"],
    "input": ["negative value", "empty string", "null reference", "invalid format", "out of range"],
    "query": ["SELECT * FROM users", "UPDATE records SET status='active'", "INSERT INTO logs"],
    "location": ["database", "config file", "log file", "cache", "memory"],
    "details": ["suspicious login attempt", "unusual access pattern", "modified system files"],
    "error": ["segmentation fault", "stack overflow", "out of memory", "deadlock detected"]
}

def format_message(template, level):
    """Format a message template with random values."""
    result = template
    for placeholder in [p for p in sample_values if '{' + p + '}' in template]:
        result = result.replace('{' + placeholder + '}', random.choice(sample_values[placeholder]))
    return result

def generate_log_entry(timestamp=None):
    """Generate a random log entry."""
    # Determine log level based on probabilities
    level = random.choices(
        list(log_levels.keys()),
        weights=list(log_levels.values()),
        k=1
    )[0]
    
    # Select random logger
    logger = random.choice(loggers)
    
    # Select and format random message template
    template = random.choice(message_templates[level])
    message = format_message(template, level)
    
    # Generate timestamp if not provided
    if timestamp is None:
        # Current time
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate source file and line
    source = f"{logger.replace('.', '/')}.py"
    line = random.randint(10, 500)
    function = f"{logger.split('.')[-1]}_{random.choice(['process', 'handle', 'get', 'update', 'create'])}"
    
    return {
        "timestamp": timestamp,
        "level": level,
        "logger": logger,
        "message": message,
        "source": source,
        "line": line,
        "function": function,
        "extra": "{}"
    }

def insert_log_entry(entry):
    """Insert a log entry into the database."""
    cursor.execute("""
    INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry["timestamp"],
        entry["level"],
        entry["logger"],
        entry["message"],
        entry["source"],
        entry["line"],
        entry["function"],
        entry["extra"]
    ))
    conn.commit()

def generate_historical_logs(days=3, entries_per_day=200):
    """Generate historical log data for the past few days."""
    print(f"Generating historical logs for the past {days} days...")
    
    now = datetime.datetime.now()
    
    for day in range(days, 0, -1):
        start_date = now - datetime.timedelta(days=day)
        
        # Generate logs throughout the day
        for i in range(entries_per_day):
            # Random time within the day
            minutes_offset = random.randint(0, 24 * 60 - 1)
            log_time = start_date + datetime.timedelta(minutes=minutes_offset)
            timestamp = log_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate and insert log entry
            entry = generate_log_entry(timestamp)
            insert_log_entry(entry)
            
            if i % 50 == 0:
                print(f"  Generated {i} of {entries_per_day} logs for {start_date.date()}")
    
    print("Historical log generation complete.")

def generate_realtime_logs(count=20, interval=0.5):
    """Generate logs in real-time with a delay between entries."""
    print(f"Generating {count} real-time logs with {interval}s interval...")
    
    for i in range(count):
        entry = generate_log_entry()
        insert_log_entry(entry)
        print(f"  [{entry['timestamp']}] {entry['level']} - {entry['logger']}: {entry['message']}")
        time.sleep(interval)
    
    print("Real-time log generation complete.")

def main():
    print(f"LogLama Sample Log Generator")
    print(f"Database: {db_path}")
    
    # Check if the logs table already has data
    cursor.execute("SELECT COUNT(*) FROM logs")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("No existing logs found. Generating historical data...")
        generate_historical_logs()
    else:
        print(f"Found {count} existing log entries.")
    
    # Always generate some real-time logs
    generate_realtime_logs()
    
    print(f"Total log entries: {cursor.execute('SELECT COUNT(*) FROM logs').fetchone()[0]}")
    print("Done. You can now view the logs in Grafana.")

if __name__ == "__main__":
    try:
        main()
    finally:
        conn.close()
