#!/usr/bin/env python3

"""
PyLogs Integration Script

This script helps integrate PyLogs into existing PyLama ecosystem components.
It updates configuration files, adds necessary imports, and ensures proper
environment variable loading before other libraries.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import PyLogs
try:
    from pylogs.config.env_loader import load_env
    PYLOGS_AVAILABLE = True
except ImportError:
    PYLOGS_AVAILABLE = False


def create_directory(path):
    """Create a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    print(f"Created directory: {path}")


def create_logging_config(component_name, target_dir):
    """Create a logging_config.py file for the component."""
    config_path = os.path.join(target_dir, "logging_config.py")
    
    # Don't overwrite existing file unless forced
    if os.path.exists(config_path):
        print(f"Logging config already exists at {config_path}. Skipping.")
        return False
    
    with open(config_path, "w") as f:
        template = f'''#!/usr/bin/env python3

"""
{component_name.capitalize()} Logging Configuration

This module configures logging for {component_name.capitalize()} using the PyLogs package.
It ensures that environment variables are loaded before any other libraries.
"""

import os
import sys
import logging
from pathlib import Path

# Add the pylogs package to the path if it's not already installed
pylogs_path = Path(__file__).parent.parent.parent.parent / 'pylogs'
if pylogs_path.exists() and str(pylogs_path) not in sys.path:
    sys.path.insert(0, str(pylogs_path))

# Import PyLogs components
try:
    from pylogs.config.env_loader import load_env, get_env
    from pylogs.utils import configure_logging, LogContext, capture_context
    from pylogs.formatters import ColoredFormatter, JSONFormatter
    from pylogs.handlers import SQLiteHandler, EnhancedRotatingFileHandler
    PYLOGS_AVAILABLE = True
except ImportError as e:
    print(f"PyLogs import error: {{e}}")
    PYLOGS_AVAILABLE = False

# Set up basic logging as a fallback
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)7s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def init_logging():
    """
    Initialize logging for {component_name.capitalize()} using PyLogs.
    
    This function should be called at the very beginning of the application
    before any other imports or configurations are done.
    """
    if not PYLOGS_AVAILABLE:
        print("PyLogs package not available. Using default logging configuration.")
        return False
    
    # Load environment variables from .env files
    load_env(verbose=True)
    
    # Get logging configuration from environment variables
    log_level = get_env('{component_name.upper()}_LOG_LEVEL', 'INFO')
    log_dir = get_env('{component_name.upper()}_LOG_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))
    db_enabled = get_env('{component_name.upper()}_DB_LOGGING', 'true').lower() in ('true', 'yes', '1')
    db_path = get_env('{component_name.upper()}_DB_PATH', os.path.join(log_dir, '{component_name}.db'))
    json_format = get_env('{component_name.upper()}_JSON_LOGS', 'false').lower() in ('true', 'yes', '1')
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logger = configure_logging(
        name='{component_name}',
        level=log_level,
        console=True,
        file=True,
        file_path=os.path.join(log_dir, '{component_name}.log'),
        database=db_enabled,
        db_path=db_path,
        json=json_format,
        context_filter=True
    )
    
    # Log initialization
    logger.info('{component_name.capitalize()} logging initialized with PyLogs')
    return True


def get_logger(name=None):
    """
    Get a logger instance.
    
    Args:
        name (str, optional): Name of the logger. Defaults to '{component_name}'.
        
    Returns:
        Logger: A configured logger instance.
    """
    if not name:
        name = '{component_name}'
    elif not name.startswith('{component_name}.'):
        name = f'{component_name}.{{name}}'
    
    if PYLOGS_AVAILABLE:
        from pylogs import get_logger as pylogs_get_logger
        return pylogs_get_logger(name)
    else:
        return logging.getLogger(name)
'''
        f.write(template)
    
    print(f"Created logging config at {config_path}")
    return True


def update_env_file(component_dir, component_name):
    """Update the .env file with PyLogs configuration."""
    env_path = os.path.join(component_dir, ".env")
    env_example_path = os.path.join(component_dir, ".env.example")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(env_path):
        if os.path.exists(env_example_path):
            shutil.copy(env_example_path, env_path)
            print(f"Created .env file from .env.example at {env_path}")
        else:
            with open(env_path, "w") as f:
                f.write(f"# {component_name.capitalize()} Environment Variables\n\n")
            print(f"Created empty .env file at {env_path}")
    
    # Read the existing .env file
    with open(env_path, "r") as f:
        env_content = f.read()
    
    # Check if PyLogs configuration already exists
    if f"{component_name.upper()}_LOG_LEVEL" in env_content:
        print(f"PyLogs configuration already exists in {env_path}. Skipping.")
        return False
    
    # Add PyLogs configuration
    with open(env_path, "a") as f:
        env_template = f'''
# PyLogs configuration
{component_name.upper()}_LOG_LEVEL=INFO
{component_name.upper()}_LOG_DIR=./logs
{component_name.upper()}_DB_LOGGING=true
{component_name.upper()}_DB_PATH=./logs/{component_name}.db
{component_name.upper()}_JSON_LOGS=false

# PyLogs advanced settings
PYLOGS_STRUCTURED_LOGGING=false
PYLOGS_MAX_LOG_SIZE=10485760  # 10 MB
PYLOGS_BACKUP_COUNT=5
'''
        f.write(env_template)
    
    print(f"Updated .env file at {env_path} with PyLogs configuration")
    return True


