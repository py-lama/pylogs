# Badge Setup Instructions for LogLama

## Quick Setup

1. **Create assets directory** in your repository root:
   ```bash
   mkdir -p assets
   ```

2. **Save the logo** as `loglama-logo.svg`

3. **Replace the top of your README.md** with the badges section

## Badge Configuration

### Required Actions

Some badges require additional setup to work properly:

#### 1. GitHub Actions CI Badge
Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        make setup
    
    - name: Run tests
      run: |
        make test
    
    - name: Run linting
      run: |
        make lint
```

#### 2. Code Coverage (Codecov)
Add to your CI workflow:

```yaml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

#### 3. PyPI Badge
Will work automatically once you publish to PyPI with:
```bash
make publish-full
```

### Optional Service Integrations

#### Code Climate
1. Go to [CodeClimate.com](https://codeclimate.com)
2. Add your repository
3. Replace the badge URL with your project's ID

#### SonarCloud
1. Go to [SonarCloud.io](https://sonarcloud.io)
2. Import your GitHub repository
3. Replace the badge URL with your project key

#### Documentation Badge
If you set up documentation hosting:
- **GitHub Pages**: Update URL to your GitHub Pages site
- **Read the Docs**: Update URL to your RTD project
- **Custom docs**: Update URL to your documentation site

## Alternative Badge Variations

### Minimal Badge Set (for new projects)
```markdown
[![PyPI version](https://badge.fury.io/py/loglama.svg)](https://badge.fury.io/py/loglama)
[![Python versions](https://img.shields.io/pypi/pyversions/loglama.svg)](https://pypi.org/project/loglama/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/py-lama/loglama/workflows/CI/badge.svg)](https://github.com/py-lama/loglama/actions)
```

### Extended Badge Set (for mature projects)
Add these badges as your project grows:
```markdown
[![Documentation Status](https://readthedocs.org/projects/loglama/badge/?version=latest)](https://loglama.readthedocs.io/en/latest/)
[![Maintainability](https://api.codeclimate.com/v1/badges/a99a88d28ad37a79dbf6/maintainability)](https://codeclimate.com/github/py-lama/loglama/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/a99a88d28ad37a79dbf6/test_coverage)](https://codeclimate.com/github/py-lama/loglama/test_coverage)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/loglama)](https://pypi.org/project/loglama/)
```

## Logo Variations

### Horizontal Logo (for headers)
The provided logo is optimized for README headers and documentation.

### Icon Only (for favicons)
Extract just the icon portion:
```svg
<svg viewBox="0 0 70 80" xmlns="http://www.w3.org/2000/svg">
  <!-- Extract the document icon and Py symbol from the main logo -->
</svg>
```

### Dark Mode Version
For dark backgrounds, create a version with light colors:
- Change text to white/light gray
- Adjust gradients for better contrast
- Use lighter stroke colors

## Badge Customization

### Color Scheme Matching
All badges use colors that complement the logo:
- **Primary Blue**: `#3b82f6` (matches logo gradient)
- **Success Green**: `#10b981` (matches accent)
- **Warning Yellow**: `#f59e0b`
- **Error Red**: `#ef4444`

### Custom Badges
Create custom badges using [Shields.io](https://shields.io/):

```markdown
![Custom Badge](https://img.shields.io/badge/PyLama-Ecosystem-3b82f6?style=flat&logo=python)
![Status](https://img.shields.io/badge/Status-Active-10b981?style=flat)
![Logging](https://img.shields.io/badge/Logging-Multi--Output-1d4ed8?style=flat)
```

## Maintenance

### Keeping Badges Updated
- **Automated**: Most badges update automatically
- **Manual**: Update version numbers in custom badges when releasing
- **Monitoring**: Regularly check that all badges are working

### Badge Health Check
Periodically verify:
- [ ] All badges load correctly
- [ ] Links point to correct resources
- [ ] No broken or outdated badges
- [ ] Consistent styling across badges

## Troubleshooting

### Common Issues

1. **Badge not updating**: Clear browser cache or check service status
2. **Wrong repository**: Ensure URLs point to correct GitHub repository
3. **Build badge failing**: Check GitHub Actions configuration
4. **Coverage badge missing**: Ensure coverage reports are uploaded

### Badge Service Status
- [Shields.io Status](https://status.shields.io/)
- [GitHub Status](https://www.githubstatus.com/)
- [PyPI Status](https://status.python.org/)