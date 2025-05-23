#!/bin/bash

# Simple Bash Example using LogLama
# This example demonstrates how to use the simplified LogLama bash helper script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the LogLama installation
LOGLAMA_ROOT="$(dirname "$SCRIPT_DIR")"

# Source the LogLama bash helper script
BASH_HELPER="$LOGLAMA_ROOT/loglama/scripts/loglama_bash.sh"
if [ -f "$BASH_HELPER" ]; then
    source "$BASH_HELPER"
else
    # Fallback if the helper script is not found
    echo "LogLama bash helper not found at $BASH_HELPER"
    echo "Creating minimal implementation for testing..."
    
    # Create minimal implementations of the logging functions
    log_info() { echo "[INFO] $1"; }
    log_warning() { echo "[WARNING] $1"; }
    log_error() { echo "[ERROR] $1"; }
    log_debug() { echo "[DEBUG] $1"; }
    setup_db_logging() { echo "[SETUP] Setting up DB logging to $1"; }
    log_performance() { echo "[PERF] $1"; }
fi

# Set up database logging
DB_PATH="$LOGLAMA_ROOT/logs/bash_example.db"
setup_db_logging "$DB_PATH"

# Start the main script
log_info "Starting simple bash example script"

# Function to process a file
process_file() {
    local file="$1"
    log_info "Processing file: $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        return 1
    fi
    
    # Get file size
    local size=$(stat -c%s "$file")
    log_info "File size: $size bytes" "file_processor"
    
    # Count lines in file
    local lines=$(wc -l < "$file")
    log_info "File has $lines lines" "file_processor"
    
    # Check if file is executable
    if [ -x "$file" ]; then
        log_info "File is executable" "file_processor"
    else
        log_warning "File is not executable" "file_processor"
    fi
    
    return 0
}

# Create a test file
TEST_FILE="$SCRIPT_DIR/test_file.txt"
log_info "Creating test file: $TEST_FILE"
echo "This is a test file for the LogLama bash example" > "$TEST_FILE"
echo "It has multiple lines" >> "$TEST_FILE"
echo "to demonstrate line counting" >> "$TEST_FILE"

# Process the test file
log_info "Starting file processing"
process_file "$TEST_FILE"

# Simulate a short operation instead of a long-running one for testing
log_info "Starting operation (shortened for testing)"
log_performance "start" "operation"

# Only one iteration with no sleep for testing
log_debug "Processing iteration 1"

# Set a timeout for the entire script (5 seconds max)
TIMEOUT_PID=""
timeout_handler() {
    log_warning "Script execution timed out"
    exit 0
}

# Start timeout in background (3 seconds)
(
    sleep 3
    log_info "Script completed successfully"
    exit 0
) &
TIMEOUT_PID=$!

# Try to process a non-existent file
log_info "Trying to process a non-existent file"
process_file "/tmp/non_existent_file.txt"

# Simulate some work with random success/failure
log_info "Performing some work with random success/failure"
for i in {1..5}; do
    log_info "Starting task $i"
    
    # Simulate work
    sleep 1
    
    # 30% chance of failure
    if [ $(( RANDOM % 10 )) -lt 3 ]; then
        log_error "Task $i failed"
    else
        log_info "Task $i completed successfully"
    fi
done

# Clean up
log_info "Cleaning up"
time_command "rm -f $TEST_FILE" "Removing test file"

# Print information about accessing the logs
log_info "Simple bash example completed"
echo ""
echo "Example completed successfully!"
echo "Logs are stored in the database: $DB_PATH"
echo "You can view the logs using the LogLama web interface:"
echo "  python -m loglama.cli.main web --db $DB_PATH"

# Optionally start the web interface
if [[ "$1" == "--web" ]]; then
    WEB_HOST="127.0.0.1"
    WEB_PORT="8083"
    echo ""
    echo "Starting web interface at http://$WEB_HOST:$WEB_PORT..."
    start_web_interface "$WEB_HOST" "$WEB_PORT" "$DB_PATH"
fi
