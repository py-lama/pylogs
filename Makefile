# PyLogs Makefile

# Default values that can be overridden
PORT ?= 5000
HOST ?= 127.0.0.1
PYTHON ?= python3
VENV_NAME ?= venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
LOG_DIR ?= ./logs
DB_PATH ?= $(LOG_DIR)/pylogs.db
EXAMPLE_DB_PATH ?= $(LOG_DIR)/example.db

.PHONY: all setup venv install test test-unit test-integration test-ansible lint format clean run-api run-web run-example view-logs run-integration help

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

# Run web interface
run-web: venv
	@echo "Starting PyLogs web interface on $(HOST):$(PORT)..."
	@$(VENV_ACTIVATE) && python -m pylogs.cli.web_viewer --host $(HOST) --port $(PORT) --db $(DB_PATH)

# Run CLI
run-cli: venv
	@echo "Starting PyLogs CLI..."
	@$(VENV_ACTIVATE) && python -m pylogs.cli.main

# Run example application
run-example: venv
	@echo "Running example application..."
	@mkdir -p $(LOG_DIR)
	@$(VENV_ACTIVATE) && python examples/example_app.py --requests 20 --log-dir $(LOG_DIR) --db-path $(EXAMPLE_DB_PATH) --json

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
	@echo "  make setup           - Create virtual environment and install dependencies"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-ansible    - Run Ansible tests"
	@echo "  make lint            - Run linting checks"
	@echo "  make format          - Format code with black and isort"
	@echo "  make run-api         - Run the API server"
	@echo "  make run-web         - Run the web interface for viewing logs"
	@echo "  make run-cli         - Run the command-line interface"
	@echo "  make run-example     - Run the example application"
	@echo "  make view-logs       - View logs from the example application"
	@echo "  make run-integration - Run the integration script"
	@echo "  make clean           - Clean up generated files"
	@echo ""
	@echo "You can override default values, e.g.: make run-web PORT=8080 HOST=0.0.0.0"
	@echo "Default log directory: $(LOG_DIR)"
	@echo "Default database path: $(DB_PATH)"
