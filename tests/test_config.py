"""Test configuration module."""

import os
from unittest.mock import patch

import pytest

from gmb.config import DashboardConfig


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test."""
    # Save original env vars
    original_env = {}
    for key in list(os.environ.keys()):
        if key.startswith("GMB_"):
            original_env[key] = os.environ[key]
            del os.environ[key]

    yield

    # Restore original env vars
    for key in list(os.environ.keys()):
        if key.startswith("GMB_"):
            del os.environ[key]
    for key, value in original_env.items():
        os.environ[key] = value


def test_config_from_env():
    """Test configuration loading from environment variables."""
    os.environ["GMB_LEAGUE_ID"] = "123456"
    os.environ["GMB_YEAR"] = "2024"
    os.environ["GMB_ESPN_S2"] = "test_espn_s2"
    os.environ["GMB_SWID"] = "test_swid"

    config = DashboardConfig.load()
    assert config.league_id == 123456
    assert config.year == 2024
    assert config.espn_s2 == "test_espn_s2"
    assert config.swid == "test_swid"


def test_config_missing_league_id():
    """Test error handling when league ID is missing."""
    # Clear all GMB environment variables (already done by fixture)
    # Mock the file and keyring loading to return empty/None
    with patch("gmb.config.DashboardConfig._load_from_yaml", return_value=None):
        with patch("gmb.config.DashboardConfig._load_from_keyring", return_value={}):
            with pytest.raises(ValueError, match="League ID must be set"):
                DashboardConfig.load()
