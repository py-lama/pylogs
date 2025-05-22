# PyLogs - Log Smart, Debug Faster, Scale Better 

A powerful logging utility for the PyLama ecosystem with CLI, API, SQLite support, and web interface for log visualization. PyLogs provides a unified logging solution that can be integrated into any application or programming language.

<div align="center">

![PyLogs Logo](pylogs-logo.svg)


[![PyPI version](https://badge.fury.io/py/pylogs.svg)](https://badge.fury.io/py/pylogs)
[![Python versions](https://img.shields.io/pypi/pyversions/pylogs.svg)](https://pypi.org/project/pylogs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/pylogs)](https://pepy.tech/project/pylogs)

[![Build Status](https://github.com/py-lama/pylogs/workflows/CI/badge.svg)](https://github.com/py-lama/pylogs/actions)
[![Coverage Status](https://codecov.io/gh/py-lama/pylogs/branch/main/graph/badge.svg)](https://codecov.io/gh/py-lama/pylogs)
[![Code Quality](https://api.codeclimate.com/v1/badges/a99a88d28ad37a79dbf6/maintainability)](https://codeclimate.com/github/py-lama/pylogs)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=py-lama_pylogs&metric=security_rating)](https://sonarcloud.io/dashboard?id=py-lama_pylogs)

[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://py-lama.github.io/pylogs/)
[![GitHub stars](https://img.shields.io/github/stars/py-lama/pylogs.svg?style=social&label=Star)](https://github.com/py-lama/pylogs)
[![GitHub forks](https://img.shields.io/github/forks/py-lama/pylogs.svg?style=social&label=Fork)](https://github.com/py-lama/pylogs/fork)
[![GitHub issues](https://img.shields.io/github/issues/py-lama/pylogs.svg)](https://github.com/py-lama/pylogs/issues)

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
- **Integration tools**: Easily integrate PyLogs into existing PyLama ecosystem components
- **Comprehensive testing**: Unit, integration, and Ansible tests for all components
- **Multi-language support**: Use PyLogs from Python, JavaScript, PHP, Ruby, Bash, and more
- **Duplicate code elimination**: Remove redundant logging configuration across projects

## Installation

```bash
# Clone the repository
git clone https://github.com/py-lama/pylogs.git
cd py-lama/pylogs

# Install the package
make setup
```

Or install directly from the repository:

```bash
pip install git+https://github.com/py-lama/pylogs.git#subdirectory=pylogs
```

## Quick Start

```python
# Basic usage
from pylogs import get_logger

# Get a logger
logger = get_logger("my_app")

# Log messages
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# Log with context
from pylogs import LogContext

with LogContext(user_id="123", action="login"):
    logger.info("User logged in")
```

## Configuration

PyLogs can be configured through environment variables or a `.env` file. Copy the `env.example` file to `.env` and modify it as needed:

```bash
cp env.example .env
```

Key configuration options:

```
# Logging Configuration
PYLOGS_LOG_LEVEL=INFO                # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
PYLOGS_LOG_DIR=./logs               # Directory to store log files
PYLOGS_CONSOLE_ENABLED=true         # Enable console logging
PYLOGS_FILE_ENABLED=true            # Enable file logging
PYLOGS_JSON_LOGS=false              # Use JSON format for logs
PYLOGS_STRUCTURED_LOGGING=false     # Use structured logging with structlog

# Database Configuration
PYLOGS_DB_LOGGING=true              # Enable database logging
PYLOGS_DB_PATH=./logs/pylogs.db     # Path to SQLite database

# Advanced Configuration
PYLOGS_MAX_LOG_SIZE=10485760        # Maximum log file size in bytes (10 MB)
PYLOGS_BACKUP_COUNT=5               # Number of backup log files to keep

# Web Interface Configuration
PYLOGS_WEB_PORT=5000                # Web interface port
PYLOGS_WEB_HOST=127.0.0.1           # Web interface host
PYLOGS_WEB_PAGE_SIZE=100            # Number of logs per page in web interface
PYLOGS_WEB_DEBUG=false              # Enable debug mode for web interface
```

Environment variables are loaded automatically at the beginning of your application, before any other imports, to ensure proper configuration.

## Usage Examples

### Advanced Configuration

```python
from pylogs import configure_logging

# Configure logging with multiple outputs
logger = configure_logging(
    name="my_app",
    level="DEBUG",
    console=True,
    file=True,
    file_path="/path/to/logs/my_app.log",
    database=True,
    db_path="/path/to/db/pylogs.db",
    json=True
)

# Now use the logger
logger.info("Application started")
```

### Using Context

```python
from pylogs import get_logger, LogContext, capture_context

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
python -m pylogs.cli.main

# View recent logs
pylogs logs view --limit 10

# View logs by level
pylogs logs view --level ERROR

# Clear logs
pylogs logs clear
```

### Using the Web Interface

```bash
# Start the web interface (new command)
make web

# Or run with custom port and host
make web PORT=8081 HOST=0.0.0.0

# Or use the CLI directly
pylogs web --port 8081 --host 0.0.0.0
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

PyLogs can be used from various programming languages and technologies. Here are some examples:

### JavaScript/Node.js

```javascript
// JavaScript integration with PyLogs
const { exec } = require('child_process');

class PyLogger {
    constructor(component = 'javascript') {
        this.component = component;
    }
    
    log(level, message, context = {}) {
        const contextStr = JSON.stringify(context).replace(/"/g, '\"');
        const cmd = `python3 -c "from pylogs.core.logger import get_logger; import json; logger = get_logger('${this.component}'); logger.${level}('${message}', extra={'context': json.loads('${contextStr}') if '${contextStr}' else {}})"`;        
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
// PHP integration with PyLogs
class PyLogger {
    private $component;
    
    public function __construct($component = 'php') {
        $this->component = $component;
    }
    
    public function log($level, $message, $context = []) {
        $contextJson = json_encode($context);
        $contextJson = str_replace('"', '\"', $contextJson);
        $cmd = "python3 -c \"from pylogs.core.logger import get_logger; import json; logger = get_logger('{$this->component}'); logger.{$level}('{$message}', extra={'context': json.loads('{$contextJson}') if '{$contextJson}' else {}})\""
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

# Bash integration with PyLogs
function pylog() {
    local level=$1
    local message=$2
    local component=${3:-"bash"}
    
    python3 -c "from pylogs.core.logger import get_logger; logger = get_logger('$component'); logger.$level('$message')"
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

PyLogs is designed to work seamlessly with other components of the PyLama ecosystem. Use the integration script to add PyLogs to any component:

```bash
# Integrate PyLogs into all components
make run-integration

# Or run directly for a specific component
python scripts/integrate_pylogs.py --component apilama
```

The integration script will:

1. Create necessary directories and files
2. Add logging configuration to the component
3. Update environment variables in `.env` and `.env.example` files
4. Provide instructions for using PyLogs in the component

Example integrations:

- **WebLama**: Track web requests and user interactions with context-aware logging
- **APILama**: Log API calls and responses with structured data for debugging
- **PyBox**: Track file operations and system events with detailed context
- **PyLLM**: Monitor LLM interactions and performance metrics

## Example Application

PyLogs includes an example application that demonstrates its features:

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

PyLogs includes comprehensive tests to ensure reliability:

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
   - Check that `PYLOGS_DB_LOGGING` is set to `true`
   - Verify the database path in `PYLOGS_DB_PATH`
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

## Removing Duplicated Code

One of the key benefits of PyLogs is the elimination of duplicated logging code across projects. The integration script helps you remove redundant code related to:

1. **Environment variable loading**: Standardized .env file loading
2. **Logging configuration**: Consistent setup across all components
3. **Debug utilities**: Common debugging functions and tools
4. **Context management**: Unified approach to context-aware logging

To remove duplicated code in your projects:

```bash
# Run the integration script
python scripts/integrate_pylogs.py --component=your_component_path

# Or for all components
python scripts/integrate_pylogs.py --all
```

This will analyze your codebase, identify duplicated logging code, and replace it with PyLogs imports.

## License

MIT
