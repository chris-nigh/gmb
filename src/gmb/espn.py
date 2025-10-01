"""ESPN Fantasy Football API client module."""
import pandas as pd  # type: ignore[import-untyped]
import requests

# Request timeout in seconds
REQUEST_TIMEOUT = 10


class ESPNFantasyLeague:
    """Client for interacting with ESPN Fantasy Football API.

    This client provides methods to fetch team data, matchups, and league information
    from ESPN's Fantasy Football API. Supports both public and private leagues
    (private leagues require authentication cookies).
    """

    def __init__(
        self, league_id: int, year: int = 2024, espn_s2: str | None = None, swid: str | None = None
    ):
        """
        Initialize ESPN Fantasy League API client.

        Args:
            league_id: Your ESPN league ID
            year: Fantasy season year
            espn_s2: ESPN session cookie (for private leagues)
            swid: ESPN user ID cookie (for private leagues)
        """
        self.league_id = league_id
        self.year = year
        self.base_url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
        self.cookies = {}
        if espn_s2 and swid:
            self.cookies = {"espn_s2": espn_s2, "SWID": swid}  # Note: SWID must be uppercase

    def _extract_matchups(self, data: dict, week: int) -> list:
        """Extract matchup data from API response.

        Args:
            data: API response data
            week: Week number for these matchups

        Returns:
            List of matchup dictionaries
        """
        matchups = []
        for game in data.get('schedule', []):
            game_week = game.get('matchupPeriodId')
            if game_week != week:
                continue

            away_team = game.get('away', {})
            home_team = game.get('home', {})

            if away_team and home_team:
                matchups.append({
                    'week': game_week,
                    'team_name': away_team.get('teamId'),
                    'points': away_team.get('totalPoints', 0),
                    'opponent_name': home_team.get('teamId'),
                    'opponent_points': home_team.get('totalPoints', 0)
                })
                matchups.append({
                    'week': game_week,
                    'team_name': home_team.get('teamId'),
                    'points': home_team.get('totalPoints', 0),
                    'opponent_name': away_team.get('teamId'),
                    'opponent_points': away_team.get('totalPoints', 0)
                })
        return matchups

    def get_teams(self) -> pd.DataFrame:
        """Get all teams in the league.

        Returns:
            DataFrame with columns: team_id, team_name, owner, wins, losses,
                                   points_for, points_against

        Raises:
            ValueError: If ESPN API access is denied (403)
            requests.HTTPError: For other HTTP errors
        """
        url = f"{self.base_url}?view=mTeam"
        response = requests.get(url, cookies=self.cookies, timeout=REQUEST_TIMEOUT)

        if response.status_code == 403:
            raise ValueError(
                "ESPN API access denied. This could be due to:\n"
                "1. Expired cookies (try getting fresh ones)\n"
                "2. Wrong cookie case (SWID vs swid)\n"
                "3. Missing or malformed cookies\n"
                "4. League access restrictions"
            )
        response.raise_for_status()

        data = response.json()

        teams_data: list[dict] = []
        for team in data["teams"]:
            teams_data.append(
                {
                    "team_id": team["id"],
                    "team_name": team["name"],
                    "owner": team["primaryOwner"],
                    "wins": team["record"]["overall"]["wins"],
                    "losses": team["record"]["overall"]["losses"],
                    "points_for": team["record"]["overall"]["pointsFor"],
                    "points_against": team["record"]["overall"]["pointsAgainst"],
                }
            )

        return pd.DataFrame(teams_data)

    def get_current_week(self) -> int:
        """Get the current scoring period (week) of the season.

        Returns:
            Current week number (defaults to 1 if not found)
        """
        url = f"{self.base_url}?view=mSettings"
        response = requests.get(url, cookies=self.cookies, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        return data.get('scoringPeriodId', 1)

    def get_matchups(self, week: int | None = None) -> pd.DataFrame:
        """Get matchup data for specific week or all weeks.

        Args:
            week: Optional week number to filter matchups. If None, gets all weeks
                 up to current with actual scores.

        Returns:
            DataFrame with columns: week, team_name, points, opponent_name, opponent_points

        Raises:
            ValueError: If requested week is in the future
        """
        current_week = self.get_current_week()

        # Get team name mappings once
        teams = self.get_teams()
        team_names = {team['team_id']: team['team_name'] for _, team in teams.iterrows()}

        if week:
            if week > current_week:
                raise ValueError(f"Week {week} is in the future (current week is {current_week})")
            weeks_to_fetch = [week]
        else:
            # For all weeks, fetch each individually to filter out unplayed weeks
            weeks_to_fetch = list(range(1, current_week + 1))

        all_matchups = []
        for w in weeks_to_fetch:
            url = f"{self.base_url}?view=mMatchup&scoringPeriodId={w}"
            response = requests.get(url, cookies=self.cookies, timeout=REQUEST_TIMEOUT)

            if response.status_code != 200:
                continue  # Skip weeks that fail

            data = response.json()
            week_matchups = self._extract_matchups(data, w)

            # Only include weeks with actual scores (filter out future/unplayed weeks)
            if week or any(m['points'] > 0 for m in week_matchups):
                all_matchups.extend(week_matchups)

        if not all_matchups:
            return pd.DataFrame(columns=['week', 'team_name', 'points', 'opponent_name', 'opponent_points'])

        # Convert to DataFrame and map team IDs to names
        df = pd.DataFrame(all_matchups)
        df['team_name'] = df['team_name'].map(team_names)
        df['opponent_name'] = df['opponent_name'].map(team_names)
        return df