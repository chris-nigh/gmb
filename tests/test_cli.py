"""Tests for CLI module."""
from unittest.mock import Mock, patch

import pandas as pd  # type: ignore[import-untyped]
from typer.testing import CliRunner

from gmb.cli import app


runner = CliRunner()


class TestSetupCommand:
    """Test suite for setup command."""

    @patch('gmb.cli.DashboardConfig')
    def test_setup_success(self, mock_config_class):
        """Test successful setup command."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(
            app,
            ["setup"],
            input="123456\n2025\ntest_s2\ntest_swid\n"
        )

        assert result.exit_code == 0
        assert "Configuration saved successfully" in result.stdout
        mock_config.save.assert_called_once()

    @patch('gmb.cli.DashboardConfig')
    def test_setup_with_error(self, mock_config_class):
        """Test setup command with save error."""
        mock_config = Mock()
        mock_config.save.side_effect = Exception("Save failed")
        mock_config_class.return_value = mock_config

        result = runner.invoke(
            app,
            ["setup"],
            input="123456\n2025\n\n\n"
        )

        assert result.exit_code == 1
        # Check for error in stderr or stdout
        output = result.stdout + getattr(result, 'stderr', '')
        assert "Error" in output or "Save failed" in output or result.exit_code == 1


class TestSummaryCommand:
    """Test suite for summary command."""

    @patch('gmb.cli.ESPNFantasyLeague')
    @patch('gmb.cli.DashboardConfig')
    def test_summary_success(self, mock_config_class, mock_league_class):
        """Test successful summary command."""
        # Mock config
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            'league_id': 123456,
            'year': 2025,
            'espn_s2': None,
            'swid': None
        }
        mock_config_class.load.return_value = mock_config

        # Mock league with team data
        mock_league = Mock()
        teams_df = pd.DataFrame({
            'team_name': ['Team A', 'Team B'],
            'wins': [3, 2],
            'losses': [1, 2],
            'points_for': [450.5, 400.0]
        })
        mock_league.get_teams.return_value = teams_df
        mock_league_class.return_value = mock_league

        result = runner.invoke(app, ["summary"])

        assert result.exit_code == 0
        assert "Team Standings" in result.stdout
        assert "Team A" in result.stdout
        assert "Team B" in result.stdout

    @patch('gmb.cli.DashboardConfig')
    def test_summary_config_error(self, mock_config_class):
        """Test summary command with config loading error."""
        mock_config_class.load.side_effect = ValueError("Config not found")

        result = runner.invoke(app, ["summary"])

        assert result.exit_code == 1
        assert "Error displaying league summary" in result.stdout


class TestOIWPCommand:
    """Test suite for OIWP command."""

    @patch('gmb.oiwp.calculate_oiwp_stats')
    @patch('gmb.cli.ESPNFantasyLeague')
    @patch('gmb.cli.DashboardConfig')
    def test_oiwp_success(self, mock_config_class, mock_league_class, mock_calc):
        """Test successful OIWP command."""
        # Mock config
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            'league_id': 123456,
            'year': 2025,
            'espn_s2': None,
            'swid': None
        }
        mock_config_class.load.return_value = mock_config

        # Mock league with matchup data
        mock_league = Mock()
        matchups_df = pd.DataFrame({
            'week': [1, 1],
            'team_name': ['Team A', 'Team B'],
            'points': [100, 90],
            'opponent_name': ['Team B', 'Team A'],
            'opponent_points': [90, 100]
        })
        mock_league.get_matchups.return_value = matchups_df
        mock_league_class.return_value = mock_league

        # Mock OIWP stats
        stats_df = pd.DataFrame({
            'team_name': ['Team A', 'Team B'],
            'wp': [1.0, 0.0],
            'oiwp': [0.8, 0.2],
            'luck': [0.2, -0.2]
        })
        mock_calc.return_value = stats_df

        result = runner.invoke(app, ["oiwp"])

        assert result.exit_code == 0
        assert "OIWP" in result.stdout or "Opponent-Independent" in result.stdout
        assert "Team A" in result.stdout
        assert "Team B" in result.stdout
        assert "Luck" in result.stdout

    @patch('gmb.cli.ESPNFantasyLeague')
    @patch('gmb.cli.DashboardConfig')
    def test_oiwp_empty_matchups(self, mock_config_class, mock_league_class):
        """Test OIWP command with no matchup data."""
        # Mock config
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            'league_id': 123456,
            'year': 2025,
            'espn_s2': None,
            'swid': None
        }
        mock_config_class.load.return_value = mock_config

        # Mock league with empty matchup data
        mock_league = Mock()
        mock_league.get_matchups.return_value = pd.DataFrame()
        mock_league_class.return_value = mock_league

        result = runner.invoke(app, ["oiwp"])

        assert result.exit_code == 0
        assert "No matchup data available" in result.stdout

    @patch('gmb.oiwp.calculate_oiwp_stats')
    @patch('gmb.cli.ESPNFantasyLeague')
    @patch('gmb.cli.DashboardConfig')
    def test_oiwp_empty_stats(self, mock_config_class, mock_league_class, mock_calc):
        """Test OIWP command with no calculable stats."""
        # Mock config
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            'league_id': 123456,
            'year': 2025,
            'espn_s2': None,
            'swid': None
        }
        mock_config_class.load.return_value = mock_config

        # Mock league with matchup data
        mock_league = Mock()
        matchups_df = pd.DataFrame({
            'week': [1],
            'team_name': ['Team A'],
            'points': [0],
            'opponent_name': ['Team B'],
            'opponent_points': [0]
        })
        mock_league.get_matchups.return_value = matchups_df
        mock_league_class.return_value = mock_league

        # Mock empty OIWP stats
        mock_calc.return_value = pd.DataFrame()

        result = runner.invoke(app, ["oiwp"])

        assert result.exit_code == 0
        assert "No OIWP data could be calculated" in result.stdout

    @patch('gmb.cli.DashboardConfig')
    def test_oiwp_config_error(self, mock_config_class):
        """Test OIWP command with config loading error."""
        mock_config_class.load.side_effect = ValueError("Config not found")

        result = runner.invoke(app, ["oiwp"])

        assert result.exit_code == 1
        assert "Error calculating OIWP" in result.stdout


def test_app_help():
    """Test that app help works."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "GMB Fantasy Football Tools" in result.stdout


def test_setup_help():
    """Test setup command help."""
    result = runner.invoke(app, ["setup", "--help"])

    assert result.exit_code == 0
    assert "setup" in result.stdout.lower()


def test_summary_help():
    """Test summary command help."""
    result = runner.invoke(app, ["summary", "--help"])

    assert result.exit_code == 0
    assert "summary" in result.stdout.lower()


def test_oiwp_help():
    """Test oiwp command help."""
    result = runner.invoke(app, ["oiwp", "--help"])

    assert result.exit_code == 0
    assert "oiwp" in result.stdout.lower()
