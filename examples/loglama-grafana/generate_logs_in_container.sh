#!/bin/bash

# Script to generate sample logs inside the LogLama container
echo "Generating sample log data in the LogLama container..."

docker exec loglama python3 -c "import sqlite3, random, datetime, time; \
conn = sqlite3.connect('/logs/loglama.db'); \
cursor = conn.cursor(); \
cursor.execute('CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, level TEXT, logger TEXT, message TEXT, source TEXT, line INTEGER, function TEXT, extra TEXT)'); \
conn.commit(); \
log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']; \
loggers = ['loglama.web', 'loglama.api', 'app.main', 'app.auth', 'system']; \
print('Generating historical logs...'); \
now = datetime.datetime.now(); \
for day in range(3, 0, -1): \
    for hour in range(0, 24, 2): \
        log_time = now - datetime.timedelta(days=day, hours=24-hour); \
        timestamp = log_time.strftime('%Y-%m-%d %H:%M:%S'); \
        for _ in range(random.randint(5, 10)): \
            level = random.choices(log_levels, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]; \
            logger = random.choice(loggers); \
            message = f'Sample {level} log message from {logger}'; \
            cursor.execute(\"INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)\", \
                (timestamp, level, logger, message, f'{logger}.py', random.randint(10, 100), 'process_request', '{}')); \
print('Generating real-time logs...'); \
for i in range(20): \
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'); \
    level = random.choices(log_levels, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]; \
    logger = random.choice(loggers); \
    message = f'Real-time {level} log message #{i} from {logger}'; \
    cursor.execute(\"INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)\", \
        (timestamp, level, logger, message, f'{logger}.py', random.randint(10, 100), 'process_request', '{}')); \
    print(f'  {timestamp} - {level} - {logger}: {message}'); \
    time.sleep(0.2); \
conn.commit(); \
count = cursor.execute('SELECT COUNT(*) FROM logs').fetchone()[0]; \
print(f'Generated {count} total log entries'); \
conn.close();"

echo "Sample log data generation complete."
