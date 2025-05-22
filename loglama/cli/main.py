#!/usr/bin/env python3
"""
Command-line interface for LogLama.

This module provides a CLI for interacting with the LogLama system and managing
the centralized environment for the entire PyLama ecosystem.
"""

import os
import sys
from pathlib import Path

import click

# Import LogLama modules
from loglama.core.env_manager import load_central_env
from loglama.core.logger import get_logger

# Import CLI utilities
from loglama.cli.utils import get_console

# Import command modules
from loglama.cli.commands.logs_commands import logs, view, clear, stats
from loglama.cli.commands.env_commands import init, env
from loglama.cli.commands.project_commands import check_deps, test, start, start_all
from loglama.cli.commands.diagnostic_commands import diagnose, version

# Get console instance
console = get_console()

# Load environment variables from the central .env file
load_central_env()


@click.group()
def cli():
    """LogLama - Powerful logging and debugging utility for PyLama ecosystem."""
    pass


# Register commands

# Log management commands
cli.add_command(logs)
cli.add_command(view)
cli.add_command(clear)
cli.add_command(stats)

# Environment management commands
cli.add_command(init)
cli.add_command(env)

# Project management commands
cli.add_command(check_deps)
cli.add_command(test)
cli.add_command(start)
cli.add_command(start_all)

# Diagnostic commands
cli.add_command(diagnose)
cli.add_command(version)


@click.command()
@click.option("--port", default=5000, help="Port to run the web interface on")
@click.option("--host", default="127.0.0.1", help="Host to bind the web interface to")
@click.option("--db", default=None, help="Path to LogLama database")
@click.option("--debug/--no-debug", default=False, help="Run in debug mode")
@click.option("--open/--no-open", default=True, help="Open browser after starting")
def web(port, host, db, debug, open):
    """Launch the web interface for viewing logs."""
    # Initialize CLI logger
    logger = get_logger("loglama.cli")
    
    try:
        # Import web interface module
        try:
            from loglama.web import create_app
        except ImportError:
            console.print("[red]Web interface module not available. Install loglama[web] for web interface support.[/red]")
            sys.exit(1)
        
        # Create and run the web application
        app = create_app(db_path=db)
        
        # Print startup message
        console.print(f"[green]Starting LogLama web interface at http://{host}:{port}/[/green]")
        
        # Open browser if requested
        if open:
            import webbrowser
            webbrowser.open(f"http://{host}:{port}/")
        
        # Run the application
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        logger.exception(f"Error starting web interface: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


# Add web command
cli.add_command(web)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        # Get logger for unhandled exceptions
        logger = get_logger("loglama.cli")
        logger.error(f"Unhandled exception in CLI: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__" or __name__ == "loglama.cli.main":
    main()
