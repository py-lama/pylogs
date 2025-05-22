#!/bin/bash

# LogLama Shell Integration Examples
# This script demonstrates how to use LogLama from shell scripts

# Set up environment variables for LogLama
export LOGLAMA_LOG_LEVEL="DEBUG"
export LOGLAMA_LOG_DIR="./logs"
export LOGLAMA_DB_LOGGING="true"
export LOGLAMA_DB_PATH="./logs/loglama.db"

# Function to log a message to LogLama
log_message() {
    local level="$1"
    local message="$2"
    local component="${3:-shell_script}"
    
    # Call the loglama CLI to log the message
    python -c "from loglama.core.logger import get_logger; logger = get_logger('$component'); logger.$level('$message')" 2>/dev/null
    
    # Print to console as well
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] [$component] $message"
}

# Example usage
echo "=== LogLama Shell Integration Example ==="
echo "Starting shell script example..."

# Log different levels
log_message "info" "Shell script started" "shell.example"
log_message "debug" "This is a debug message" "shell.example"
log_message "warning" "This is a warning message" "shell.example"

# Simulate an error
if [ ! -f "/tmp/nonexistent_file.txt" ]; then
    log_message "error" "File not found: /tmp/nonexistent_file.txt" "shell.example"
fi

# Log with different components
log_message "info" "Database connection established" "shell.database"
log_message "info" "User authentication successful" "shell.auth"

# Simulate a loop with logging
echo "Performing operations..."
for i in {1..5}; do
    log_message "info" "Processing item $i" "shell.process"
    sleep 1
done

# Log completion
log_message "info" "Shell script completed successfully" "shell.example"

echo "\nTo view logs, run: loglama web --port 8081 --host 0.0.0.0"
echo "=== End of Example ==="
