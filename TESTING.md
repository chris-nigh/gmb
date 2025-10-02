# Testing and Code Coverage

This project uses pytest for testing and pytest-cov for code coverage analysis.

## Running Tests

### Basic test run
```bash
pytest
```

### With coverage (configured by default)
```bash
pytest  # Automatically generates coverage report
```

### Quick run without coverage
```bash
pytest --no-cov
```

### Run specific tests
```bash
pytest tests/test_oiwp.py
pytest tests/test_oiwp.py::TestTeamOIWP::test_wp_calculation
```

### Verbose output
```bash
pytest -v
pytest -vv  # Extra verbose
```

## Coverage Reports

Coverage is automatically generated when you run `pytest`. Two reports are created:

### 1. Terminal Report
Shows coverage summary and lists lines not covered:
```
---------- coverage: platform darwin, python 3.13.7 -----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/gmb/__init__.py                2      0   100%
src/gmb/cli.py                   145     12    92%   23-25, 89-92
src/gmb/espn.py                   98      5    95%   45-47
...
------------------------------------------------------------
TOTAL                            823     45    95%
```

### 2. HTML Report
Interactive HTML report generated in `htmlcov/`:
```bash
# View in browser
open htmlcov/index.html
```

The HTML report shows:
- Overall coverage percentage
- Per-file coverage with line-by-line highlighting
- Which branches weren't tested
- Easy navigation through your codebase

## Current Test Coverage

Your library has tests for:
- ✅ CLI commands (`test_cli.py`)
- ✅ Configuration loading (`test_config.py`)
- ✅ ESPN API client (`test_espn.py`, `test_espn_keeper.py`)
- ✅ OIWP calculations (`test_oiwp.py`)
- ✅ Visualization components (`test_viz.py`)

## Adding New Tests

When adding new features:
1. Write tests in the appropriate `test_*.py` file
2. Run `pytest` to verify tests pass and check coverage
3. Aim for >80% coverage on new code
4. Use the HTML report to find untested code paths

## Coverage Configuration

Coverage settings are in `pyproject.toml`:
- **Source**: `src/gmb/` (what to measure)
- **Omit**: Tests, cache, config files (what to ignore)
- **Exclude lines**: Comments, abstract methods, debug code

## Continuous Integration

Add this to your CI pipeline:
```bash
pytest --cov-fail-under=80  # Fail if coverage drops below 80%
```

## Tips for Good Coverage

1. **Test edge cases**: Empty inputs, None values, errors
2. **Test error paths**: Exception handling, validation
3. **Mock external dependencies**: API calls, file I/O
4. **Use fixtures**: Share test data across tests
5. **Parametrize**: Test multiple inputs with `@pytest.mark.parametrize`

## Example: Improving Coverage

If coverage report shows:
```
src/gmb/keeper.py    145    23    84%   67-72, 89-95
```

1. Open `htmlcov/index.html` in browser
2. Click on `keeper.py`
3. Red lines = not covered, green = covered
4. Write tests for the red sections
