#!/bin/bash

# Example of using LogLama from a Bash script
# This script demonstrates how to use LogLama's CLI to log messages from Bash

# Set the path to the PyLama root directory
PYLAMA_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Function to log a message using LogLama
log_message() {
    local level="$1"
    local message="$2"
    local component="${3:-bash_script}"
    
    # Use Python to call LogLama's logger
    python3 -c "import sys; sys.path.append('$PYLAMA_ROOT'); from loglama.core.logger import get_logger; logger = get_logger('$component'); logger.$level('$message')" 
}

# Function to initialize LogLama environment
initialize_loglama() {
    echo "Initializing LogLama environment..."
    python3 -c "import sys; sys.path.append('$PYLAMA_ROOT'); from loglama.core.env_manager import load_central_env, ensure_required_env_vars; load_central_env(); ensure_required_env_vars()"
    echo "LogLama environment initialized"
}

# Main script
echo "Starting Bash example script"

# Initialize LogLama environment
initialize_loglama

# Log messages at different levels
log_message "info" "Starting bash script execution"
log_message "debug" "Debug information from bash"

# Simulate some work
echo "Performing some work..."
sleep 1

# Log a warning
log_message "warning" "This is a warning from the bash script"

# Simulate an error
if ! command -v non_existent_command &> /dev/null; then
    log_message "error" "Command \"non_existent_command\" not found"
fi

# Log completion
log_message "info" "Bash script execution completed"

echo "Bash example script completed"
echo "Check the logs using: python -m loglama.cli.main logs"
