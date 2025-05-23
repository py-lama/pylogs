#!/bin/bash

# LogLama-Grafana Integration Setup Script
# This script sets up a complete LogLama-Grafana integration with proper permissions

set -e

# Color definitions
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${GREEN}=== LogLama + Grafana Integration Setup ===${NC}\n"

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}Error: Docker is not running or not accessible${NC}"
    exit 1
fi

# Stop any existing containers
echo -e "${BLUE}Stopping any existing containers...${NC}"
docker compose -f docker-compose.simple.yml down 2>/dev/null || true

# Clean up existing logs directory with permission issues
echo -e "${BLUE}Setting up logs directory with proper permissions...${NC}"
sudo rm -rf logs
mkdir -p logs
chmod 777 logs

# Create a sample SQLite database with proper permissions
echo -e "${BLUE}Creating initial sample database...${NC}"
cat > logs/init_db.py << EOL
import sqlite3
import os

db_path = "loglama.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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
conn.close()

print(f"Created initial database at {db_path}")
os.chmod(db_path, 0o666)  # Make readable/writable by all
EOL

cd logs
python3 init_db.py
cd ..

# Build and start the services
echo -e "${BLUE}Building and starting LogLama and Grafana...${NC}"
docker compose -f docker-compose.simple.yml build --no-cache
docker compose -f docker-compose.simple.yml up -d

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 5

# Generate sample log data
echo -e "${BLUE}Generating sample log data...${NC}"
docker exec loglama python3 -c "

import sqlite3
import random
import datetime
import time
import os

# Connect to the SQLite database
db_path = '/logs/loglama.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create logs table if it doesn't exist
cursor.execute(\"\"\"
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
\"\"\")
conn.commit()

# Log levels
log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
loggers = ['loglama.web', 'loglama.api', 'app.main', 'app.auth', 'system']

# Generate historical logs (past 3 days)
print('Generating historical logs...')
now = datetime.datetime.now()
for day in range(3, 0, -1):
    for hour in range(0, 24, 4):  # Every 4 hours to reduce volume
        log_time = now - datetime.timedelta(days=day, hours=24-hour)
        timestamp = log_time.strftime('%Y-%m-%d %H:%M:%S')
        # Generate 5-10 logs per time period
        for _ in range(random.randint(5, 10)):
            level = random.choices(log_levels, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]
            logger = random.choice(loggers)
            message = f'Sample {level} log message from {logger}'
            cursor.execute(\"INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)\",
                (timestamp, level, logger, message, f'{logger}.py', random.randint(10, 100), 'process_request', '{}'))

# Generate real-time logs
print('Generating real-time logs...')
for i in range(20):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = random.choices(log_levels, weights=[0.5, 0.3, 0.15, 0.04, 0.01], k=1)[0]
    logger = random.choice(loggers)
    message = f'Real-time {level} log message #{i} from {logger}'
    cursor.execute(\"INSERT INTO logs (timestamp, level, logger, message, source, line, function, extra) VALUES (?, ?, ?, ?, ?, ?, ?, ?)\",
        (timestamp, level, logger, message, f'{logger}.py', random.randint(10, 100), 'process_request', '{}'))
    print(f'  {timestamp} - {level} - {logger}: {message}')
    time.sleep(0.1)

conn.commit()
count = cursor.execute('SELECT COUNT(*) FROM logs').fetchone()[0]
print(f'Generated {count} total log entries')
conn.close()
"

# Check if services are running
if docker ps | grep -q "loglama.*Up"; then
    echo -e "${GREEN}LogLama is running${NC}"
else
    echo -e "${YELLOW}Warning: LogLama container is not running properly${NC}"
    echo "Checking logs:"
    docker logs loglama
    exit 1
fi

if docker ps | grep -q "grafana.*Up"; then
    echo -e "${GREEN}Grafana is running${NC}"
else
    echo -e "${YELLOW}Warning: Grafana container is not running properly${NC}"
    echo "Checking logs:"
    docker logs grafana
    exit 1
fi

# Show access URLs
echo -e "\n${GREEN}=== Access Information ===${NC}"
echo -e "LogLama Web UI: ${BLUE}http://localhost:5000${NC}"
echo -e "Grafana Dashboard: ${BLUE}http://localhost:3001${NC}"
echo -e "  - Default login: ${YELLOW}admin / admin${NC}"
echo -e "\nTo view logs:"
echo -e "  ${YELLOW}docker compose -f docker-compose.simple.yml logs -f${NC}"
echo -e "\nTo stop the services:"
echo -e "  ${YELLOW}docker compose -f docker-compose.simple.yml down${NC}"

# Instructions for setting up Grafana connection
echo -e "\n${GREEN}=== Setting Up Grafana Connection ===${NC}"
echo -e "1. Log into Grafana at ${BLUE}http://localhost:3001${NC} with admin/admin"
echo -e "2. Go to Connections > Data Sources > Add data source"
echo -e "3. Select 'SQLite'"
echo -e "4. Configure with these settings:"
echo -e "   - Name: ${YELLOW}LogLama${NC}"
echo -e "   - Path: ${YELLOW}/logs/loglama.db${NC}"
echo -e "5. Click 'Save & Test'"
echo -e "6. Create a new dashboard with SQL queries like:"
echo -e "   ${YELLOW}SELECT timestamp as time, level, logger, message FROM logs ORDER BY timestamp DESC LIMIT 100${NC}"

# Open browser if xdg-open is available
if command -v xdg-open &> /dev/null; then
    echo -e "\n${BLUE}Opening LogLama Web UI in browser...${NC}"
    xdg-open http://localhost:5000
    sleep 2
    echo -e "${BLUE}Opening Grafana Dashboard in browser...${NC}"
    xdg-open http://localhost:3001
fi

echo -e "\n${GREEN}Setup complete! See GRAFANA_CONNECTION_GUIDE.md for detailed instructions.${NC}"
