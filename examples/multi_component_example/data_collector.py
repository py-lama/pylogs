#!/usr/bin/env python3
"""
Data Collector Script

This script demonstrates how to use LogLama for logging in a data collection script.
It simulates collecting data from various sources and saving it to files.
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# Add the PyLama root directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import LogLama modules
from loglama.core.logger import get_logger, setup_logging
from loglama.core.env_manager import load_central_env

# Load environment variables from the central .env file
load_central_env()

# Set up logging
setup_logging()

# Get a logger for this script
logger = get_logger("data_collector")


def collect_data_from_source(source_name, num_records=10):
    """Simulate collecting data from a source."""
    logger.info(f"Collecting data from {source_name}", extra={"source": source_name, "records": num_records})
    
    try:
        # Simulate data collection
        data = []
        with logger.time(f"collect_{source_name}"):
            for i in range(num_records):
                # Simulate some processing time
                import time
                time.sleep(0.05)
                
                # Generate a random data point
                data_point = {
                    "id": f"{source_name}_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "value": random.uniform(0, 100),
                    "category": random.choice(["A", "B", "C"]),
                    "source": source_name
                }
                data.append(data_point)
        
        logger.info(f"Successfully collected {len(data)} records from {source_name}")
        return data
    except Exception as e:
        logger.exception(f"Error collecting data from {source_name}")
        return []


def save_data(data, filename):
    """Save collected data to a file."""
    file_path = Path(__file__).parent / "data" / filename
    
    logger.info(f"Saving data to {filename}", extra={"file_path": str(file_path), "record_count": len(data)})
    
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data successfully saved to {filename}")
        return True
    except Exception as e:
        logger.exception(f"Error saving data to {filename}")
        return False


def main():
    """Main function that collects data from multiple sources."""
    logger.info("Starting data collection process")
    
    # Collect data from multiple sources
    sources = ["api", "database", "file_system"]
    all_data = []
    
    for source in sources:
        source_data = collect_data_from_source(source, num_records=random.randint(5, 15))
        all_data.extend(source_data)
    
    # Save the combined data
    if all_data:
        combined_filename = f"combined_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_success = save_data(all_data, combined_filename)
        
        if save_success:
            logger.info("Data collection process completed successfully")
        else:
            logger.error("Data collection process completed with errors")
    else:
        logger.warning("No data collected from any source")


if __name__ == "__main__":
    main()
