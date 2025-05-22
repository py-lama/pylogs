#!/usr/bin/env python3

"""
Test script for the PyLogs to LogLama migration tools.

This script creates a sample project with PyLogs references and then runs
the migration script to verify it correctly updates them to LogLama.

Usage:
    python test_migration.py
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Sample code with PyLogs references
SAMPLE_CODE = """
#!/usr/bin/env python3

# Import loglama
import loglama
from loglama import get_logger, setup_logging
from loglama.handlers import SQLiteHandler
from loglama.formatters import JSONFormatter

# Environment variables
LOGLAMA_LOG_LEVEL = os.environ.get('LOGLAMA_LOG_LEVEL', 'INFO')
LOGLAMA_DB_PATH = os.environ.get('LOGLAMA_DB_PATH', 'logs.db')

# Setup logging
def init_logging():
    # Load environment variables
    loglama.load_env(verbose=True)
    
    # Create log directory
    log_dir = loglama.get_env('LOGLAMA_LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Setup logging
    logger = setup_logging(
        name="loglama_example",
        level=LOGLAMA_LOG_LEVEL,
        console=True,
        file=True,
        file_path=f"{log_dir}/loglama_example.log",
        database=True,
        db_path=LOGLAMA_DB_PATH,
        json_format=True
    )
    
    return logger

# Use LogContext
def log_with_context():
    logger = get_logger("loglama_example")
    
    with loglama.LogContext(user="test_user", operation="test"):
        logger.info("This is a log message with context")

# Configuration file paths
loglama_config_path = "./loglama_config.json"
loglama_diagnostic_report = "./loglama_diagnostic_report.json"

# Main function
def main():
    logger = init_logging()
    logger.info("PyLogs example application started")
    log_with_context()
    
    # Create a loglama_handler
    loglama_handler = SQLiteHandler(db_path=LOGLAMA_DB_PATH)
    
    # Create a loglama_formatter
    loglama_formatter = JSONFormatter()
    
    logger.info("PyLogs example application finished")

if __name__ == "__main__":
    main()
"""

# Sample .env file with PyLogs references
SAMPLE_ENV = """
# PyLogs configuration
LOGLAMA_LOG_LEVEL=DEBUG
LOGLAMA_LOG_DIR=./logs
LOGLAMA_DB_PATH=./logs/loglama.db
LOGLAMA_WEB_PORT=8080
"""

# Sample requirements.txt with PyLogs references
SAMPLE_REQUIREMENTS = """
# Project dependencies
loglama>=1.0.0
flask>=2.0.0
sqlite3>=3.0.0
"""

# Sample README.md with PyLogs references
SAMPLE_README = """
# Sample Project

This is a sample project that uses PyLogs for logging.

## Installation

```bash
pip install loglama
```

## Usage

```python
from loglama import get_logger

logger = get_logger(__name__)
logger.info("Hello, PyLogs!")
```

## Environment Variables

- `LOGLAMA_LOG_LEVEL`: The log level (default: INFO)
- `LOGLAMA_LOG_DIR`: The directory to store log files (default: ./logs)
- `LOGLAMA_DB_PATH`: The path to the SQLite database (default: ./logs/loglama.db)
"""


def create_sample_project(base_dir):
    """Create a sample project with PyLogs references."""
    # Create project structure
    project_dir = Path(base_dir) / "sample_project"
    src_dir = project_dir / "src"
    logs_dir = project_dir / "logs"
    config_dir = project_dir / "config"
    
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)
    
    # Create sample files
    with open(src_dir / "app.py", "w") as f:
        f.write(SAMPLE_CODE)
    
    with open(project_dir / ".env", "w") as f:
        f.write(SAMPLE_ENV)
    
    with open(project_dir / "requirements.txt", "w") as f:
        f.write(SAMPLE_REQUIREMENTS)
    
    with open(project_dir / "README.md", "w") as f:
        f.write(SAMPLE_README)
    
    with open(config_dir / "loglama_config.json", "w") as f:
        f.write('{"version": "1.0.0", "handlers": ["console", "file", "database"]}')
    
    # Create a subdirectory with loglama in the name
    loglama_dir = project_dir / "loglama_utils"
    os.makedirs(loglama_dir, exist_ok=True)
    
    with open(loglama_dir / "helpers.py", "w") as f:
        f.write('"""Helper functions for loglama."""\n\nfrom loglama import get_logger\n\nlogger = get_logger("loglama_utils")')
    
    return project_dir


def run_migration_script(project_dir, script_path, report_only=True, verbose=True):
    """Run the migration script on the sample project."""
    cmd = [
        sys.executable,
        str(script_path),
        "--path", str(project_dir),
        "--output", str(project_dir / "migration_report.json")
    ]
    
    if report_only:
        cmd.append("--report-only")
    
    if verbose:
        cmd.append("--verbose")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def verify_migration(project_dir):
    """Verify that the migration was successful."""
    issues = []
    
    # Check if files were renamed
    if not (project_dir / "loglama_utils").exists() and not (project_dir / "loglama_utils").exists():
        issues.append("Directory 'loglama_utils' was not renamed to 'loglama_utils'")
    
    if (project_dir / "config" / "loglama_config.json").exists() and not (project_dir / "config" / "loglama_config.json").exists():
        issues.append("File 'loglama_config.json' was not renamed to 'loglama_config.json'")
    
    # Check file contents
    with open(project_dir / "src" / "app.py", "r") as f:
        app_content = f.read()
        if "import loglama" in app_content:
            issues.append("'import loglama' was not updated to 'import loglama'")
        if "LOGLAMA_LOG_LEVEL" in app_content:
            issues.append("'LOGLAMA_LOG_LEVEL' was not updated to 'LOGLAMA_LOG_LEVEL'")
    
    with open(project_dir / ".env", "r") as f:
        env_content = f.read()
        if "LOGLAMA_LOG_LEVEL" in env_content:
            issues.append("'LOGLAMA_LOG_LEVEL' in .env was not updated to 'LOGLAMA_LOG_LEVEL'")
    
    with open(project_dir / "requirements.txt", "r") as f:
        req_content = f.read()
        if "loglama>=" in req_content:
            issues.append("'loglama>=' in requirements.txt was not updated to 'loglama>='")
    
    with open(project_dir / "README.md", "r") as f:
        readme_content = f.read()
        if "pip install loglama" in readme_content:
            issues.append("'pip install loglama' in README.md was not updated to 'pip install loglama'")
    
    return issues


def main():
    # Path to the migration script
    script_path = Path(__file__).parent / "migrate_to_loglama.py"
    
    if not script_path.exists():
        print(f"Error: Migration script not found at {script_path}")
        return 1
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating sample project in {temp_dir}...")
        project_dir = create_sample_project(temp_dir)
        
        # First run in report-only mode
        print("\nRunning migration script in report-only mode...")
        result = run_migration_script(project_dir, script_path, report_only=True)
        print(f"Exit code: {result.returncode}")
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        
        # Then run for real
        print("\nRunning migration script for real...")
        result = run_migration_script(project_dir, script_path, report_only=False)
        print(f"Exit code: {result.returncode}")
        print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
        
        # Verify the migration
        print("\nVerifying migration...")
        issues = verify_migration(project_dir)
        
        if issues:
            print("Migration issues found:")
            for issue in issues:
                print(f"- {issue}")
            return 1
        else:
            print("Migration successful! All PyLogs references were updated to LogLama.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
