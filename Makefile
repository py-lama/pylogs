# LogLama Makefile

# Default values that can be overridden
PORT ?= 8081
HOST ?= 127.0.0.1
PYTHON ?= python3
VENV_NAME ?= venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
LOG_DIR ?= ./logs
DB_PATH ?= $(LOG_DIR)/loglama.db
EXAMPLE_DB_PATH ?= $(LOG_DIR)/example.db

.PHONY: all setup venv install test test-unit test-integration test-ansible lint format clean run-api web run-example view-logs run-integration run-examples build publish publish-test check-publish help

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
	@$(VENV_ACTIVATE) && pip install poetry
	@$(VENV_ACTIVATE) && poetry install --with dev
	@echo "Dependencies installed."

# Setup the project (create venv and install dependencies)
setup: install
	@echo "LogLama setup completed."

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
	@$(VENV_ACTIVATE) && ansible-playbook tests/ansible/test_loglama.yml -v

# Run linting checks
lint: venv
	@echo "Running linting checks..."
	@$(VENV_ACTIVATE) && flake8 loglama/
	@$(VENV_ACTIVATE) && mypy loglama/

# Format code
format: venv
	@echo "Formatting code..."
	@$(VENV_ACTIVATE) && black loglama/
	@$(VENV_ACTIVATE) && isort loglama/

# Build package with Poetry
build: venv
	@echo "Building package with Poetry..."
	@$(VENV_ACTIVATE) && poetry build
	@echo "Package built successfully. Artifacts in dist/"

# Check if package is ready for publishing
check-publish: venv lint test
	@echo "Checking if package is ready for publishing..."
	@$(VENV_ACTIVATE) && poetry check
	@echo "Package is ready for publishing."

# Publish to TestPyPI
publish-test: venv build
	@echo "Publishing to TestPyPI..."
	@$(VENV_ACTIVATE) && poetry publish -r testpypi
	@echo "Published to TestPyPI. Test with:"
	@echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ loglama"

# Publish to PyPI (production)
publish: venv check-publish
	@echo "Publishing to PyPI..."
	@echo "WARNING: This will publish to PyPI (production). This action cannot be undone."
	@read -p "Are you sure you want to continue? (y/N): " confirm && [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]
	@$(VENV_ACTIVATE) && poetry publish
	@echo "Published to PyPI. Install with: pip install loglama"

# Full publishing workflow using the publish script
publish-full: venv
	@echo "Running full publishing workflow..."
	@chmod +x scripts/publish.sh
	@./scripts/publish.sh

# Dry run of the publishing process
publish-dry-run: venv
	@echo "Running dry run of publishing process..."
	@chmod +x scripts/publish.sh
	@./scripts/publish.sh --dry-run

# Quick publish (skip tests and TestPyPI)
publish-quick: venv
	@echo "Running quick publish (skip tests and TestPyPI)..."
	@chmod +x scripts/publish.sh
	@./scripts/publish.sh --skip-tests --skip-testpypi

# Configure PyPI credentials
configure-pypi: venv
	@echo "Configuring PyPI credentials..."
	@echo "You'll need API tokens from PyPI and TestPyPI"
	@echo "Get them from:"
	@echo "  PyPI: https://pypi.org/manage/account/token/"
	@echo "  TestPyPI: https://test.pypi.org/manage/account/token/"
	@echo ""
	@read -p "Enter PyPI token: " pypi_token && \
		$(VENV_ACTIVATE) && poetry config pypi-token.pypi $$pypi_token
	@read -p "Enter TestPyPI token: " testpypi_token && \
		$(VENV_ACTIVATE) && poetry config pypi-token.testpypi $$testpypi_token
	@echo "Credentials configured successfully."

# Show current version
version: venv
	@echo "Current version:"
	@$(VENV_ACTIVATE) && poetry version

# Bump version (patch)
version-patch: venv
	@echo "Bumping patch version..."
	@$(VENV_ACTIVATE) && poetry version patch
	@git add pyproject.toml
	@git commit -m "Bump version to $$($(VENV_ACTIVATE) && poetry version -s)"

