# loglama/diagnostics/troubleshoot.py

"""Troubleshooting functions for LogLama."""

import os
import sys
import json
import time
import sqlite3
import logging
import platform
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

from ..core.logger import get_logger, setup_logging
from ..utils.context import LogContext
from ..handlers.sqlite_handler import SQLiteHandler
from .health import (
    check_system_health,
    verify_logging_setup,
    diagnose_context_issues,
    check_database_connection,
    check_file_permissions
)

# Create a logger for the troubleshooting module
trouble_logger = get_logger("loglama.troubleshoot")


def troubleshoot_logging(log_dir: Optional[str] = None, 
                        log_level: str = "INFO") -> Dict[str, Any]:
    """Troubleshoot logging issues by running a series of tests.
    
    Args:
        log_dir: Optional directory for log files
        log_level: Log level to use for tests
        
    Returns:
        Dict[str, Any]: Troubleshooting results
    """
    results = {
        "status": "success",
        "tests": [],
        "issues": [],
        "fixes_applied": []
    }
    
    # If no log_dir provided, create a temporary one
    temp_dir = None
    if not log_dir:
        temp_dir = tempfile.TemporaryDirectory()
        log_dir = temp_dir.name
    
    try:
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Test 1: Basic file logging
        test_file = os.path.join(log_dir, "test_basic.log")
        try:
            logger = setup_logging(
                name="test_basic",
                level=log_level,
                console=False,
                file=True,
                file_path=test_file
            )
            
            logger.info("Basic logging test")
            
            # Check if file exists and contains message
            if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                with open(test_file, "r") as f:
                    content = f.read()
                    if "Basic logging test" in content:
                        results["tests"].append({
                            "name": "Basic file logging",
                            "status": "pass"
                        })
                    else:
                        results["tests"].append({
                            "name": "Basic file logging",
                            "status": "fail",
                            "reason": "Message not found in log file"
                        })
                        results["issues"].append("File handler not writing messages correctly")
            else:
                results["tests"].append({
                    "name": "Basic file logging",
                    "status": "fail",
                    "reason": "Log file not created or empty"
                })
                results["issues"].append("File handler not creating log file")
                
                # Try to fix by ensuring directory permissions
                os.chmod(log_dir, 0o755)
                results["fixes_applied"].append("Updated log directory permissions")
        except Exception as e:
            results["tests"].append({
                "name": "Basic file logging",
                "status": "error",
                "reason": str(e)
            })
            results["issues"].append(f"Basic logging error: {str(e)}")
        
        # Test 2: JSON formatting
        test_json_file = os.path.join(log_dir, "test_json.log")
        try:
            json_logger = setup_logging(
                name="test_json",
                level=log_level,
                console=False,
                file=True,
                file_path=test_json_file,
                json=True
            )
            
            json_logger.info("JSON formatting test")
            
            # Check if file exists and contains valid JSON
            if os.path.exists(test_json_file) and os.path.getsize(test_json_file) > 0:
                with open(test_json_file, "r") as f:
                    line = f.readline().strip()
                    try:
                        log_entry = json.loads(line)
                        if log_entry.get("message") == "JSON formatting test":
                            results["tests"].append({
                                "name": "JSON formatting",
                                "status": "pass"
                            })
                        else:
                            results["tests"].append({
                                "name": "JSON formatting",
                                "status": "fail",
                                "reason": "Message not found in JSON"
                            })
                            results["issues"].append("JSON formatter not including message")
                    except json.JSONDecodeError:
                        results["tests"].append({
                            "name": "JSON formatting",
                            "status": "fail",
                            "reason": "Invalid JSON format"
                        })
                        results["issues"].append("JSON formatter producing invalid JSON")
            else:
                results["tests"].append({
                    "name": "JSON formatting",
                    "status": "fail",
                    "reason": "JSON log file not created or empty"
                })
                results["issues"].append("JSON file handler not working")
        except Exception as e:
            results["tests"].append({
                "name": "JSON formatting",
                "status": "error",
                "reason": str(e)
            })
            results["issues"].append(f"JSON logging error: {str(e)}")
        
        # Test 3: Multiple handlers
        test_multi_file = os.path.join(log_dir, "test_multi.log")
        test_multi_db = os.path.join(log_dir, "test_multi.db")
        try:
            multi_logger = setup_logging(
                name="test_multi",
                level=log_level,
                console=True,
                file=True,
                file_path=test_multi_file,
                database=True,
                db_path=test_multi_db,
                json=True
            )
            
            multi_logger.info("Multiple handlers test")
            
            # Check if both file and database were updated
            file_ok = False
            db_ok = False
            
            if os.path.exists(test_multi_file) and os.path.getsize(test_multi_file) > 0:
                with open(test_multi_file, "r") as f:
                    content = f.read()
                    if "Multiple handlers test" in content:
                        file_ok = True
            
            if os.path.exists(test_multi_db):
                try:
                    conn = sqlite3.connect(test_multi_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM logs WHERE message = ?", ("Multiple handlers test",))
                    if cursor.fetchone():
                        db_ok = True
                    conn.close()
                except Exception:
                    pass
            
            if file_ok and db_ok:
                results["tests"].append({
                    "name": "Multiple handlers",
                    "status": "pass"
                })
            else:
                results["tests"].append({
                    "name": "Multiple handlers",
                    "status": "fail",
                    "reason": f"File handler: {'OK' if file_ok else 'Failed'}, DB handler: {'OK' if db_ok else 'Failed'}"
                })
                if not file_ok:
                    results["issues"].append("File handler not working with multiple handlers")
                if not db_ok:
                    results["issues"].append("Database handler not working with multiple handlers")
        except Exception as e:
            results["tests"].append({
                "name": "Multiple handlers",
                "status": "error",
                "reason": str(e)
            })
            results["issues"].append(f"Multiple handlers error: {str(e)}")
    
    except Exception as e:
        results["status"] = "error"
        results["issues"].append(f"General troubleshooting error: {str(e)}")
    
    # Clean up if using temporary directory
    if temp_dir:
        temp_dir.cleanup()
    
    # Update overall status
    if any(test["status"] == "fail" or test["status"] == "error" for test in results["tests"]):
        results["status"] = "failed"
    
    return results


def troubleshoot_context(log_dir: Optional[str] = None) -> Dict[str, Any]:
    """Troubleshoot context handling issues.
    
    Args:
        log_dir: Optional directory for log files
        
    Returns:
        Dict[str, Any]: Troubleshooting results
    """
    results = {
        "status": "success",
        "tests": [],
        "issues": [],
        "fixes_applied": []
    }
    
    # If no log_dir provided, create a temporary one
    temp_dir = None
    if not log_dir:
        temp_dir = tempfile.TemporaryDirectory()
        log_dir = temp_dir.name
    
    try:
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Test 1: Basic context with LogContext
        test_context_file = os.path.join(log_dir, "test_context.log")
        test_context_db = os.path.join(log_dir, "test_context.db")
        try:
            context_logger = setup_logging(
                name="test_context",
                level="INFO",
                console=False,
                file=True,
                file_path=test_context_file,
                database=True,
                db_path=test_context_db,
                json=True,
                context_filter=True
            )
            
            with LogContext(user="test_user", request_id="test123"):
                context_logger.info("Context test message")
            
            # Check if context was added to log file
            file_context_ok = False
            if os.path.exists(test_context_file) and os.path.getsize(test_context_file) > 0:
                with open(test_context_file, "r") as f:
                    content = f.read()
                    if "test_user" in content and "test123" in content:
                        file_context_ok = True
            
            # Check if context was added to database
            db_context_ok = False
            if os.path.exists(test_context_db):
                try:
                    conn = sqlite3.connect(test_context_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT context FROM logs WHERE message = ?", ("Context test message",))
                    row = cursor.fetchone()
                    if row:
                        context = json.loads(row[0])
                        if context.get("user") == "test_user" and context.get("request_id") == "test123":
                            db_context_ok = True
                    conn.close()
                except Exception:
                    pass
            
            if file_context_ok and db_context_ok:
                results["tests"].append({
                    "name": "Basic context handling",
                    "status": "pass"
                })
            else:
                results["tests"].append({
                    "name": "Basic context handling",
                    "status": "fail",
                    "reason": f"File context: {'OK' if file_context_ok else 'Failed'}, DB context: {'OK' if db_context_ok else 'Failed'}"
                })
                if not file_context_ok:
                    results["issues"].append("Context not added to log file")
                if not db_context_ok:
                    results["issues"].append("Context not added to database")
        except Exception as e:
            results["tests"].append({
                "name": "Basic context handling",
                "status": "error",
                "reason": str(e)
            })
            results["issues"].append(f"Context handling error: {str(e)}")
        
        # Test 2: Nested context
        test_nested_file = os.path.join(log_dir, "test_nested.log")
        try:
            nested_logger = setup_logging(
                name="test_nested",
                level="INFO",
                console=False,
                file=True,
                file_path=test_nested_file,
                json=True,
                context_filter=True
            )
            
            with LogContext(outer="outer_value"):
                nested_logger.info("Outer context message")
                with LogContext(inner="inner_value"):
                    nested_logger.info("Nested context message")
                nested_logger.info("Back to outer context")
            
            # Check if nested context was handled correctly
            if os.path.exists(test_nested_file) and os.path.getsize(test_nested_file) > 0:
                with open(test_nested_file, "r") as f:
                    lines = f.readlines()
                    if len(lines) >= 3:
                        try:
                            outer_log = json.loads(lines[0])
                            nested_log = json.loads(lines[1])
                            back_log = json.loads(lines[2])
                            
                            outer_ok = outer_log.get("outer") == "outer_value" and "inner" not in outer_log
                            nested_ok = nested_log.get("outer") == "outer_value" and nested_log.get("inner") == "inner_value"
                            back_ok = back_log.get("outer") == "outer_value" and "inner" not in back_log
                            
                            if outer_ok and nested_ok and back_ok:
                                results["tests"].append({
                                    "name": "Nested context handling",
                                    "status": "pass"
                                })
                            else:
                                results["tests"].append({
                                    "name": "Nested context handling",
                                    "status": "fail",
                                    "reason": "Nested context not handled correctly"
                                })
                                results["issues"].append("LogContext not preserving context stack properly")
                        except (json.JSONDecodeError, IndexError):
                            results["tests"].append({
                                "name": "Nested context handling",
                                "status": "fail",
                                "reason": "Invalid JSON or missing log entries"
                            })
                            results["issues"].append("Error processing nested context logs")
                    else:
                        results["tests"].append({
                            "name": "Nested context handling",
                            "status": "fail",
                            "reason": "Not enough log entries"
                        })
                        results["issues"].append("Not all context log messages were written")
            else:
                results["tests"].append({
                    "name": "Nested context handling",
                    "status": "fail",
                    "reason": "Log file not created or empty"
                })
                results["issues"].append("Nested context log file not created")
        except Exception as e:
            results["tests"].append({
                "name": "Nested context handling",
                "status": "error",
                "reason": str(e)
            })
            results["issues"].append(f"Nested context error: {str(e)}")
    
    except Exception as e:
        results["status"] = "error"
        results["issues"].append(f"General context troubleshooting error: {str(e)}")
    
    # Clean up if using temporary directory
    if temp_dir:
        temp_dir.cleanup()
    
    # Update overall status
    if any(test["status"] == "fail" or test["status"] == "error" for test in results["tests"]):
        results["status"] = "failed"
    
    return results


def troubleshoot_database(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Troubleshoot database issues.
    
    Args:
        db_path: Optional path to an existing database file
        
    Returns:
        Dict[str, Any]: Troubleshooting results
    """
    results = {
        "status": "success",
        "tests": [],
        "issues": [],
        "fixes_applied": []
    }
    
    # If no db_path provided, create a temporary one
    temp_dir = None
    if not db_path:
        temp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(temp_dir.name, "test_db.db")
    
    try:
        # Test 1: Database creation
        try:
            handler = SQLiteHandler(db_path)
            
            if os.path.exists(db_path):
                results["tests"].append({
                    "name": "Database creation",
                    "status": "pass"
                })
            else:
                results["tests"].append({
                    "name": "Database creation",
                    "status": "fail",
                    "reason": "Database file not created"
                })
                results["issues"].append("SQLiteHandler not creating database file")
        except Exception as e:
            results["tests"].append({
                "name": "Database creation",
                "status": "error",
                "reason": str(e)
            })
            results["issues"].append(f"Database creation error: {str(e)}")
        
        # Test 2: Table creation
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
                if cursor.fetchone():
                    results["tests"].append({
                        "name": "Table creation",
                        "status": "pass"
                    })
                else:
                    results["tests"].append({
                        "name": "Table creation",
                        "status": "fail",
                        "reason": "Logs table not created"
                    })
                    results["issues"].append("SQLiteHandler not creating logs table")
                    
                    # Try to fix by creating the table
                    try:
                        handler = SQLiteHandler(db_path)
                        handler.create_table()
                        results["fixes_applied"].append("Created logs table")
                    except Exception:
                        pass
                
                conn.close()
            except Exception as e:
                results["tests"].append({
                    "name": "Table creation",
                    "status": "error",
                    "reason": str(e)
                })
                results["issues"].append(f"Table creation error: {str(e)}")
        
        # Test 3: Record insertion
        if os.path.exists(db_path):
            try:
                # Create a test record
                record = logging.LogRecord(
                    name="test_db",
                    level=logging.INFO,
                    pathname="test_db.py",
                    lineno=1,
                    msg="Database insertion test",
                    args=(),
                    exc_info=None
                )
                setattr(record, "context", {"test": "value"})
                
                # Create handler and emit record
                handler = SQLiteHandler(db_path)
                handler.emit(record)
                
                # Check if record was inserted
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM logs WHERE message = ?", ("Database insertion test",))
                if cursor.fetchone():
                    results["tests"].append({
                        "name": "Record insertion",
                        "status": "pass"
                    })
                else:
                    results["tests"].append({
                        "name": "Record insertion",
                        "status": "fail",
                        "reason": "Record not inserted"
                    })
                    results["issues"].append("SQLiteHandler not inserting records")
                
                conn.close()
            except Exception as e:
                results["tests"].append({
                    "name": "Record insertion",
                    "status": "error",
                    "reason": str(e)
                })
                results["issues"].append(f"Record insertion error: {str(e)}")
    
    except Exception as e:
        results["status"] = "error"
        results["issues"].append(f"General database troubleshooting error: {str(e)}")
    
    # Clean up if using temporary directory
    if temp_dir:
        temp_dir.cleanup()
    
    # Update overall status
    if any(test["status"] == "fail" or test["status"] == "error" for test in results["tests"]):
        results["status"] = "failed"
    
    return results


def generate_diagnostic_report() -> Dict[str, Any]:
    """Generate a comprehensive diagnostic report for LogLama.
    
    Returns:
        Dict[str, Any]: Comprehensive diagnostic report
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "python_path": sys.executable,
            "cwd": os.getcwd()
        },
        "components": {}
    }
    
    # Run health checks
    report["components"]["health"] = check_system_health()
    
    # Run troubleshooting
    report["components"]["logging"] = troubleshoot_logging()
    report["components"]["context"] = troubleshoot_context()
    report["components"]["database"] = troubleshoot_database()
    
    # Determine overall status
    component_statuses = [
        report["components"]["health"]["status"] == "healthy",
        report["components"]["logging"]["status"] == "success",
        report["components"]["context"]["status"] == "success",
        report["components"]["database"]["status"] == "success"
    ]
    
    if all(component_statuses):
        report["status"] = "healthy"
    elif any(not status for status in component_statuses):
        report["status"] = "degraded"
    else:
        report["status"] = "failing"
    
    # Collect all issues
    report["issues"] = []
    report["issues"].extend(report["components"]["health"]["issues"])
    report["issues"].extend(report["components"]["logging"]["issues"])
    report["issues"].extend(report["components"]["context"]["issues"])
    report["issues"].extend(report["components"]["database"]["issues"])
    
    # Collect all fixes applied
    report["fixes_applied"] = []
    if "fixes_applied" in report["components"]["logging"]:
        report["fixes_applied"].extend(report["components"]["logging"]["fixes_applied"])
    if "fixes_applied" in report["components"]["context"]:
        report["fixes_applied"].extend(report["components"]["context"]["fixes_applied"])
    if "fixes_applied" in report["components"]["database"]:
        report["fixes_applied"].extend(report["components"]["database"]["fixes_applied"])
    
    # Generate recommendations
    report["recommendations"] = []
    report["recommendations"].extend(report["components"]["health"]["recommendations"])
    
    return report
