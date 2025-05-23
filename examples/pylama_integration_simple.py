#!/usr/bin/env python3
"""
Simplified example of using LogLama with other PyLama components.

This example demonstrates how to use LogLama in a script that interacts with
other PyLama components, with fallbacks for when components aren't available.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import LogLama
sys.path.append(str(Path(__file__).parent.parent.parent))

# Create minimal logging functions if LogLama is not available
def setup_minimal_logging():
    class MinimalLogger:
        def info(self, msg, **kwargs): print(f"[INFO] {msg}")
        def warning(self, msg, **kwargs): print(f"[WARNING] {msg}")
        def error(self, msg, **kwargs): print(f"[ERROR] {msg}")
        def debug(self, msg, **kwargs): print(f"[DEBUG] {msg}")
    return MinimalLogger()

# Try to import LogLama
try:
    # Try importing from installed package first
    from loglama.logger import setup_logging, get_logger
    
    # Set up logging
    setup_logging(name="pylama_integration", level="DEBUG", db_logging=True)
    logger = get_logger("pylama_integration")
except ImportError:
    try:
        # Try importing from core module
        from loglama.core.logger import setup_logging, get_logger
        
        # Set up logging
        setup_logging(name="pylama_integration", level="DEBUG", db_logging=True)
        logger = get_logger("pylama_integration")
    except ImportError:
        # Use minimal logging if LogLama is not available
        logger = setup_minimal_logging()

# Simplified environment management
def load_central_env():
    logger.info("Loading central environment variables")
    # In a real application, this would load from a central .env file
    return True

def ensure_required_env_vars():
    logger.info("Ensuring required environment variables are set")
    # In a real application, this would check for required variables
    return True

def get_project_path():
    logger.info("Getting project path")
    return Path(__file__).parent.parent.parent

def check_dependencies(component_name):
    logger.info(f"Checking dependencies for {component_name}")
    # In a real application, this would check if dependencies are installed
    return True

# Load environment variables
load_central_env()
ensure_required_env_vars()

def check_dependencies():
    """Check dependencies for PyLLM and PyBox."""
    logger.info("Checking PyLama component dependencies")
    
    # Check PyLLM dependencies
    logger.info("Checking PyLLM dependencies")
    pyllm_ok = check_dependencies("pyllm")
    if pyllm_ok:
        logger.info("PyLLM dependencies OK")
    else:
        logger.warning("PyLLM dependencies missing")
    
    # Check PyBox dependencies
    logger.info("Checking PyBox dependencies")
    pybox_ok = check_dependencies("pybox")
    if pybox_ok:
        logger.info("PyBox dependencies OK")
    else:
        logger.warning("PyBox dependencies missing")
    
    return pyllm_ok and pybox_ok

def import_pyllm():
    """Simulate importing PyLLM modules."""
    logger.info("Importing PyLLM modules")
    
    try:
        # In a real application, this would import actual PyLLM modules
        # from pyllm.model import load_model
        # from pyllm.generation import generate_text
        
        logger.info("PyLLM modules imported successfully")
        return True
    except ImportError as e:
        logger.error(f"Error importing PyLLM modules: {e}")
        return False

def main():
    """Main function that demonstrates LogLama integration with PyLama components."""
    logger.info("Starting PyLama integration example")
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        logger.warning("Some dependencies are missing, but continuing anyway")
    
    # Import PyLLM modules
    pyllm_ok = import_pyllm()
    if not pyllm_ok:
        logger.warning("Could not import PyLLM modules, using fallback")
    
    # Simulate some work
    logger.info("Processing data...")
    for i in range(3):
        logger.debug(f"Processing step {i+1}/3")
        time.sleep(0.1)  # Short sleep to simulate work
    
    # Log success
    logger.info("PyLama integration example completed successfully")
    return 0

if __name__ == "__main__":
    exit_code = main()
    print("\nCheck the logs to see the output. You can use the LogLama CLI to view them:")
    print("  loglama logs --app pylama_integration")
    print("  loglama logs --level ERROR")
    sys.exit(exit_code)
