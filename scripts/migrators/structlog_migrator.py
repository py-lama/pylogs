#!/usr/bin/env python3

"""
Migrator for structlog.

This migrator converts code using structlog to use LogLama instead.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union

from .base_migrator import BaseMigrator, MigrationReport


class StructlogMigrator(BaseMigrator):
    """Migrator for structlog."""
    
    def __init__(self):
        super().__init__()
        self.name = "structlog"
        self.file_patterns = [r"structlog[_\-]?config\.py", r"log[_\-]?config\.py"]
        self.dir_patterns = [r"structlog"]
        
        # Patterns to find and replace
        self.patterns = {
            "imports": [
                (r"import\s+structlog", "import loglama"),
                (r"from\s+structlog\s+import\s+(.+)", r"from loglama import \1"),
                (r"from\s+structlog\.(\w+)\s+import\s+(.+)", r"from loglama.\1 import \2"),
            ],
            "config": [
                (r"structlog\.configure\((.*)\)", self._replace_configure),
                (r"structlog\.get_logger\(([^\)]*)\)", r"loglama.get_logger(\1)"),
                (r"structlog\.stdlib\.BoundLogger", r"loglama.LogContext"),
                (r"structlog\.processors\.(\w+)\(([^\)]*)\)", self._replace_processor),
            ],
            "context": [
                (r"(\w+)\.bind\(([^\)]*)\)", r"LogContext(\2)"),
                (r"(\w+)\.new\(([^\)]*)\)", r"LogContext(\2)"),
            ],
        }
    
    def _replace_configure(self, match):
        """Replace structlog.configure() with loglama configuration."""
        args = match.group(1)
        
        # This is a complex conversion that might need manual adjustment
        return f"# LogLama uses setup_logging() instead of configure()\n# The following line was converted from structlog:\n# structlog.configure({args})\n# You may need to adjust the parameters manually"
    
    def _replace_processor(self, match):
        """Replace structlog processors with LogLama equivalents."""
        processor_name = match.group(1)
        args = match.group(2)
        
        # Map structlog processors to LogLama equivalents
        processor_map = {
            "TimeStamper": "# LogLama automatically adds timestamps",
            "JSONRenderer": "# Use json_format=True in setup_logging() for JSON output",
            "ConsoleRenderer": "# LogLama has built-in console rendering",
            "format_exc_info": "# LogLama automatically formats exception info",
            "UnicodeDecoder": "# LogLama handles Unicode automatically",
            "add_log_level": "# LogLama automatically adds log levels",
        }
        
        if processor_name in processor_map:
            return processor_map[processor_name]
        else:
            return f"# LogLama doesn't have a direct equivalent for this structlog processor:\n# structlog.processors.{processor_name}({args})"
    
    def migrate_content(self, content: str, file_path: Path, report: MigrationReport, verbose: bool) -> str:
        """Migrate structlog references in the content."""
        original_content = content
        
        # First add the import for LogContext if we're going to use it
        if ".bind(" in content or ".new(" in content or "BoundLogger" in content:
            if "from loglama import LogContext" not in content and "import loglama" not in content:
                if "import structlog" in content:
                    content = content.replace("import structlog", "import loglama\nfrom loglama import LogContext")
                elif "from structlog import" in content:
                    # Find the first from structlog import line
                    match = re.search(r"from\s+structlog\s+import\s+(.+)", content)
                    if match:
                        old_import = match.group(0)
                        new_import = f"{old_import}\nfrom loglama import LogContext"
                        content = content.replace(old_import, new_import)
        
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
        
        return content
    
    def get_renamed_file(self, file_name: str) -> str:
        """Get the new name for a file."""
        if re.search(r"structlog[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        elif re.search(r"log[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        return file_name
    
    def get_renamed_directory(self, dir_name: str) -> str:
        """Get the new name for a directory."""
        if dir_name.lower() == "structlog":
            return "logging"
        return dir_name
    
    def create_loglama_config(self, base_path: Path, report: MigrationReport, report_only: bool, verbose: bool):
        """Create LogLama configuration files based on existing logging configuration."""
        # Look for existing logging configuration files
        config_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if re.search(r"structlog[_\-]?config\.py", file, re.IGNORECASE) or \
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
        return '''\
#!/usr/bin/env python3

"""
Logging configuration for the application.

This module initializes LogLama and provides functions for getting loggers.
"""

import os
import sys
from pathlib import Path

# Try to import LogLama, with fallback to structlog
try:
    from loglama import setup_logging, get_logger, LogContext
    from loglama.config.env_loader import load_env, get_env
    from loglama.formatters import ColoredFormatter, JSONFormatter
    from loglama.handlers import SQLiteHandler, EnhancedRotatingFileHandler
    LOGLAMA_AVAILABLE = True
except ImportError:
    import structlog
    import logging
    LOGLAMA_AVAILABLE = False
    print("LogLama not available, falling back to structlog")


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
        
        # Create log directory if it doesn\'t exist
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
        # Fallback to structlog
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )
        
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logger = structlog.get_logger("app")
        logger.info("Logging initialized with structlog")
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
        return structlog.get_logger(name)
'''
