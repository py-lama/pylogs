#!/usr/bin/env python3

"""
Migrator for Loguru.

This migrator converts code using Loguru to use LogLama instead.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union

from .base_migrator import BaseMigrator, MigrationReport


class LoguruMigrator(BaseMigrator):
    """Migrator for Loguru."""
    
    def __init__(self):
        super().__init__()
        self.name = "loguru"
        self.file_patterns = [r"loguru[_\-]?config\.py", r"log[_\-]?config\.py"]
        self.dir_patterns = [r"loguru"]
        
        # Patterns to find and replace
        self.patterns = {
            "imports": [
                (r"import\s+loguru", "import loglama"),
                (r"from\s+loguru\s+import\s+(.+)", r"from loglama import \1"),
                (r"from\s+loguru\s+import\s+logger\s*", "from loglama import get_logger\n\nlogger = get_logger(__name__)"),
            ],
            "config": [
                (r"logger\.configure\((.*)\)", self._replace_configure),
                (r"logger\.add\(([^\)]*)\)", self._replace_add),
                (r"logger\.remove\(([^\)]*)\)", r"# LogLama handles handler removal differently\n# The following line was converted from loguru:\n# logger.remove(\1)"),
                (r"logger\.level\(([^\)]*)\)", r"logger.set_level(\1)"),
            ],
            "logging": [
                (r"logger\.debug\(([^\)]*)\)", r"logger.debug(\1)"),
                (r"logger\.info\(([^\)]*)\)", r"logger.info(\1)"),
                (r"logger\.warning\(([^\)]*)\)", r"logger.warning(\1)"),
                (r"logger\.error\(([^\)]*)\)", r"logger.error(\1)"),
                (r"logger\.critical\(([^\)]*)\)", r"logger.critical(\1)"),
                (r"logger\.exception\(([^\)]*)\)", r"logger.exception(\1)"),
                (r"logger\.log\(([^\)]*)\)", r"logger.log(\1)"),
                (r"logger\.trace\(([^\)]*)\)", r"logger.debug(\1)  # LogLama doesn't have trace, using debug instead"),
                (r"logger\.success\(([^\)]*)\)", r"logger.info(\1)  # LogLama doesn't have success, using info instead"),
            ],
            "context": [
                (r"logger\.bind\(([^\)]*)\)", r"LogContext(\1)"),
                (r"with\s+logger\.contextualize\(([^\)]*)\)\s*:", r"with LogContext(\1):"),
            ],
        }
    
    def _replace_configure(self, match):
        """Replace logger.configure() with loglama.setup_logging()."""
        args = match.group(1)
        
        # This is a complex conversion that might need manual adjustment
        return f"# LogLama uses setup_logging() instead of configure()\n# The following line was converted from loguru:\n# logger.configure({args})\n# You may need to adjust the parameters manually"
    
    def _replace_add(self, match):
        """Replace logger.add() with loglama.setup_logging() or handlers."""
        args = match.group(1)
        
        # Try to determine what kind of handler is being added
        if 'sys.stdout' in args or 'sys.stderr' in args:
            return f"# LogLama handles console output in setup_logging()\n# The following line was converted from loguru:\n# logger.add({args})"
        elif '"' in args or "'" in args:  # Likely a file path
            # Extract the file path if possible
            file_path_match = re.search(r'["\'](.*?)["\'](.*)', args)
            if file_path_match:
                file_path = file_path_match.group(1)
                rest_args = file_path_match.group(2)
                return f"# LogLama handles file output in setup_logging()\n# The following line was converted from loguru:\n# logger.add(\"{file_path}\"{rest_args})"
        
        # Default fallback for complex cases
        return f"# LogLama handles handlers differently\n# The following line was converted from loguru:\n# logger.add({args})\n# You may need to adjust this manually"
    
    def migrate_content(self, content: str, file_path: Path, report: MigrationReport, verbose: bool) -> str:
        """Migrate loguru references in the content."""
        original_content = content
        
        # First add the import for LogContext if we're going to use it
        if "logger.bind" in content or "logger.contextualize" in content:
            if "from loglama import LogContext" not in content and "import loglama" not in content:
                if "import loguru" in content:
                    content = content.replace("import loguru", "import loglama\nfrom loglama import LogContext")
                elif "from loguru import" in content:
                    # Find the first from loguru import line
                    match = re.search(r"from\s+loguru\s+import\s+(.+)", content)
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
        if re.search(r"loguru[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        elif re.search(r"log[_\-]?config\.py", file_name, re.IGNORECASE):
            return "logging_config.py"
        return file_name
    
    def get_renamed_directory(self, dir_name: str) -> str:
        """Get the new name for a directory."""
        if dir_name.lower() == "loguru":
            return "logging"
        return dir_name
    
    def create_loglama_config(self, base_path: Path, report: MigrationReport, report_only: bool, verbose: bool):
        """Create LogLama configuration files based on existing logging configuration."""
        # Look for existing logging configuration files
        config_files = []
        for root, _, files in os.walk(base_path):
            for file in files:
                if re.search(r"loguru[_\-]?config\.py", file, re.IGNORECASE) or \
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
        return """
#!/usr/bin/env python3

"""
Logging configuration for the application.

This module initializes LogLama and provides functions for getting loggers.
"""

import os
import sys
from pathlib import Path

# Try to import LogLama, with fallback to loguru
try:
    from loglama import setup_logging, get_logger, LogContext
    from loglama.config.env_loader import load_env, get_env
    from loglama.formatters import ColoredFormatter, JSONFormatter
    from loglama.handlers import SQLiteHandler, EnhancedRotatingFileHandler
    LOGLAMA_AVAILABLE = True
except ImportError:
    from loguru import logger
    LOGLAMA_AVAILABLE = False
    print("LogLama not available, falling back to loguru")


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
        # Fallback to loguru
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(sys.stderr, level="INFO")
        
        # Add file handler
        os.makedirs("./logs", exist_ok=True)
        logger.add("./logs/app.log", rotation="10 MB", retention="1 week")
        
        logger.info("Logging initialized with loguru")
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
        return logger.bind(name=name)
"""
