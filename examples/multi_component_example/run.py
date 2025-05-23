#!/usr/bin/env python3

"""
Runner script for the multi-component example.

This script orchestrates the execution of all components in the workflow:
1. Data Collector
2. Data Processor
3. Model Inference
4. Results Analyzer

All logs are captured by LogLama for centralized logging and monitoring.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the LogLama package to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import LogLama
try:
    # Try importing from installed package first
    from loglama.logger import setup_logging, get_logger
except ImportError:
    try:
        # Try importing from core module
        from loglama.core.logger import setup_logging, get_logger
    except ImportError:
        # Create minimal logging functions if LogLama is not available
        def setup_logging(name="runner", level="INFO", **kwargs):
            return None
            
        def get_logger(name="runner"):
            class MinimalLogger:
                def info(self, msg, **kwargs): print(f"[INFO] {msg}")
                def warning(self, msg, **kwargs): print(f"[WARNING] {msg}")
                def error(self, msg, **kwargs): print(f"[ERROR] {msg}")
                def debug(self, msg, **kwargs): print(f"[DEBUG] {msg}")
            return MinimalLogger()

# Set up logging
setup_logging(name="multi_component_runner", level="INFO", db_logging=True)
logger = get_logger("multi_component_runner")

# Get the directory where this script is located
script_dir = Path(__file__).parent

# Component scripts
components = [
    "data_collector.py",
    "data_processor.py",
    "model_inference.py",
    "results_analyzer.py"
]

def run_component(component_script):
    """
    Run a component script and return its success status.
    """
    script_path = script_dir / component_script
    if not script_path.exists():
        logger.error(f"Component script not found: {component_script}")
        return False
    
    logger.info(f"Running component: {component_script}")
    try:
        # Run the component with a timeout of 5 seconds
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.info(f"Component completed successfully: {component_script}")
            return True
        else:
            logger.error(f"Component failed: {component_script}")
            logger.error(f"Error output: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning(f"Component timed out: {component_script}")
        return False
    except Exception as e:
        logger.error(f"Error running component {component_script}: {e}")
        return False

def main():
    """
    Run all components in sequence.
    """
    logger.info("Starting multi-component workflow")
    
    success_count = 0
    for component in components:
        if run_component(component):
            success_count += 1
    
    logger.info(f"Workflow completed: {success_count}/{len(components)} components succeeded")
    
    if success_count == len(components):
        logger.info("All components completed successfully!")
        return 0
    else:
        logger.warning(f"Some components failed: {len(components) - success_count} failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())
