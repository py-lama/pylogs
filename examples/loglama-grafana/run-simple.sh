#!/bin/bash

# Simple script to run LogLama with Grafana integration
set -e

echo "=== LogLama + Grafana Integration (Simple Version) ==="

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not accessible"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Build and start the services
echo "Building and starting LogLama and Grafana..."
docker compose -f docker-compose.simple.yml down
docker compose -f docker-compose.simple.yml build
docker compose -f docker-compose.simple.yml up -d

# Generate sample log data for the dashboard
echo "
Generating sample log data for the dashboard..."
./generate_logs_in_container.sh

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check if services are running
if docker compose -f docker-compose.simple.yml ps | grep -q "loglama.*Up"; then
    echo "LogLama is running"
else
    echo "Warning: LogLama container is not running properly"
fi

if docker compose -f docker-compose.simple.yml ps | grep -q "grafana.*Up"; then
    echo "Grafana is running"
else
    echo "Warning: Grafana container is not running properly"
fi

# Show access URLs
echo ""
echo "=== Access Information ==="
echo "LogLama Web UI: http://localhost:5000"
echo "Grafana Dashboard: http://localhost:3001"
echo "  - Default login: admin / admin"
echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose.simple.yml logs -f"
echo ""
echo "To stop the services:"
echo "  docker compose -f docker-compose.simple.yml down"

# Open browser if xdg-open is available
if command -v xdg-open &> /dev/null; then
    echo "Opening LogLama Web UI in browser..."
    xdg-open http://localhost:5000
    sleep 2
    echo "Opening Grafana Dashboard in browser..."
    xdg-open http://localhost:3001
fi
