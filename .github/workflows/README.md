# GitHub Actions Workflows

This directory contains CI/CD workflows for the GMB Fantasy Football project.

## Workflows

### CI Pipeline (`ci.yml`)

Runs on every push and pull request to the `main` branch.

**Test Job:**
- Runs on Python 3.13
- Installs all dependencies
- Executes pytest with coverage
- Uploads coverage report to Codecov

**Lint Job:**
- Checks code formatting with ruff
- Runs ruff linter
- Performs mypy type checking

## Status Badges

Add these to your README.md:

```markdown
![CI](https://github.com/chris-nigh/gmb/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/chris-nigh/gmb/branch/main/graph/badge.svg)](https://codecov.io/gh/chris-nigh/gmb)
```

## Running Locally

To run the same checks that CI runs:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest

# Check formatting
ruff format --check .

# Run linter
ruff check .

# Type checking
mypy src/gmb --ignore-missing-imports
```

## Troubleshooting

**Coverage upload fails:**
- This is optional and won't fail the build
- To enable: Add `CODECOV_TOKEN` secret to your GitHub repository
- Get token from: https://codecov.io/gh/chris-nigh/gmb

**Tests fail locally but pass in CI:**
- Make sure you have all dev dependencies: `pip install -e ".[dev]"`
- Check Python version: `python --version` (should be 3.13)
- Clear cache: `pytest --cache-clear`

**Linting fails:**
- Auto-fix issues: `ruff check --fix .`
- Format code: `ruff format .`
