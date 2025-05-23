# Publishing Guide for LogLama with Grafana Integration

This guide provides instructions for preparing and publishing the LogLama package with Grafana integration capabilities.

## Package Preparation

### 1. Update Package Dependencies

Ensure your `pyproject.toml` includes the necessary dependencies for Grafana integration:

```toml
[tool.poetry.dependencies]
python = "^3.8"
flask = "^2.0.0"
sqlite3-utils = "^0.1.0"
# Add any other dependencies needed for Grafana integration

[tool.poetry.dev-dependencies]
pytest = "^7.0.0"
```

### 2. Include Example Files

Make sure the following files are included in your package:

- `examples/loglama-grafana/docker-compose.simple.yml`
- `examples/loglama-grafana/Dockerfile.simple`
- `examples/loglama-grafana/run-simple.sh`
- `examples/loglama-grafana/generate_logs_in_container.sh`
- `examples/loglama-grafana/grafana-provisioning/` (directory with all configuration files)
- `examples/loglama-grafana/INTEGRATION_GUIDE.md`

### 3. Update Documentation

Update the main README.md to mention Grafana integration capabilities:

```markdown
## Grafana Integration

LogLama can be integrated with Grafana for advanced visualization and monitoring. See the [Grafana Integration Guide](examples/loglama-grafana/INTEGRATION_GUIDE.md) for details.
```

## Publishing to PyPI

### 1. Version Bump

Bump the version in your `pyproject.toml` file:

```bash
cd /path/to/loglama
python scripts/simple_publish.py --bump-version
```

### 2. Build and Publish

Use the simplified publishing script we created earlier:

```bash
cd /path/to/loglama
python scripts/simple_publish.py
```

This will:
- Automatically bump the version number
- Build the package
- Publish to PyPI using the existing token configuration

Alternatively, you can use the token-checking script:

```bash
cd /path/to/loglama
python scripts/publish_with_token_check.py
```

## Publishing Docker Images

### 1. Build Docker Image

```bash
cd /path/to/loglama
docker build -t loglama:latest -f examples/loglama-grafana/Dockerfile.simple .
```

### 2. Tag for Docker Hub

```bash
docker tag loglama:latest yourusername/loglama:latest
docker tag loglama:latest yourusername/loglama:$(python -c "import toml; print(toml.load('pyproject.toml')['tool']['poetry']['version'])")
```

### 3. Push to Docker Hub

```bash
docker login
docker push yourusername/loglama:latest
docker push yourusername/loglama:$(python -c "import toml; print(toml.load('pyproject.toml')['tool']['poetry']['version'])")
```

## Testing the Published Package

### 1. Install from PyPI

```bash
pip install loglama
# or with specific version
pip install loglama==x.y.z
```

### 2. Test Grafana Integration

```bash
# Clone the examples repository or copy the example files
git clone https://github.com/py-lama/loglama-examples.git
cd loglama-examples/loglama-grafana

# Run the integration
./run-simple.sh
```

## Continuous Integration

Consider setting up GitHub Actions for automated testing and publishing:

1. Create `.github/workflows/publish.yml` for automated PyPI publishing
2. Create `.github/workflows/docker.yml` for automated Docker image building

## Release Notes

When publishing a new version, include information about the Grafana integration in your release notes:

```markdown
## v1.2.0

### New Features
- Added Grafana integration for advanced log visualization
- Included example Docker Compose setup for LogLama + Grafana
- Added automated dashboard provisioning

### Bug Fixes
- Fixed issue with SQLite database path in Docker containers
- Improved error handling in web interface
```

---

For more information on publishing Python packages, see the [Python Packaging User Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/).
