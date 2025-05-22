#!/usr/bin/env python3
"""
Advanced logging system for the PyLama ecosystem.

This module provides enhanced logging capabilities with support for:
- Multiple output formats (console, file, database, web)
- Log levels with rich formatting
- Context-aware logging
- Integration with SQLite for persistent storage
- Structured logging with structlog
"""

import os
import sys
import time
import json
import logging
import threading
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, cast

# Import structlog for structured logging
import structlog

# Try to import rich for enhanced console output
try:
    import rich
    from rich.console import Console
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import environment loader
from pylogs.config.env_loader import get_env, load_env

# Import the context utilities
from pylogs.utils.context import LogContext, _context_storage

# Ensure environment variables are loaded
load_env(verbose=False)

# Default configuration from environment variables
DEFAULT_LOG_LEVEL = get_env("PYLOGS_LEVEL", "INFO")
DEFAULT_LOG_FORMAT = get_env("PYLOGS_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
DEFAULT_DATE_FORMAT = get_env("PYLOGS_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
DEFAULT_LOG_DIR = get_env("PYLOGS_DIR", "logs")
DEFAULT_DB_PATH = get_env("PYLOGS_DB_PATH", "pylogs.db")
DEFAULT_STRUCTURED = get_env("PYLOGS_STRUCTURED", False, as_type=bool)

# Create a thread local storage for context information
thread_local = threading.local()

# Map string log levels to their numeric values
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class ContextFilter(logging.Filter):
    """Filter that adds context information to log records."""
    
    def filter(self, record):
        """Add context information to the log record."""
        # Get context from LogContext
        context = LogContext.get_context()
        
        # Add context to record as a dictionary
        record.context = context
        
        # Also add each context item as an attribute on the record
        for key, value in context.items():
            setattr(record, key, value)
        
        # Add process and thread information
        record.process_name = f"Process-{os.getpid()}"
        record.thread_name = threading.current_thread().name
        
        return True


class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON strings after gathering all the log record info."""
    
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "process": record.process,
            "process_name": getattr(record, "process_name", "unknown"),
            "thread": record.thread,
            "thread_name": getattr(record, "thread_name", "unknown"),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add context info if available
        if hasattr(record, "context") and record.context:
            try:
                if isinstance(record.context, str):
                    context = json.loads(record.context)
                else:
                    context = record.context
                # Include context directly in the log data
                log_data.update(context)
                # Also include it as a separate field
                log_data["context"] = context
            except (json.JSONDecodeError, TypeError):
                log_data["context"] = str(record.context)
        
        # Add all other attributes from the record
        for key, value in record.__dict__.items():
            if key not in [
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread", "threadName",
                "context", "process_name", "thread_name"
            ] and not key.startswith("_"):
                log_data[key] = value
                
        return json.dumps(log_data)


def _configure_structlog():
    """Configure structlog for structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def setup_logging(
    name: Optional[str] = None,
    level: Optional[Union[str, int]] = None,
    console: bool = True,
    file: bool = False,
    file_path: Optional[Union[str, Path]] = None,
    database: bool = False,
    db_path: Optional[Union[str, Path]] = None,
    json_format: bool = False,
    json: Optional[bool] = None,
    context_filter: bool = False,
    rich_logging: Optional[bool] = None,
    structured: Optional[bool] = None,
) -> Union[logging.Logger, structlog.BoundLogger]:
    """
    Set up logging with the specified configuration.
    
    Args:
        name: Logger name (default: root logger)
        level: Log level (default: from environment or INFO)
        console: Whether to log to console (default: True)
        file: Whether to log to a file (default: False)
        file_path: Path to log file (default: None)
        database: Whether to log to database (default: False)
        db_path: Path to SQLite database (default: None)
        json_format: Whether to use JSON formatting (default: False)
        json: Alias for json_format
        context_filter: Whether to add the context filter (default: False)
        rich_logging: Whether to use rich formatting (default: auto-detect)
        structured: Whether to use structlog for structured logging (default: from environment)
        
    Returns:
        Logger object configured according to the specified parameters
    """
    # Handle json alias
    if json is not None:
        json_format = json
        
    # Determine whether to use structured logging
    if structured is None:
        structured = DEFAULT_STRUCTURED
    
    # Configure structlog if using structured logging
    if structured:
        _configure_structlog()
        
        # Get a structlog logger
        if name is None:
            # Use the calling module's name if not provided
            frame = sys._getframe(1)
            name = frame.f_globals.get("__name__", "root")
            
        # Set the log level for the stdlib logger that structlog uses
        if level is None:
            level = DEFAULT_LOG_LEVEL
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), logging.INFO)
            
        # Get the standard library logger that structlog will use
        stdlib_logger = logging.getLogger(name)
        stdlib_logger.setLevel(level)
        
        # Clear any existing handlers
        for handler in stdlib_logger.handlers[:]:
            stdlib_logger.removeHandler(handler)
        
        # Add console handler if requested
        if console:
            if rich_logging is None:
                rich_logging = RICH_AVAILABLE
                
            if rich_logging and RICH_AVAILABLE:
                console_handler = RichHandler(rich_tracebacks=True)
            else:
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
                console_handler.setFormatter(formatter)
                
            stdlib_logger.addHandler(console_handler)
        
        # Add file handler if requested
        if file:
            # Ensure the log directory exists
            if file_path is None:
                log_dir = DEFAULT_LOG_DIR
            else:
                log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            if file_path is None:
                file_path = os.path.join(log_dir, f"{name}.log")
            file_handler = logging.FileHandler(file_path)
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
            file_handler.setFormatter(formatter)
            stdlib_logger.addHandler(file_handler)
        
        # Add database handler if requested
        if database:
            # Import here to avoid circular imports
            try:
                from pylogs.handlers.sqlite_handler import SQLiteHandler
                if db_path is None:
                    db_path = DEFAULT_DB_PATH
                db_handler = SQLiteHandler(db_path)
                stdlib_logger.addHandler(db_handler)
            except ImportError:
                print("SQLite handler not available. Install pylogs[db] for database support.")
        
        # Return a structlog logger that wraps the stdlib logger
        return structlog.get_logger(name)
    else:
        # Use standard library logging
        # Get the logger
        logger = logging.getLogger(name)
        
        # Clear any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Set the log level
        if level is None:
            level = DEFAULT_LOG_LEVEL
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # Add the context filter if requested
        if context_filter:
            logger.addFilter(ContextFilter())
        
        # Create formatter
        if json_format:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        
        # Add console handler if requested
        if console:
            # Use rich handler if available and requested
            if rich_logging is None:
                rich_logging = RICH_AVAILABLE
                
            if rich_logging and RICH_AVAILABLE:
                console_handler = RichHandler(rich_tracebacks=True)
            else:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                
            logger.addHandler(console_handler)
        
        # Add file handler if requested
        if file:
            # Ensure the log directory exists
            if file_path is None:
                log_dir = DEFAULT_LOG_DIR
            else:
                log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            if file_path is None:
                file_path = os.path.join(log_dir, f"{name}.log")
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Add database handler if requested
        if database:
            # Import here to avoid circular imports
            try:
                from pylogs.handlers.sqlite_handler import SQLiteHandler
                if db_path is None:
                    db_path = DEFAULT_DB_PATH
                db_handler = SQLiteHandler(db_path)
                logger.addHandler(db_handler)
            except ImportError:
                print("SQLite handler not available. Install pylogs[db] for database support.")
        
        return logger


