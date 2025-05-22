#!/usr/bin/env python3
"""
Standalone example of using LogLama in a single file.

This example includes all necessary imports and setup to use LogLama in a single file,
making it easy to copy and use in any project. It doesn't require the full PyLama ecosystem
to be installed, just the LogLama package.
"""

import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Try to import the utility module to set up the Python path
try:
    from utils import setup_loglama_path
    setup_loglama_path()
except ImportError:
    # Fallback if utils.py is not available
    current_dir = Path(__file__).parent.absolute()
    py_lama_root = current_dir.parent.parent
    loglama_dir = current_dir.parent
    sys.path.append(str(py_lama_root))
    sys.path.append(str(loglama_dir))

# Try to import LogLama modules
try:
    from loglama.core.logger import get_logger, setup_logging
    from loglama.core.env_manager import load_central_env
    LOGLAMA_AVAILABLE = True
except ImportError:
    LOGLAMA_AVAILABLE = False
    # Fallback logger if LogLama is not available
    def setup_fallback_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    class FallbackLogger:
        def __init__(self, name):
            self.logger = logging.getLogger(name)
        
        def debug(self, msg, **kwargs):
            if kwargs.get('extra'):
                msg = f"{msg} {json.dumps(kwargs['extra'])}"
            self.logger.debug(msg)
        
        def info(self, msg, **kwargs):
            if kwargs.get('extra'):
                msg = f"{msg} {json.dumps(kwargs['extra'])}"
            self.logger.info(msg)
        
        def warning(self, msg, **kwargs):
            if kwargs.get('extra'):
                msg = f"{msg} {json.dumps(kwargs['extra'])}"
            self.logger.warning(msg)
        
        def error(self, msg, **kwargs):
            if kwargs.get('extra'):
                msg = f"{msg} {json.dumps(kwargs['extra'])}"
            self.logger.error(msg)
        
        def exception(self, msg, **kwargs):
            if kwargs.get('extra'):
                msg = f"{msg} {json.dumps(kwargs['extra'])}"
            self.logger.exception(msg)
        
        def time(self, operation_name):
            class TimingContext:
                def __init__(self, logger, operation):
                    self.logger = logger
                    self.operation = operation
                    self.start_time = None
                
                def __enter__(self):
                    self.start_time = datetime.now()
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    end_time = datetime.now()
                    duration = (end_time - self.start_time).total_seconds()
                    self.logger.info(
                        f"Operation '{self.operation}' completed", 
                        extra={"duration_seconds": duration}
                    )
            
            return TimingContext(self, operation_name)
    
    def get_logger(name):
        return FallbackLogger(name)


# Set up logging (either LogLama or fallback)
if LOGLAMA_AVAILABLE:
    # Try to load environment variables from the central .env file
    try:
        load_central_env()
    except Exception:
        pass  # Continue even if central .env can't be loaded
    
    # Set up LogLama logging
    setup_logging()
    print("Using LogLama for logging")
else:
    # Set up fallback logging
    setup_fallback_logging()
    print("LogLama not available, using fallback logger")

# Get a logger for this script
logger = get_logger("standalone_example")


def process_data(data):
    """Process some data and log the results."""
    logger.info(f"Processing data", extra={"data_size": len(data)})
    
    result = {}
    with logger.time("data_processing"):
        # Simulate data processing
        import time
        time.sleep(0.5)
        
        for item in data:
            try:
                result[item] = len(item) * 2
            except Exception as e:
                logger.exception(f"Error processing item: {item}")
    
    logger.info("Data processing completed", extra={"result_size": len(result)})
    return result


def main():
    """Main function that demonstrates standalone LogLama usage."""
    logger.info("Starting standalone example")
    
    # Process some sample data
    sample_data = ["apple", "banana", "cherry", "date"]
    results = process_data(sample_data)
    
    # Log the results
    logger.info("Processing results", extra={"results": results})
    
    # Try to process invalid data
    try:
        invalid_results = process_data([1, 2, 3])
    except Exception as e:
        logger.error(f"Failed to process invalid data: {e}")
    
    logger.info("Standalone example completed")


if __name__ == "__main__":
    main()
    
    if LOGLAMA_AVAILABLE:
        print("\nCheck the logs using the LogLama CLI:")
        print("python -m loglama.cli.main logs")
    else:
        print("\nLogging completed using the fallback logger")
