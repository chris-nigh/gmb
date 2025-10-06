"""Taylor Swift Eras analysis for fantasy football."""

from datetime import datetime, timedelta
from typing import Any, TypedDict

import pandas as pd


class EraDict(TypedDict):
    """Type definition for era dictionary."""

    era: str
    start_date: datetime
    end_date: datetime


# Taylor Swift album release dates
TAYLOR_ERAS: list[EraDict] = [
    {
        "era": "Taylor Swift",
        "start_date": datetime(2006, 10, 24),
        "end_date": datetime(2008, 11, 11),
    },
    {
        "era": "Fearless",
        "start_date": datetime(2008, 11, 11),
        "end_date": datetime(2010, 10, 25),
    },
    {
        "era": "Speak Now",
        "start_date": datetime(2010, 10, 25),
        "end_date": datetime(2012, 10, 22),
    },
    {
        "era": "Red",
        "start_date": datetime(2012, 10, 22),
        "end_date": datetime(2014, 10, 27),
    },
    {
        "era": "1989",
        "start_date": datetime(2014, 10, 27),
        "end_date": datetime(2017, 11, 10),
    },
    {
        "era": "Reputation",
        "start_date": datetime(2017, 11, 10),
        "end_date": datetime(2019, 8, 23),
    },
    {
        "era": "Lover",
        "start_date": datetime(2019, 8, 23),
        "end_date": datetime(2020, 7, 24),
    },
    {
        "era": "Folklore",
        "start_date": datetime(2020, 7, 24),
        "end_date": datetime(2020, 12, 11),
    },
    {
        "era": "Evermore",
        "start_date": datetime(2020, 12, 11),
        "end_date": datetime(2022, 10, 21),
    },
    {
        "era": "Midnights",
        "start_date": datetime(2022, 10, 21),
        "end_date": datetime(2024, 4, 19),
    },
    {
        "era": "The Tortured Poets Department",
        "start_date": datetime(2024, 4, 19),
        "end_date": datetime(2025, 10, 3),
    },
    {
        "era": "The Life of a Showgirl",
        "start_date": datetime(2025, 10, 3),
        "end_date": datetime(2025, 12, 31),  # Current era, end date is placeholder
    },
]


def get_week_date(year: int, week: int) -> datetime:
    """Convert a fantasy football week number to an approximate date.

    Args:
        year: Fantasy football season year
        week: Week number (1-17 typically)

    Returns:
        Approximate date for that week
    """
    # NFL season typically starts the first Tuesday after Labor Day (first Monday in September)
    # Week 1 is usually the second week of September
    # We'll approximate: first game of week N is roughly Sept 1 + (N-1) * 7 days
    season_start = datetime(year, 9, 1)
    return season_start + timedelta(days=(week - 1) * 7)


def get_era_for_date(date: datetime) -> str:
    """Get the Taylor Swift era for a specific date.

    Args:
        date: The date to check

    Returns:
        The era name for that date
    """
    for era in TAYLOR_ERAS:
        if era["start_date"] <= date < era["end_date"]:
            return era["era"]
    return "Unknown Era"


def get_era_for_year(year: int) -> str:
    """Get the Taylor Swift era(s) for a given fantasy football season year.

    DEPRECATED: Use get_era_for_date() with actual game dates instead.

    Args:
        year: Fantasy football season year

    Returns:
        String describing the era(s) for that season
    """
    # Fantasy football seasons typically run from late August/early September to late December/early January
    season_start = datetime(year, 8, 1)
    season_end = datetime(year, 12, 31)

    eras_in_season = []
    for era in TAYLOR_ERAS:
        # Check if this era overlaps with the fantasy season
        if era["start_date"] <= season_end and era["end_date"] >= season_start:
            eras_in_season.append(era["era"])

    if len(eras_in_season) == 1:
        return eras_in_season[0]
    elif len(eras_in_season) > 1:
        return f"{eras_in_season[0]} / {eras_in_season[-1]}"
    else:
        return "Unknown Era"


def calculate_era_win_percentages(historical_matchups: list[dict[str, Any]]) -> pd.DataFrame:
    """Calculate winning percentage by Taylor Swift era for each owner.

    Args:
        historical_matchups: List of dictionaries with keys:
            - year: int
            - week: int
            - team_name: str
            - owner: str
            - points: float
            - opponent_points: float

    Returns:
        DataFrame with columns: owner, era, games, wins, losses, win_pct
    """
    # Add era information and win/loss to each game
    for game in historical_matchups:
        game_date = get_week_date(game["year"], game["week"])
        game["era"] = get_era_for_date(game_date)
        game["win"] = 1 if game["points"] > game["opponent_points"] else 0
        game["loss"] = 1 if game["points"] < game["opponent_points"] else 0

    df = pd.DataFrame(historical_matchups)

    # Group by owner and era to calculate aggregated stats
    era_stats = df.groupby(["owner", "era"]).agg({"win": "sum", "loss": "sum"}).reset_index()

    # Rename columns for consistency
    era_stats = era_stats.rename(columns={"win": "wins", "loss": "losses"})

    # Calculate win percentage and games played
    era_stats["games"] = era_stats["wins"] + era_stats["losses"]
    era_stats["win_pct"] = era_stats["wins"] / era_stats["games"]

    # Sort by era chronologically (based on order in TAYLOR_ERAS)
    era_order = [era["era"] for era in TAYLOR_ERAS]
    era_stats["era_order"] = era_stats["era"].apply(
        lambda x: era_order.index(x) if x in era_order else 999
    )
    era_stats = era_stats.sort_values(["era_order", "owner"]).drop(columns=["era_order"])

    return era_stats[["owner", "era", "games", "wins", "losses", "win_pct"]]


def get_historical_matchups_data(
    league_id: int,
    start_year: int,
    end_year: int,
    espn_s2: str | None = None,
    swid: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch historical matchup data from ESPN for multiple years.

    Args:
        league_id: ESPN league ID
        start_year: First year to fetch (inclusive)
        end_year: Last year to fetch (inclusive)
        espn_s2: ESPN session cookie (for private leagues)
        swid: ESPN user ID cookie (for private leagues)

    Returns:
        List of individual game records across all years
    """
    from .espn import ESPNFantasyLeague

    all_matchups = []

    for year in range(start_year, end_year + 1):
        try:
            league = ESPNFantasyLeague(
                league_id=league_id,
                year=year,
                espn_s2=espn_s2,
                swid=swid,
            )

            # Get teams to map team names to owners
            teams_df = league.get_teams()
            team_to_owner = {team["team_name"]: team["owner"] for _, team in teams_df.iterrows()}

            # Get all matchups for this year
            matchups_df = league.get_matchups()

            for _, matchup in matchups_df.iterrows():
                all_matchups.append(
                    {
                        "year": year,
                        "week": matchup["week"],
                        "team_name": matchup["team_name"],
                        "owner": team_to_owner.get(matchup["team_name"], "Unknown"),
                        "points": matchup["points"],
                        "opponent_points": matchup["opponent_points"],
                    }
                )

        except Exception as e:
            print(f"Warning: Could not fetch data for year {year}: {e}")
            continue

    return all_matchups
