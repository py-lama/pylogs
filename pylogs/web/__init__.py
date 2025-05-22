"""PyLogs Web Interface.

This module provides a web interface for viewing and querying logs stored in SQLite database.
"""

from pylogs.web.app import create_app

__all__ = ['create_app']
