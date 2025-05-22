# PyLogs Integration Scripts

This directory contains scripts to help integrate PyLogs into existing PyLama ecosystem components.

## integrate_pylogs.py

This script helps you integrate PyLogs into any component of the PyLama ecosystem. It will:

1. Create a `logging_config.py` module in the target component
2. Update `.env` and `.env.example` files with PyLogs configuration
3. Create necessary directories (logs, etc.)

### Usage

```bash
# Integrate PyLogs into a specific component
./integrate_pylogs.py --component apilama

# Integrate PyLogs into all components in the PyLama ecosystem
./integrate_pylogs.py --all

# Specify a custom base directory
./integrate_pylogs.py --all --dir /path/to/py-lama

# Generate a report without making any changes
./integrate_pylogs.py --all --report-only
```

### Integration Status Report

The script can generate a comprehensive report of the PyLogs integration status across all components using the `--report-only` flag. This is useful for checking which components have already been integrated and which ones still need work.

The report includes the following information for each component:

- Whether the component has a `logging_config.py` file
- Whether the component has a logs directory
- Whether the component's `.env` file includes PyLogs configuration
- Whether the component's `.env.example` file includes PyLogs configuration
- Overall integration status (fully integrated or not)

Example report output:

```
=== PyLogs Integration Report ===

Component Status:

apilama         | ✅ Fully integrated
pybox           | ✅ Fully integrated
pyllm           | ✅ Fully integrated
pylama          | ✅ Fully integrated
shellama        | ✅ Fully integrated
weblama         | ✅ Fully integrated
```

### Integration Steps

After running the script, you'll need to update your component's main module to use PyLogs. Add the following at the very top of your main module (before any other imports):

```python
# Initialize logging first, before any other imports
from your_component.logging_config import init_logging, get_logger

# Initialize logging with PyLogs
init_logging()

# Now import other standard libraries
import os
import sys
# ... other imports

# Get a logger
logger = get_logger('your_module')
```

### Integrated Components

The following PyLama ecosystem components have been integrated with PyLogs:

1. **APILama**: REST API gateway for the PyLama ecosystem
2. **PyBox**: Sandbox environment for executing code
3. **PyLLM**: LLM service for code generation
4. **PyLama**: Core component for the PyLama ecosystem
5. **ShellLama**: Shell command execution service
6. **WebLama**: Web interface for the PyLama ecosystem

You can check the integration status of each component using the `--report-only` flag as described above.

### Benefits of Using PyLogs

1. **Early Environment Loading**: PyLogs loads environment variables from `.env` files before any other libraries, preventing issues with incorrect configuration.

2. **Structured Logging**: PyLogs provides structured logging capabilities, making it easier to search and analyze logs.

3. **Multiple Outputs**: Logs can be sent to console, files, SQLite database, and more.

4. **Context-Aware Logging**: Add context to your logs for better debugging.

5. **Consistent Interface**: All components use the same logging interface, making it easier to understand and maintain.

6. **Web Interface**: Access and filter logs through a convenient web interface using the `pylogs web` command.

### Configuration

PyLogs can be configured through environment variables in your `.env` file:

```
# PyLogs configuration
COMPONENT_LOG_LEVEL=INFO                # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
COMPONENT_LOG_DIR=./logs               # Directory to store log files
COMPONENT_DB_LOGGING=true              # Enable database logging for advanced querying
COMPONENT_DB_PATH=./logs/component.db  # Path to SQLite database for logs
COMPONENT_JSON_LOGS=false              # Use JSON format for logs (useful for log processors)

# PyLogs advanced settings
PYLOGS_STRUCTURED_LOGGING=false        # Use structured logging with structlog
PYLOGS_MAX_LOG_SIZE=10485760           # Maximum log file size in bytes (10 MB)
PYLOGS_BACKUP_COUNT=5                  # Number of backup log files to keep
```

Replace `COMPONENT` with your component name (e.g., `APILAMA`, `WEBLAMA`, etc.).
