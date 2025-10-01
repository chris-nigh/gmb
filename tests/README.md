# GMB Fantasy Football - Test Suite

## Overview

Comprehensive test suite for the GMB Fantasy Football Dashboard library with **42 unit tests** covering all major functionality.

## Test Coverage

### Test Files

#### `test_espn.py` - ESPN API Client Tests (12 tests)
Tests for the ESPN Fantasy Football API client:
- ✅ League initialization with/without authentication
- ✅ Current week detection from API
- ✅ Team data retrieval with proper error handling
- ✅ Matchup data extraction and filtering
- ✅ Single week vs. all weeks data fetching
- ✅ Future week validation
- ✅ Zero score filtering for unplayed weeks
- ✅ HTTP 403 Forbidden error handling

#### `test_oiwp.py` - OIWP Calculation Tests (16 tests)
Tests for Opponent-Independent Winning Percentage calculations:
- ✅ TeamOIWP class initialization and properties
- ✅ Winning percentage (WP) calculations
- ✅ OIWP calculation with various scenarios
- ✅ Luck metric calculation (WP - OIWP)
- ✅ Multiple teams OIWP comparison
- ✅ Empty data handling
- ✅ Zero score filtering
- ✅ Actual wins vs. expected wins
- ✅ Edge cases (zero weeks, single team, etc.)

#### `test_cli.py` - CLI Command Tests (12 tests)
Tests for command-line interface:
- ✅ Setup command with success/error scenarios
- ✅ Query command for league standings
- ✅ OIWP analysis command
- ✅ Empty data handling
- ✅ Configuration error handling
- ✅ Help text for all commands

#### `test_config.py` - Configuration Tests (2 tests)
Tests for configuration management:
- ✅ Loading from environment variables
- ✅ Missing league ID validation

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_espn.py -v
pytest tests/test_oiwp.py -v
pytest tests/test_cli.py -v
pytest tests/test_config.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=gmb --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_espn.py::TestESPNFantasyLeague::test_get_teams_success -v
```

## Test Statistics

- **Total Tests:** 42
- **Passing:** 42 (100%)
- **Test Files:** 4
- **Code Coverage:** Comprehensive coverage of core functionality

## Key Testing Features

### Mocking & Isolation
- Uses `unittest.mock` for external dependencies
- Isolated tests with proper fixtures
- No actual API calls during testing

### Test Organization
- Tests grouped by functionality
- Clear test class organization
- Descriptive test names following pattern: `test_<what>_<condition>`

### Edge Cases Covered
- Empty data scenarios
- Error conditions (403, network failures, etc.)
- Missing configuration
- Zero scores in unplayed weeks
- Future week validation
- Boundary conditions

### Assertions
- Comprehensive assertions for all return values
- Error message validation
- Exit code verification for CLI commands
- DataFrame structure validation

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:
```yaml
- name: Run tests
  run: pytest tests/ -v --cov=gmb
```

## Adding New Tests

When adding new functionality:

1. Create test method in appropriate test class
2. Use descriptive name: `test_<feature>_<scenario>`
3. Follow AAA pattern:
   - **Arrange:** Set up test data and mocks
   - **Act:** Call the function/method being tested
   - **Assert:** Verify expected outcomes
4. Add docstring explaining what is being tested

### Example Test
```python
def test_get_teams_success(self, mock_get):
    """Test successful retrieval of team data."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"teams": [...]}
    mock_get.return_value = mock_response

    # Act
    league = ESPNFantasyLeague(league_id=123456, year=2025)
    teams_df = league.get_teams()

    # Assert
    assert isinstance(teams_df, pd.DataFrame)
    assert len(teams_df) == 2
```

## Dependencies

Test dependencies are listed in `requirements-dev.txt`:
- pytest>=7.4.0
- pytest-cov (for coverage reports)
- pandas-stubs>=2.0.0 (for type checking)

## Type Checking

All test files are lint-clean with proper type annotations and `# type: ignore[import-untyped]` comments where needed for third-party libraries.
