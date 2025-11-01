# GMB Project Instructions

These instructions apply to all conversations and tasks in this project.

## Python Environment

### UV Package Manager
- **ALWAYS use `uv`** for package management and running Python commands
- `uv` automatically detects and uses `.venv/` - **no activation needed**
- This project uses **Python 3.13** in the local venv
- Benefits of uv:
  - 10-100x faster than pip
  - Automatic virtual environment detection
  - Better dependency resolution
  - Consistent with project's Makefile and uv.lock

### Common UV Commands
- Install packages: `uv pip install <package>`
- Run tools in venv: `uv run <command>` (e.g., `uv run pytest`)
- Sync dependencies: `uv pip install -e .`
- Update lock file: `uv pip freeze > requirements.lock`

## Code Quality Standards

### Formatting and Linting
- **Always use ruff** for code formatting and linting
- Follow the project's existing style:
  - Line length: 100 characters
  - Quote style: double quotes
  - Target version: Python 3.13
- Before completing any task involving code changes:
  - Run `uv run ruff format .` to auto-format code
  - Run `uv run ruff check .` to check for linting issues
  - Run `uv run ruff check --fix .` if auto-fixable issues exist

### Type Checking
- **Maintain strict mypy compliance**
- All code must pass `uv run mypy src/gmb` with strict mode enabled
- Add type hints to all functions and methods
- Use proper type annotations from typing module when needed

### Testing
- **Create unit tests with good coverage** for all new features and bug fixes
- Place tests in the `tests/` directory following the `test_*.py` naming convention
- Aim for comprehensive coverage of:
  - Happy paths
  - Edge cases
  - Error conditions
- Run tests: `uv run pytest --cov=src/gmb --cov-report=term-missing`
- Ensure all tests pass before marking work complete

## File Management

### Cleanup
- **Clean up unneeded files** before committing:
  - CSV files generated from standalone runs (e.g., `*.csv` in project root)
  - Temporary data files
  - Debug output files
  - Any generated files not needed in version control
- Check for and remove files that should be in `.gitignore`

## Git Workflow

### Pre-commit Hooks
- This project uses **standard `pre-commit` framework** (see `.pre-commit-config.yaml`)
- Hooks automatically run on every commit to ensure CI checks pass locally
- Claude-specific cleanup hooks are configured in `.claude/hooks.md`
- The pre-commit hooks will:
  1. Auto-format code with ruff
  2. Auto-fix linting issues where possible
  3. Run type checking with mypy
  4. Run tests with coverage
  5. Perform standard file checks (trailing whitespace, file endings, etc.)

### Before Committing
- The pre-commit hooks will automatically verify:
  1. Tests pass with good coverage
  2. Ruff formatting is clean
  3. Ruff linting passes
  4. Mypy type checking passes
- Review the pre-commit hook output carefully
- If hooks fail, fix the issues and commit again
- Clean up any temporary/generated files (handled by `.claude/hooks.md` for Claude commits)

### Commit Messages
- Use clear, descriptive commit messages
- Follow conventional commit style when appropriate
- Include the Claude Code attribution footer:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

## Project-Specific Guidelines

### Code Organization
- Keep the modular structure: separate concerns between API clients (`espn.py`, `espn_keeper.py`), analytics (`oiwp.py`, `keeper.py`, `taylor_eras.py`), and visualization (`viz.py`)
- Place new analytics functions in appropriate modules
- Update `app.py` to integrate new features into the dashboard

### Dependencies
- Add new dependencies to `pyproject.toml` in the appropriate section (`dependencies` or `dev`)
- Keep numpy pinned to `<2.0.0` for compatibility with dash-bio
- Document any new dependencies in commit messages

### Documentation
- Update README.md if adding user-facing features
- Add docstrings to all new functions and classes
- Include type hints in function signatures (they serve as inline documentation)

### Vermont Theme
- Maintain the Vermont/Green Mountain Boys theme in visualizations
- Use the existing color schemes defined in `viz.py`
- Keep the visual identity consistent across new features
