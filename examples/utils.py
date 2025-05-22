#!/usr/bin/env python3
"""
Utility functions for LogLama examples.

This module provides helper functions for setting up the Python path
and importing LogLama modules in example scripts.
"""

import os
import sys
from pathlib import Path


def setup_loglama_path():
    """
    Set up the Python path to import LogLama modules.
    
    This function adds the necessary directories to sys.path to ensure
    that LogLama modules can be imported in example scripts.
    """
    # Get the current file's directory
    current_dir = Path(__file__).parent.absolute()
    
    # Add the parent directory to the path (py-lama root)
    py_lama_root = current_dir.parent.parent
    if str(py_lama_root) not in sys.path:
        sys.path.append(str(py_lama_root))
    
    # Add the loglama directory to the path
    loglama_dir = current_dir.parent
    if str(loglama_dir) not in sys.path:
        sys.path.append(str(loglama_dir))
    
    # Return the paths that were added
    return {
        "py_lama_root": str(py_lama_root),
        "loglama_dir": str(loglama_dir)
    }
