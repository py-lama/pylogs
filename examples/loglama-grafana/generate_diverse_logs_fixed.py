#!/usr/bin/env python3

import logging
import sqlite3
import os
import random
import time
from datetime import datetime, timedelta

# Configure the database path
DB_PATH = '/logs/loglama.db'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('diverse_logs_generator')

# Define components and their log patterns
COMPONENTS = [
    {
        'name': 'app.api',
        'messages': [
            'API request received for {endpoint}',
            'API request processed in {time}ms',
            'API rate limit exceeded for client {client_id}',
            'API authentication failed for client {client_id}',
            'API endpoint {endpoint} not found',
            'API response sent with status {status}',
            'API request validation failed: {reason}',
            'API cache hit for {endpoint}',
            'API cache miss for {endpoint}',
            'API request timed out after {time}ms'
        ]
    },
    {
        'name': 'app.database',
        'messages': [
            'Database query executed in {time}ms',
            'Database connection established',
            'Database connection failed: {reason}',
            'Database transaction committed',
            'Database transaction rolled back: {reason}',
            'Database query failed: {reason}',
            'Database query returned {count} results',
            'Database index created for {table}.{column}',
            'Database backup completed in {time}s',
            'Database optimization completed in {time}s'
        ]
    },
    {
        'name': 'app.auth',
        'messages': [
            'User {username} logged in successfully',
            'User {username} login failed: {reason}',
            'User {username} password reset requested',
            'User {username} password changed',
            'User {username} account locked after {count} failed attempts',
            'User {username} session expired',
            'User {username} permissions updated',
            'OAuth token issued for user {username}',
            'OAuth token revoked for user {username}',
            'Two-factor authentication enabled for user {username}'
        ]
    },
    {
        'name': 'app.ui',
        'messages': [
            'Page {page} loaded in {time}ms',
            'User interface rendering completed',
            'User interface component {component} failed to load',
            'User interface theme changed to {theme}',
            'User interface language changed to {language}',
            'User interface form submission validated',
            'User interface form submission failed validation',
            'User interface modal dialog opened',
            'User interface modal dialog closed',
            'User interface notification displayed'
        ]
    },
    {
        'name': 'app.network',
        'messages': [
            'Network connection established to {host}',
            'Network connection failed to {host}: {reason}',
            'Network packet loss detected: {percent}%',
            'Network latency increased to {time}ms',
            'Network throughput: {throughput} MB/s',
            'Network DNS resolution failed for {host}',
            'Network proxy configuration updated',
            'Network SSL certificate validation failed for {host}',
            'Network bandwidth throttled to {bandwidth} MB/s',
            'Network connection closed to {host}'
        ]
    },
    {
        'name': 'system',
        'messages': [
            'System startup completed in {time}s',
            'System shutdown initiated',
            'System memory usage: {percent}%',
            'System CPU usage: {percent}%',
            'System disk usage: {percent}%',
            'System service {service} started',
            'System service {service} stopped',
            'System update available: version {version}',
            'System backup completed',
            'System error detected: {error}'
        ]
    },
    {
        'name': 'loglama_web',
        'messages': [
            'Web server started on port {port}',
            'Web request received: {method} {path}',
            'Web response sent: {status}',
            'Web session created for user {username}',
            'Web session expired for user {username}',
            'Web static file not found: {path}',
            'Web template rendering completed in {time}ms',
            'Web form submission received',
            'Web redirect issued to {path}',
            'Web server configuration reloaded'
        ]
    },
    {
        'name': 'loglama_collector',
        'messages': [
            'Log collector started',
            'Log collector connected to source {source}',
            'Log collector disconnected from source {source}',
            'Log collector processed {count} log entries',
            'Log collector filter applied: {filter}',
            'Log collector buffer utilization: {percent}%',
            'Log collector rate: {rate} logs/second',
            'Log collector error: {error}',
            'Log collector configuration updated',
            'Log collector flush completed in {time}ms'
        ]
    }
]

