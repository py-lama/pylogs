# PyLogs

A powerful logging utility for the PyLama ecosystem with CLI, API, and SQLite support.

## Features

- **Multi-output logging**: Console, file, SQLite database, and API endpoints
- **Structured logging**: Support for structured logging with `structlog`
- **Context-aware logging**: Add context to your logs for better debugging
- **Web interface**: Visualize and manage logs through a web dashboard
- **RESTful API**: Access and manage logs programmatically
- **Command-line interface**: Interact with logs from the terminal
- **Environment configuration**: Easy configuration through environment variables
- **Custom formatters**: JSON and colored output for better readability
- **Enhanced handlers**: Improved file rotation, SQLite storage, and API integration

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/py-lama.git
cd py-lama/pylogs

# Install the package
make setup
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

# Database Configuration
PYLOGS_DB_ENABLED=true              # Enable database logging
PYLOGS_DB_PATH=./db/pylogs.db       # Path to SQLite database

# API and Web Interface Configuration
PYLOGS_API_PORT=5000                # API server port
PYLOGS_WEB_PORT=5001                # Web interface port
```

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
# Start the web interface
make run-web

# Or run with custom port
make run-web PORT=8080 HOST=0.0.0.0
```

Then open your browser at http://localhost:5001 (or your custom port).

### Using the API

```bash
# Start the API server
make run-api

# Or run with custom port
make run-api PORT=8080 HOST=0.0.0.0
```

API endpoints:

- `GET /api/logs` - Get all logs
- `GET /api/logs/{id}` - Get a specific log
- `POST /api/logs` - Add a new log
- `DELETE /api/logs/{id}` - Delete a log
- `GET /api/stats` - Get logging statistics

## Integration with PyLama Ecosystem

PyLogs is designed to work seamlessly with other components of the PyLama ecosystem:

- **WebLama**: Use PyLogs to track web requests and user interactions
- **APILama**: Log API calls and responses for debugging and monitoring
- **PyBox**: Track file operations and system events
- **PyLLM**: Monitor LLM interactions and performance

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

# Clean up generated files
make clean
```

## License

MIT
