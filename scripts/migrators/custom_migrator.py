#!/usr/bin/env python3

"""
Migrator for custom logging implementations.

This migrator converts code using custom logging implementations to use LogLama instead.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union

from .base_migrator import BaseMigrator, MigrationReport


class CustomMigrator(BaseMigrator):
    """Migrator for custom logging implementations."""
    
    def __init__(self):
        super().__init__()
        self.name = "custom"
        self.file_patterns = [r"log[_\-]?config\.py", r"logger\.py"]
        self.dir_patterns = [r"logging", r"logger"]
        
        # Patterns to find and replace - these are more generic and might need manual adjustment
        self.patterns = {
            "custom_logger": [
                # Common patterns for custom loggers
                (r"class\s+(\w+)Logger\s*\(.*\):\s*", self._replace_custom_logger_class),
                (r"def\s+log_(\w+)\s*\(([^\)]*)\):\s*", self._replace_custom_log_method),
                (r"def\s+(\w+)_log\s*\(([^\)]*)\):\s*", self._replace_custom_log_method),
                (r"def\s+get_(\w+)_logger\s*\(([^\)]*)\):\s*", r"def get_\1_logger(\2):\n    # Replaced with LogLama\n    return loglama.get_logger(\2)\n"),
            ],
            "log_calls": [
                # Common patterns for log calls
                (r"log\.(\w+)\(([^\)]*)\)", r"logger.\1(\2)"),
                (r"(\w+)_log\.(\w+)\(([^\)]*)\)", r"logger.\2(\3)"),
                (r"log_(\w+)\(([^\)]*)\)", r"logger.\1(\2)"),
                (r"(\w+)_log\(([^\)]*)\)", r"logger.info(\2)  # Converted from custom log call"),
            ],
            "log_levels": [
                # Common patterns for log levels
                (r"LOG_LEVEL_(\w+)", r"loglama.\1"),
                (r"(\w+)_LOG_LEVEL", r"loglama.INFO  # Converted from custom log level"),
            ],
        }
    
    def _replace_custom_logger_class(self, match):
        """Replace a custom logger class with LogLama."""
        class_name = match.group(1)
        
        return f"# Custom logger class '{class_name}Logger' replaced with LogLama\n# Original class definition was:\n# {match.group(0)}\n# Use loglama.get_logger() instead\n"
    
    def _replace_custom_log_method(self, match):
        """Replace a custom log method with LogLama."""
        level = match.group(1).lower()
        args = match.group(2)
        
        # Map common level names to standard levels
        level_map = {
            "debug": "debug",
            "info": "info",
            "information": "info",
            "warn": "warning",
            "warning": "warning",
            "error": "error",
            "err": "error",
            "critical": "critical",
            "fatal": "critical",
            "exception": "exception",
        }
        
        mapped_level = level_map.get(level, "info")
        
        return f"def log_{level}({args}):\n    # Replaced with LogLama\n    logger.{mapped_level}(message)  # Adjust parameters as needed\n"
    
    def migrate_content(self, content: str, file_path: Path, report: MigrationReport, verbose: bool) -> str:
        """Migrate custom logging references in the content."""
        original_content = content
        
        # Add LogLama import if we're going to use it
        if not any(x in content for x in ["import loglama", "from loglama import"]):
            # Add import at the top of the file, after any existing imports
            import_match = re.search(r"((?:import|from)\s+[\w\.]+(?:\s+import\s+[\w\.]+)?\s*\n)+", content)
            if import_match:
                imports_end = import_match.end()
                content = content[:imports_end] + "\nimport loglama\nfrom loglama import get_logger\n" + content[imports_end:]
            else:
                # No imports found, add at the top
                content = "import loglama\nfrom loglama import get_logger\n\n" + content
            
            if verbose:
                print(f"Added LogLama imports to {file_path}")
            
            report.add_change(str(file_path), "import", "", "import loglama\nfrom loglama import get_logger")
        
        # Process each pattern category
        for category, patterns in self.patterns.items():
            for pattern, replacement in patterns:
                for match in re.finditer(pattern, content):
                    old_text = match.group(0)
                    if callable(replacement):
                        new_text = replacement(match)
                    else:
                        new_text = re.sub(pattern, replacement, old_text)
                    
                    if verbose:
                        print(f"Found {category}: {old_text} -> {new_text}")
                    
                    report.add_change(str(file_path), category, old_text, new_text)
                    content = content.replace(old_text, new_text)
        
        # Add a logger initialization if it doesn't exist
        if "logger = get_logger" not in content and "logger = loglama.get_logger" not in content:
            # Try to find a good place to add it - after imports but before first function/class
            first_def = re.search(r"(def|class)\s+", content)
            if first_def:
                insert_pos = first_def.start()
                logger_init = "\n# Initialize logger\nlogger = get_logger(__name__)\n\n"
                content = content[:insert_pos] + logger_init + content[insert_pos:]
                
                if verbose:
                    print(f"Added logger initialization to {file_path}")
                
                report.add_change(str(file_path), "logger_init", "", logger_init.strip())
        
        return content
    
    def get_renamed_file(self, file_name: str) -> str:
        """Get the new name for a file."""
        if re.search(r"log[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        elif re.search(r"logger\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        return file_name
    
    def get_renamed_directory(self, dir_name: str) -> str:
        """Get the new name for a directory."""
        if dir_name.lower() in ["logging", "logger"]:
            return "logging"
        return dir_name
    
    def create_loglama_config(self, base_path: Path, report: MigrationReport, report_only: bool, verbose: bool):
        """Create LogLama configuration files based on existing logging configuration."""
        # Look for existing logging configuration files
        config_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if re.search(r"log[_\-]?config\.py", file, re.IGNORECASE) or \
                   re.search(r"logger\.py", file, re.IGNORECASE):
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
        return """
#!/usr/bin/env python3

"""
Logging configuration for the application.

This module initializes LogLama and provides functions for getting loggers.
"""

import os
import sys
from pathlib import Path

# Import LogLama
from loglama import setup_logging, get_logger, LogContext
from loglama.config.env_loader import load_env, get_env
from loglama.formatters import ColoredFormatter, JSONFormatter
from loglama.handlers import SQLiteHandler, EnhancedRotatingFileHandler


def init_logging():
    """Initialize logging for the application."""
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


def get_app_logger(name):
    """Get a logger for the application.
    
    Args:
        name: Name of the logger
        
    Returns:
        A logger instance
    """
    return get_logger(name)
"""
