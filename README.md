# LogLama - Log Smart, Debug Faster, Scale Better 

A powerful logging utility for the PyLama ecosystem with CLI, API, SQLite support, web interface for log visualization, and auto-diagnostic capabilities. LogLama provides a unified logging solution that can be integrated into any application or programming language.

<div align="center">

![LogLama Logo](loglama-logo.svg)


[![PyPI version](https://badge.fury.io/py/loglama.svg)](https://badge.fury.io/py/loglama)
[![Python versions](https://img.shields.io/pypi/pyversions/loglama.svg)](https://pypi.org/project/loglama/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/loglama)](https://pepy.tech/project/loglama)

[![Build Status](https://github.com/py-lama/loglama/workflows/CI/badge.svg)](https://github.com/py-lama/loglama/actions)
[![Coverage Status](https://codecov.io/gh/py-lama/loglama/branch/main/graph/badge.svg)](https://codecov.io/gh/py-lama/loglama)
[![Code Quality](https://api.codeclimate.com/v1/badges/a99a88d28ad37a79dbf6/maintainability)](https://codeclimate.com/github/py-lama/loglama)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=py-lama_loglama&metric=security_rating)](https://sonarcloud.io/dashboard?id=py-lama_loglama)

[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://py-lama.github.io/loglama/)
[![GitHub stars](https://img.shields.io/github/stars/py-lama/loglama.svg?style=social&label=Star)](https://github.com/py-lama/loglama)
[![GitHub forks](https://img.shields.io/github/forks/py-lama/loglama.svg?style=social&label=Fork)](https://github.com/py-lama/loglama/fork)
[![GitHub issues](https://img.shields.io/github/issues/py-lama/loglama.svg)](https://github.com/py-lama/loglama/issues)

[![Poetry](https://img.shields.io/badge/packaging-poetry-blue.svg)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)

</div>

---

## Features

- **Multi-output logging**: Console, file, SQLite database, and API endpoints
- **Structured logging**: Support for structured logging with `structlog`
- **Context-aware logging**: Add context to your logs for better debugging
- **Web interface**: Visualize, filter, and query logs through an interactive web dashboard with dark mode and real-time updates
- **RESTful API**: Access and manage logs programmatically
- **Command-line interface**: Interact with logs from the terminal with rich formatting
- **Environment configuration**: Easy configuration through environment variables
- **Custom formatters**: JSON and colored output for better readability
- **Enhanced handlers**: Improved file rotation, SQLite storage, and API integration
- **Integration tools**: Easily integrate LogLama into existing PyLama ecosystem components
- **Comprehensive testing**: Unit, integration, and Ansible tests for all components
- **Multi-language support**: Use LogLama from Python, JavaScript, PHP, Ruby, Bash, and more
- **Duplicate code elimination**: Remove redundant logging configuration across projects
- **Auto-diagnostic capabilities**: Automatically diagnose and fix common logging issues
- **Smart decorators**: Simplify logging and context management with powerful decorators
- **Environment testing**: Ansible playbooks to test LogLama in different environments

## Installation

```bash
# Clone the repository
git clone https://github.com/py-lama/loglama.git
cd py-lama/loglama

# Install the package
make setup
```

Or install directly from the repository:

```bash
pip install git+https://github.com/py-lama/loglama.git#subdirectory=loglama
```

## Quick Start

```python
# Basic usage
from loglama import get_logger

# Get a logger
logger = get_logger("my_app")

# Log messages
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Log with context
from loglama import LogContext

with LogContext(user_id="123", action="login"):
    logger.info("User logged in")
```

## Configuration

LogLama can be configured through environment variables or a `.env` file. Copy the `env.example` file to `.env` and modify it as needed:

```bash
cp env.example .env
```

Key configuration options:

```
# Logging Configuration
LOGLAMA_LOG_LEVEL=INFO                # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGLAMA_LOG_DIR=./logs               # Directory to store log files
LOGLAMA_CONSOLE_ENABLED=true         # Enable console logging
LOGLAMA_FILE_ENABLED=true            # Enable file logging
LOGLAMA_JSON_LOGS=false              # Use JSON format for logs
LOGLAMA_STRUCTURED_LOGGING=false     # Use structured logging with structlog

# Database Configuration
LOGLAMA_DB_LOGGING=true              # Enable database logging
LOGLAMA_DB_PATH=./logs/loglama.db     # Path to SQLite database

# Advanced Configuration
LOGLAMA_MAX_LOG_SIZE=10485760        # Maximum log file size in bytes (10 MB)
LOGLAMA_BACKUP_COUNT=5               # Number of backup log files to keep

# Web Interface Configuration
LOGLAMA_WEB_PORT=5000                # Web interface port
LOGLAMA_WEB_HOST=127.0.0.1           # Web interface host
LOGLAMA_WEB_PAGE_SIZE=100            # Number of logs per page in web interface
LOGLAMA_WEB_DEBUG=false              # Enable debug mode for web interface
```

Environment variables are loaded automatically at the beginning of your application, before any other imports, to ensure proper configuration.

## Usage Examples

### Advanced Configuration

```python
from loglama import configure_logging

# Configure logging with multiple outputs
logger = configure_logging(
    name="my_app",
    level="DEBUG",
    console=True,
    file=True,
    file_path="/path/to/logs/my_app.log",
    database=True,
    db_path="/path/to/db/loglama.db",
    json=True
)

# Now use the logger
logger.info("Application started")
```

### Using Context

```python
from loglama import get_logger, LogContext, capture_context

logger = get_logger("my_app")

# Using the context manager
with LogContext(user_id="123", request_id="abc-123"):
    logger.info("Processing request")
    
    # Nested context
    with LogContext(action="validate"):
        logger.debug("Validating request data")

# Using the decorator
@capture_context(module="auth")
def authenticate_user(username):
    logger.info(f"Authenticating user: {username}")
```

### Using the CLI

```bash
# Start the CLI
make run-cli

# Or run directly
python -m loglama.cli.main

# View recent logs
loglama logs view --limit 10

# View logs by level
loglama logs view --level ERROR

# Clear logs
loglama logs clear
```

### Using the Web Interface

```bash
# Start the web interface (new command)
make web

# Or run with custom port and host
make web PORT=8081 HOST=0.0.0.0

# Or use the CLI directly
loglama web --port 8081 --host 0.0.0.0
```

Then open your browser at http://localhost:8081 (or your custom port).

The web interface provides:

- **Log Filtering**: Filter logs by level, component, date range, and text search
- **Pagination**: Navigate through large log sets with pagination
- **Statistics**: View log statistics by level, component, and time period
- **Log Details**: View detailed information about each log entry, including context
- **Real-time Updates**: Auto-refresh to see the latest entries in real-time
- **Dark Mode**: Toggle between light and dark themes for better visibility
- **Export**: Export logs to CSV for further analysis
- **Responsive Design**: Works on desktop and mobile devices

### Using the API

```bash
# Start the API server
make run-api

# Or run with custom port
make run-api PORT=8080 HOST=0.0.0.0
```

API endpoints:

- `GET /api/logs` - Get logs with optional filtering
  - Query parameters: `level`, `search`, `start_date`, `end_date`, `component`, `page`, `page_size`
- `GET /api/logs/{id}` - Get a specific log by ID
- `GET /api/stats` - Get logging statistics (counts by level, component, etc.)
- `GET /api/levels` - Get available log levels
- `GET /api/components` - Get available components (logger names)
- `POST /api/logs` - Add a new log (for external applications)

## Multi-Language Support

LogLama can be used from various programming languages and technologies. Here are some examples:

### JavaScript/Node.js

```javascript
// JavaScript integration with LogLama
const { exec } = require('child_process');

class PyLogger {
    constructor(component = 'javascript') {
        this.component = component;
    }
    
    log(level, message, context = {}) {
        const contextStr = JSON.stringify(context).replace(/"/g, '\"');
        const cmd = `python3 -c "from loglama.core.logger import get_logger; import json; logger = get_logger('${this.component}'); logger.${level}('${message}', extra={'context': json.loads('${contextStr}') if '${contextStr}' else {}})"`;        
        exec(cmd);
    }
    
    debug(message, context = {}) { this.log('debug', message, context); }
    info(message, context = {}) { this.log('info', message, context); }
    warning(message, context = {}) { this.log('warning', message, context); }
    error(message, context = {}) { this.log('error', message, context); }
}

// Usage
const logger = new PyLogger('my_js_app');
logger.info('Hello from JavaScript!', { user: 'js_user' });
```

### PHP

```php
<?php
// PHP integration with LogLama
class PyLogger {
    private $component;
    
    public function __construct($component = 'php') {
        $this->component = $component;
    }
    
    public function log($level, $message, $context = []) {
        $contextJson = json_encode($context);
        $contextJson = str_replace('"', '\"', $contextJson);
        $cmd = "python3 -c \"from loglama.core.logger import get_logger; import json; logger = get_logger('{$this->component}'); logger.{$level}('{$message}', extra={'context': json.loads('{$contextJson}') if '{$contextJson}' else {}})\""
;
        exec($cmd);
    }
    
    public function info($message, $context = []) { $this->log('info', $message, $context); }
    public function error($message, $context = []) { $this->log('error', $message, $context); }
}

// Usage
$logger = new PyLogger('my_php_app');
$logger->info('Hello from PHP!', ['user' => 'php_user']);
?>
```

### Bash

```bash
#!/bin/bash

# Bash integration with LogLama
function pylog() {
    local level=$1
    local message=$2
    local component=${3:-"bash"}
    
    python3 -c "from loglama.core.logger import get_logger; logger = get_logger('$component'); logger.$level('$message')"
}

# Usage
pylog "info" "Hello from Bash!" "my_bash_script"
pylog "error" "Something went wrong" "my_bash_script"
```

Run the multi-language examples with:

```bash
# Run all multi-language examples
make run-examples

# Run shell examples specifically
make run-shell-examples
```

## Integration with PyLama Ecosystem

LogLama is designed to work seamlessly with other components of the PyLama ecosystem. Use the integration script to add LogLama to any component:

```bash
# Integrate LogLama into all components
make run-integration

# Or run directly for a specific component
python scripts/integrate_loglama.py --component apilama
```

The integration script will:

1. Create necessary directories and files
2. Add logging configuration to the component
3. Update environment variables in `.env` and `.env.example` files
4. Provide instructions for using LogLama in the component

Example integrations:

- **WebLama**: Track web requests and user interactions with context-aware logging
- **APILama**: Log API calls and responses with structured data for debugging
- **PyBox**: Track file operations and system events with detailed context
- **PyLLM**: Monitor LLM interactions and performance metrics

## Example Application

LogLama includes an example application that demonstrates its features:

```bash
# Run the example application
make run-example

# View the generated logs in the web interface
make view-logs
```

The example application simulates a web service processing requests and demonstrates:

- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Context-aware logging with request IDs and user IDs
- Error handling and exception logging
- Structured logging with additional context fields
- Database logging for later analysis

## Testing

LogLama includes comprehensive tests to ensure reliability:

```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run Ansible tests (requires Ansible)
make test-ansible
```

The test suite includes:

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test components working together
- **Web interface tests**: Test the web interface functionality
- **SQLite tests**: Verify database logging and querying
- **Ansible tests**: Test shell scripts, interactive mode, and API functionality

## Development

```bash
# Install development dependencies
make setup

# Run tests
make test

# Run linting checks
make lint

# Format code
make format

# Run example application
make run-example

# View logs in web interface
make view-logs

# Clean up generated files
make clean
```

## Troubleshooting

### Common Issues

1. **Missing logs in database**
   - Check that `LOGLAMA_DB_LOGGING` is set to `true`
   - Verify the database path in `LOGLAMA_DB_PATH`
   - Ensure the directory for the database exists

2. **Web interface shows no logs**
   - Verify the database path when starting the web interface
   - Check that logs have been written to the database
   - Try running the example application to generate sample logs

3. **Integration script fails**
   - Ensure the target component directory exists
   - Check that you have write permissions to the directory
   - Verify that Python is installed and in your PATH

4. **Context not appearing in logs**
   - Ensure `context_filter=True` is set when configuring logging
   - Check that you're using `LogContext` or `capture_context` correctly
   - For structured logging, verify `structured=True` is set

### Getting Help

If you encounter issues not covered here, please:

1. Check the logs in the `logs` directory
2. Run the tests to verify your installation
3. Open an issue on the GitHub repository

## Duplicate Code Elimination

One of the key benefits of LogLama is the elimination of duplicated logging code across projects. The integration script helps you remove redundant code related to:

1. **Environment variable loading**: Standardized .env file loading
2. **Logging configuration**: Consistent setup across all components
3. **Debug utilities**: Common debugging functions and tools
4. **Context management**: Unified approach to context-aware logging

To remove duplicated code in your projects:

```bash
# Run the integration script
python scripts/integrate_loglama.py --component=your_component_path

# Or for all components
python scripts/integrate_loglama.py --all
```

This will analyze your codebase, identify duplicated logging code, and replace it with LogLama imports.

## Auto-Diagnostic Capabilities

LogLama includes powerful auto-diagnostic tools to help identify and fix common issues in your applications:

### Diagnostic Tools

```bash
# Run a system health check
python -m loglama.cli diagnose -c health

# Generate a comprehensive diagnostic report
python -m loglama.cli diagnose -c report -o diagnostic_report.json

# Troubleshoot specific components
python -m loglama.cli diagnose -c troubleshoot-logging
python -m loglama.cli diagnose -c troubleshoot-context
python -m loglama.cli diagnose -c troubleshoot-database
```

### Auto-Repair Decorators

LogLama provides smart decorators that can automatically detect and fix common issues:

```python
from loglama.decorators import auto_fix, log_errors, with_diagnostics

# Automatically fix common issues and log errors
@auto_fix
def my_function():
    # Your code here
    pass

# Log all errors with detailed context
@log_errors
def process_data(data):
    # Process data with automatic error logging
    pass

# Run diagnostics before and after function execution
@with_diagnostics
def critical_operation():
    # Operation will be monitored and diagnosed
    pass
```

### Environment Testing

Test LogLama in different environments using the included Ansible playbooks:

```bash
# Run all tests locally
cd tests/ansible
ansible-playbook -i inventory.ini loglama_test_playbook.yml --limit local

# Test on remote servers
ansible-playbook -i inventory.ini loglama_test_playbook.yml --limit remote
```

### Integrating Diagnostics in Your Projects

You can easily integrate LogLama diagnostics into your own projects:

```python
from loglama.diagnostics import check_system_health, generate_diagnostic_report
from loglama.utils.auto_fix import apply_fixes

# Check for issues
health_result = check_system_health()

# Apply automatic fixes if issues are found
if health_result['issues']:
    apply_fixes(health_result['issues'])
    
# Generate a diagnostic report for your application
report = generate_diagnostic_report()
```

## Contributing

We welcome contributions to LogLama. Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to contribute.

## License

[LICENSE](LICENSE)