def update_env_example_file(component_dir, component_name):
    """Update the .env.example file with PyLogs configuration."""
    env_example_path = os.path.join(component_dir, ".env.example")
    
    # Create .env.example file if it doesn't exist
    if not os.path.exists(env_example_path):
        with open(env_example_path, "w") as f:
            f.write(f"# {component_name.capitalize()} Environment Variables\n\n")
        print(f"Created empty .env.example file at {env_example_path}")
    
    # Read the existing .env.example file
    with open(env_example_path, "r") as f:
        env_content = f.read()
    
    # Check if PyLogs configuration already exists
    if f"{component_name.upper()}_LOG_LEVEL" in env_content:
        print(f"PyLogs configuration already exists in {env_example_path}. Skipping.")
        return False
    
    # Add PyLogs configuration
    with open(env_example_path, "a") as f:
        env_example_template = f'''
# PyLogs configuration
# These settings control the PyLogs integration
{component_name.upper()}_LOG_LEVEL=INFO                # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
{component_name.upper()}_LOG_DIR=./logs               # Directory to store log files
{component_name.upper()}_DB_LOGGING=true              # Enable database logging for advanced querying
{component_name.upper()}_DB_PATH=./logs/{component_name}.db    # Path to SQLite database for logs
{component_name.upper()}_JSON_LOGS=false              # Use JSON format for logs (useful for log processors)

# PyLogs advanced settings
PYLOGS_STRUCTURED_LOGGING=false      # Use structured logging with structlog
PYLOGS_MAX_LOG_SIZE=10485760         # Maximum log file size in bytes (10 MB)
PYLOGS_BACKUP_COUNT=5                # Number of backup log files to keep
'''
        f.write(env_example_template)
    
    print(f"Updated .env.example file at {env_example_path} with PyLogs configuration")
    return True


def integrate_component(component_dir, component_name):
    """Integrate PyLogs into a component."""
    print(f"\nIntegrating PyLogs into {component_name.capitalize()}...")
    
    # Ensure the component directory exists
    if not os.path.exists(component_dir):
        print(f"Component directory {component_dir} does not exist. Skipping.")
        return False
    
    # Create logs directory
    logs_dir = os.path.join(component_dir, "logs")
    create_directory(logs_dir)
    
    # Determine the module directory
    module_dir = os.path.join(component_dir, component_name)
    if not os.path.exists(module_dir):
        print(f"Module directory {module_dir} does not exist. Creating it.")
        create_directory(module_dir)
    
    # Create __init__.py if it doesn't exist
    init_path = os.path.join(module_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write(f"""{component_name.capitalize()} module.
""")
        print(f"Created __init__.py at {init_path}")
    
    # Create logging_config.py
    create_logging_config(component_name, module_dir)
    
    # Update .env and .env.example files
    update_env_file(component_dir, component_name)
    update_env_example_file(component_dir, component_name)
    
    print(f"PyLogs integration for {component_name.capitalize()} complete!")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Integrate PyLogs into PyLama ecosystem components.")
    parser.add_argument("--component", "-c", help="Component to integrate PyLogs into (e.g., apilama, weblama)")
    parser.add_argument("--all", "-a", action="store_true", help="Integrate PyLogs into all components")
    parser.add_argument("--dir", "-d", help="Base directory containing the components")
    args = parser.parse_args()
    
    # Check if PyLogs is available
    if not PYLOGS_AVAILABLE:
        print("PyLogs package is not available. Please install it first.")
        return 1
    
    # Determine the base directory
    if args.dir:
        base_dir = args.dir
    else:
        base_dir = str(Path(__file__).parent.parent.parent)
    
    print(f"Using base directory: {base_dir}")
    
    # List of components to integrate
    components = []
    if args.all:
        # Detect all components in the base directory
        for item in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, item)) and item not in ["pylogs", "venv", ".venv", ".git"]:
                components.append(item)
    elif args.component:
        components = [args.component]
    else:
        print("Please specify a component with --component or use --all to integrate all components.")
        return 1
    
    print(f"Components to integrate: {', '.join(components)}")
    
    # Integrate PyLogs into each component
    for component in components:
        component_dir = os.path.join(base_dir, component)
        integrate_component(component_dir, component)
    
    print("\nPyLogs integration complete!")
    print("\nTo use PyLogs in your components, add the following at the top of your main module:")
    print("```python")
    print("# Initialize logging first, before any other imports")
    print("from your_component.logging_config import init_logging, get_logger")
    print("")
    print("# Initialize logging with PyLogs")
    print("init_logging()")
    print("")
    print("# Get a logger")
    print("logger = get_logger('your_module')")
    print("```")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
