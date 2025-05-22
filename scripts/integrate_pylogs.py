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
    
    # Check if the database exists and handle schema changes
    if db_enabled and os.path.exists(db_path):
        try:
            # Try to connect to the database to check if it has the correct schema
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info(logs)")
            columns = [column[1] for column in cursor.fetchall()]
            conn.close()
            
            # Check if the required columns exist
            required_columns = ['level', 'level_no', 'logger_name', 'message']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"Database schema outdated. Missing columns: {missing_columns}")
                print(f"Recreating database at {db_path}")
                os.remove(db_path)
                print("Old database removed. A new one will be created automatically.")
        except Exception as e:
            print(f"Error checking database schema: {e}")
            print(f"Recreating database at {db_path}")
            os.remove(db_path)
            print("Old database removed. A new one will be created automatically.")
    
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
    """
    Integrate PyLogs into a component.
    
    Args:
        component_dir (str): Path to the component directory
        component_name (str): Name of the component
        
    Returns:
        dict: Status report of the integration process
    """
    print(f"\nIntegrating PyLogs into {component_name}...")
    
    status = {
        'component': component_name,
        'success': False,
        'logs_dir_created': False,
        'config_file_created': False,
        'env_updated': False,
        'env_example_updated': False,
        'errors': []
    }
    
    # Check if component directory exists
    if not os.path.isdir(component_dir):
        error_msg = f"Component directory {component_dir} does not exist."
        print(f"Error: {error_msg}")
        status['errors'].append(error_msg)
        return status
    
    # Create logs directory
    logs_dir = os.path.join(component_dir, 'logs')
    try:
        create_directory(logs_dir)
        status['logs_dir_created'] = True
    except PermissionError as e:
        error_msg = f"Could not create logs directory at {logs_dir} due to permission error: {str(e)}"
        print(f"Warning: {error_msg}")
        print(f"Please create the directory manually or run this script with appropriate permissions.")
        status['errors'].append(error_msg)
    
    # Create logging_config.py
    component_module_dir = os.path.join(component_dir, component_name)
    if os.path.isdir(component_module_dir):
        if create_logging_config(component_name, component_module_dir):
            status['config_file_created'] = True
    else:
        error_msg = f"Component module directory {component_module_dir} does not exist."
        print(f"Warning: {error_msg}")
        print(f"Skipping creation of logging_config.py.")
        status['errors'].append(error_msg)
    
    # Update .env and .env.example files
    if update_env_file(component_dir, component_name):
        status['env_updated'] = True
    
    if update_env_example_file(component_dir, component_name):
        status['env_example_updated'] = True
    
    # Set overall success status
    status['success'] = (
        status['logs_dir_created'] or not os.path.isdir(component_module_dir)
    ) and (
        status['config_file_created'] or not os.path.isdir(component_module_dir)
    )
    
    print(f"PyLogs integration for {component_name} {'completed successfully' if status['success'] else 'completed with warnings'}.")
    return status


def main():
    """
    Main function for integrating PyLogs into PyLama ecosystem components.
    
    Parses command line arguments and integrates PyLogs into the specified components.
    Generates a comprehensive report of the integration status.
    """
    parser = argparse.ArgumentParser(description="Integrate PyLogs into PyLama ecosystem components.")
    parser.add_argument("--component", "-c", help="Component to integrate PyLogs into (e.g., apilama, weblama)")
    parser.add_argument("--all", "-a", action="store_true", help="Integrate PyLogs into all components")
    parser.add_argument("--dir", "-d", help="Base directory containing the components")
    parser.add_argument("--report-only", "-r", action="store_true", help="Only generate a report without making changes")
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
    integration_results = []
    if args.all:
        # Detect all components in the base directory
        # Skip directories that are not actual components
        excluded_dirs = [
            "pylogs", "venv", ".venv", ".git", ".tox", ".pytest_cache", "__pycache__", 
            "logs", "data", ".idea", "dist", "build", "node_modules"
        ]
        for item in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, item)) and item not in excluded_dirs:
                components.append(item)
    elif args.component:
        components = [args.component]
    else:
        print("Please specify a component with --component or use --all to integrate all components.")
        return 1
    
    print(f"Components to integrate: {', '.join(components)}")
    
    # Check if components already have PyLogs integrated
    def check_component_integration(component_name, component_dir):
        status = {
            'component': component_name,
            'has_logging_config': False,
            'has_logs_dir': False,
            'env_has_pylogs': False,
            'env_example_has_pylogs': False,
            'fully_integrated': False
        }
        
        # Check for logging_config.py
        component_module_dir = os.path.join(component_dir, component_name)
        logging_config_path = os.path.join(component_module_dir, 'logging_config.py')
        status['has_logging_config'] = os.path.exists(logging_config_path)
        
        # Check for logs directory
        logs_dir = os.path.join(component_dir, 'logs')
        status['has_logs_dir'] = os.path.exists(logs_dir)
        
        # Check .env file for PyLogs configuration
        env_path = os.path.join(component_dir, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
                status['env_has_pylogs'] = f'{component_name.upper()}_LOG_LEVEL' in env_content
        
        # Check .env.example file for PyLogs configuration
        env_example_path = os.path.join(component_dir, '.env.example')
        if os.path.exists(env_example_path):
            with open(env_example_path, 'r') as f:
                env_example_content = f.read()
                status['env_example_has_pylogs'] = f'{component_name.upper()}_LOG_LEVEL' in env_example_content
        
        # Determine if fully integrated
        status['fully_integrated'] = (
            status['has_logging_config'] and 
            status['has_logs_dir'] and 
            status['env_has_pylogs'] and 
            status['env_example_has_pylogs']
        )
        
        return status
    
    # Generate report for all components
    if args.report_only:
        print("\nGenerating PyLogs integration report...")
        for component in components:
            component_dir = os.path.join(base_dir, component)
            status = check_component_integration(component, component_dir)
            integration_results.append(status)
    else:
        # Integrate PyLogs into each component
        for component in components:
            component_dir = os.path.join(base_dir, component)
            result = integrate_component(component_dir, component)
            integration_results.append(result)
    
    # Generate and print report
    print("\n=== PyLogs Integration Report ===")
    print("\nComponent Status:\n")
    
    for result in integration_results:
        component = result['component']
        if args.report_only:
            status_str = "✅ Fully integrated" if result['fully_integrated'] else "❌ Not fully integrated"
            print(f"{component:15} | {status_str}")
            if not result['fully_integrated']:
                missing = []
                if not result['has_logging_config']:
                    missing.append("logging_config.py")
                if not result['has_logs_dir']:
                    missing.append("logs directory")
                if not result['env_has_pylogs']:
                    missing.append(".env configuration")
                if not result['env_example_has_pylogs']:
                    missing.append(".env.example configuration")
                print(f"               Missing: {', '.join(missing)}")
        else:
            status_str = "✅ Success" if result['success'] else "⚠️ Completed with warnings"
            print(f"{component:15} | {status_str}")
            if result['errors']:
                print(f"               Warnings: {len(result['errors'])}")
    
    print("\nTo use PyLogs in your components, add the following at the top of your main module:")
    print("```python")
    print("# Initialize logging first, before any other imports")
    print("from your_component.logging_config import init_logging, get_logger")
    print("")
    print("# Initialize logging with PyLogs")
    print("init_logging()")
    print("")
    print("# Get a logger for this module")
    print("logger = get_logger('module_name')")
    print("```")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
