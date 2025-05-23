#!/usr/bin/env python3

"""
Standalone Multi-Language Integration Example

This script demonstrates the concept of multi-language logging
without requiring the LogLama package to be installed.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Minimal logger implementation
class MinimalLogger:
    def __init__(self, name):
        self.name = name
    
    def info(self, msg, **kwargs):
        self._log("INFO", msg, **kwargs)
    
    def warning(self, msg, **kwargs):
        self._log("WARNING", msg, **kwargs)
    
    def error(self, msg, **kwargs):
        self._log("ERROR", msg, **kwargs)
    
    def debug(self, msg, **kwargs):
        self._log("DEBUG", msg, **kwargs)
    
    def _log(self, level, msg, **kwargs):
        context = ", ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        if context:
            print(f"[{level}] [{self.name}] {msg} ({context})")
        else:
            print(f"[{level}] [{self.name}] {msg}")

# Create logger
logger = MinimalLogger("multilanguage")

def create_example_files():
    """Create example files for different programming languages."""
    examples_dir = Path(__file__).parent
    
    # JavaScript example
    js_file = examples_dir / "js_example.js"
    with open(js_file, "w") as f:
        f.write("""
// JavaScript Logging Example

// Function to log messages
function logMessage(level, message) {
    console.log(`[${level}] ${message}`);
}

// Log some messages
logMessage('INFO', 'Starting JavaScript example');
logMessage('DEBUG', 'Initializing variables');

// Simulate an error
try {
    throw new Error('Example error');
} catch (error) {
    logMessage('ERROR', `Caught error: ${error.message}`);
}

logMessage('INFO', 'JavaScript example completed');
""")
    
    # Bash example
    bash_file = examples_dir / "bash_example_mini.sh"
    with open(bash_file, "w") as f:
        f.write("""
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
""")
    
    # Make the bash file executable
    os.chmod(bash_file, 0o755)
    
    return {"js": js_file, "bash": bash_file}

def run_python_examples():
    """Run Python examples with logging."""
    logger.info("Starting Python examples")
    
    # Log different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    
    # Simulate an error
    try:
        result = 10 / 0
    except Exception as e:
        logger.error(f"Caught an error: {e}")
    
    # Log with additional context
    logger.info("Logging with context", component="python_example", status="success")
    
    logger.info("Python examples completed")

def run_external_examples(example_files):
    """Run examples from other programming languages."""
    logger.info("Starting external language examples")
    
    # Run JavaScript example with Node.js if available
    js_file = example_files.get("js")
    if js_file and os.path.exists(js_file):
        logger.info("Running JavaScript example")
        try:
            # Check if Node.js is installed
            node_check = subprocess.run(["which", "node"], capture_output=True, text=True)
            if node_check.returncode == 0:
                # Run the JavaScript file
                result = subprocess.run(["node", js_file], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("JavaScript example completed successfully")
                    logger.debug(f"Output: {result.stdout}")
                else:
                    logger.error(f"JavaScript example failed: {result.stderr}")
            else:
                logger.warning("Node.js not found, skipping JavaScript example")
        except Exception as e:
            logger.error(f"Error running JavaScript example: {e}")
    
    # Run Bash example
    bash_file = example_files.get("bash")
    if bash_file and os.path.exists(bash_file):
        logger.info("Running Bash example")
        try:
            result = subprocess.run(["bash", bash_file], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Bash example completed successfully")
                logger.debug(f"Output: {result.stdout}")
            else:
                logger.error(f"Bash example failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error running Bash example: {e}")
    
    logger.info("External language examples completed")

def main():
    """Main function to run all examples."""
    logger.info("Starting multi-language examples")
    
    # Create example files
    example_files = create_example_files()
    
    # Run Python examples
    run_python_examples()
    
    # Run examples from other languages
    run_external_examples(example_files)
    
    logger.info("All examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
