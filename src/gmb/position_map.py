"""ESPN position ID to position name mapping."""

# ESPN position ID mappings for fantasy football
POSITION_MAP = {
    1: "QB",  # Team QB (rare)
    2: "RB",
    3: "WR",
    4: "TE",
    7: "OP",  # Offensive Player
    8: "DT",
    9: "DE",
    10: "LB",
    11: "DL",
    12: "CB",
    13: "S",
    14: "DB",
    15: "DP",
    16: "D/ST",
    17: "K",
    18: "P",
    19: "HC",  # Head Coach
    20: "BE",  # Bench
    21: "IR",
    22: "Unknown",
    23: "RB/WR/TE",  # Flex
}


def get_position_name(position_id: int | str) -> str:
    """Convert ESPN position ID to position name.

    Args:
        position_id: ESPN position ID (int or string)

    Returns:
        Position name string (e.g., "QB", "RB", "WR")
    """
    try:
        pos_id = int(position_id)
        return POSITION_MAP.get(pos_id, f"POS{pos_id}")
    except (ValueError, TypeError):
        return str(position_id)
