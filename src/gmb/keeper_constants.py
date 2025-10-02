"""Constants for keeper league rules and calculations."""

# Keeper pricing rules
# Cost structure: Original cost + increment per year
# Year 1: original + $5, Year 2: original + $10, Year 3: original + $15
KEEPER_YEAR_INCREMENTS = {
    1: 5,  # First year keeping: +$5
    2: 10,  # Second year keeping: +$10
    3: 15,  # Third year keeping: +$15
}
MAX_KEEP_YEARS = 3  # Maximum years a player can be kept
GO_BACK_YEARS = 3  # Years of history to analyze

# Transaction timing
MS_IN_DAY = 1000 * 60 * 60 * 24  # Milliseconds in a day
DROP_TO_PICKUP = 7 * MS_IN_DAY  # Time window for waiver clearing (7 days)
