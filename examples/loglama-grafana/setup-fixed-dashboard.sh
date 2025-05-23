#!/bin/bash

# Stop existing containers
docker stop loglama grafana
docker rm loglama grafana

# Create directories for volumes
mkdir -p ./logs
mkdir -p ./grafana-provisioning/datasources
mkdir -p ./grafana-provisioning/dashboards

# Create datasource configuration
cat > ./grafana-provisioning/datasources/loglama.yml << 'EOF'
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
EOF

# Create dashboard configuration
cat > ./grafana-provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'LogLama Dashboards'
    orgId: 1
    folder: 'LogLama'
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

# Create dashboard JSON
cat > ./grafana-provisioning/dashboards/loglama-dashboard.json << 'EOF'
{
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
  "id": null,
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
        "w": 12,
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
          "queryText": "SELECT strftime('%Y-%m-%dT%H:%M:%S', substr(timestamp, 1, 19)) as time, count(*) as value, level as metric FROM log_records GROUP BY level, strftime('%Y-%m-%dT%H:%M', timestamp) ORDER BY time;",
          "queryType": "table",
          "rawQueryText": "SELECT strftime('%Y-%m-%dT%H:%M:%S', substr(timestamp, 1, 19)) as time, count(*) as value, level as metric FROM log_records GROUP BY level, strftime('%Y-%m-%dT%H:%M', timestamp) ORDER BY time;",
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
            "mode": "palette-classic"
          },
          "custom": {
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            }
          },
          "mappings": []
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "displayLabels": ["percent"],
        "legend": {
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "pieType": "pie",
        "reduceOptions": {
          "calcs": ["sum"],
          "fields": "",
          "values": false
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "Log Level Distribution",
      "type": "piechart",
      "targets": [
        {
          "datasource": {
            "type": "frser-sqlite-datasource",
            "uid": "loglama"
          },
          "queryText": "SELECT level as metric, COUNT(*) as value FROM log_records GROUP BY level;",
          "queryType": "table",
          "rawQueryText": "SELECT level as metric, COUNT(*) as value FROM log_records GROUP BY level;",
          "refId": "A"
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
        "h": 12,
        "w": 24,
        "x": 0,
        "y": 8
      },
      "id": 3,
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
          "queryText": "SELECT timestamp, level, logger_name as logger, message FROM log_records ORDER BY timestamp DESC LIMIT 100;",
          "queryType": "table",
          "rawQueryText": "SELECT timestamp, level, logger_name as logger, message FROM log_records ORDER BY timestamp DESC LIMIT 100;",
          "refId": "A"
        }
      ],
      "title": "Recent Logs",
      "type": "table"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["loglama", "logs"],
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
}
EOF

# Start LogLama container
docker run -d \
  --name loglama \
  -p 5000:5000 \
  -v $(pwd)/logs:/logs \
  -e LOGLAMA_LOG_DIR=/logs \
  -e LOGLAMA_CONSOLE_ENABLED=true \
  -e LOGLAMA_SQLITE_ENABLED=true \
  -e LOGLAMA_SQLITE_PATH=/logs/loglama.db \
  -e FLASK_APP=loglama.web.app \
  -e HOST=0.0.0.0 \
  loglama-grafana:simple

# Start Grafana container
docker run -d \
  --name grafana \
  -p 3001:3000 \
  -v $(pwd)/logs:/logs:ro \
  -v $(pwd)/grafana-provisioning/datasources:/etc/grafana/provisioning/datasources:ro \
  -v $(pwd)/grafana-provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -e GF_INSTALL_PLUGINS=frser-sqlite-datasource \
  grafana/grafana:latest

# Generate sample logs
sleep 5
docker exec loglama python -c "import logging, random, time; from datetime import datetime, timedelta; import sqlite3; import os; class SQLiteHandler(logging.Handler):\n    def __init__(self, db_path):\n        logging.Handler.__init__(self)\n        self.db_path = db_path\n        os.makedirs(os.path.dirname(db_path), exist_ok=True)\n        conn = sqlite3.connect(db_path)\n        cursor = conn.cursor()\n        cursor.execute(\"\"\"\n        CREATE TABLE IF NOT EXISTS log_records (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            timestamp TEXT NOT NULL,\n            level TEXT NOT NULL,\n            level_number INTEGER NOT NULL,\n            logger_name TEXT NOT NULL,\n            message TEXT NOT NULL,\n            file_path TEXT,\n            line_number INTEGER,\n            function TEXT,\n            module TEXT,\n            process_id INTEGER,\n            process_name TEXT,\n            thread_id INTEGER,\n            thread_name TEXT,\n            exception_info TEXT,\n            context TEXT\n        )\n        \"\"\")\n        conn.commit()\n        conn.close()\n    def emit(self, record):\n        conn = sqlite3.connect(self.db_path)\n        cursor = conn.cursor()\n        cursor.execute(\"\"\"\n        INSERT INTO log_records (timestamp, level, level_number, logger_name, message, file_path, line_number, function, module)\n        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)\n        \"\"\", (\n            datetime.fromtimestamp(record.created).isoformat(),\n            record.levelname,\n            record.levelno,\n            record.name,\n            record.getMessage(),\n            record.pathname if hasattr(record, 'pathname') else '',\n            record.lineno if hasattr(record, 'lineno') else 0,\n            record.funcName if hasattr(record, 'funcName') else '',\n            record.module if hasattr(record, 'module') else ''\n        ))\n        conn.commit()\n        conn.close()\ndb_path = '/logs/loglama.db'\nhandler = SQLiteHandler(db_path)\nlogger = logging.getLogger('test')\nlogger.setLevel(logging.DEBUG)\nlogger.addHandler(handler)\nconsole = logging.StreamHandler()\nconsole.setLevel(logging.INFO)\nlogger.addHandler(console)\nlevels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]\nloggers = ['app.api', 'app.database', 'app.auth', 'app.ui', 'app.network', 'system']\nmessages = ['User login successful', 'User login failed', 'Database query executed', 'API request processed', 'File upload completed', 'Authentication token expired', 'Data validation error', 'Network connection timeout', 'Cache miss', 'Background job started', 'Background job completed', 'Configuration loaded', 'Memory usage high', 'CPU usage spike detected', 'Disk space running low']\nnum_logs = 200\nnow = datetime.now()\nfor i in range(num_logs):\n    level_idx = random.choices([0, 1, 2, 3, 4], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]\n    level = levels[level_idx]\n    logger_name = random.choice(loggers)\n    message = random.choice(messages)\n    if 'login' in message:\n        message += f\" for user user_{random.randint(1000, 9999)}\"\n    elif 'query' in message:\n        message += f\" in {random.choice(['users', 'orders', 'products', 'settings'])} table\"\n    elif 'API' in message:\n        message += f\" for endpoint /{random.choice(['users', 'orders', 'products', 'auth'])}\"\n    record = logging.LogRecord(\n        name=logger_name,\n        level=level,\n        pathname=__file__,\n        lineno=random.randint(10, 500),\n        msg=message,\n        args=(),\n        exc_info=None\n    )\n    time_offset = timedelta(seconds=random.randint(0, 6 * 60 * 60))\n    record.created = (now - time_offset).timestamp()\n    handler.emit(record)\n    if (i + 1) % 20 == 0:\n        print(f\"Generated {i + 1}/{num_logs} logs\")\n    time.sleep(0.05)\nprint(f\"Successfully generated {num_logs} logs in {db_path}\")"

echo "Setup complete!"
echo "LogLama Web UI: http://localhost:5000"
echo "Grafana Dashboard: http://localhost:3001 (admin/admin)"