# Bump version (minor)
version-minor: venv
	@echo "Bumping minor version..."
	@$(VENV_ACTIVATE) && poetry version minor
	@git add pyproject.toml
	@git commit -m "Bump version to $$($(VENV_ACTIVATE) && poetry version -s)"

# Bump version (major)
version-major: venv
	@echo "Bumping major version..."
	@$(VENV_ACTIVATE) && poetry version major
	@git add pyproject.toml
	@git commit -m "Bump version to $$($(VENV_ACTIVATE) && poetry version -s)"

# Run API server
run-api: venv
	@echo "Starting LogLama API server on $(HOST):$(PORT)..."
	@$(VENV_ACTIVATE) && python -m loglama.api.server --host $(HOST) --port $(PORT)

# Run web interface (legacy method)
run-web: web

# Run web interface with new command
web: venv
	@echo "Starting LogLama web interface on $(HOST):$(PORT)..."
	@$(VENV_ACTIVATE) && python -m loglama.cli.main web --host $(HOST) --port $(PORT) --db $(DB_PATH)

# Run CLI
run-cli: venv
	@echo "Starting LogLama CLI..."
	@$(VENV_ACTIVATE) && python -m loglama.cli.main

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
	@$(VENV_ACTIVATE) && python -m loglama.cli.web_viewer --host $(HOST) --port $(PORT) --db $(EXAMPLE_DB_PATH)

# Run integration script to integrate LogLama into a component
run-integration: venv
	@echo "Running LogLama integration script..."
	@$(VENV_ACTIVATE) && python scripts/integrate_loglama.py --all

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "Cleanup completed."

# Display help information
help:
	@echo "LogLama Makefile Commands:"
	@echo ""
	@echo "Setup and Development:"
	@echo "  make setup          - Set up the project (create venv and install dependencies)"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-ansible   - Run Ansible tests"
	@echo "  make lint           - Run linting checks"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean up generated files"
	@echo ""
	@echo "Version Management:"
	@echo "  make version        - Show current version"
	@echo "  make version-patch  - Bump patch version (0.1.0 -> 0.1.1)"
	@echo "  make version-minor  - Bump minor version (0.1.0 -> 0.2.0)"
	@echo "  make version-major  - Bump major version (0.1.0 -> 1.0.0)"
	@echo ""
	@echo "Building and Publishing:"
	@echo "  make build          - Build package with Poetry"
	@echo "  make check-publish  - Check if package is ready for publishing"
	@echo "  make configure-pypi - Configure PyPI and TestPyPI credentials"
	@echo "  make publish-test   - Publish to TestPyPI"
	@echo "  make publish        - Publish to PyPI (production)"
	@echo "  make publish-full   - Run full publishing workflow with checks"
	@echo "  make publish-dry-run - Dry run of publishing process"
	@echo "  make publish-quick  - Quick publish (skip tests and TestPyPI)"
	@echo ""
	@echo "Running LogLama:"
	@echo "  make run-api        - Run API server"
	@echo "  make web            - Run web interface"
	@echo "  make run-cli        - Run CLI"
	@echo ""
	@echo "Examples and Integration:"
	@echo "  make run-example    - Run example application"
	@echo "  make run-examples   - Run multi-language examples"
	@echo "  make run-shell-examples - Run shell examples"
	@echo "  make view-logs      - View logs from example application"
	@echo "  make run-integration - Run integration script"
	@echo ""
	@echo "Environment variables that can be set:"
	@echo "  PORT              - Port for web/API server (default: 8081)"
	@echo "  HOST              - Host for web/API server (default: 127.0.0.1)"
	@echo "  PYTHON            - Python interpreter to use (default: python3)"
	@echo "  VENV_NAME         - Name of virtual environment (default: venv)"
	@echo "  LOG_DIR           - Directory for logs (default: ./logs)"
	@echo "  DB_PATH           - Path to SQLite database (default: ./logs/loglama.db)"
	@echo "  EXAMPLE_DB_PATH   - Path to example SQLite database (default: ./logs/example.db)"
	@echo ""
	@echo "Example usage:"
	@echo "  make web PORT=8081 HOST=0.0.0.0"
	@echo "  make run-examples LOG_DIR=/tmp/logs"
	@echo "  make publish-test"
	@echo "  make version-patch && make publish-full"