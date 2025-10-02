"""Data models for GMB fantasy football library."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class Player:
    """Represents a fantasy football player."""

    player_id: int
    name: str
    position: str
    team: str | None = None
    projected_points: float = 0.0
    points: float = 0.0

    @classmethod
    def from_espn_data(cls, data: dict[str, Any]) -> Player:
        """Create Player from ESPN API response data.

        Args:
            data: Player data from ESPN API

        Returns:
            Player instance
        """
        player_data = data.get("player", {})
        return cls(
            player_id=data.get("playerId", 0),
            name=player_data.get("fullName", "Unknown"),
            position=player_data.get("defaultPositionId", "Unknown"),
            team=player_data.get("proTeamId"),
            projected_points=data.get("projectedPoints", 0.0),
            points=data.get("points", 0.0),
        )


class TransactionType(Enum):
    """Types of league transactions."""

    ADD = "ADD"
    DROP = "DROP"
    WAIVER = "WAIVER"
    TRADE = "TRADE"
    DRAFT = "DRAFT"


@dataclass
class Transaction:
    """Represents a league transaction."""

    transaction_type: TransactionType
    player_name: str
    team_name: str
    timestamp: int
    bid_amount: int | None = None

    @classmethod
    def from_espn_data(cls, data: dict[str, Any], teams_map: dict[int, str]) -> Transaction | None:
        """Create Transaction from ESPN API response data.

        Args:
            data: Transaction data from ESPN API
            teams_map: Mapping of team IDs to team names

        Returns:
            Transaction instance or None if invalid
        """
        # Extract transaction type
        type_map = {
            178: TransactionType.ADD,
            179: TransactionType.DROP,
            180: TransactionType.WAIVER,
            181: TransactionType.TRADE,
        }

        trans_type_id = data.get("type")
        trans_type = type_map.get(trans_type_id) if trans_type_id else None
        if not trans_type:
            return None

        # Extract player info
        items = data.get("items", [])
        if not items:
            return None

        item = items[0]
        player_name = item.get("playerName", "Unknown")
        team_id = item.get("toTeamId") or item.get("fromTeamId", 0)
        team_name = teams_map.get(team_id, "Unknown")

        return cls(
            transaction_type=trans_type,
            player_name=player_name,
            team_name=team_name,
            timestamp=data.get("proposedDate", 0),
            bid_amount=data.get("bidAmount"),
        )


@dataclass
class DraftPick:
    """Represents a draft pick."""

    player_name: str
    team_name: str
    round_num: int
    pick_num: int
    keeper: bool
    cost: int

    @classmethod
    def from_espn_data(cls, data: dict[str, Any], teams_map: dict[int, str]) -> DraftPick:
        """Create DraftPick from ESPN API response data.

        Args:
            data: Draft pick data from ESPN API
            teams_map: Mapping of team IDs to team names

        Returns:
            DraftPick instance
        """
        return cls(
            player_name=data.get("playerName", "Unknown"),
            team_name=teams_map.get(data.get("teamId", 0), "Unknown"),
            round_num=data.get("roundId", 0),
            pick_num=data.get("overallPickNumber", 0),
            keeper=data.get("keeper", False),
            cost=data.get("bidAmount", 0),
        )
