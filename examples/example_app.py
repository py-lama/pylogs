#!/usr/bin/env python3

"""
LogLama Example Application

This example demonstrates how to use LogLama in a real-world application.
It includes examples of different logging levels, context, and handlers.
"""

import os
import sys
import time
import random
import argparse
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import LogLama components
from loglama.config.env_loader import load_env, get_env
from loglama.core.logger import setup_logging, get_logger
from loglama.utils.context import LogContext, capture_context


@capture_context(operation="process_item")
def process_item(item_id, data):
    """Process an item with context tracking."""
    logger = get_logger("example.processor")
    logger.info(f"Processing item {item_id}", extra={"item_id": item_id})
    
    try:
        # Simulate processing
        time.sleep(0.1)
        
        if random.random() < 0.2:  # 20% chance of warning
            logger.warning(f"Item {item_id} has unusual data", extra={"item_id": item_id, "data": data})
        
        if random.random() < 0.1:  # 10% chance of error
            raise ValueError(f"Invalid data format for item {item_id}")
        
        logger.info(f"Successfully processed item {item_id}", extra={"item_id": item_id})
        return True
    except Exception as e:
        logger.exception(f"Error processing item {item_id}: {str(e)}", extra={"item_id": item_id})
        return False


def simulate_request(request_id, user_id):
    """Simulate a user request with context."""
    logger = get_logger("example.api")
    
    with LogContext(request_id=request_id, user_id=user_id):
        logger.info(f"Received request {request_id} from user {user_id}")
        
        # Process multiple items in this request
        items_count = random.randint(1, 5)
        success_count = 0
        
        for i in range(items_count):
            item_id = f"{request_id}-{i}"
            data = {"value": random.randint(1, 100)}
            
            if process_item(item_id, data):
                success_count += 1
        
        logger.info(
            f"Request {request_id} completed with {success_count}/{items_count} successful items",
            extra={"success_rate": success_count/items_count if items_count > 0 else 0}
        )


def main():
    """Main function to run the example application."""
    parser = argparse.ArgumentParser(description="LogLama Example Application")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests to simulate")
    parser.add_argument("--log-dir", help="Directory for log files")
    parser.add_argument("--db-path", help="Path to SQLite database for logs")
    parser.add_argument("--json", action="store_true", help="Use JSON format for logs")
    parser.add_argument("--structured", action="store_true", help="Use structured logging")
    args = parser.parse_args()
    
    # Load environment variables
    load_env(verbose=True)
    
    # Set up logging configuration
    log_dir = args.log_dir or get_env("LOGLAMA_LOG_DIR", "./logs")
    db_path = args.db_path or get_env("LOGLAMA_DB_PATH", os.path.join(log_dir, "example.db"))
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Initialize logging
    logger = setup_logging(
        name="example",
        level="DEBUG",
        console=True,
        file=True,
        file_path=os.path.join(log_dir, "example.log"),
        database=True,
        db_path=db_path,
        json=args.json,
        structured=args.structured,
        context_filter=True
    )
    
    logger.info("Starting LogLama Example Application")
    
    # Simulate user requests
    for i in range(args.requests):
        request_id = f"req-{i+1:04d}"
        user_id = f"user-{random.randint(1, 10):02d}"
        
        simulate_request(request_id, user_id)
        
        # Small delay between requests
        time.sleep(0.2)
    
    logger.info(f"Completed {args.requests} simulated requests")
    logger.info(f"Logs are available in:\n- File: {os.path.join(log_dir, 'example.log')}\n- Database: {db_path}")
    logger.info("You can view the logs using the LogLama web interface:\n  python -m loglama.cli.web_viewer --db " + db_path)


if __name__ == "__main__":
    main()
