#!/usr/bin/env python3
"""
Simplified Python example using LogLama's new simple logger interface.

This example demonstrates how to use the simplified logging interface
with automatic context capture and decorators.
"""

import os
import random
import sys
import time
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the simplified logger interface
from loglama.core.simple_logger import (
    info, debug, warning, error, exception,
    timed, logged, configure_db_logging, configure_web_logging, set_global_context
)

# Configure database logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")
os.makedirs(log_dir, exist_ok=True)
db_path = os.path.join(log_dir, "simple_example.db")
configure_db_logging(db_path)

# Set some global context that will be included in all log messages
set_global_context(
    application="simple_example",
    version="1.0.0",
    environment="development"
)

# Example function with the @timed decorator
@timed
def process_data(data):
    """Process some data and return the result."""
    info(f"Processing data with {len(data)} items")
    
    result = {}
    for item in data:
        # Simulate some processing time
        time.sleep(0.1)
        
        try:
            # 10% chance of an error
            if random.random() < 0.1:
                raise ValueError(f"Error processing item {item}")
                
            # Process the item
            result[item] = len(str(item)) * 2
            debug(f"Processed item {item}", item_value=item, result_value=result[item])
            
        except Exception as e:
            error(f"Failed to process item {item}", item_value=item, error_type=type(e).__name__)
    
    info(f"Completed processing {len(data)} items with {len(result)} successes")
    return result


# Example function with the @logged decorator
@logged(log_args=True, log_result=True, comment="Example calculation function")
def calculate_value(x, y, operation="add"):
    """Perform a calculation based on the specified operation."""
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        return x / y
    else:
        raise ValueError(f"Unknown operation: {operation}")


# Example function with both decorators
@timed
@logged(level="debug")
def generate_report(data):
    """Generate a report from the data."""
    info("Generating report")
    
    # Simulate report generation
    time.sleep(0.5)
    
    report = {
        "total_items": len(data),
        "average_value": sum(data.values()) / len(data) if data else 0,
        "max_value": max(data.values()) if data else 0,
        "min_value": min(data.values()) if data else 0
    }
    
    info("Report generated", report_stats=report)
    return report


def main():
    """Main function to demonstrate the simplified logging interface."""
    info("Starting simplified LogLama example")
    
    try:
        # Generate some test data
        data = {f"item-{i}": random.randint(1, 100) for i in range(10)}
        info("Generated test data", data_size=len(data))
        
        # Process the data
        processed_data = process_data(data.keys())
        
        # Perform some calculations
        calculate_value(10, 5, "add")
        calculate_value(10, 5, "subtract")
        calculate_value(10, 5, "multiply")
        
        try:
            # This will cause an exception
            calculate_value(10, 0, "divide")
        except Exception as e:
            exception("Error in calculation", operation="divide")
        
        # Generate a report
        report = generate_report(processed_data)
        
        # Print information about accessing the logs
        print("\nExample completed successfully!")
        print(f"Logs are stored in the database: {db_path}")
        print("You can view the logs using the LogLama web interface:")
        print(f"  python -m loglama.cli.main web --db {db_path}")
        
        # Optionally start the web interface
        if "--web" in sys.argv:
            web_host = "127.0.0.1"
            web_port = 8082
            configure_web_logging(web_host, web_port)
            print(f"\nStarting web interface at http://{web_host}:{web_port}...")
            os.system(f"python -m loglama.cli.main web --host {web_host} --port {web_port} --db {db_path}")
    
    except Exception as e:
        exception("Unhandled exception in main")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
