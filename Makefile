# PyLogs Makefile

# Default values that can be overridden
PORT ?= 8081
HOST ?= 127.0.0.1
PYTHON ?= python3
VENV_NAME ?= venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
LOG_DIR ?= ./logs
DB_PATH ?= $(LOG_DIR)/pylogs.db
EXAMPLE_DB_PATH ?= $(LOG_DIR)/example.db

.PHONY: all setup venv install test test-unit test-integration test-ansible lint format clean run-api web run-example view-logs run-integration run-examples help

all: help

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV_NAME)
	@echo "Virtual environment created at $(VENV_NAME)/"

# Install dependencies
install: venv
	@echo "Installing dependencies..."
	@$(VENV_ACTIVATE) && pip install --upgrade pip
	@$(VENV_ACTIVATE) && pip install -e .
	@$(VENV_ACTIVATE) && pip install -e .[dev]
	@echo "Dependencies installed."

# Setup the project (create venv and install dependencies)
setup: install
	@echo "PyLogs setup completed."

# Run all tests
test: test-unit test-integration
	@echo "All tests completed."

# Run unit tests
test-unit: venv
	@echo "Running unit tests..."
	@$(VENV_ACTIVATE) && pytest tests/unit/ -v

# Run integration tests
test-integration: venv
	@echo "Running integration tests..."
	@$(VENV_ACTIVATE) && pytest tests/integration/ -v

# Run Ansible tests
test-ansible: venv
	@echo "Running Ansible tests..."
	@$(VENV_ACTIVATE) && ansible-playbook tests/ansible/test_pylogs.yml -v

# Run linting checks
lint: venv
	@echo "Running linting checks..."
	@$(VENV_ACTIVATE) && flake8 pylogs/
	@$(VENV_ACTIVATE) && mypy pylogs/

# Format code
format: venv
	@echo "Formatting code..."
	@$(VENV_ACTIVATE) && black pylogs/
	@$(VENV_ACTIVATE) && isort pylogs/

# Run API server
run-api: venv
	@echo "Starting PyLogs API server on $(HOST):$(PORT)..."
	@$(VENV_ACTIVATE) && python -m pylogs.api.server --host $(HOST) --port $(PORT)

# Run web interface (legacy method)
run-web: web

# Run web interface with new command
web: venv
	@echo "Starting PyLogs web interface on $(HOST):$(PORT)..."
	@$(VENV_ACTIVATE) && python -m pylogs.cli.main web --host $(HOST) --port $(PORT) --db $(DB_PATH)

# Run CLI
run-cli: venv
	@echo "Starting PyLogs CLI..."
	@$(VENV_ACTIVATE) && python -m pylogs.cli.main

# Run example application
run-example: venv
	@echo "Running example application..."
	@mkdir -p $(LOG_DIR)
	@$(VENV_ACTIVATE) && python examples/example_app.py --requests 20 --log-dir $(LOG_DIR) --db-path $(EXAMPLE_DB_PATH) --json

# Run multi-language examples
run-examples: venv
	@echo "Running multi-language examples..."
	@mkdir -p $(LOG_DIR)
	@$(VENV_ACTIVATE) && python examples/multilanguage_examples.py

# Run shell examples
run-shell-examples: venv
	@echo "Running shell examples..."
	@mkdir -p $(LOG_DIR)
	@$(VENV_ACTIVATE) && bash examples/shell_examples.sh

# View logs from example application
view-logs: venv
	@echo "Starting web interface to view example logs on $(HOST):$(PORT)..."
	@$(VENV_ACTIVATE) && python -m pylogs.cli.web_viewer --host $(HOST) --port $(PORT) --db $(EXAMPLE_DB_PATH)

# Run integration script to integrate PyLogs into a component
run-integration: venv
	@echo "Running PyLogs integration script..."
	@$(VENV_ACTIVATE) && python scripts/integrate_pylogs.py --all

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed."

# Display help information
help:
	@echo "PyLogs Makefile Commands:"
	@echo "  make setup          - Set up the project (create venv and install dependencies)"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-ansible   - Run Ansible tests"
	@echo "  make lint           - Run linting checks"
	@echo "  make format         - Format code"
	@echo "  make run-api        - Run API server"
	@echo "  make web            - Run web interface (new command)"
	@echo "  make run-web        - Run web interface (legacy method)"
	@echo "  make run-cli        - Run CLI"
	@echo "  make run-example    - Run example application"
	@echo "  make run-examples   - Run multi-language examples"
	@echo "  make run-shell-examples - Run shell examples"
	@echo "  make view-logs      - View logs from example application"
	@echo "  make run-integration - Run integration script"
	@echo "  make clean          - Clean up generated files"
	@echo ""
	@echo "Environment variables that can be set:"
	@echo "  PORT              - Port for web/API server (default: 8081)"
	@echo "  HOST              - Host for web/API server (default: 127.0.0.1)"
	@echo "  PYTHON            - Python interpreter to use (default: python3)"
	@echo "  VENV_NAME         - Name of virtual environment (default: venv)"
	@echo "  LOG_DIR           - Directory for logs (default: ./logs)"
	@echo "  DB_PATH           - Path to SQLite database (default: ./logs/pylogs.db)"
	@echo "  EXAMPLE_DB_PATH   - Path to example SQLite database (default: ./logs/example.db)"
	@echo ""
	@echo "Example usage:"
	@echo "  make web PORT=8081 HOST=0.0.0.0"
	@echo "  make run-examples LOG_DIR=/tmp/logs"
