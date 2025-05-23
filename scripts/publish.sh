#!/bin/bash

# LogLama Publishing Script
# This script automates the process of building and publishing LogLama to PyPI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON=${PYTHON:-python3}
VENV_NAME=${VENV_NAME:-venv}
VENV_ACTIVATE=". ${VENV_NAME}/bin/activate"

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_git_status() {
    print_status "Checking git status..."

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes:"
        git status --short
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Aborted by user"
            exit 1
        fi
    fi

    print_success "Git status check passed"
}

check_version() {
    print_status "Checking version..."

    # Get current version from pyproject.toml
    CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    print_status "Current version: $CURRENT_VERSION"

    # Check if version tag already exists
    if git tag | grep -q "^v$CURRENT_VERSION$"; then
        print_error "Version tag v$CURRENT_VERSION already exists"
        print_status "Available tags:"
        git tag | tail -5
        exit 1
    fi

    print_success "Version check passed"
}

run_tests() {
    print_status "Running tests..."

    if [ ! -d "$VENV_NAME" ]; then
        print_error "Virtual environment not found. Run 'make setup' first."
        exit 1
    fi

    # Run unit tests
    print_status "Running unit tests..."
    eval "$VENV_ACTIVATE && pytest tests/unit/ -v"

    # Run integration tests
    print_status "Running integration tests..."
    eval "$VENV_ACTIVATE && pytest tests/integration/ -v"

    print_success "All tests passed"
}

run_quality_checks() {
    print_status "Running code quality checks..."

    # Run linting
    print_status "Running flake8..."
    eval "$VENV_ACTIVATE && flake8 loglama/"

    # Run type checking
    print_status "Running mypy..."
    eval "$VENV_ACTIVATE && mypy loglama/"

    print_success "Quality checks passed"
}

build_package() {
    print_status "Building package..."

    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/

    # Build with Poetry
    eval "$VENV_ACTIVATE && poetry build"

    # Verify build artifacts
    if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
        print_error "Build failed - no artifacts found in dist/"
        exit 1
    fi

    print_success "Package built successfully"
    ls -la dist/
}

publish_to_testpypi() {
    print_status "Publishing to TestPyPI..."

    # Check if TestPyPI token is configured
    if ! eval "$VENV_ACTIVATE && poetry config pypi-token.testpypi" > /dev/null 2>&1; then
        print_warning "TestPyPI token not configured"
        print_status "Configure it with: poetry config pypi-token.testpypi <your-token>"
        read -p "Skip TestPyPI publishing? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        return 0
    fi

    # Publish to TestPyPI
    eval "$VENV_ACTIVATE && poetry publish -r testpypi"

    print_success "Published to TestPyPI"
    print_status "Test installation with:"
    echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ loglama"
}

publish_to_pypi() {
    print_status "Publishing to PyPI..."

    # Check if PyPI token is configured
    if ! eval "$VENV_ACTIVATE && poetry config pypi-token.pypi" > /dev/null 2>&1; then
        print_error "PyPI token not configured"
        print_status "Configure it with: poetry config pypi-token.pypi <your-token>"
        exit 1
    fi

    # Final confirmation
    print_warning "This will publish to PyPI (production). This action cannot be undone."
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Aborted by user"
        exit 1
    fi

    # Publish to PyPI
    eval "$VENV_ACTIVATE && poetry publish"

    print_success "Published to PyPI"
    print_status "Install with: pip install loglama"
}

create_git_tag() {
    print_status "Creating git tag..."

    CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

    # Create and push tag
    git tag "v$CURRENT_VERSION"
    git push origin "v$CURRENT_VERSION"

    print_success "Created and pushed tag v$CURRENT_VERSION"
}

# Main script
main() {
    print_status "Starting LogLama publishing process..."

    # Parse command line arguments
    SKIP_TESTS=false
    SKIP_TESTPYPI=false
    SKIP_TAG=false
    DRY_RUN=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-testpypi)
                SKIP_TESTPYPI=true
                shift
                ;;
            --skip-tag)
                SKIP_TAG=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-tests      Skip running tests"
                echo "  --skip-testpypi   Skip publishing to TestPyPI"
                echo "  --skip-tag        Skip creating git tag"
                echo "  --dry-run         Run all checks but don't publish"
                echo "  -h, --help        Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Pre-flight checks
    check_git_status
    check_version

    # Run tests unless skipped
    if [ "$SKIP_TESTS" = false ]; then
        run_tests
        run_quality_checks
    else
        print_warning "Skipping tests"
    fi

    # Build package
    build_package

    # Dry run mode - stop here
    if [ "$DRY_RUN" = true ]; then
        print_warning "Dry run mode - stopping before publishing"
        exit 0
    fi

    # Publish to TestPyPI unless skipped
    if [ "$SKIP_TESTPYPI" = false ]; then
        publish_to_testpypi

        # Ask user to test the package
        print_status "Please test the package from TestPyPI before proceeding"
        read -p "Continue with PyPI publishing? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Stopped before PyPI publishing"
            exit 0
        fi
    else
        print_warning "Skipping TestPyPI publishing"
    fi

    # Publish to PyPI
    publish_to_pypi

    # Create git tag unless skipped
    if [ "$SKIP_TAG" = false ]; then
        create_git_tag
    else
        print_warning "Skipping git tag creation"
    fi

    print_success "Publishing process completed successfully!"
    print_status "Package is now available at: https://pypi.org/project/loglama/"
}

# Run main function
main "$@"