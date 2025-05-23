#!/bin/bash

# LogLama-Grafana Connection Script
# This script sets up the connection between LogLama and Grafana

# Color definitions
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${GREEN}=== Setting up LogLama-Grafana Connection ===${NC}\n"

# Create Grafana provisioning directories
mkdir -p grafana-provisioning/datasources
mkdir -p grafana-provisioning/dashboards

# Create datasource configuration
echo -e "${BLUE}Creating Grafana datasource configuration...${NC}"
cat > grafana-provisioning/datasources/loglama.yml << EOL
apiVersion: 1

datasources:
  - name: LogLama
    type: frser-sqlite-datasource
    access: proxy
    uid: loglama
    isDefault: true
    jsonData:
      path: /logs/loglama.db
    version: 1
    editable: true
EOL

# Update docker-compose file to include Grafana provisioning
echo -e "${BLUE}Updating Docker Compose configuration...${NC}"
sed -i 's|      - ./logs:/logs:ro|      - ./logs:/logs:ro\n      - ./grafana-provisioning/datasources:/etc/grafana/provisioning/datasources:ro|g' docker-compose.simple.yml

# Restart containers
echo -e "${BLUE}Restarting Docker containers...${NC}"
docker compose -f docker-compose.simple.yml down
docker compose -f docker-compose.simple.yml up -d

# Wait for containers to start
sleep 5

# Check if containers are running
if docker ps | grep -q "loglama.*Up"; then
    echo -e "${GREEN}LogLama is running${NC}"
else
    echo -e "${YELLOW}Warning: LogLama container is not running properly${NC}"
    docker logs loglama
    exit 1
fi

if docker ps | grep -q "grafana.*Up"; then
    echo -e "${GREEN}Grafana is running${NC}"
else
    echo -e "${YELLOW}Warning: Grafana container is not running properly${NC}"
    docker logs grafana
    exit 1
fi

# Create a simple database initialization script
echo -e "${BLUE}Creating database initialization script...${NC}"
cat > init_loglama_db.py << EOL
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
EOL

# Run the database initialization script
python3 init_loglama_db.py

# Print instructions
echo -e "\n${GREEN}=== LogLama-Grafana Connection Setup Complete! ===${NC}"
echo -e "\nAccess Information:"
echo -e "LogLama Web UI: ${BLUE}http://localhost:5000${NC}"
echo -e "Grafana Dashboard: ${BLUE}http://localhost:3001${NC}"
echo -e "  - Default login: ${YELLOW}admin / admin${NC}"

echo -e "\n${GREEN}=== Manual Grafana Connection Instructions ===${NC}"
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
    xdg-open http://localhost:3001/connections/add-new-connection
fi
