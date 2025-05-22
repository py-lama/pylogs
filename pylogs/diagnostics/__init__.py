# pylogs/diagnostics/__init__.py

"""Diagnostics module for PyLogs."""

from .health import (
    check_system_health,
    verify_logging_setup,
    diagnose_context_issues,
    check_database_connection,
    check_file_permissions
)

from .troubleshoot import (
    troubleshoot_logging,
    troubleshoot_context,
    troubleshoot_database,
    generate_diagnostic_report
)

__all__ = [
    "check_system_health",
    "verify_logging_setup",
    "diagnose_context_issues",
    "check_database_connection",
    "check_file_permissions",
    "troubleshoot_logging",
    "troubleshoot_context",
    "troubleshoot_database",
    "generate_diagnostic_report"
]
