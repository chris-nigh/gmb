"""Tests for ESPN API client module."""

from unittest.mock import Mock, patch

import pandas as pd  # type: ignore[import-untyped]
import pytest
import requests

from gmb.espn import ESPNFantasyLeague


class TestESPNFantasyLeague:
    """Test suite for ESPNFantasyLeague class."""

    def test_init(self):
        """Test initialization of ESPNFantasyLeague."""
        league = ESPNFantasyLeague(league_id=123456, year=2025, espn_s2="test_s2", swid="test_swid")

        assert league.league_id == 123456
        assert league.year == 2025
        assert league.cookies == {"espn_s2": "test_s2", "SWID": "test_swid"}
        assert "123456" in league.base_url
        assert "2025" in league.base_url

    def test_init_without_cookies(self):
        """Test initialization without authentication cookies."""
        league = ESPNFantasyLeague(league_id=123456, year=2025)

        assert league.cookies == {}

    @patch("requests.get")
    def test_get_current_week(self, mock_get):
        """Test getting current week from API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"scoringPeriodId": 5}
        mock_get.return_value = mock_response

        league = ESPNFantasyLeague(league_id=123456, year=2025)
        week = league.get_current_week()

        assert week == 5
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_current_week_default(self, mock_get):
        """Test getting current week defaults to 1 if not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        league = ESPNFantasyLeague(league_id=123456, year=2025)
        week = league.get_current_week()

        assert week == 1

    @patch("requests.get")
    def test_get_current_week_error(self, mock_get):
        """Test error handling when getting current week fails."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response

        league = ESPNFantasyLeague(league_id=123456, year=2025)

        with pytest.raises(requests.HTTPError):
            league.get_current_week()

    @patch("requests.get")
    def test_get_teams_success(self, mock_get):
        """Test successful retrieval of team data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "teams": [
                {
                    "id": 1,
                    "name": "Team A",
                    "primaryOwner": "owner1",
                    "record": {
                        "overall": {
                            "wins": 3,
                            "losses": 1,
                            "pointsFor": 450.5,
                            "pointsAgainst": 380.2,
                        }
                    },
                },
                {
                    "id": 2,
                    "name": "Team B",
                    "primaryOwner": "owner2",
                    "record": {
                        "overall": {
                            "wins": 2,
                            "losses": 2,
                            "pointsFor": 400.0,
                            "pointsAgainst": 420.0,
                        }
                    },
                },
            ]
        }
        mock_get.return_value = mock_response

        league = ESPNFantasyLeague(league_id=123456, year=2025)
        teams_df = league.get_teams()

        assert isinstance(teams_df, pd.DataFrame)
        assert len(teams_df) == 2
        assert teams_df.iloc[0]["team_name"] == "Team A"
        assert teams_df.iloc[0]["wins"] == 3
        assert teams_df.iloc[1]["team_name"] == "Team B"

    @patch("requests.get")
    def test_get_teams_forbidden(self, mock_get):
        """Test 403 Forbidden error handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        league = ESPNFantasyLeague(league_id=123456, year=2025)

        with pytest.raises(ValueError, match="ESPN API access denied"):
            league.get_teams()

    def test_extract_matchups(self):
        """Test extraction of matchup data from API response."""
        league = ESPNFantasyLeague(league_id=123456, year=2025)

        api_data = {
            "schedule": [
                {
                    "matchupPeriodId": 1,
                    "away": {"teamId": 1, "totalPoints": 120.5},
                    "home": {"teamId": 2, "totalPoints": 110.3},
                },
                {
                    "matchupPeriodId": 1,
                    "away": {"teamId": 3, "totalPoints": 95.0},
                    "home": {"teamId": 4, "totalPoints": 105.2},
                },
            ]
        }

        matchups = league._extract_matchups(api_data, 1)

        assert len(matchups) == 4  # 2 games x 2 perspectives each
        assert matchups[0]["week"] == 1
        assert matchups[0]["team_name"] == 1
        assert matchups[0]["points"] == 120.5
        assert matchups[0]["opponent_name"] == 2
        assert matchups[0]["opponent_points"] == 110.3

    @patch.object(ESPNFantasyLeague, "get_current_week")
    @patch.object(ESPNFantasyLeague, "get_teams")
    @patch("requests.get")
    def test_get_matchups_single_week(self, mock_get, mock_get_teams, mock_get_week):
        """Test getting matchups for a single week."""
        mock_get_week.return_value = 5

        mock_teams_df = pd.DataFrame({"team_id": [1, 2], "team_name": ["Team A", "Team B"]})
        mock_get_teams.return_value = mock_teams_df

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "schedule": [
                {
                    "matchupPeriodId": 3,
                    "away": {"teamId": 1, "totalPoints": 115.0},
                    "home": {"teamId": 2, "totalPoints": 105.0},
                }
            ]
        }
        mock_get.return_value = mock_response

        league = ESPNFantasyLeague(league_id=123456, year=2025)
        matchups_df = league.get_matchups(week=3)

        assert isinstance(matchups_df, pd.DataFrame)
        assert len(matchups_df) == 2
        assert matchups_df.iloc[0]["team_name"] == "Team A"
        assert matchups_df.iloc[0]["points"] == 115.0

    @patch.object(ESPNFantasyLeague, "get_current_week")
    @patch.object(ESPNFantasyLeague, "get_teams")
    def test_get_matchups_future_week_error(self, mock_get_teams, mock_get_week):
        """Test error when requesting future week."""
        mock_get_week.return_value = 5

        league = ESPNFantasyLeague(league_id=123456, year=2025)

        with pytest.raises(ValueError, match="in the future"):
            league.get_matchups(week=10)

    @patch.object(ESPNFantasyLeague, "get_current_week")
    @patch.object(ESPNFantasyLeague, "get_teams")
    @patch("requests.get")
    def test_get_matchups_all_weeks(self, mock_get, mock_get_teams, mock_get_week):
        """Test getting matchups for all weeks."""
        mock_get_week.return_value = 2

        mock_teams_df = pd.DataFrame({"team_id": [1, 2], "team_name": ["Team A", "Team B"]})
        mock_get_teams.return_value = mock_teams_df

        # Mock responses for weeks 1 and 2
        mock_response_w1 = Mock()
        mock_response_w1.status_code = 200
        mock_response_w1.json.return_value = {
            "schedule": [
                {
                    "matchupPeriodId": 1,
                    "away": {"teamId": 1, "totalPoints": 100.0},
                    "home": {"teamId": 2, "totalPoints": 90.0},
                }
            ]
        }

        mock_response_w2 = Mock()
        mock_response_w2.status_code = 200
        mock_response_w2.json.return_value = {
            "schedule": [
                {
                    "matchupPeriodId": 2,
                    "away": {"teamId": 1, "totalPoints": 110.0},
                    "home": {"teamId": 2, "totalPoints": 95.0},
                }
            ]
        }

        mock_get.side_effect = [mock_response_w1, mock_response_w2]

        league = ESPNFantasyLeague(league_id=123456, year=2025)
        matchups_df = league.get_matchups()

        assert isinstance(matchups_df, pd.DataFrame)
        assert len(matchups_df) == 4  # 2 weeks x 2 perspectives
        assert matchups_df["week"].nunique() == 2

    @patch.object(ESPNFantasyLeague, "get_current_week")
    @patch.object(ESPNFantasyLeague, "get_teams")
    @patch("requests.get")
    def test_get_matchups_filters_zero_scores(self, mock_get, mock_get_teams, mock_get_week):
        """Test that weeks with zero scores are filtered out."""
        mock_get_week.return_value = 2

        mock_teams_df = pd.DataFrame({"team_id": [1, 2], "team_name": ["Team A", "Team B"]})
        mock_get_teams.return_value = mock_teams_df

        # Week 1 has scores, week 2 has all zeros
        mock_response_w1 = Mock()
        mock_response_w1.status_code = 200
        mock_response_w1.json.return_value = {
            "schedule": [
                {
                    "matchupPeriodId": 1,
                    "away": {"teamId": 1, "totalPoints": 100.0},
                    "home": {"teamId": 2, "totalPoints": 90.0},
                }
            ]
        }

        mock_response_w2 = Mock()
        mock_response_w2.status_code = 200
        mock_response_w2.json.return_value = {
            "schedule": [
                {
                    "matchupPeriodId": 2,
                    "away": {"teamId": 1, "totalPoints": 0.0},
                    "home": {"teamId": 2, "totalPoints": 0.0},
                }
            ]
        }

        mock_get.side_effect = [mock_response_w1, mock_response_w2]

        league = ESPNFantasyLeague(league_id=123456, year=2025)
        matchups_df = league.get_matchups()

        # Should only include week 1
        assert len(matchups_df) == 2
        assert matchups_df["week"].unique().tolist() == [1]
