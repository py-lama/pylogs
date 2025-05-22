#!/usr/bin/env python3

"""
Migrator for Python's standard logging module.

This migrator converts code using Python's built-in logging module to use LogLama instead.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union

from .base_migrator import BaseMigrator, MigrationReport


class LoggingMigrator(BaseMigrator):
    """Migrator for Python's standard logging module."""
    
    def __init__(self):
        super().__init__()
        self.name = "logging"
        self.file_patterns = [r"logging[_\-]?config\.py", r"log[_\-]?config\.py"]
        self.dir_patterns = [r"logging"]
        
        # Patterns to find and replace
        self.patterns = {
            "imports": [
                (r"import\s+logging", "import loglama"),
                (r"from\s+logging\s+import\s+(.+)", r"from loglama import \1"),
                (r"from\s+logging\.(\w+)\s+import\s+(.+)", r"from loglama.\1 import \2"),
            ],
            "config": [
                (r"logging\.basicConfig\((.*)\)", self._replace_basic_config),
                (r"logging\.getLogger\(([^\)]*)\)", r"loglama.get_logger(\1)"),
                (r"logging\.FileHandler\(([^\)]*)\)", r"loglama.handlers.EnhancedRotatingFileHandler(\1)"),
                (r"logging\.StreamHandler\(([^\)]*)\)", r"loglama.handlers.ConsoleHandler(\1)"),
                (r"logging\.(DEBUG|INFO|WARNING|ERROR|CRITICAL)", r"loglama.\1"),
            ],
            "handlers": [
                (r"logging\.handlers\.(\w+)\(([^\)]*)\)", r"loglama.handlers.\1(\2)"),
            ],
            "formatters": [
                (r"logging\.Formatter\(([^\)]*)\)", r"loglama.formatters.ColoredFormatter(\1)"),
            ],
            "logger_methods": [
                (r"(\w+)\.setLevel\(([^\)]*)\)", r"\1.set_level(\2)"),
                (r"(\w+)\.addHandler\(([^\)]*)\)", r"\1.add_handler(\2)"),
                (r"(\w+)\.removeHandler\(([^\)]*)\)", r"\1.remove_handler(\2)"),
                (r"(\w+)\.addFilter\(([^\)]*)\)", r"\1.add_filter(\2)"),
                (r"(\w+)\.removeFilter\(([^\)]*)\)", r"\1.remove_filter(\2)"),
            ],
        }
    
    def _replace_basic_config(self, match):
        """Replace logging.basicConfig() with loglama.setup_logging()."""
        args = match.group(1)
        
        # Convert arguments from basicConfig to setup_logging
        args = args.replace("level=", "level=")
        args = args.replace("format=", "format=")
        args = args.replace("filename=", "file_path=")
        args = args.replace("filemode=", "# filemode is not needed in LogLama, ")
        
        return f"loglama.setup_logging({args})"
    
    def migrate_content(self, content: str, file_path: Path, report: MigrationReport, verbose: bool) -> str:
        """Migrate logging references in the content."""
        original_content = content
        
        # Process imports
        for pattern, replacement in self.patterns["imports"]:
            for match in re.finditer(pattern, content):
                old_import = match.group(0)
                if callable(replacement):
                    new_import = replacement(match)
                else:
                    new_import = re.sub(pattern, replacement, old_import)
                
                if verbose:
                    print(f"Found import: {old_import} -> {new_import}")
                
                report.add_change(str(file_path), "import", old_import, new_import)
                content = content.replace(old_import, new_import)
        
        # Process configuration
        for pattern, replacement in self.patterns["config"]:
            for match in re.finditer(pattern, content):
                old_config = match.group(0)
                if callable(replacement):
                    new_config = replacement(match)
                else:
                    new_config = re.sub(pattern, replacement, old_config)
                
                if verbose:
                    print(f"Found config: {old_config} -> {new_config}")
                
                report.add_change(str(file_path), "config", old_config, new_config)
                content = content.replace(old_config, new_config)
        
        # Process handlers
        for pattern, replacement in self.patterns["handlers"]:
            for match in re.finditer(pattern, content):
                old_handler = match.group(0)
                if callable(replacement):
                    new_handler = replacement(match)
                else:
                    new_handler = re.sub(pattern, replacement, old_handler)
                
                if verbose:
                    print(f"Found handler: {old_handler} -> {new_handler}")
                
                report.add_change(str(file_path), "handler", old_handler, new_handler)
                content = content.replace(old_handler, new_handler)
        
        # Process formatters
        for pattern, replacement in self.patterns["formatters"]:
            for match in re.finditer(pattern, content):
                old_formatter = match.group(0)
                if callable(replacement):
                    new_formatter = replacement(match)
                else:
                    new_formatter = re.sub(pattern, replacement, old_formatter)
                
                if verbose:
                    print(f"Found formatter: {old_formatter} -> {new_formatter}")
                
                report.add_change(str(file_path), "formatter", old_formatter, new_formatter)
                content = content.replace(old_formatter, new_formatter)
        
        # Process logger methods
        for pattern, replacement in self.patterns["logger_methods"]:
            for match in re.finditer(pattern, content):
                old_method = match.group(0)
                if callable(replacement):
                    new_method = replacement(match)
                else:
                    new_method = re.sub(pattern, replacement, old_method)
                
                if verbose:
                    print(f"Found logger method: {old_method} -> {new_method}")
                
                report.add_change(str(file_path), "logger_method", old_method, new_method)
                content = content.replace(old_method, new_method)
        
        return content
    
    def get_renamed_file(self, file_name: str) -> str:
        """Get the new name for a file."""
        if re.search(r"logging[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        elif re.search(r"log[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        return file_name
    
    def get_renamed_directory(self, dir_name: str) -> str:
        """Get the new name for a directory."""
        if dir_name.lower() == "logging":
            return "logging"
        return dir_name
    
    def create_loglama_config(self, base_path: Path, report: MigrationReport, report_only: bool, verbose: bool):
        """Create LogLama configuration files based on existing logging configuration."""
        # Look for existing logging configuration files
        config_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if re.search(r"logging[_\-]?config\.py", file, re.IGNORECASE) or \
                   re.search(r"log[_\-]?config\.py", file, re.IGNORECASE):
                    config_files.append(Path(root) / file)
        
        if not config_files:
            # Create a new logging_config.py if none exists
            config_file = base_path / "logging_config.py"
            config_content = self._generate_default_config()
            
            if verbose:
                print(f"Creating new LogLama configuration file: {config_file}")
            
            report.add_change(str(config_file), "new_file", "", config_content)
            
            if not report_only:
                with open(config_file, 'w') as f:
                    f.write(config_content)
        else:
            # We've already migrated existing config files in the migrate_content method
            if verbose:
                print(f"Found existing logging configuration files: {config_files}")
    
    def _generate_default_config(self) -> str:
        """Generate a default LogLama configuration file."""
        return '''
#!/usr/bin/env python3

"""
Logging configuration for the application.

This module initializes LogLama and provides functions for getting loggers.
"""

import os
import sys
from pathlib import Path

# Try to import LogLama, with fallback to built-in logging
try:
    from loglama import setup_logging, get_logger, LogContext
    from loglama.config.env_loader import load_env, get_env
    from loglama.formatters import ColoredFormatter, JSONFormatter
    from loglama.handlers import SQLiteHandler, EnhancedRotatingFileHandler
    LOGLAMA_AVAILABLE = True
except ImportError:
    import logging
    LOGLAMA_AVAILABLE = False
    print("LogLama not available, falling back to built-in logging")


def init_logging():
    """Initialize logging for the application."""
    if LOGLAMA_AVAILABLE:
        # Load environment variables from .env file
        load_env(verbose=True)
        
        # Get configuration from environment variables
        log_level = get_env("APP_LOG_LEVEL", "INFO")
        log_dir = get_env("APP_LOG_DIR", "./logs")
        db_logging = get_env("APP_DB_LOGGING", "false").lower() == "true"
        db_path = get_env("APP_DB_PATH", f"{log_dir}/app.db")
        json_logs = get_env("APP_JSON_LOGS", "false").lower() == "true"
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup logging with LogLama
        logger = setup_logging(
            name="app",
            level=log_level,
            console=True,
            file=True,
            file_path=f"{log_dir}/app.log",
            database=db_logging,
            db_path=db_path,
            json_format=json_logs
        )
        
        logger.info("Logging initialized with LogLama")
        return logger
    else:
        # Fallback to built-in logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("app.log"),
            ]
        )
        logger = logging.getLogger("app")
        logger.info("Logging initialized with built-in logging")
        return logger


def get_app_logger(name):
    """Get a logger for the application.
    
    Args:
        name: Name of the logger
        
    Returns:
        A logger instance
    """
    if LOGLAMA_AVAILABLE:
        return get_logger(name)
    else:
        return logging.getLogger(name)
'''
