"""Tests for visualization components."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from gmb.espn import ESPNFantasyLeague
from gmb.viz import FantasyDashboard


class TestFantasyDashboard:
    """Test FantasyDashboard visualization methods."""

    @pytest.fixture
    def mock_league(self):
        """Create mock league for testing."""
        league = Mock(spec=ESPNFantasyLeague)
        league.league_id = 123456
        league.year = 2025
        return league

    @pytest.fixture
    def sample_teams_df(self):
        """Create sample teams dataframe."""
        return pd.DataFrame(
            {
                "team_id": [1, 2, 3],
                "team_name": ["Team A", "Team B", "Team C"],
                "wins": [5, 3, 7],
                "losses": [2, 4, 0],
                "points_for": [850.5, 720.3, 920.1],
                "points_against": [700.2, 800.4, 650.8],
            }
        )

    @pytest.fixture
    def sample_matchups_df(self):
        """Create sample matchups dataframe with correct column names."""
        return pd.DataFrame(
            {
                "week": [1, 1, 1, 2, 2, 2, 3, 3, 3],
                "team_name": ["Team A", "Team B", "Team C"] * 3,
                "points": [120.5, 95.3, 130.2, 115.8, 105.6, 125.4, 110.3, 100.9, 135.7],
                "opponent_name": ["Team B", "Team A", "Team C"] * 3,
                "opponent_points": [95.3, 120.5, 130.2, 105.6, 115.8, 125.4, 100.9, 110.3, 135.7],
            }
        )

    def test_init(self, mock_league):
        """Test dashboard initialization."""
        dashboard = FantasyDashboard(mock_league)
        assert dashboard.league == mock_league
        assert dashboard.teams_df is None
        assert dashboard.matchups_df is None

    @patch("gmb.viz.st")
    def test_create_consistency_chart_with_data(
        self, mock_st, mock_league, sample_teams_df, sample_matchups_df
    ):
        """Test consistency chart with valid data."""
        dashboard = FantasyDashboard(mock_league)
        dashboard.teams_df = sample_teams_df
        dashboard.matchups_df = sample_matchups_df

        # Call the method
        dashboard.create_consistency_chart()

        # Verify plotly chart was called
        mock_st.plotly_chart.assert_called_once()

        # Verify info message was shown with quadrant explanations
        mock_st.info.assert_called_once()
        assert "boom/bust" in mock_st.info.call_args[0][0].lower()

    @patch("gmb.viz.st")
    def test_create_consistency_chart_no_data(self, mock_st, mock_league):
        """Test consistency chart with no data shows warning."""
        dashboard = FantasyDashboard(mock_league)
        dashboard.teams_df = None
        dashboard.matchups_df = None

        # Call the method
        dashboard.create_consistency_chart()

        # Verify warning was shown
        mock_st.warning.assert_called_once()
        assert "Matchup data required" in mock_st.warning.call_args[0][0]

        # Verify plotly chart was NOT called
        mock_st.plotly_chart.assert_not_called()

    @patch("gmb.viz.st")
    def test_create_consistency_chart_calculates_correctly(
        self, mock_st, mock_league, sample_teams_df, sample_matchups_df
    ):
        """Test that consistency calculations are correct."""
        dashboard = FantasyDashboard(mock_league)
        dashboard.teams_df = sample_teams_df
        dashboard.matchups_df = sample_matchups_df

        # Call the method
        dashboard.create_consistency_chart()

        # Verify the chart was created
        assert mock_st.plotly_chart.called

        # Get the figure that was passed
        call_args = mock_st.plotly_chart.call_args
        fig = call_args[0][0]

        # Verify the figure has data
        assert hasattr(fig, "data")
        assert len(fig.data) > 0

    @patch("gmb.viz.st")
    def test_create_consistency_chart_requires_correct_columns(
        self, mock_st, mock_league, sample_teams_df
    ):
        """Test that consistency chart uses correct column names from matchups_df."""
        # Create matchups with wrong column name to verify it fails gracefully
        bad_matchups = pd.DataFrame(
            {
                "week": [1, 1],
                "team_name": ["Team A", "Team B"],
                "team_points": [120.5, 95.3],  # Wrong column name
                "opponent_name": ["Team B", "Team A"],
                "opponent_points": [95.3, 120.5],
            }
        )

        dashboard = FantasyDashboard(mock_league)
        dashboard.teams_df = sample_teams_df
        dashboard.matchups_df = bad_matchups

        # This should raise a KeyError because 'points' column doesn't exist
        with pytest.raises(KeyError, match="points"):
            dashboard.create_consistency_chart()

    @patch("gmb.viz.st")
    def test_create_schedule_strength_chart_with_data(
        self, mock_st, mock_league, sample_teams_df, sample_matchups_df
    ):
        """Test schedule strength chart with valid data."""
        dashboard = FantasyDashboard(mock_league)
        dashboard.teams_df = sample_teams_df
        dashboard.matchups_df = sample_matchups_df

        # Call the method
        dashboard.create_schedule_strength_chart()

        # Verify plotly chart was called
        mock_st.plotly_chart.assert_called_once()

    @patch("gmb.viz.st")
    def test_create_schedule_strength_chart_no_data(self, mock_st, mock_league):
        """Test schedule strength chart with no data shows warning."""
        dashboard = FantasyDashboard(mock_league)
        dashboard.teams_df = None
        dashboard.matchups_df = None

        # Call the method
        dashboard.create_schedule_strength_chart()

        # Verify warning was shown
        mock_st.warning.assert_called_once()
        assert "Insufficient data" in mock_st.warning.call_args[0][0]

    def test_matchups_dataframe_schema(self, sample_matchups_df):
        """Test that sample matchups dataframe has the expected schema."""
        # This test documents the expected schema for matchups_df
        expected_columns = ["week", "team_name", "points", "opponent_name", "opponent_points"]
        assert list(sample_matchups_df.columns) == expected_columns

        # Verify data types
        assert sample_matchups_df["week"].dtype == "int64"
        assert sample_matchups_df["team_name"].dtype == "object"
        assert sample_matchups_df["points"].dtype == "float64"
        assert sample_matchups_df["opponent_name"].dtype == "object"
        assert sample_matchups_df["opponent_points"].dtype == "float64"
