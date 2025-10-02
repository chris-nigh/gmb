"""OIWP (Opponent-Independent Winning Percentage) calculations."""

import warnings

import pandas as pd


class TeamOIWP:
    def __init__(self, name: str, current_week: int, total_teams: int):
        self._name: str = name
        self._wins: int = 0
        self._losses: int = 0
        self._oiwins: int = 0
        self._current_week = current_week
        self._total_teams = total_teams

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"TeamOIWP(name={self._name!r}, wp={self.wp:.3f}, oiwp={self.oiwp:.3f}, luck={self.luck:+.3f})"

    @property
    def wp(self) -> float:
        return self._wins / self._current_week

    @property
    def oiwp(self) -> float:
        """Calculate opponent-independent winning percentage.

        Returns the fraction of possible wins achieved when compared against
        all other teams each week.
        """
        total_possible_wins = (self._total_teams - 1) * self._current_week
        return self._oiwins / total_possible_wins if total_possible_wins > 0 else 0.0

    @property
    def luck(self) -> float:
        return self.wp - self.oiwp

    @property
    def record(self) -> str:
        """Return actual record as 'W-L' string."""
        return f"{self._wins}-{self._losses}"

    @property
    def predicted_record(self) -> str:
        """Return OIWP-predicted record as 'W-L' string.

        Predicted wins are calculated by rounding OIWP * games played.
        """
        games_played = self._wins + self._losses
        predicted_wins = round(self.oiwp * games_played)
        predicted_losses = games_played - predicted_wins
        return f"{predicted_wins}-{predicted_losses}"

    @property
    def schedule_wins(self) -> int:
        """Return schedule wins: actual wins minus predicted wins.

        Positive values indicate favorable schedule (more wins than expected).
        Negative values indicate tough schedule (fewer wins than expected).
        """
        games_played = self._wins + self._losses
        predicted_wins = round(self.oiwp * games_played)
        return self._wins - predicted_wins

    def add_win(self) -> None:
        self._wins += 1

    def add_loss(self) -> None:
        self._losses += 1

    def add_oiwins(self, week_wins: int) -> None:
        """Add wins for a given week.

        Args:
            week_wins: Number of teams beaten this week
        """
        self._oiwins += week_wins


def _validate_oiwp_results(results_df: pd.DataFrame) -> None:
    """Validate OIWP calculation results for data quality issues.

    Checks that:
    - All values are in expected ranges (0.0 to 1.0)
    - Mean WP is approximately 0.500 (zero-sum property)
    - Mean OIWP is approximately 0.500 (zero-sum property)
    - Sum of luck values is approximately 0.0 (zero-sum property)

    Args:
        results_df: DataFrame with wp, oiwp, and luck columns

    Raises:
        warnings.UserWarning: If data quality issues are detected
    """
    if results_df.empty:
        return

    # Check value ranges
    for col in ["wp", "oiwp"]:
        if (results_df[col] < 0.0).any() or (results_df[col] > 1.0).any():
            warnings.warn(
                f"Invalid {col.upper()} values detected: should be between 0.0 and 1.0. "
                f"Range: {results_df[col].min():.3f} to {results_df[col].max():.3f}",
                UserWarning,
                stacklevel=3,
            )

    if (results_df["luck"] < -1.0).any() or (results_df["luck"] > 1.0).any():
        warnings.warn(
            f"Invalid luck values detected: should be between -1.0 and 1.0. "
            f"Range: {results_df['luck'].min():.3f} to {results_df['luck'].max():.3f}",
            UserWarning,
            stacklevel=3,
        )

    # Check zero-sum properties (allow 0.01 margin for rounding)
    margin = 0.01

    mean_wp = results_df["wp"].mean()
    if abs(mean_wp - 0.500) > margin:
        warnings.warn(
            f"Mean WP is {mean_wp:.3f}, expected ~0.500. This suggests data quality issues.",
            UserWarning,
            stacklevel=3,
        )

    mean_oiwp = results_df["oiwp"].mean()
    if abs(mean_oiwp - 0.500) > margin:
        warnings.warn(
            f"Mean OIWP is {mean_oiwp:.3f}, expected ~0.500. "
            f"This suggests calculation errors or data quality issues.",
            UserWarning,
            stacklevel=3,
        )

    sum_luck = results_df["luck"].sum()
    if abs(sum_luck) > margin * len(results_df):  # Scale margin by number of teams
        warnings.warn(
            f"Sum of luck values is {sum_luck:.3f}, expected ~0.0. "
            f"This suggests calculation errors (luck should be zero-sum).",
            UserWarning,
            stacklevel=3,
        )


def calculate_oiwp_stats(matchups_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate OIWP (Opponent-Independent Winning Percentage) stats.

    OIWP measures how well a team would perform if they played against every
    other team in the league each week. It helps identify teams that are truly
    strong vs. those who have benefited from favorable matchups.

    Args:
        matchups_df: DataFrame with columns: week, team_name, points, opponent_points

    Returns:
        DataFrame with columns: team_name, wp (winning percentage),
                               oiwp, luck (wp - oiwp)
                               Sorted by OIWP descending
    """
    # Only consider weeks with actual scores
    scored_weeks = matchups_df[matchups_df["points"] > 0]["week"].unique()
    if len(scored_weeks) == 0:
        return pd.DataFrame(columns=["team_name", "wp", "oiwp", "luck"])

    current_week = max(scored_weeks)
    total_teams = len(matchups_df["team_name"].unique())

    team_dict: dict[str, TeamOIWP] = {}

    # Initialize teams
    for team in matchups_df["team_name"].unique():
        team_dict[team] = TeamOIWP(team, current_week, total_teams)

    # Calculate actual wins and losses
    for _, row in matchups_df.iterrows():
        if row["points"] > row["opponent_points"]:
            team_dict[row["team_name"]].add_win()
        elif row["points"] < row["opponent_points"]:
            team_dict[row["team_name"]].add_loss()

    # Calculate OIWP - for each week, compare each team's score against every other team
    for week in range(1, current_week + 1):
        # Collect unique scores for each team this week
        week_scores = {}
        for _, row in matchups_df[matchups_df["week"] == week].iterrows():
            if row["team_name"] not in week_scores:
                week_scores[row["team_name"]] = row["points"]

        # Compare each team against all others
        for team_name, team_score in week_scores.items():
            wins = sum(
                1
                for other_name, other_score in week_scores.items()
                if other_name != team_name and team_score > other_score
            )
            team_dict[team_name].add_oiwins(wins)

    # Create results dataframe
    results = []
    for team in team_dict.values():
        results.append(
            {
                "team_name": team.name,
                "record": team.record,
                "predicted_record": team.predicted_record,
                "wp": team.wp,
                "oiwp": team.oiwp,
                "luck": team.luck,
                "schedule_wins": team.schedule_wins,
            }
        )

    results_df = pd.DataFrame(results).sort_values("oiwp", ascending=False)

    # Validate output values
    _validate_oiwp_results(results_df)

    return results_df