# Define placeholders and their possible values
def get_placeholder_value(placeholder):
    """Get a value for a placeholder."""
    placeholders = {
        'endpoint': [
            '/api/users', '/api/products', '/api/orders', '/api/auth/login',
            '/api/auth/logout', '/api/settings', '/api/reports', '/api/analytics',
            '/api/notifications', '/api/search'
        ],
        'time': lambda: str(random.randint(1, 5000)),
        'client_id': lambda: f'client_{random.randint(1000, 9999)}',
        'status': ['200 OK', '201 Created', '400 Bad Request', '401 Unauthorized', '403 Forbidden', '404 Not Found', '500 Internal Server Error'],
        'reason': [
            'Invalid input', 'Missing required field', 'Database error',
            'Network timeout', 'Authentication failed', 'Permission denied',
            'Resource not found', 'Service unavailable', 'Rate limit exceeded',
            'Internal error'
        ],
        'count': lambda: str(random.randint(1, 1000)),
        'table': ['users', 'products', 'orders', 'settings', 'logs', 'sessions', 'permissions'],
        'column': ['id', 'name', 'email', 'created_at', 'updated_at', 'status', 'type'],
        'username': lambda: f'user_{random.randint(1000, 9999)}',
        'page': ['home', 'dashboard', 'profile', 'settings', 'products', 'orders', 'reports', 'admin'],
        'component': ['header', 'footer', 'sidebar', 'modal', 'form', 'table', 'chart', 'notification'],
        'theme': ['light', 'dark', 'blue', 'green', 'custom'],
        'language': ['en', 'es', 'fr', 'de', 'ja', 'zh', 'ru', 'pt'],
        'host': lambda: f'{random.choice(["api", "db", "auth", "cdn", "storage"])}.example.com',
        'percent': lambda: str(random.randint(1, 100)),
        'throughput': lambda: str(round(random.uniform(0.1, 100.0), 2)),
        'bandwidth': lambda: str(round(random.uniform(0.1, 10.0), 2)),
        'service': ['web', 'database', 'cache', 'queue', 'worker', 'scheduler', 'mailer'],
        'version': lambda: f'{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
        'error': [
            'Out of memory', 'Disk full', 'Connection refused', 'Timeout',
            'Invalid configuration', 'Missing dependency', 'Version mismatch',
            'Corrupt data', 'Hardware failure', 'Resource exhaustion'
        ],
        'port': lambda: str(random.choice([80, 443, 8080, 8443, 3000, 5000])),
        'method': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        'path': ['/', '/dashboard', '/profile', '/settings', '/login', '/logout', '/register', '/admin'],
        'source': ['app', 'database', 'system', 'network', 'security', 'user', 'external'],
        'filter': ['level:INFO', 'level:ERROR', 'component:app', 'component:system', 'timerange:1h', 'timerange:24h'],
        'rate': lambda: str(random.randint(10, 5000))
    }
    
    if placeholder in placeholders:
        value = placeholders[placeholder]
        if callable(value):
            return value()
        else:
            return random.choice(value)
    return f'{{{placeholder}}}'

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

def replace_placeholders(message):
    """Replace placeholders in a message with random values."""
    import re
    
    # Find all placeholders in the message
    placeholders = re.findall(r'\{(\w+)\}', message)
    
    # Replace each placeholder with a random value
    for placeholder in placeholders:
        replacement = get_placeholder_value(placeholder)
        message = message.replace(f'{{{placeholder}}}', replacement)
    
    return message

def insert_log(component, level, message, timestamp=None):
    """Insert a log record into the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Use current time if timestamp not provided
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Get level number
        level_number = get_level_number(level)
        
        # Insert log record
        cursor.execute("""
        INSERT INTO log_records (
            timestamp, level, level_number, logger_name, message, 
            file_path, line_number, function, module
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            level,
            level_number,
            component,
            message,
            f'/app/{component.replace(".", "/")}.py',  # Generate a plausible file path
            random.randint(10, 500),  # Random line number
            f'handle_{random.choice(["request", "event", "process", "task"])}',  # Random function name
            component.split('.')[-1]  # Module name from component
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error inserting log: {e}")
        return False

def generate_diverse_logs(count=50, time_range_hours=6):
    """Generate diverse logs across different components and levels."""
    # Generate logs with timestamps spread over the specified time range
    now = datetime.now()
    
    # Level weights (INFO most common, CRITICAL least common)
    level_weights = {
        'DEBUG': 0.2,
        'INFO': 0.6,
        'WARNING': 0.15,
        'ERROR': 0.04,
        'CRITICAL': 0.01
    }
    
    logs_generated = 0
    
    for _ in range(count):
        # Select a random component
        component = random.choice(COMPONENTS)
        component_name = component['name']
        
        # Select a random message template from the component
        message_template = random.choice(component['messages'])
        
        # Replace placeholders in the message
        message = replace_placeholders(message_template)
        
        # Select a log level based on weights
        level = random.choices(
            list(level_weights.keys()),
            weights=list(level_weights.values())
        )[0]
        
        # Generate a timestamp within the specified time range
        time_offset = timedelta(seconds=random.randint(0, time_range_hours * 3600))
        log_timestamp = (now - time_offset).isoformat()
        
        # Insert the log
        if insert_log(component_name, level, message, log_timestamp):
            logs_generated += 1
    
    logger.info(f"Generated {logs_generated} diverse logs")
    return logs_generated

def main():
    """Main function to generate diverse logs."""
    # Ensure database schema
    ensure_db_schema()
    
    # Generate diverse logs
    generate_diverse_logs(count=100, time_range_hours=6)
    
    logger.info("Diverse log generation completed successfully")

if __name__ == "__main__":
    main()
