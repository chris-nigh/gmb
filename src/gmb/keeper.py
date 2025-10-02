"""Keeper player management with eligibility tracking."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .keeper_constants import DROP_TO_PICKUP, GO_BACK_YEARS, KEEPER_YEAR_INCREMENTS, MAX_KEEP_YEARS
from .models import TransactionType
from .position_map import get_position_name


@dataclass
class KeeperEligibility:
    """Keeper eligibility information for a player."""

    player_name: str
    team_name: str
    position: str
    years_kept: int
    years_remaining: int
    eligible: bool
    current_cost: int | str
    last_cost: int | None
    drafted_history: list[bool]
    kept_history: list[bool]
    cleared_waivers: list[bool]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DataFrame creation."""
        # Convert position ID to name
        position_name = get_position_name(self.position)

        result = {
            "player_name": self.player_name,
            "team_name": self.team_name,
            "position": position_name,
            "position_id": self.position,  # Keep original ID for sorting
            "years_kept": self.years_kept,
            "years_remaining": self.years_remaining,
            "eligible": self.eligible,
            "keeper_cost": self.current_cost,
            "last_cost": self.last_cost,
        }

        # Add historical columns
        for i, (drafted, kept, cleared) in enumerate(
            zip(self.drafted_history, self.kept_history, self.cleared_waivers)
        ):
            year_offset = GO_BACK_YEARS - i - 1
            result[f"drafted_y{year_offset}"] = drafted
            result[f"kept_y{year_offset}"] = kept
            result[f"cleared_y{year_offset}"] = cleared

        return result


class KeeperAnalyzer:
    """Analyzes keeper eligibility for fantasy football players."""

    def __init__(
        self,
        draft_history: list[pd.DataFrame],
        transaction_history: list[pd.DataFrame],
    ):
        """Initialize analyzer with historical data.

        Args:
            draft_history: List of draft DataFrames (newest first)
            transaction_history: List of transaction DataFrames (newest first)
        """
        self.draft_history = draft_history
        self.transaction_history = transaction_history

    def analyze_player(
        self,
        player_name: str,
        team_name: str,
        position: str,
    ) -> KeeperEligibility:
        """Analyze keeper eligibility for a single player.

        Args:
            player_name: Player's full name
            team_name: Current team name
            position: Player position

        Returns:
            KeeperEligibility object with all eligibility info
        """
        # Get draft history
        drafted_history = []
        kept_history = []
        draft_costs = []

        for draft_df in self.draft_history:
            player_picks = draft_df[draft_df["player_name"] == player_name]
            if len(player_picks) > 0:
                pick = player_picks.iloc[0]
                drafted_history.append(True)
                kept_history.append(pick["keeper"])
                draft_costs.append(pick["cost"])
            else:
                drafted_history.append(False)
                kept_history.append(False)
                draft_costs.append(None)

        # Get transaction history and determine waiver clears
        cleared_waivers = []
        for trans_df in self.transaction_history:
            player_trans = trans_df[trans_df["player_name"] == player_name]
            player_trans = player_trans.sort_values("timestamp", ascending=False)

            cleared = self._did_clear_waivers(player_trans)
            cleared_waivers.append(cleared)

        # Calculate keeper years
        years_kept = 0
        for i in range(GO_BACK_YEARS):
            if kept_history[i] and not cleared_waivers[i]:
                years_kept += 1
            else:
                break

        years_remaining = MAX_KEEP_YEARS - years_kept
        eligible = years_remaining > 0

        # Calculate cost based on years already kept
        if not eligible:
            # Use 999 instead of "N/A" for better sorting (will display as "-" in UI)
            current_cost: int | str = 999
        else:
            # Years kept + 1 (because we're calculating cost for NEXT year)
            next_year_num = years_kept + 1
            # Get increment for this year
            increment = KEEPER_YEAR_INCREMENTS.get(next_year_num, KEEPER_YEAR_INCREMENTS[MAX_KEEP_YEARS])

            # Add increment to original draft cost
            last_cost = draft_costs[0] if draft_costs[0] is not None else 0
            current_cost = last_cost + increment

        return KeeperEligibility(
            player_name=player_name,
            team_name=team_name,
            position=position,
            years_kept=years_kept,
            years_remaining=years_remaining,
            eligible=eligible,
            current_cost=current_cost,
            last_cost=draft_costs[0],
            drafted_history=drafted_history,
            kept_history=kept_history,
            cleared_waivers=cleared_waivers,
        )

    @staticmethod
    def _did_clear_waivers(transactions: pd.DataFrame) -> bool:
        """Determine if player cleared waivers based on transactions.

        Args:
            transactions: DataFrame of player transactions (sorted newest first)

        Returns:
            True if player cleared waivers
        """
        if len(transactions) == 0:
            return False

        for i in range(len(transactions)):
            row = transactions.iloc[i]
            trans_type = row["type"]

            # If added from FA, cleared waivers
            if trans_type == TransactionType.ADD.value:
                return True

            # Check waiver timing
            if trans_type == TransactionType.WAIVER.value and i + 1 < len(transactions):
                next_row = transactions.iloc[i + 1]
                time_diff = row["timestamp"] - next_row["timestamp"]

                if time_diff > DROP_TO_PICKUP:
                    return True

        return False

    def analyze_roster(self, roster: pd.DataFrame, team_name: str) -> pd.DataFrame:
        """Analyze keeper eligibility for entire roster.

        Args:
            roster: DataFrame with player roster
            team_name: Team name

        Returns:
            DataFrame with keeper eligibility for all players
        """
        eligibilities = []

        for _, player in roster.iterrows():
            eligibility = self.analyze_player(
                player_name=player["name"],
                team_name=team_name,
                position=player["position"],
            )
            eligibilities.append(eligibility.to_dict())

        return pd.DataFrame(eligibilities)
