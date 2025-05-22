#!/usr/bin/env python3
"""
Command-line interface for LogLama.

This module provides a CLI for interacting with the LogLama system and managing
the centralized environment for the entire PyLama ecosystem.
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

# Import LogLama modules
from loglama.config.env_loader import load_env, get_env
from loglama.core.logger import get_logger, setup_logging
from loglama.cli.diagnostics import main as diagnostics_main
from loglama.core.env_manager import (
    load_central_env, ensure_required_env_vars, 
    check_project_dependencies, install_project_dependencies,
    run_project_tests, start_project, get_central_env_path
)

# Load environment variables from the central .env file
load_central_env()

# Set up logger
logger = get_logger("loglama.cli", rich_logging=RICH_AVAILABLE)


@click.group()
def cli():
    """LogLama - Powerful logging and debugging utility for PyLama ecosystem."""
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
            db = get_env('LOGLAMA_DB_PATH', None)
            if not db:
                log_dir = get_env('LOGLAMA_LOG_DIR', './logs')
                db = os.path.join(log_dir, 'loglama.db')
        
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
                from loglama.db.models import create_tables, get_session
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
        from loglama.cli.web_viewer import run_app
        
        # Print info message
        url = f"http://{host}:{port}"
        if RICH_AVAILABLE:
            console.print(f"[bold green]Starting LogLama web interface on {url}[/bold green]")
            console.print(f"[green]Using database: {db}[/green]")
        else:
            click.echo(f"Starting LogLama web interface on {url}")
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
@click.option("--force/--no-force", default=False, help="Force initialization even if already initialized")
def init(env_file, verbose, force):
    """Initialize LogLama configuration and the centralized environment."""
    # Get the central .env path
    central_env_path = get_central_env_path()
    
    if verbose:
        console.print(f"[bold]Using central .env file: {central_env_path}[/bold]")
    
    # Load environment variables from specified file or central .env
    if env_file:
        # Copy the specified .env file to the central location
        if verbose:
            console.print(f"[yellow]Copying {env_file} to central location {central_env_path}[/yellow]")
        try:
            import shutil
            shutil.copy2(env_file, central_env_path)
            success = load_central_env()
        except Exception as e:
            console.print(f"[red]Error copying .env file: {str(e)}[/red]")
            success = False
    else:
        # Load from central location
        success = load_central_env()
        
        # If not successful or force is True, ensure required variables
        if not success or force:
            if verbose:
                console.print("[yellow]Ensuring all required environment variables are set...[/yellow]")
            missing_vars = ensure_required_env_vars()
            if missing_vars:
                if verbose:
                    console.print("[green]Added the following missing environment variables:[/green]")
                    for project, vars in missing_vars.items():
                        console.print(f"[bold]{project}:[/bold]")
                        for var, value in vars.items():
                            console.print(f"  {var} = {value}")
            success = True
    
    if success:
        if verbose:
            console.print("[green]Successfully loaded environment variables.[/green]")
    else:
        if verbose:
            console.print("[yellow]No .env file found. Using default configuration.[/yellow]")
    
    # Initialize database
    try:
        from loglama.db.models import create_tables
        create_tables()
        if verbose:
            console.print("[green]Successfully initialized database.[/green]")
    except ImportError:
        if verbose:
            console.print("[yellow]Database module not available. Install loglama[db] for database support.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error initializing database: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--level", default=None, help="Filter by log level (e.g., INFO, ERROR)")
@click.option("--logger", default=None, help="Filter by logger name")
@click.option("--module", default=None, help="Filter by module name")
@click.option("--limit", default=50, help="Maximum number of logs to display")
@click.option("--json/--no-json", default=False, help="Output in JSON format")
def logs(level, logger_name, module, limit, json_output):
    """Display log records from the database."""
    # Initialize CLI logger
    from loglama.core.logger import get_logger
    logger = get_logger("loglama.cli")
    
    try:
        # Import database modules
        try:
            from loglama.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install loglama[db] for database support.[/red]")
            sys.exit(1)
        
        # Ensure tables exist
        create_tables()
        
        # Create session and query
        session = get_session()
        query = session.query(LogRecord)
        
        # Apply filters
        if level:
            query = query.filter(LogRecord.level == level.upper())
        if logger_name:
            query = query.filter(LogRecord.logger_name.like(f"%{logger_name}%"))
        if module:
            query = query.filter(LogRecord.module.like(f"%{module}%"))
        
        # Apply limit and ordering
        query = query.order_by(LogRecord.timestamp.desc()).limit(limit)
        
        # Execute query
        log_records = query.all()
        
        # Close session
        session.close()
        
        if json_output:
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
            from loglama.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install loglama[db] for database support.[/red]")
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
            from loglama.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install loglama[db] for database support.[/red]")
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
@click.option("--command", "-c", required=True, 
              type=click.Choice(["health", "verify", "context", "database", "files", 
                                "troubleshoot-logging", "troubleshoot-context", 
                                "troubleshoot-database", "report"]),
              help="Diagnostic command to run")
@click.option("--output", "-o", help="Output file for reports")
@click.option("--log-dir", "-d", help="Directory for test log files")
@click.option("--db-path", "-p", help="Path to database file")
@click.option("--log-level", "-l", default="INFO", help="Log level to use for tests")
def diagnose(command, output, log_dir, db_path, log_level):
    """Run diagnostic tools to troubleshoot LogLama issues."""
    # Prepare arguments for the diagnostics CLI
    args = [command]
    
    if output and command in ["health", "report"]:
        args.extend(["--output", output])
    
    if log_dir and command in ["verify", "context", "files", "troubleshoot-logging", "troubleshoot-context"]:
        args.extend(["--log-dir", log_dir])
    
    if db_path and command in ["database", "troubleshoot-database"]:
        args.extend(["--db-path", db_path])
    
    if log_level and command == "troubleshoot-logging":
        args.extend(["--log-level", log_level])
    
    # Run the diagnostics CLI with the prepared arguments
    sys.argv = ["loglama-diagnostics"] + args
    return diagnostics_main()


@cli.command()
def stats():
    """Show statistics about log records."""
    try:
        # Import database modules
        try:
            from loglama.db.models import LogRecord, get_session, create_tables
        except ImportError:
            console.print("[red]Database module not available. Install loglama[db] for database support.[/red]")
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
    """Show LogLama version information."""
    from loglama import __version__
    if RICH_AVAILABLE:
        console.print(f"[bold]LogLama[/bold] version [green]{__version__}[/green]")
    else:
        click.echo(f"LogLama version {__version__}")


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


@cli.command()
@click.argument("project", required=True, type=click.Choice(["loglama", "pylama", "pyllm", "pybox", "all"]))
@click.option("--install/--no-install", default=True, help="Install missing dependencies")
@click.option("--verbose/--quiet", default=True, help="Show verbose output")
def check_deps(project, install, verbose):
    """Check and optionally install dependencies for a project."""
    # Ensure environment variables are loaded
    load_central_env()
    
    if project == "all":
        projects = ["loglama", "pylama", "pyllm", "pybox"]
    else:
        projects = [project]
    
    all_success = True
    for proj in projects:
        if verbose:
            console.print(f"\n[bold]Checking dependencies for {proj}...[/bold]")
        
        # Check dependencies
        success, missing_deps, output = check_project_dependencies(proj)
        
        if success:
            if verbose:
                console.print(f"[green]All dependencies for {proj} are installed.[/green]")
        else:
            all_success = False
            if verbose:
                console.print(f"[yellow]Missing dependencies for {proj}:[/yellow]")
                for dep in missing_deps:
                    console.print(f"  - {dep}")
            
            # Install dependencies if requested
            if install and missing_deps:
                if verbose:
                    console.print(f"[yellow]Installing missing dependencies for {proj}...[/yellow]")
                
                install_success, install_output = install_project_dependencies(proj)
                
                if install_success:
                    if verbose:
                        console.print(f"[green]Successfully installed dependencies for {proj}.[/green]")
                    all_success = True
                else:
                    if verbose:
                        console.print(f"[red]Failed to install dependencies for {proj}:[/red]")
                        console.print(install_output)
    
    if not all_success:
        sys.exit(1)


@cli.command()
@click.argument("project", required=True, type=click.Choice(["loglama", "pylama", "pyllm", "pybox", "all"]))
@click.option("--verbose/--quiet", default=True, help="Show verbose output")
def test(project, verbose):
    """Run tests for a project."""
    # Ensure environment variables are loaded
    load_central_env()
    
    if project == "all":
        projects = ["loglama", "pylama", "pyllm", "pybox"]
    else:
        projects = [project]
    
    all_success = True
    for proj in projects:
        if verbose:
            console.print(f"\n[bold]Running tests for {proj}...[/bold]")
        
        # Run tests
        success, output = run_project_tests(proj)
        
        if success:
            if verbose:
                console.print(f"[green]Tests for {proj} passed.[/green]")
        else:
            all_success = False
            if verbose:
                console.print(f"[red]Tests for {proj} failed:[/red]")
                console.print(output)
    
    if not all_success:
        sys.exit(1)


@cli.command()
@click.argument("project", required=True, type=click.Choice(["loglama", "pylama", "pyllm", "pybox"]))
@click.option("--check-deps/--no-check-deps", default=True, help="Check dependencies before starting")
@click.option("--install-deps/--no-install-deps", default=True, help="Install missing dependencies")
@click.option("--verbose/--quiet", default=True, help="Show verbose output")
@click.argument("args", nargs=-1)
def start(project, check_deps, install_deps, verbose, args):
    """Start a project with the centralized environment."""
    # Ensure environment variables are loaded
    load_central_env()
    
    # Check dependencies if requested
    if check_deps:
        if verbose:
            console.print(f"[bold]Checking dependencies for {project}...[/bold]")
        
        success, missing_deps, output = check_project_dependencies(project)
        
        if not success and install_deps:
            if verbose:
                console.print(f"[yellow]Installing missing dependencies for {project}...[/yellow]")
            
            install_success, install_output = install_project_dependencies(project)
            
            if not install_success:
                if verbose:
                    console.print(f"[red]Failed to install dependencies for {project}:[/red]")
                    console.print(install_output)
                sys.exit(1)
    
    # Start the project
    if verbose:
        console.print(f"[bold]Starting {project}...[/bold]")
    
    success, process, output = start_project(project, list(args))
    
    if success:
        if verbose:
            console.print(f"[green]{project} started successfully.[/green]")
            console.print("Press Ctrl+C to stop...")
        
        try:
            # Wait for the process to complete or for the user to interrupt
            if process:
                stdout, stderr = process.communicate()
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr, file=sys.stderr)
        except KeyboardInterrupt:
            if process:
                process.terminate()
            if verbose:
                console.print(f"\n[yellow]{project} stopped.[/yellow]")
    else:
        if verbose:
            console.print(f"[red]Failed to start {project}:[/red]")
            console.print(output)
        sys.exit(1)


@cli.command()
@click.option("--check-deps/--no-check-deps", default=True, help="Check dependencies before starting")
@click.option("--install-deps/--no-install-deps", default=True, help="Install missing dependencies")
@click.option("--verbose/--quiet", default=True, help="Show verbose output")
@click.option("--loglama/--no-loglama", default=True, help="Start LogLama")
@click.option("--pylama/--no-pylama", default=True, help="Start PyLama")
@click.option("--pyllm/--no-pyllm", default=True, help="Start PyLLM")
@click.option("--pybox/--no-pybox", default=True, help="Start PyBox")
@click.option("--weblama/--no-weblama", default=True, help="Start WebLama")
def start_all(check_deps, install_deps, verbose, loglama, pylama, pyllm, pybox, weblama):
    """Start all PyLama ecosystem services."""
    # Ensure environment variables are loaded
    load_central_env()
    
    # Determine which projects to start
    projects = []
    if loglama:
        projects.append("loglama")
    if pylama:
        projects.append("pylama")
    if pyllm:
        projects.append("pyllm")
    if pybox:
        projects.append("pybox")
    
    # Check dependencies if requested
    if check_deps:
        for project in projects:
            if verbose:
                console.print(f"[bold]Checking dependencies for {project}...[/bold]")
            
            success, missing_deps, output = check_project_dependencies(project)
            
            if not success and install_deps:
                if verbose:
                    console.print(f"[yellow]Installing missing dependencies for {project}...[/yellow]")
                
                install_success, install_output = install_project_dependencies(project)
                
                if not install_success:
                    if verbose:
                        console.print(f"[red]Failed to install dependencies for {project}:[/red]")
                        console.print(install_output)
                    sys.exit(1)
    
    # Start the projects
    processes = {}
    for project in projects:
        if verbose:
            console.print(f"[bold]Starting {project}...[/bold]")
        
        # Determine arguments for each project
        args = []
        if project == "loglama":
            args = ["web"]
        
        success, process, output = start_project(project, args)
        
        if success:
            if verbose:
                console.print(f"[green]{project} started successfully.[/green]")
            processes[project] = process
        else:
            if verbose:
                console.print(f"[red]Failed to start {project}:[/red]")
                console.print(output)
            
            # Stop any started processes
            for p_name, p in processes.items():
                if p:
                    p.terminate()
                    if verbose:
                        console.print(f"[yellow]Stopped {p_name}.[/yellow]")
            
            sys.exit(1)
    
    # Start WebLama if requested
    if weblama and processes:
        if verbose:
            console.print("[bold]Starting WebLama...[/bold]")
        
        # Import the ecosystem module to start WebLama
        try:
            # This assumes the ecosystem module is available
            from pylama.ecosystem import start_service
            success = start_service("weblama")
            
            if success:
                if verbose:
                    console.print("[green]WebLama started successfully.[/green]")
            else:
                if verbose:
                    console.print("[red]Failed to start WebLama.[/red]")
        except ImportError:
            if verbose:
                console.print("[yellow]Could not import ecosystem module to start WebLama.[/yellow]")
                console.print("[yellow]Please start WebLama manually.[/yellow]")
    
    if verbose:
        console.print("\n[green]All services started successfully.[/green]")
        console.print("Press Ctrl+C to stop all services...")
    
    try:
        # Wait for the user to interrupt
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop all processes
        for p_name, p in processes.items():
            if p:
                p.terminate()
                if verbose:
                    console.print(f"[yellow]Stopped {p_name}.[/yellow]")
        
        # Stop WebLama if it was started
        if weblama:
            try:
                from pylama.ecosystem import stop_service
                stop_service("weblama")
                if verbose:
                    console.print("[yellow]Stopped WebLama.[/yellow]")
            except ImportError:
                pass
        
        if verbose:
            console.print("\n[yellow]All services stopped.[/yellow]")


@cli.command()
@click.option("--verbose/--quiet", default=True, help="Show verbose output")
def env(verbose):
    """Show the current environment variables."""
    # Ensure environment variables are loaded
    load_central_env()
    
    # Get the central .env path
    central_env_path = get_central_env_path()
    
    if verbose:
        console.print(f"[bold]Central .env file: {central_env_path}[/bold]")
    
    # Check if the file exists
    if not central_env_path.exists():
        if verbose:
            console.print("[yellow]Central .env file does not exist.[/yellow]")
            console.print("[yellow]Run 'loglama init' to create it.[/yellow]")
        return
    
    # Read the .env file
    try:
        with open(central_env_path, "r") as f:
            env_content = f.read()
        
        # Parse the .env file
        env_vars = {}
        for line in env_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
        
        # Display the environment variables
        if RICH_AVAILABLE:
            table = Table(title="Environment Variables")
            table.add_column("Variable", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Used By", style="yellow")
            
            for key, value in sorted(env_vars.items()):
                # Determine which projects use this variable
                used_by = []
                for project, vars in _required_env_vars.items():
                    if key in vars:
                        used_by.append(project)
                
                table.add_row(key, value, ", ".join(used_by) if used_by else "")
            
            console.print(table)
        else:
            console.print("Environment Variables:")
            for key, value in sorted(env_vars.items()):
                # Determine which projects use this variable
                used_by = []
                for project, vars in _required_env_vars.items():
                    if key in vars:
                        used_by.append(project)
                
                used_by_str = f" (used by: {', '.join(used_by)})" if used_by else ""
                console.print(f"{key} = {value}{used_by_str}")
    except Exception as e:
        if verbose:
            console.print(f"[red]Error reading .env file: {str(e)}[/red]")


if __name__ == "__main__":
    main()