def get_logger(
    name: Optional[str] = None,
    **kwargs
) -> Union[logging.Logger, structlog.BoundLogger]:
    """
    Get a logger with the specified name and configuration.
    
    This is the main entry point for getting a logger in the PyLama ecosystem.
    
    Args:
        name: Logger name (default: calling module name)
        **kwargs: Additional configuration parameters for setup_logging
        
    Returns:
        Configured logger object
    """
    # If name is not provided, use the calling module's name
    if name is None:
        frame = sys._getframe(1)
        name = frame.f_globals.get("__name__", "")
    
    return setup_logging(name, **kwargs)


def set_context(**kwargs) -> None:
    """
    Set context information for the current thread.
    
    Args:
        **kwargs: Context information to add to log records
    """
    LogContext.update_context(**kwargs)


def clear_context() -> None:
    """Clear context information for the current thread."""
    LogContext.clear_context()


def with_context(func: Optional[Callable] = None, **context_kwargs):
    """
    Decorator to add context information to all log records within a function.
    
    Can be used as @with_context or @with_context(param1="value1", param2="value2")
    
    Args:
        func: Function to decorate
        **context_kwargs: Context information to add to log records
        
    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Use LogContext as a context manager
            with LogContext(**context_kwargs):
                return f(*args, **kwargs)
        return wrapper
    
    # Handle both @with_context and @with_context(param="value") forms
    if func is None:
        return decorator
    return decorator(func)


def log_execution_time(logger: Optional[Union[logging.Logger, structlog.BoundLogger]] = None, level: str = "INFO"):
    """
    Decorator to log the execution time of a function.
    
    Args:
        logger: Logger to use (default: get a new logger with the function's module name)
        level: Log level to use (default: INFO)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the logger
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)
            
            # Get the log level
            log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
            
            # Log the start of the function
            if isinstance(logger, structlog.BoundLogger):
                # structlog logger
                log_method = getattr(logger, level.lower(), logger.info)
                log_method(f"Starting {func.__name__}")
            else:
                # standard logger
                logger.log(log_level, f"Starting {func.__name__}")
            
            # Record the start time
            start_time = time.time()
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                
                # Calculate the execution time
                execution_time = time.time() - start_time
                
                # Log the end of the function
                if isinstance(logger, structlog.BoundLogger):
                    # structlog logger
                    log_method(f"Finished {func.__name__}", duration_seconds=execution_time)
                else:
                    # standard logger
                    logger.log(log_level, f"Finished {func.__name__} in {execution_time:.4f} seconds")
                
                return result
            except Exception as e:
                # Calculate the execution time
                execution_time = time.time() - start_time
                
                # Log the exception
                if isinstance(logger, structlog.BoundLogger):
                    # structlog logger
                    logger.exception(f"Exception in {func.__name__}", 
                                    duration_seconds=execution_time, 
                                    error=str(e))
                else:
                    # standard logger
                    logger.exception(f"Exception in {func.__name__} after {execution_time:.4f} seconds: {str(e)}")
                
                # Re-raise the exception
                raise
        return wrapper
    return decorator


# Initialize the default logger
default_logger = get_logger("pylogs")
