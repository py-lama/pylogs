#!/usr/bin/env python3
"""
LogLama-Grafana Integration Setup Script

This script sets up the LogLama-Grafana integration by:
1. Creating a proper SQLite database for LogLama
2. Generating sample log data
3. Configuring Docker containers
4. Providing instructions for Grafana connection
"""

import os
import subprocess
import sqlite3
import random
import datetime
import time
import sys

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def print_color(color, message):
    """Print colored message"""
    print(f"{color}{message}{NC}")

def run_command(command):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_logs_directory():
    """Set up logs directory with proper permissions"""
    print_color(BLUE, "Setting up logs directory...")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Ensure everyone can write to it
    os.chmod("logs", 0o777)
    
    return os.path.abspath("logs")

def create_sqlite_database(logs_dir):
    """Create SQLite database for LogLama"""
    print_color(BLUE, "Creating SQLite database for LogLama...")
    
    db_path = os.path.join(logs_dir, "loglama.db")
    
    # Create database and table
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
    
    # Make database writable by all
    os.chmod(db_path, 0o666)
    
    print_color(GREEN, f"Created database at {db_path}")
    return db_path

def generate_sample_logs(db_path):
    """Generate sample log data"""
    print_color(BLUE, "Generating sample log data...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Log levels and loggers
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    loggers = ['loglama.web', 'loglama.api', 'app.main', 'app.auth', 'system']
    
    # Generate historical logs (past 3 days)
    print("Generating historical logs...")
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
    print("Generating real-time logs...")
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
        print(f"  {timestamp} - {level} - {logger}: {message}")
        time.sleep(0.1)
    
    conn.commit()
    count = cursor.execute('SELECT COUNT(*) FROM logs').fetchone()[0]
    print_color(GREEN, f"Generated {count} total log entries")
    conn.close()

def update_docker_compose(db_path):
    """Update docker-compose.yml with correct database path"""
    print_color(BLUE, "Updating Docker Compose configuration...")
    
    # Create a new docker-compose file with absolute paths
    with open("docker-compose.yml", "w") as f:
        f.write(f"""# LogLama with Grafana integration

services:
  loglama:
    build:
      context: ../..
      dockerfile: examples/loglama-grafana/Dockerfile.simple
    image: loglama-grafana:simple
    container_name: loglama
    ports:
      - "5000:5000"
    volumes:
      - {os.path.abspath('logs')}:/logs
    environment:
      - LOGLAMA_LOG_DIR=/logs
      - LOGLAMA_CONSOLE_ENABLED=true
      - LOGLAMA_SQLITE_ENABLED=true
      - LOGLAMA_SQLITE_PATH=/logs/loglama.db
      - FLASK_APP=loglama.web.app
      - HOST=0.0.0.0
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - {os.path.abspath('logs')}:/logs:ro
      - {os.path.abspath('grafana-provisioning/datasources')}:/etc/grafana/provisioning/datasources:ro
      - {os.path.abspath('grafana-provisioning/dashboards')}:/etc/grafana/provisioning/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=frser-sqlite-datasource
    depends_on:
      - loglama
    restart: unless-stopped

volumes:
  grafana-data:
""")
    
    print_color(GREEN, "Docker Compose configuration updated with absolute paths")

def setup_grafana_provisioning():
    """Set up Grafana provisioning for automatic datasource and dashboard"""
    print_color(BLUE, "Setting up Grafana provisioning...")
    
    # Create directories
    os.makedirs("grafana-provisioning/datasources", exist_ok=True)
    os.makedirs("grafana-provisioning/dashboards", exist_ok=True)
    
    # Create datasource configuration
    with open("grafana-provisioning/datasources/loglama.yml", "w") as f:
        f.write("""apiVersion: 1

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
""")
    
    # Create dashboard configuration
    with open("grafana-provisioning/dashboards/dashboard.yml", "w") as f:
        f.write("""apiVersion: 1

providers:
  - name: 'LogLama Dashboards'
    orgId: 1
    folder: 'LogLama'
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
""")
    
    # Create dashboard JSON
    with open("grafana-provisioning/dashboards/loglama-dashboard.json", "w") as f:
        f.write("""{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "frser-sqlite-datasource",
        "uid": "loglama"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "Log Levels Over Time",
      "type": "timeseries",
      "targets": [
        {
          "datasource": {
            "type": "frser-sqlite-datasource",
            "uid": "loglama"
          },
          "queryText": "SELECT timestamp as time, count(*) as value, level as metric FROM logs GROUP BY level, strftime('%Y-%m-%d %H:%M', timestamp) ORDER BY timestamp;",
          "queryType": "table",
          "rawQueryText": "SELECT timestamp as time, count(*) as value, level as metric FROM logs GROUP BY level, strftime('%Y-%m-%d %H:%M', timestamp) ORDER BY timestamp;",
          "refId": "A",
          "timeColumns": ["time"]
        }
      ]
    },
    {
      "datasource": {
        "type": "frser-sqlite-datasource",
        "uid": "loglama"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "auto",
            "cellOptions": {
              "type": "auto"
            },
            "inspect": false
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "yellow",
                "value": "WARNING"
              },
              {
                "color": "red",
                "value": "ERROR"
              },
              {
                "color": "purple",
                "value": "CRITICAL"
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "level"
            },
            "properties": [
              {
                "id": "custom.cellOptions",
                "value": {
                  "type": "color-text"
                }
              },
              {
                "id": "mappings",
                "value": [
                  {
                    "options": {
                      "DEBUG": {
                        "color": "blue",
                        "index": 0
                      },
                      "ERROR": {
                        "color": "red",
                        "index": 2
                      },
                      "INFO": {
                        "color": "green",
                        "index": 1
                      },
                      "WARNING": {
                        "color": "orange",
                        "index": 3
                      }
                    },
                    "type": "value"
                  }
                ]
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 16,
        "w": 24,
        "x": 0,
        "y": 8
      },
      "id": 2,
      "options": {
        "cellHeight": "sm",
        "footer": {
          "countRows": false,
          "fields": "",
          "reducer": ["sum"],
          "show": false
        },
        "showHeader": true
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": {
            "type": "frser-sqlite-datasource",
            "uid": "loglama"
          },
          "queryText": "SELECT timestamp, level, logger, message FROM logs ORDER BY timestamp DESC LIMIT 100;",
          "queryType": "table",
          "rawQueryText": "SELECT timestamp, level, logger, message FROM logs ORDER BY timestamp DESC LIMIT 100;",
          "refId": "A",
          "timeColumns": ["timestamp"]
        }
      ],
      "title": "Recent Logs",
      "type": "table"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "LogLama Dashboard",
  "uid": "loglama-dashboard",
  "version": 1,
  "weekStart": ""
}""")
    
    print_color(GREEN, "Grafana provisioning set up successfully")

def start_docker_containers():
    """Start Docker containers"""
    print_color(BLUE, "Starting Docker containers...")
    
    # Stop any existing containers
    run_command("docker compose down")
    
    # Build and start containers
    success, output = run_command("docker compose build --no-cache")
    if not success:
        print_color(RED, "Failed to build Docker containers:")
        print(output)
        return False
    
    success, output = run_command("docker compose up -d")
    if not success:
        print_color(RED, "Failed to start Docker containers:")
        print(output)
        return False
    
    print_color(GREEN, "Docker containers started successfully")
    return True

def check_containers_running():
    """Check if containers are running"""
    print_color(BLUE, "Checking container status...")
    time.sleep(5)  # Wait for containers to initialize
    
    # Check LogLama
    success, output = run_command("docker ps | grep loglama")
    if not success or "Up" not in output:
        print_color(RED, "LogLama container is not running properly:")
        run_command("docker logs loglama")
        return False
    
    # Check Grafana
    success, output = run_command("docker ps | grep grafana")
    if not success or "Up" not in output:
        print_color(RED, "Grafana container is not running properly:")
        run_command("docker logs grafana")
        return False
    
    print_color(GREEN, "All containers are running properly")
    return True

def open_browser():
    """Open browser to access LogLama and Grafana"""
    print_color(BLUE, "Opening web browsers...")
    
    try:
        import webbrowser
        webbrowser.open("http://localhost:5000")
        time.sleep(1)
        webbrowser.open("http://localhost:3001")
    except Exception as e:
        print_color(YELLOW, f"Failed to open browser: {e}")
        print_color(YELLOW, "Please manually open http://localhost:5000 and http://localhost:3001")

def print_instructions():
    """Print instructions for using LogLama and Grafana"""
    print("\n" + "-"*80)
    print_color(GREEN, "LogLama-Grafana Integration Setup Complete!")
    print("-"*80)
    
    print("\nAccess Information:")
    print_color(BLUE, "LogLama Web UI: http://localhost:5000")
    print_color(BLUE, "Grafana Dashboard: http://localhost:3001")
    print_color(YELLOW, "  - Default login: admin / admin")
    
    print("\nTo view logs:")
    print_color(YELLOW, "  docker compose logs -f")
    
    print("\nTo stop the services:")
    print_color(YELLOW, "  docker compose down")
    
    print("\nTo create a Grafana connection to LogLama:")
    print("1. Log into Grafana at http://localhost:3001 with admin/admin")
    print("2. Go to Connections > Data Sources > Add data source")
    print("3. Select 'SQLite'")
    print("4. Configure with these settings:")
    print_color(YELLOW, "   - Name: LogLama")
    print_color(YELLOW, "   - Path: /logs/loglama.db")
    print("5. Click 'Save & Test'")
    print("6. Create a new dashboard with SQL queries like:")
    print_color(YELLOW, "   SELECT timestamp as time, level, logger, message FROM logs ORDER BY timestamp DESC LIMIT 100")
    
    print("\nFor more information, see the documentation files:")
    print_color(BLUE, "  - GRAFANA_CONNECTION_GUIDE.md")
    print_color(BLUE, "  - INTEGRATION_GUIDE.md")
    print_color(BLUE, "  - PUBLISHING_GUIDE.md")

def main():
    """Main function"""
    print_color(GREEN, "=== LogLama-Grafana Integration Setup ===")
    
    # Setup logs directory
    logs_dir = setup_logs_directory()
    
    # Create SQLite database
    db_path = create_sqlite_database(logs_dir)
    
    # Generate sample logs
    generate_sample_logs(db_path)
    
    # Set up Grafana provisioning
    setup_grafana_provisioning()
    
    # Update docker-compose.yml
    update_docker_compose(db_path)
    
    # Start Docker containers
    if not start_docker_containers():
        return 1
    
    # Check containers running
    if not check_containers_running():
        return 1
    
    # Print instructions
    print_instructions()
    
    # Open browser
    open_browser()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
