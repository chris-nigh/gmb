"""Tests for ESPN Keeper League functionality."""
import pytest
from unittest.mock import Mock, patch
import pandas as pd

from gmb.espn_keeper import ESPNKeeperLeague


class TestESPNKeeperLeague:
    """Test ESPN Keeper League API client."""

    @pytest.fixture
    def league(self):
        """Create test league instance."""
        return ESPNKeeperLeague(
            league_id=123456,
            year=2025,
            espn_s2="test_s2",
            swid="test_swid"
        )

    def test_init(self, league):
        """Test league initialization."""
        assert league.league_id == 123456
        assert league.year == 2025
        assert league.cookies["espn_s2"] == "test_s2"
        assert league.cookies["SWID"] == "test_swid"

    @patch('gmb.espn_keeper.requests.get')
    def test_get_all_player_stats_success(self, mock_get, league):
        """Test getting all active player stats."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player": {
                    "id": 1,
                    "fullName": "Patrick Mahomes",
                    "defaultPositionId": 0,
                    "stats": [
                        {"statSourceId": 0, "statSplitTypeId": 0, "appliedTotal": 250.5},
                        {"statSourceId": 0, "statSplitTypeId": 0, "appliedTotal": 35.2}  # Current week
                    ]
                }
            },
            {
                "player": {
                    "id": 2,
                    "fullName": "Christian McCaffrey",
                    "defaultPositionId": 2,
                    "stats": [
                        {"statSourceId": 0, "statSplitTypeId": 0, "appliedTotal": 180.3},
                        {"statSourceId": 0, "statSplitTypeId": 0, "appliedTotal": 28.5}
                    ]
                }
            }
        ]
        mock_get.return_value = mock_response

        # Call method
        result = league.get_all_player_stats(2025)

        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "/players" in call_args[0][0]
        assert call_args[1]["params"]["view"] == "kona_playercard"
        assert "filterActive" in call_args[1]["headers"]["x-fantasy-filter"]

        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["player_id", "player_name", "position_id", "total_points"]

        # Verify data - should use last stat entry
        mahomes = result[result["player_name"] == "Patrick Mahomes"].iloc[0]
        assert mahomes["player_id"] == 1
        assert mahomes["position_id"] == 0
        assert mahomes["total_points"] == 35.2  # Uses last matching stat

        cmc = result[result["player_name"] == "Christian McCaffrey"].iloc[0]
        assert cmc["player_id"] == 2
        assert cmc["position_id"] == 2
        assert cmc["total_points"] == 28.5

    @patch('gmb.espn_keeper.requests.get')
    def test_get_all_player_stats_handles_empty_stats(self, mock_get, league):
        """Test handling players with no stats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "player": {
                    "id": 1,
                    "fullName": "Rookie Player",
                    "defaultPositionId": 2,
                    "stats": []  # No stats
                }
            }
        ]
        mock_get.return_value = mock_response

        result = league.get_all_player_stats(2025)

        assert len(result) == 1
        assert result.iloc[0]["total_points"] == 0

    @patch('gmb.espn_keeper.requests.get')
    def test_get_all_player_stats_api_error(self, mock_get, league):
        """Test error handling for failed API call."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to get player stats"):
            league.get_all_player_stats(2025)

    @patch('gmb.espn_keeper.requests.get')
    def test_get_player_stats_rostered_only(self, mock_get, league):
        """Test getting rostered player stats uses mRoster view."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "teams": [
                {
                    "id": 1,
                    "name": "Team A",
                    "roster": {
                        "entries": [
                            {
                                "playerPoolEntry": {
                                    "player": {
                                        "id": 1,
                                        "fullName": "Player One",
                                        "defaultPositionId": 0,
                                        "stats": [
                                            {"statSourceId": 0, "statSplitTypeId": 0, "appliedTotal": 50.0}
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        result = league.get_player_stats(2025)

        # Verify it uses mRoster view, not /players endpoint
        call_args = mock_get.call_args
        assert "/players" not in call_args[0][0]
        assert call_args[1]["params"]["view"] == ["mRoster", "mTeam"]

        assert len(result) == 1
        assert result.iloc[0]["player_name"] == "Player One"
