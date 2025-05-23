
#!/bin/bash

# Bash Logging Example

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    echo "[$level] $message"
}

# Log some messages
log_message "INFO" "Starting Bash example"
log_message "DEBUG" "Initializing variables"

# Simulate an error
if ! command -v non_existent_command &> /dev/null; then
    log_message "ERROR" "Command not found: non_existent_command"
fi

log_message "INFO" "Bash example completed"
