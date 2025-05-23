# LogLama-Grafana Integration Guide

This guide provides detailed instructions for integrating LogLama with Grafana for advanced log visualization and monitoring.

## Overview

LogLama is a centralized logging system for the PyLama ecosystem. By integrating with Grafana, you can create powerful dashboards to visualize and analyze your logs, set up alerts, and gain deeper insights into your application's behavior.

## Prerequisites

- Docker and Docker Compose installed
- Basic familiarity with SQL queries
- LogLama installed and configured

## Quick Start

1. Navigate to the LogLama-Grafana example directory:
   ```bash
   cd /path/to/loglama/examples/loglama-grafana
   ```

2. Run the setup script:
   ```bash
   ./run-simple.sh
   ```

3. Access the interfaces:
   - LogLama Web UI: http://localhost:5000
   - Grafana Dashboard: http://localhost:3001 (login: admin/admin)

## Manual Setup

If you prefer to set up the integration manually, follow these steps:

### 1. Start LogLama and Grafana

```bash
# Start the services
docker compose -f docker-compose.simple.yml up -d

# Generate sample log data (optional)
./generate_logs_in_container.sh
```

### 2. Configure Grafana Data Source

1. Log into Grafana at http://localhost:3001 with admin/admin
2. Navigate to Connections → Data Sources → Add new data source
3. Select "SQLite" from the list
4. Configure the data source:
   - Name: LogLama
   - Path: `/logs/loglama.db`
5. Click "Save & Test"

### 3. Create a Dashboard

1. Navigate to Dashboards → New → New Dashboard
2. Click "Add visualization"
3. Select the "LogLama" data source
4. Create a query like:
   ```sql
   SELECT timestamp as time, level, logger, message 
   FROM logs 
   ORDER BY timestamp DESC 
   LIMIT 100
   ```
5. Configure visualization settings and save your dashboard

## Advanced Configuration

### Custom SQL Queries

Here are some useful SQL queries for LogLama logs:

#### Log Count by Level
```sql
SELECT level, COUNT(*) as count 
FROM logs 
GROUP BY level 
ORDER BY count DESC
```

#### Logs Over Time
```sql
SELECT 
  strftime('%Y-%m-%d %H:%M', timestamp) as time_bucket, 
  COUNT(*) as count, 
  level as metric 
FROM logs 
GROUP BY time_bucket, level 
ORDER BY time_bucket
```

#### Error Analysis
```sql
SELECT timestamp, logger, message, source, line 
FROM logs 
WHERE level IN ('ERROR', 'CRITICAL') 
ORDER BY timestamp DESC
```

### Setting Up Alerts

Grafana allows you to set up alerts based on your log data:

1. Edit a panel in your dashboard
2. Go to the "Alert" tab
3. Configure alert conditions (e.g., when ERROR logs exceed a threshold)
4. Set notification channels (email, Slack, etc.)

## Troubleshooting

### Common Issues

1. **LogLama container not starting**: Check the logs with `docker logs loglama`
2. **SQLite data source not working**: Ensure the SQLite plugin is installed in Grafana
3. **No data in dashboards**: Verify the database path and that logs are being written

## Publishing Your Integration

To share your LogLama-Grafana integration with others:

1. Export your Grafana dashboards (Share → Export)
2. Include the dashboard JSON files in your project
3. Document the setup process in your README

## Next Steps

- Create custom dashboards for specific use cases
- Set up persistent storage for your logs
- Integrate with other monitoring tools
- Contribute your dashboards back to the LogLama community

---

For more information, see the [LogLama documentation](https://github.com/py-lama/loglama) and [Grafana documentation](https://grafana.com/docs/).
