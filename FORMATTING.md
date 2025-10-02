# Code Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and linting.

## Installation

Install development dependencies including ruff:

```bash
# Using pip
pip install -e ".[dev]"

# Or install just ruff
pip install ruff
```

## Usage

### Format code
```bash
# Format all Python files
ruff format .

# Format specific files
ruff format src/gmb/ app.py tests/

# Check what would be formatted (dry run)
ruff format --check .
```

### Lint code
```bash
# Lint all Python files
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Lint specific files
ruff check src/gmb/ app.py tests/
```

### Pre-commit
You can also set up ruff to run automatically before each commit:

```bash
pip install pre-commit
pre-commit install
```

## Configuration

Ruff is configured in `pyproject.toml`:
- Line length: 100 characters
- Target Python version: 3.13
- Linting rules: E (pycodestyle errors), F (pyflakes), I (isort), W (warnings), UP (pyupgrade)
- Format style: double quotes, space indentation
