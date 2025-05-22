#!/usr/bin/env python3
"""
Command-line interface for PyLogs.

This module provides a CLI for interacting with the PyLogs system.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import click

# Try to import rich for enhanced console output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to simple print functions
    class SimpleConsole:
        def print(self, *args, **kwargs):
            print(*args)
            
        def log(self, *args, **kwargs):
            print(*args)
    
    console = SimpleConsole()

# Import PyLogs modules
from pylogs.config.env_loader import load_env, get_env
from pylogs.core.logger import get_logger, setup_logging
from pylogs.cli.diagnostics import main as diagnostics_main

# Load environment variables
load_env()

# Set up logger
logger = get_logger("pylogs.cli", rich_logging=RICH_AVAILABLE)


@click.group()
def cli():
    """PyLogs - Powerful logging and debugging utility for PyLama ecosystem."""
    pass


@cli.command()
@click.option("--port", default=5000, help="Port to run the web interface on")
@click.option("--host", default="127.0.0.1", help="Host to bind the web interface to")
@click.option("--db", help="Path to SQLite database file")
@click.option("--debug/--no-debug", default=False, help="Run in debug mode")
@click.option("--open/--no-open", default=True, help="Open browser automatically")
def web(port, host, db, debug, open):
    """Launch the web interface for viewing logs."""
    try:
        # Get database path from environment if not provided
        if not db:
            db = get_env('PYLOGS_DB_PATH', None)
            if not db:
                log_dir = get_env('PYLOGS_LOG_DIR', './logs')
                db = os.path.join(log_dir, 'pylogs.db')
        
        # Ensure the database directory exists
        db_dir = os.path.dirname(db)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            if RICH_AVAILABLE:
                console.print(f"[green]Created directory {db_dir}[/green]")
            else:
                click.echo(f"Created directory {db_dir}")
        
        if not os.path.exists(db):
            if RICH_AVAILABLE:
                console.print(f"[yellow]Warning: Database file not found at {db}[/yellow]")
                console.print("[yellow]Creating an empty database file...[/yellow]")
            else:
                click.echo(f"Warning: Database file not found at {db}")
                click.echo("Creating an empty database file...")
            
            # Create an empty database file
            try:
                from pylogs.db.models import create_tables, get_session
                create_tables(db_path=db)
                if RICH_AVAILABLE:
                    console.print("[green]Created database tables[/green]")
                else:
                    click.echo("Created database tables")
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[red]Error creating database: {str(e)}[/red]")
                else:
                    click.echo(f"Error creating database: {str(e)}")
        
        # Import the web viewer module
        from pylogs.cli.web_viewer import run_app
        
        # Print info message
        url = f"http://{host}:{port}"
        if RICH_AVAILABLE:
            console.print(f"[bold green]Starting PyLogs web interface on {url}[/bold green]")
            console.print(f"[green]Using database: {db}[/green]")
        else:
            click.echo(f"Starting PyLogs web interface on {url}")
            click.echo(f"Using database: {db}")
        
        # Open browser if requested
        if open:
            import webbrowser
            webbrowser.open(url)
        
        # Run the web application
        run_app(host=host, port=port, db_path=db)
    except Exception as e:
        logger.exception(f"Error starting web interface: {str(e)}")
        if RICH_AVAILABLE:
            console.print(f"[red]Error: {str(e)}[/red]")
        else:
            click.echo(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--env-file", help="Path to .env file to load")
@click.option("--verbose/--quiet", default=True, help="Show verbose output")
def init(env_file, verbose):
    """Initialize PyLogs configuration."""
    # Load environment variables
    success = load_env(env_file, verbose=verbose)
    
    if success:
        if verbose:
            console.print("[green]Successfully loaded environment variables.[/green]")
    else:
        if verbose:
            console.print("[yellow]No .env file found. Using default configuration.[/yellow]")
    
    # Initialize database
    try:
        from pylogs.db.models import create_tables
        create_tables()
        if verbose:
            console.print("[green]Successfully initialized database.[/green]")
    except ImportError:
        if verbose:
            console.print("[yellow]Database module not available. Install pylogs[db] for database support.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error initializing database: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--level", default=None, help="Filter by log level (e.g., INFO, ERROR)")
@click.option("--logger", default=None, help="Filter by logger name")
@click.option("--module", default=None, help="Filter by module name")
@click.option("--limit", default=50, help="Maximum number of logs to display")
@click.option("--json/--no-json", default=False, help="Output in JSON format")
def logs(level, logger, module, limit, json):
    """Display log records from the database."""
    try:
        # Import database modules
        try:
            from pylogs.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install pylogs[db] for database support.[/red]")
            sys.exit(1)
        
        # Ensure tables exist
        create_tables()
        
        # Create session and query
        session = get_session()
        query = session.query(LogRecord)
        
        # Apply filters
        if level:
            query = query.filter(LogRecord.level == level.upper())
        if logger:
            query = query.filter(LogRecord.logger_name.like(f"%{logger}%"))
        if module:
            query = query.filter(LogRecord.module.like(f"%{module}%"))
        
        # Apply limit and ordering
        query = query.order_by(LogRecord.timestamp.desc()).limit(limit)
        
        # Execute query
        log_records = query.all()
        
        # Close session
        session.close()
        
        if json:
            # Output in JSON format
            results = [record.to_dict() for record in log_records]
            click.echo(json.dumps(results, indent=2, default=str))
        else:
            # Output in table format
            if RICH_AVAILABLE:
                table = Table(title="Log Records")
                table.add_column("ID", justify="right")
                table.add_column("Timestamp")
                table.add_column("Level")
                table.add_column("Logger")
                table.add_column("Message")
                
                for record in log_records:
                    level_style = {
                        "DEBUG": "dim",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "bold red",
                    }.get(record.level, "")
                    
                    table.add_row(
                        str(record.id),
                        record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        f"[{level_style}]{record.level}[/{level_style}]",
                        record.logger_name,
                        record.message[:100] + ("..." if len(record.message) > 100 else "")
                    )
                
                console.print(table)
            else:
                # Fallback to simple table
                click.echo(f"{'ID':>5} | {'Timestamp':<19} | {'Level':<8} | {'Logger':<20} | Message")
                click.echo("-" * 80)
                
                for record in log_records:
                    click.echo(
                        f"{record.id:>5} | "
                        f"{record.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<19} | "
                        f"{record.level:<8} | "
                        f"{record.logger_name[:20]:<20} | "
                        f"{record.message[:100] + ('...' if len(record.message) > 100 else '')}"
                    )
    except Exception as e:
        logger.exception(f"Error displaying logs: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("log_id", type=int)
def view(log_id):
    """View details of a specific log record."""
    try:
        # Import database modules
        try:
            from pylogs.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install pylogs[db] for database support.[/red]")
            sys.exit(1)
        
        # Ensure tables exist
        create_tables()
        
        # Create session and query
        session = get_session()
        record = session.query(LogRecord).filter(LogRecord.id == log_id).first()
        
        # Close session
        session.close()
        
        if not record:
            console.print(f"[red]Log record with ID {log_id} not found[/red]")
            sys.exit(1)
        
        if RICH_AVAILABLE:
            # Rich output
            console.print(f"[bold]Log Record #{record.id}[/bold]")
            console.print(f"[bold]Timestamp:[/bold] {record.timestamp}")
            
            level_style = {
                "DEBUG": "dim",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red",
            }.get(record.level, "")
            console.print(f"[bold]Level:[/bold] [{level_style}]{record.level}[/{level_style}]")
            
            console.print(f"[bold]Logger:[/bold] {record.logger_name}")
            console.print(f"[bold]Module:[/bold] {record.module}")
            console.print(f"[bold]Function:[/bold] {record.function}")
            console.print(f"[bold]Line:[/bold] {record.line_number}")
            console.print(f"[bold]Process:[/bold] {record.process_name} ({record.process_id})")
            console.print(f"[bold]Thread:[/bold] {record.thread_name} ({record.thread_id})")
            console.print(f"[bold]Message:[/bold]\n{record.message}")
            
            if record.exception_info:
                console.print(f"[bold]Exception:[/bold]\n{record.exception_info}")
            
            if record.context:
                try:
                    context = json.loads(record.context)
                    console.print(f"[bold]Context:[/bold]")
                    console.print(json.dumps(context, indent=2))
                except json.JSONDecodeError:
                    console.print(f"[bold]Context:[/bold]\n{record.context}")
        else:
            # Simple output
            click.echo(f"Log Record #{record.id}")
            click.echo(f"Timestamp: {record.timestamp}")
            click.echo(f"Level: {record.level}")
            click.echo(f"Logger: {record.logger_name}")
            click.echo(f"Module: {record.module}")
            click.echo(f"Function: {record.function}")
            click.echo(f"Line: {record.line_number}")
            click.echo(f"Process: {record.process_name} ({record.process_id})")
            click.echo(f"Thread: {record.thread_name} ({record.thread_id})")
            click.echo(f"Message:\n{record.message}")
            
            if record.exception_info:
                click.echo(f"Exception:\n{record.exception_info}")
            
            if record.context:
                try:
                    context = json.loads(record.context)
                    click.echo(f"Context:\n{json.dumps(context, indent=2)}")
                except json.JSONDecodeError:
                    click.echo(f"Context:\n{record.context}")
    except Exception as e:
        logger.exception(f"Error viewing log record: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--level", default=None, help="Filter by log level (e.g., INFO, ERROR)")
@click.option("--logger", default=None, help="Filter by logger name")
@click.option("--module", default=None, help="Filter by module name")
@click.option("--all", is_flag=True, help="Clear all logs (ignores other filters)")
@click.confirmation_option(prompt="Are you sure you want to clear these logs?")
def clear(level, logger, module, all):
    """Clear log records from the database."""
    try:
        # Import database modules
        try:
            from pylogs.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install pylogs[db] for database support.[/red]")
            sys.exit(1)
        
        # Ensure tables exist
        create_tables()
        
        # Create session and query
        session = get_session()
        query = session.query(LogRecord)
        
        # Apply filters if not clearing all
        if not all:
            if level:
                query = query.filter(LogRecord.level == level.upper())
            if logger:
                query = query.filter(LogRecord.logger_name.like(f"%{logger}%"))
            if module:
                query = query.filter(LogRecord.module.like(f"%{module}%"))
        
        # Get count before deletion
        count = query.count()
        
        # Delete matching records
        query.delete()
        session.commit()
        
        # Close session
        session.close()
        
        console.print(f"[green]Deleted {count} log records[/green]")
    except Exception as e:
        logger.exception(f"Error clearing logs: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def stats():
    """Show statistics about log records."""
    try:
        # Import database modules
        try:
            from pylogs.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install pylogs[db] for database support.[/red]")
            sys.exit(1)
        
        # Ensure tables exist
        create_tables()
        
        # Create session
        session = get_session()
        
        # Get total count
        total_count = session.query(LogRecord).count()
        
        # Get counts by level
        level_counts = {}
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            count = session.query(LogRecord).filter(LogRecord.level == level).count()
            level_counts[level] = count
        
        # Get counts by logger
        logger_counts = {}
        loggers = session.query(LogRecord.logger_name).distinct().all()
        for (logger_name,) in loggers:
            count = session.query(LogRecord).filter(LogRecord.logger_name == logger_name).count()
            logger_counts[logger_name] = count
        
        # Close session
        session.close()
        
        if RICH_AVAILABLE:
            # Rich output
            console.print(f"[bold]Total Log Records:[/bold] {total_count}")
            
            # Level statistics
            level_table = Table(title="Log Levels")
            level_table.add_column("Level")
            level_table.add_column("Count", justify="right")
            level_table.add_column("Percentage", justify="right")
            
            for level, count in level_counts.items():
                percentage = (count / total_count * 100) if total_count > 0 else 0
                level_style = {
                    "DEBUG": "dim",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold red",
                }.get(level, "")
                
                level_table.add_row(
                    f"[{level_style}]{level}[/{level_style}]",
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(level_table)
            
            # Logger statistics
            if logger_counts:
                logger_table = Table(title="Loggers")
                logger_table.add_column("Logger")
                logger_table.add_column("Count", justify="right")
                logger_table.add_column("Percentage", justify="right")
                
                for logger_name, count in logger_counts.items():
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    logger_table.add_row(
                        logger_name,
                        str(count),
                        f"{percentage:.1f}%"
                    )
                
                console.print(logger_table)
        else:
            # Simple output
            click.echo(f"Total Log Records: {total_count}")
            
            # Level statistics
            click.echo("\nLog Levels:")
            click.echo(f"{'Level':<10} | {'Count':>8} | Percentage")
            click.echo("-" * 35)
            
            for level, count in level_counts.items():
                percentage = (count / total_count * 100) if total_count > 0 else 0
                click.echo(f"{level:<10} | {count:>8} | {percentage:.1f}%")
            
            # Logger statistics
            if logger_counts:
                click.echo("\nLoggers:")
                click.echo(f"{'Logger':<30} | {'Count':>8} | Percentage")
                click.echo("-" * 55)
                
                for logger_name, count in logger_counts.items():
                    percentage = (count / total_count * 100) if total_count > 0 else 0
                    logger_display = logger_name[:30]
                    click.echo(f"{logger_display:<30} | {count:>8} | {percentage:.1f}%")
    except Exception as e:
        logger.exception(f"Error showing stats: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
def version():
    """Show PyLogs version information."""
    from pylogs import __version__
    if RICH_AVAILABLE:
        console.print(f"[bold]PyLogs[/bold] version [green]{__version__}[/green]")
    else:
        click.echo(f"PyLogs version {__version__}")


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        logger.exception(f"Unhandled exception in CLI: {str(e)}")
        if RICH_AVAILABLE:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
        else:
            click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
