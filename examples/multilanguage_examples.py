#!/usr/bin/env python3

"""
LogLama Multi-Language Integration Examples

This script demonstrates how to integrate LogLama with different programming languages
and technologies, showing the flexibility of the logging system.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import LogLama modules
try:
    # Try importing from installed package first
    from loglama.core.logger import setup_logging, get_logger
    from loglama.utils.context import LogContext
except ImportError:
    # Fall back to local import if package is not installed
    from loglama.logger import setup_logging, get_logger
    from loglama.context import LogContext

# Set up logging
logger = setup_logging(name="loglama_examples", level="DEBUG", db_logging=True)


def create_example_files():
    """Create example files for different programming languages."""
    examples_dir = Path(__file__).parent
    
    # JavaScript example
    js_file = examples_dir / "js_example.js"
    with open(js_file, "w") as f:
        f.write("""
// JavaScript LogLama integration example
const { exec } = require('child_process');

class PyLogger {
    constructor(component = 'javascript') {
        this.component = component;
    }
    
    log(level, message, context = {}) {
        const contextStr = JSON.stringify(context).replace(/"/g, '\\"');
        const cmd = `python3 -c "from loglama.core.logger import get_logger; import json; logger = get_logger('${this.component}'); logger.${level}('${message}', extra={'context': json.loads('${contextStr}') if '${contextStr}' else {}})"`;        
        exec(cmd, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error logging to LogLama: ${error.message}`);
                return;
            }
            if (stderr) {
                console.error(`LogLama stderr: ${stderr}`);
                return;
            }
        });
    }
    
    debug(message, context = {}) { this.log('debug', message, context); }
    info(message, context = {}) { this.log('info', message, context); }
    warning(message, context = {}) { this.log('warning', message, context); }
    error(message, context = {}) { this.log('error', message, context); }
    critical(message, context = {}) { this.log('critical', message, context); }
}

// Usage example
const logger = new PyLogger('js_example');
logger.info('Hello from JavaScript!', { user: 'js_user', action: 'test' });
logger.error('Something went wrong in JavaScript', { error_code: 500 });

console.log('Logs sent to LogLama!');
        """)
    
    # PHP example
    php_file = examples_dir / "php_example.php"
    with open(php_file, "w") as f:
        f.write("""
<?php
// PHP integration with LogLama
class PyLogger {
    private $component;
    
    public function __construct($component = 'php') {
        $this->component = $component;
    }
    
    public function log($level, $message, $context = []) {
        $contextJson = json_encode($context);
        $contextJson = str_replace('"', '\\"', $contextJson);
        $cmd = "python3 -c \"from loglama.core.logger import get_logger; import json; logger = get_logger('{$this->component}'); logger.{$level}('{$message}', extra={'context': json.loads('{$contextJson}') if '{$contextJson}' else {}})\"";
        exec($cmd, $output, $returnVar);
        
        if ($returnVar !== 0) {
            echo "Error logging to LogLama: " . implode("\n", $output) . "\n";
        }
    }
    
    public function debug($message, $context = []) { $this->log('debug', $message, $context); }
    public function info($message, $context = []) { $this->log('info', $message, $context); }
    public function warning($message, $context = []) { $this->log('warning', $message, $context); }
    public function error($message, $context = []) { $this->log('error', $message, $context); }
    public function critical($message, $context = []) { $this->log('critical', $message, $context); }
}

// Usage example
$logger = new PyLogger('php_example');
$logger->info('Hello from PHP!', ['user' => 'php_user', 'action' => 'test']);
$logger->error('Something went wrong in PHP', ['error_code' => 500]);

echo "Logs sent to LogLama!\n";
?>
        """)
    
    # Ruby example
    ruby_file = examples_dir / "ruby_example.rb"
    with open(ruby_file, "w") as f:
        f.write("""
# Ruby integration with LogLama
class PyLogger
  def initialize(component = 'ruby')
    @component = component
  end
  
  def log(level, message, context = {})
    context_json = context.to_json.gsub('"', '\\"')
    cmd = "python3 -c \"from loglama.core.logger import get_logger; import json; logger = get_logger('#{@component}'); logger.#{level}('#{message}', extra={'context': json.loads('#{context_json}') if '#{context_json}' else {}})\""    
    system(cmd)
  end
  
  def debug(message, context = {}); log('debug', message, context); end
  def info(message, context = {}); log('info', message, context); end
  def warning(message, context = {}); log('warning', message, context); end
  def error(message, context = {}); log('error', message, context); end
  def critical(message, context = {}); log('critical', message, context); end
end

# Usage example
logger = PyLogger.new('ruby_example')
logger.info('Hello from Ruby!', {user: 'ruby_user', action: 'test'})
logger.error('Something went wrong in Ruby', {error_code: 500})

puts 'Logs sent to LogLama!'
        """)
    
    # Bash example
    bash_file = examples_dir / "bash_example.sh"
    with open(bash_file, "w") as f:
        f.write("""
#!/bin/bash

# Bash integration with LogLama
function pylog() {
    local level=$1
    local message=$2
    local component=${3:-"bash"}
    local context=${4:-"{}"}
    
    python3 -c "from loglama.core.logger import get_logger; import json; logger = get_logger('$component'); logger.$level('$message', extra={'context': json.loads('$context') if '$context' else {}})" 2>/dev/null
}

# Usage examples
pylog "info" "Hello from Bash!" "bash_example" '{"user":"bash_user","action":"test"}'
pylog "error" "Something went wrong in Bash" "bash_example" '{"error_code":500}'

echo "Logs sent to LogLama!"
        """)
    
    # Make bash script executable
    os.chmod(bash_file, 0o755)
    
    return {
        "js": js_file,
        "php": php_file,
        "ruby": ruby_file,
        "bash": bash_file
    }


def run_python_examples():
    """Run Python examples with LogLama."""
    print("\n=== Running Python Examples ===")
    
    # Basic logging
    logger.info("This is an info message from Python")
    logger.warning("This is a warning message from Python")
    logger.error("This is an error message from Python")
    
    # Logging with context
    with LogContext(user="admin", operation="backup"):
        logger.info("Performing backup operation")
    
    # Logging with extra data
    logger.info("User logged in", extra={"user_id": 123, "ip": "192.168.1.1"})
    
    # Logging exceptions
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("An exception occurred")
    
    print("Python examples completed")


def run_external_examples(example_files):
    """Run examples from other programming languages."""
    # Run Bash example
    print("\n=== Running Bash Example ===")
    try:
        subprocess.run([example_files["bash"]], check=True)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Error running Bash example: {e}")
    
    # Run JavaScript example if Node.js is available
    print("\n=== Running JavaScript Example ===")
    try:
        if subprocess.run(["which", "node"], capture_output=True).returncode == 0:
            subprocess.run(["node", example_files["js"]], check=True)
        else:
            print("Node.js not found, skipping JavaScript example")
    except subprocess.SubprocessError as e:
        print(f"Error running JavaScript example: {e}")
    
    # Run PHP example if PHP is available
    print("\n=== Running PHP Example ===")
    try:
        if subprocess.run(["which", "php"], capture_output=True).returncode == 0:
            subprocess.run(["php", example_files["php"]], check=True)
        else:
            print("PHP not found, skipping PHP example")
    except subprocess.SubprocessError as e:
        print(f"Error running PHP example: {e}")
    
    # Run Ruby example if Ruby is available
    print("\n=== Running Ruby Example ===")
    try:
        if subprocess.run(["which", "ruby"], capture_output=True).returncode == 0:
            subprocess.run(["ruby", example_files["ruby"]], check=True)
        else:
            print("Ruby not found, skipping Ruby example")
    except subprocess.SubprocessError as e:
        print(f"Error running Ruby example: {e}")


def main():
    """Main function to run all examples."""
    print("LogLama Multi-Language Integration Examples")
    print("===========================================\n")
    
    # Create example files
    example_files = create_example_files()
    
    # Run Python examples
    run_python_examples()
    
    # Run examples from other languages
    run_external_examples(example_files)
    
    print("\n=== All Examples Completed ===")
    print("To view logs, run: loglama web --port 8081 --host 0.0.0.0")


if __name__ == "__main__":
    main()
