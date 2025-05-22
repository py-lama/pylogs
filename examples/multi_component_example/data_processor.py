#!/usr/bin/env python3
"""
Data Processor Script

This script demonstrates how to use LogLama for logging in a data processing script.
It loads data collected by the data_collector.py script, processes it, and saves the results.
"""

import os
import sys
import json
import glob
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
logger = get_logger("data_processor")


def find_latest_data_file():
    """Find the most recent data file in the data directory."""
    data_dir = Path(__file__).parent / "data"
    data_files = list(data_dir.glob("combined_data_*.json"))
    
    if not data_files:
        logger.error("No data files found")
        return None
    
    # Sort by modification time (most recent first)
    latest_file = max(data_files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found latest data file: {latest_file.name}")
    return latest_file


def load_data(file_path):
    """Load data from a JSON file."""
    logger.info(f"Loading data from {file_path.name}")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded {len(data)} records from {file_path.name}")
        return data
    except Exception as e:
        logger.exception(f"Error loading data from {file_path.name}")
        return []


def process_data(data):
    """Process the data by categorizing and calculating statistics."""
    if not data:
        logger.warning("No data to process")
        return {}
    
    logger.info(f"Processing {len(data)} records", extra={"record_count": len(data)})
    
    try:
        with logger.time("data_processing"):
            # Categorize data by source and category
            categorized = {}
            for item in data:
                source = item.get("source", "unknown")
                category = item.get("category", "unknown")
                
                if source not in categorized:
                    categorized[source] = {}
                
                if category not in categorized[source]:
                    categorized[source][category] = []
                
                categorized[source][category].append(item)
            
            # Calculate statistics for each category
            statistics = {}
            for source, categories in categorized.items():
                statistics[source] = {}
                for category, items in categories.items():
                    values = [item.get("value", 0) for item in items]
                    if values:
                        statistics[source][category] = {
                            "count": len(values),
                            "min": min(values),
                            "max": max(values),
                            "avg": sum(values) / len(values),
                            "sum": sum(values)
                        }
        
        logger.info(f"Data processing completed", extra={"categories": len(statistics)})
        return {
            "categorized": categorized,
            "statistics": statistics
        }
    except Exception as e:
        logger.exception("Error during data processing")
        return {}


def save_processed_data(processed_data, filename):
    """Save processed data to a file."""
    file_path = Path(__file__).parent / "data" / filename
    
    logger.info(f"Saving processed data to {filename}", extra={"file_path": str(file_path)})
    
    try:
        with open(file_path, "w") as f:
            json.dump(processed_data, f, indent=2)
        logger.info(f"Processed data successfully saved to {filename}")
        return True
    except Exception as e:
        logger.exception(f"Error saving processed data to {filename}")
        return False


def main():
    """Main function that processes data from the latest data file."""
    logger.info("Starting data processing")
    
    # Find the latest data file
    latest_file = find_latest_data_file()
    if not latest_file:
        logger.error("Data processing failed: No data file found")
        return False
    
    # Load the data
    data = load_data(latest_file)
    if not data:
        logger.error("Data processing failed: Could not load data")
        return False
    
    # Process the data
    processed_data = process_data(data)
    if not processed_data:
        logger.error("Data processing failed: Processing error")
        return False
    
    # Save the processed data
    processed_filename = f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_success = save_processed_data(processed_data, processed_filename)
    
    if save_success:
        logger.info("Data processing completed successfully")
        return True
    else:
        logger.error("Data processing failed: Could not save processed data")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
