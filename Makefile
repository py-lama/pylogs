# PyLogs Makefile

# Default values that can be overridden
PORT ?= 5000
HOST ?= 127.0.0.1
PYTHON ?= python3
VENV_NAME ?= venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate

.PHONY: all setup venv install test lint format clean run-api run-web help

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

# Run tests
test: venv
	@echo "Running tests..."
	@$(VENV_ACTIVATE) && pytest tests/ -v

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
	@$(VENV_ACTIVATE) && python -m pylogs.web.app --host $(HOST) --port $(PORT)

# Run CLI
run-cli: venv
	@echo "Starting PyLogs CLI..."
	@$(VENV_ACTIVATE) && python -m pylogs.cli.main

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
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black and isort"
	@echo "  make run-api    - Run the API server (PORT=5000 HOST=127.0.0.1)"
	@echo "  make run-web    - Run the web interface (PORT=5000 HOST=127.0.0.1)"
	@echo "  make run-cli    - Run the command-line interface"
	@echo "  make clean      - Clean up generated files"
	@echo ""
	@echo "You can override default values, e.g.: make run-web PORT=8080 HOST=0.0.0.0"
