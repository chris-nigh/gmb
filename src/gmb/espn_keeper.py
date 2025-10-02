"""ESPN API client extensions for keeper league functionality."""

from __future__ import annotations

import pandas as pd
import requests

from .espn import REQUEST_TIMEOUT, ESPNFantasyLeague


class ESPNKeeperLeague(ESPNFantasyLeague):
    """Extended ESPN client with keeper league functionality."""

    def get_draft_picks(self, year: int | None = None) -> pd.DataFrame:
        """Get draft picks for a given year.

        Args:
            year: Season year (defaults to current year)

        Returns:
            DataFrame with draft pick information
        """
        year = year or self.year
        url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}"

        # Get both draft details and team info
        params = {"view": ["mDraftDetail", "mTeam", "mRoster"]}
        response = requests.get(
            url,
            cookies=self.cookies,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get draft data: {response.status_code}")

        data = response.json()

        # Build team ID to name mapping
        teams_map = {}
        for team in data.get("teams", []):
            team_id = team.get("id")
            # Try to get name from different possible locations
            team_name = team.get("name") or team.get("location", "Unknown")
            if team_id:
                teams_map[team_id] = team_name

        # Build player ID to name mapping from all team rosters
        player_id_to_name = {}
        for team in data.get("teams", []):
            roster = team.get("roster", {})
            entries = roster.get("entries", [])
            for entry in entries:
                player_data = entry.get("playerPoolEntry", {}).get("player", {})
                player_id = player_data.get("id")
                player_name = player_data.get("fullName", "Unknown")
                if player_id:
                    player_id_to_name[player_id] = player_name

        # Parse draft picks
        draft_detail = data.get("draftDetail", {})
        picks_data = draft_detail.get("picks", [])

        picks = []
        for pick_data in picks_data:
            player_id = pick_data.get("playerId")
            player_name = player_id_to_name.get(player_id, f"Unknown (ID: {player_id})")

            picks.append(
                {
                    "player_name": player_name,
                    "team_name": teams_map.get(pick_data.get("teamId", 0), "Unknown"),
                    "round": pick_data.get("roundId", 0),
                    "pick": pick_data.get("overallPickNumber", 0),
                    "keeper": pick_data.get("keeper", False),
                    "cost": pick_data.get("bidAmount", 0),
                }
            )

        return pd.DataFrame(picks)

    def get_transactions(self, year: int | None = None) -> pd.DataFrame:
        """Get all transactions for a given year.

        Args:
            year: Season year (defaults to current year)

        Returns:
            DataFrame with transaction information
        """
        year = year or self.year
        url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}"

        # Use the kona_playercard view to get player transactions
        import json

        params = {"view": "kona_playercard"}
        headers_dict = {"filterActive": {"value": True}}

        response = requests.get(
            f"{url}/players",
            cookies=self.cookies,
            params=params,
            headers={"x-fantasy-filter": json.dumps(headers_dict)},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get transactions: {response.status_code}")

        players_data = response.json()

        # Build a mapping of player IDs to names for quick lookup
        player_id_to_name = {}
        for player_entry in players_data:
            player_id = player_entry.get("id")
            player_name = player_entry.get("player", {}).get("fullName", "Unknown")
            if player_id:
                player_id_to_name[player_id] = player_name

        transactions = []
        for player_entry in players_data:
            # Each player_entry contains transactions where this player was involved
            for transaction in player_entry.get("transactions", []):
                # Skip draft transactions
                if transaction.get("type") == "DRAFT":
                    continue

                for item in transaction.get("items", []):
                    # Skip lineup items
                    if item.get("type") == "LINEUP":
                        continue

                    # Get the player name from the item's playerId
                    player_id = item.get("playerId")
                    player_name = player_id_to_name.get(player_id, "Unknown")

                    # Determine timestamp
                    timestamp = transaction.get("processedDate", transaction.get("proposedDate", 0))

                    # Determine transaction type
                    if transaction.get("type") == "WAIVER" and item.get("type") == "ADD":
                        trans_type = "WAIVER"
                    elif item.get("type") == "ADD":
                        trans_type = "ADD"
                    elif item.get("type") == "DROP":
                        trans_type = "DROP"
                    elif item.get("type") == "TRADE":
                        continue
                    else:
                        trans_type = "UNKNOWN"

                    transactions.append(
                        {
                            "type": trans_type,
                            "player_name": player_name,
                            "team_name": "Unknown",  # Not easily available in this view
                            "timestamp": timestamp,
                            "bid_amount": transaction.get("bidAmount"),
                        }
                    )

        # Always return a DataFrame with the expected columns, even if empty
        columns = ["type", "player_name", "team_name", "timestamp", "bid_amount"]
        return pd.DataFrame(transactions, columns=columns)

    def get_roster(self, team_id: int, year: int | None = None) -> pd.DataFrame:
        """Get roster for a specific team.

        Args:
            team_id: ESPN team ID
            year: Season year (defaults to current year)

        Returns:
            DataFrame with player roster information
        """
        year = year or self.year
        url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}"
        params = {"view": "mRoster"}

        response = requests.get(
            url,
            cookies=self.cookies,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get roster: {response.status_code}")

        data = response.json()

        # Find the specific team
        team_data = None
        for team in data.get("teams", []):
            if team["id"] == team_id:
                team_data = team
                break

        if not team_data:
            raise ValueError(f"Team {team_id} not found")

        # Parse roster
        roster = team_data.get("roster", {})
        entries = roster.get("entries", [])

        players = []
        for entry in entries:
            player_data = entry.get("playerPoolEntry", {}).get("player", {})
            players.append(
                {
                    "player_id": player_data.get("id"),
                    "name": player_data.get("fullName", "Unknown"),
                    "position": player_data.get("defaultPositionId"),
                    "team": player_data.get("proTeamId"),
                }
            )

        return pd.DataFrame(players)

    def get_player_stats(self, year: int | None = None) -> pd.DataFrame:
        """Get player statistics for all rostered players.

        Args:
            year: Season year (defaults to current year)

        Returns:
            DataFrame with player stats including total points
        """
        year = year or self.year
        url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}"

        # Use mRoster and mTeam views to get player stats
        params = {"view": ["mRoster", "mTeam"]}

        response = requests.get(
            url,
            cookies=self.cookies,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get player stats: {response.status_code}")

        data = response.json()

        # Get all teams and their rosters with stats
        players_stats = []
        for team in data.get("teams", []):
            team_id = team.get("id")
            team_name = team.get("name", "Unknown")
            roster = team.get("roster", {})
            entries = roster.get("entries", [])

            for entry in entries:
                player_data = entry.get("playerPoolEntry", {}).get("player", {})
                player_id = player_data.get("id")
                player_name = player_data.get("fullName", "Unknown")
                position_id = player_data.get("defaultPositionId")

                # Get stats - total points for the season
                # Note: There may be multiple stats with same IDs, take the last one (most recent)
                stats = player_data.get("stats", [])
                total_points = 0
                for stat in stats:
                    # Look for the season total stat (statSourceId == 0, statSplitTypeId == 0)
                    if stat.get("statSourceId") == 0 and stat.get("statSplitTypeId") == 0:
                        total_points = stat.get("appliedTotal", 0)
                        # Don't break - keep looking for more recent stat

                players_stats.append(
                    {
                        "player_id": player_id,
                        "player_name": player_name,
                        "team_id": team_id,
                        "team_name": team_name,
                        "position_id": position_id,
                        "total_points": total_points,
                    }
                )

        return pd.DataFrame(players_stats)

    def get_all_player_stats(self, year: int | None = None) -> pd.DataFrame:
        """Get player statistics for ALL active players in the league.

        Args:
            year: Season year (defaults to current year)

        Returns:
            DataFrame with player stats including total points for all active players
        """
        year = year or self.year
        url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{self.league_id}/players"

        # Use kona_playercard view with filterActive to get all active players
        params = {"view": "kona_playercard"}
        headers = {"x-fantasy-filter": '{"filterActive":{"value":true}}'}

        response = requests.get(
            url,
            cookies=self.cookies,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get player stats: {response.status_code}")

        data = response.json()

        # Get all players from the player pool
        players_stats = []
        for entry in data:
            player_data = entry.get("player", {})
            player_id = player_data.get("id")
            player_name = player_data.get("fullName", "Unknown")
            position_id = player_data.get("defaultPositionId")

            # Get stats - total points for the season
            # Note: There may be multiple stats with same IDs, take the last one (most recent)
            stats = player_data.get("stats", [])
            total_points = 0
            for stat in stats:
                # Look for the season total stat (statSourceId == 0, statSplitTypeId == 0)
                if stat.get("statSourceId") == 0 and stat.get("statSplitTypeId") == 0:
                    total_points = stat.get("appliedTotal", 0)
                    # Don't break - keep looking for more recent stat

            players_stats.append(
                {
                    "player_id": player_id,
                    "player_name": player_name,
                    "position_id": position_id,
                    "total_points": total_points,
                }
            )

        return pd.DataFrame(players_stats)
