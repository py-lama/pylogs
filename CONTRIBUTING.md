# Contributing to LogLama

Thank you for your interest in contributing to LogLama! This document provides comprehensive guidelines for contributors to help maintain code quality and consistency across the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style and Standards](#code-style-and-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Publishing and Releases](#publishing-and-releases)
- [Community Guidelines](#community-guidelines)
- [Getting Help](#getting-help)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Make (for using Makefile commands)
- Poetry (will be installed during setup)

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/loglama.git
   cd loglama
   ```
3. **Set up the development environment**:
   ```bash
   make setup
   ```
4. **Verify the installation**:
   ```bash
   make test
   ```

## Development Environment Setup

### Virtual Environment

LogLama uses Python virtual environments to manage dependencies. The setup is automated through the Makefile:

```bash
# Create virtual environment and install dependencies
make setup

# Activate the virtual environment manually (if needed)
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows
```

### Dependencies

LogLama uses Poetry for dependency management. Dependencies are defined in `pyproject.toml`:

- **Runtime dependencies**: Required for LogLama to function
- **Development dependencies**: Required for development, testing, and publishing

### Environment Configuration

Create a `.env` file for local development:

```bash
cp env.example .env
```

Key configuration options:
```bash
# Logging Configuration
LOGLAMA_LOG_LEVEL=DEBUG
LOGLAMA_LOG_DIR=./logs
LOGLAMA_CONSOLE_ENABLED=true
LOGLAMA_FILE_ENABLED=true
LOGLAMA_JSON_LOGS=false
LOGLAMA_STRUCTURED_LOGGING=false

# Database Configuration
LOGLAMA_DB_LOGGING=true
LOGLAMA_DB_PATH=./logs/loglama.db

# Web Interface Configuration
LOGLAMA_WEB_PORT=8081
LOGLAMA_WEB_HOST=127.0.0.1
LOGLAMA_WEB_DEBUG=true
```

## Project Structure

```
loglama/
├── loglama/                 # Main package
│   ├── core/              # Core logging functionality
│   ├── cli/               # Command-line interface
│   ├── api/               # REST API server
│   ├── web/               # Web interface
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── ansible/           # Ansible playbooks for testing
├── examples/              # Example applications
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── Makefile              # Development commands
├── pyproject.toml        # Project configuration
└── README.md             # Project overview
```

### Key Components

- **`loglama/core/`**: Core logging functionality, logger configuration, and context management
- **`loglama/cli/`**: Command-line interface for interacting with logs
- **`loglama/api/`**: RESTful API for programmatic access to logs
- **`loglama/web/`**: Web interface for log visualization and management
- **`loglama/utils/`**: Common utilities and helper functions

## Development Workflow

### 1. Choose an Issue

- Look for issues labeled `good first issue` for beginners
- Check the issue tracker for bugs and feature requests
- If working on something new, create an issue first to discuss it

### 2. Create a Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/issue-description

# For documentation
git checkout -b docs/improvement-description
```

### 3. Make Changes

- Follow the [Code Style and Standards](#code-style-and-standards)
- Write tests for new functionality
- Update documentation as needed
- Keep commits small and focused

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Run code quality checks
make lint
```

### 5. Format Your Code

```bash
# Format code automatically
make format
```

## Code Style and Standards

### Python Code Style

LogLama follows PEP 8 with some specific conventions:

- **Line length**: Maximum 88 characters (Black default)
- **Import organization**: Organized with `isort`
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Required for all public classes, functions, and methods

### Code Quality Tools

- **Black**: Automatic code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **mypy**: Static type checking

### Example Code Style

```python
from typing import Optional, Dict, Any
import logging
from loglama.core.context import LogContext


class ExampleLogger:
    """Example logger class demonstrating LogLama conventions.
    
    Args:
        name: The logger name, used to identify the logger instance
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to enable console output
        file: Whether to enable file output
        database: Whether to enable database logging
        **kwargs: Additional configuration options
    
    Returns:
        Configured logger instance
    
    Raises:
        ValueError: If an invalid logging level is provided
        IOError: If file logging is enabled but the file cannot be created
    
    Example:
        >>> logger = configure_logging(
        ...     name="my_app",
        ...     level="DEBUG",
        ...     console=True,
        ...     file=True,
        ...     file_path="/var/log/my_app.log"
        ... )
        >>> logger.info("Application started")
    """
```

## Submitting Changes

### Pull Request Process

1. **Ensure your branch is up to date**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run the full test suite**:
   ```bash
   make test
   make lint
   ```

3. **Push your changes**:
   ```bash
   git push origin your-branch
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Description of changes made
   - Any breaking changes noted

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Testing
- [ ] Tests pass locally (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No unnecessary files included
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and quality checks
2. **Code Review**: Maintainers review code for quality and correctness
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, maintainers will merge the PR

## Publishing and Releases

### Version Management

LogLama uses semantic versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Bumping Versions

```bash
# Bump patch version (0.1.0 -> 0.1.1)
make version-patch

# Bump minor version (0.1.0 -> 0.2.0)
make version-minor

# Bump major version (0.1.0 -> 1.0.0)
make version-major
```

### Publishing Process

Only maintainers can publish to PyPI. The process is automated:

```bash
# Configure PyPI credentials (one-time setup)
make configure-pypi

# Full publishing workflow with all checks
make publish-full

# Quick publish (for hotfixes)
make publish-quick

# Dry run to test the process
make publish-dry-run
```

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version number is bumped appropriately
- [ ] Release notes are prepared
- [ ] Breaking changes are documented

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** in all interactions
- **Be constructive** when providing feedback
- **Be patient** with new contributors
- **Be inclusive** and welcoming to people of all backgrounds

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, and general discussion
- **Pull Requests**: Code reviews and technical discussions
- **GitHub Discussions**: Community questions and broader topics

### Reporting Issues

When reporting bugs:

1. **Search existing issues** first
2. **Use the issue template** provided
3. **Include reproduction steps**
4. **Provide system information**
5. **Include relevant logs**

Example bug report:
```markdown
## Bug Description
Brief description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.10.5]
- LogLama version: [e.g., 0.1.0]

## Additional Context
Any other relevant information.
```

### Feature Requests

When requesting features:

1. **Describe the problem** the feature would solve
2. **Explain the proposed solution**
3. **Consider alternative solutions**
4. **Assess the impact** on existing functionality

## Development Tips

### Debugging

Use the example application to test changes:

```bash
# Generate sample logs
make run-example

# View logs in web interface
make view-logs

# Use CLI to inspect logs
make run-cli
```

### Performance Considerations

- **Minimize I/O operations** in hot paths
- **Use appropriate data structures** for the task
- **Consider memory usage** for large log files
- **Profile code** when optimizing performance

### Security Considerations

- **Validate all inputs** from external sources
- **Sanitize log messages** to prevent injection attacks
- **Use parameterized queries** for database operations
- **Be careful with file paths** to prevent directory traversal

### Common Patterns

#### Adding a New CLI Command

```python
# In loglama/cli/commands/new_command.py
import click
from loglama.core.logger import get_logger


@click.command()
@click.option('--param', help='Parameter description')
def new_command(param: str) -> None:
    """Description of the new command."""
    logger = get_logger("cli.new_command")
    logger.info(f"Executing new command with param: {param}")
    # Command implementation
```

#### Adding a New API Endpoint

```python
# In loglama/api/routes/new_route.py
from flask import Blueprint, request, jsonify
from loglama.core.logger import get_logger

new_bp = Blueprint('new', __name__)
logger = get_logger("api.new")


@new_bp.route('/api/new', methods=['GET'])
def get_new_data():
    """Get new data endpoint."""
    logger.info("New endpoint accessed")
    # Implementation
    return jsonify({"status": "success", "data": []})
```

## Getting Help

### Documentation

- **README.md**: Project overview and quick start
- **API Documentation**: Available at `/api/docs` when running the API server
- **Code Examples**: Check the `examples/` directory

### Support Channels

1. **GitHub Issues**: For bug reports and feature requests
2. **GitHub Discussions**: For questions and community support
3. **Code Comments**: Inline documentation in the codebase

### Troubleshooting

Common issues and solutions:

#### Tests Failing
```bash
# Ensure dependencies are up to date
make clean
make setup
make test
```

#### Import Errors
```bash
# Ensure LogLama is installed in development mode
pip install -e .
```

#### Database Issues
```bash
# Clear the database and regenerate
rm -f logs/loglama.db
make run-example
```

#### Web Interface Not Loading
```bash
# Check if the database exists and has data
ls -la logs/
make run-example  # Generate sample data
make view-logs    # Start web interface
```

### Best Practices Summary

1. **Start small**: Begin with small, focused changes
2. **Test thoroughly**: Write tests and run the full suite
3. **Document changes**: Update documentation and add examples
4. **Follow conventions**: Use established patterns and styles
5. **Ask questions**: Don't hesitate to ask for help or clarification
6. **Be patient**: Code review and feedback are part of the process

## Contributing Examples

### Example 1: Adding a New Log Filter

```python
# Add to loglama/core/filters.py
class DateRangeFilter:
    """Filter logs by date range."""
    
    def __init__(self, start_date: str, end_date: str):
        self.start_date = start_date
        self.end_date = end_date
    
    def apply(self, logs: List[LogEntry]) -> List[LogEntry]:
        """Apply date range filter to logs."""
        # Implementation here
        return filtered_logs
```

### Example 2: Adding a New Output Format

```python
# Add to loglama/core/formatters.py
class XMLFormatter:
    """Format logs as XML."""
    
    def format(self, record: LogRecord) -> str:
        """Format a log record as XML."""
        # Implementation here
        return xml_string
```

### Example 3: Adding Configuration Option

```python
# Add to environment configuration
LOGLAMA_XML_OUTPUT = os.getenv("LOGLAMA_XML_OUTPUT", "false").lower() == "true"

# Use in logger configuration
if config.xml_output:
    handler.setFormatter(XMLFormatter())
```

---

Thank you for contributing to LogLama! Your contributions help make logging better for everyone in the PyLama ecosystem. The logger name
        level: The logging level
        config: Optional configuration dictionary
    """
    
    def __init__(
        self, 
        name: str, 
        level: str = "INFO",
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.level = level
        self.config = config or {}
        self._logger = logging.getLogger(name)
    
    def log_with_context(self, message: str, **context: Any) -> None:
        """Log a message with context.
        
        Args:
            message: The log message
            **context: Additional context fields
        """
        with LogContext(**context):
            self._logger.info(message)
```

### Commit Message Convention

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(cli): add log filtering by date range
fix(web): resolve pagination issue in log viewer
docs(api): update API endpoint documentation
test(core): add tests for context management
```

## Testing Guidelines

### Test Structure

Tests are organized in three categories:

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test components working together
3. **Ansible Tests** (`tests/ansible/`): Test shell scripts and system integration

### Writing Tests

Use pytest for all tests:

```python
import pytest
from loglama.core.logger import get_logger
from loglama.core.context import LogContext


class TestLogger:
    """Test suite for logger functionality."""
    
    def test_basic_logging(self):
        """Test basic logging functionality."""
        logger = get_logger("test")
        # Test implementation here
        assert logger is not None
    
    def test_context_logging(self):
        """Test context-aware logging."""
        logger = get_logger("test")
        
        with LogContext(user_id="123"):
            logger.info("Test message")
        
        # Verify context was captured
        # Test implementation here
    
    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """Provide a temporary database path for testing."""
        return tmp_path / "test.db"
```

### Test Coverage

- Aim for 90%+ test coverage
- All new features must include tests
- Bug fixes should include regression tests

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/unit/test_logger.py -v

# Run specific test method
pytest tests/unit/test_logger.py::TestLogger::test_basic_logging -v
```

## Documentation

### Code Documentation

- All public classes, functions, and methods must have docstrings
- Use Google-style docstrings
- Include type information in docstrings when helpful

### User Documentation

- Update README.md for new features
- Add examples for new functionality
- Update CLI help text when adding new commands

### API Documentation

- Document all API endpoints
- Include request/response examples
- Update OpenAPI specifications if applicable
