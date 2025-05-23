# Setting Up Grafana Connection with LogLama

This guide provides step-by-step instructions for creating a connection between Grafana and LogLama's SQLite database.

## Prerequisites

- LogLama and Grafana containers running (via `run-simple.sh`)
- Access to Grafana web interface (http://localhost:3001)

## Step 1: Access Grafana

1. Open your browser and navigate to http://localhost:3001
2. Log in with the default credentials:
   - Username: `admin`
   - Password: `admin`
3. You may be prompted to change the password - you can do this or skip for now

## Step 2: Install SQLite Plugin (if not already installed)

Our Docker setup should have automatically installed the SQLite plugin, but if not:

1. Navigate to Administration → Plugins
2. Search for "SQLite"
3. Look for "SQLite Datasource" by frser
4. Click "Install"

## Step 3: Add LogLama as a Data Source

1. In the Grafana sidebar, click on "Connections"
2. Click "Add new connection" or "Data sources"
3. Search for "SQLite" and select it
4. Configure the data source with these settings:
   - Name: `LogLama`
   - Path: `/logs/loglama.db` (this is the path inside the Grafana container)
5. Click "Save & test"
6. You should see a success message indicating the connection works

## Step 4: Create a Dashboard

1. In the Grafana sidebar, click on "Dashboards"
2. Click "New" → "New Dashboard"
3. Click "Add visualization"
4. Select the "LogLama" data source
5. In the query editor, enter this SQL query:
   ```sql
   SELECT 
     timestamp as time, 
     level, 
     logger, 
     message 
   FROM logs 
   ORDER BY timestamp DESC 
   LIMIT 100
   ```
6. Click "Run query" to test
7. Configure the visualization (Table is recommended for this query)
8. Click "Apply" to add the panel to your dashboard
9. Click the save icon to save your dashboard with a name like "LogLama Logs"

## Step 5: Create Additional Visualizations

Here are some useful visualizations to add to your dashboard:

### Log Levels Distribution (Pie Chart)

```sql
SELECT 
  level as metric, 
  COUNT(*) as value 
FROM logs 
GROUP BY level
```

### Logs Over Time (Time Series)

```sql
SELECT 
  timestamp as time, 
  COUNT(*) as value, 
  level as metric 
FROM logs 
GROUP BY level, strftime('%Y-%m-%d %H:%M', timestamp) 
ORDER BY timestamp
```

### Recent Errors (Table)

```sql
SELECT 
  timestamp as time, 
  logger, 
  message, 
  source, 
  line 
FROM logs 
WHERE level IN ('ERROR', 'CRITICAL') 
ORDER BY timestamp DESC 
LIMIT 50
```

## Step 6: Configure Dashboard Settings

1. Click the gear icon in the top right to access dashboard settings
2. Set up auto-refresh (e.g., every 5s or 10s) to see new logs as they arrive
3. Adjust the time range to show relevant data (e.g., last 6 hours)
4. Add variables if needed for filtering (e.g., by log level or logger)

## Step 7: Set Up Alerts (Optional)

1. Edit a panel (e.g., the error logs panel)
2. Go to the "Alert" tab
3. Configure alert conditions (e.g., when ERROR logs exceed a threshold)
4. Set notification channels (email, Slack, etc.)

## Troubleshooting

### No Data Showing

1. Verify the LogLama container is running: `docker ps | grep loglama`
2. Check that logs are being written: `docker exec loglama sqlite3 /logs/loglama.db "SELECT COUNT(*) FROM logs"`
3. Generate sample logs: `./generate_logs_in_container.sh`
4. Verify the data source connection in Grafana

### Connection Failed

1. Check that the SQLite plugin is installed
2. Verify the database path is correct (`/logs/loglama.db`)
3. Ensure the volume is correctly mounted in the docker-compose file

## Next Steps

- Export your dashboard for sharing with others
- Set up persistent storage for your logs
- Create more advanced queries and visualizations
- Integrate with other monitoring tools

---

For more information, see the [Grafana SQLite Plugin Documentation](https://grafana.com/grafana/plugins/frser-sqlite-datasource/) and [LogLama Documentation](https://github.com/py-lama/loglama).
