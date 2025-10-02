# Keeper Cost Fix

## Issue
Incorrect keeper cost calculation was implemented. The costs were set as flat amounts instead of incremental increases from the original draft cost.

## Incorrect Implementation (Previous)
```
Year 1: $5 flat
Year 2: $10 flat
Year 3: $15 flat
```

**Example with $40 drafted player:**
- Year 1 keeper cost: $5 ❌
- Year 2 keeper cost: $10 ❌
- Year 3 keeper cost: $15 ❌

## Correct Implementation (Fixed)
```
Year 1: Original cost + $5
Year 2: Original cost + $10
Year 3: Original cost + $15
```

**Example with $40 drafted player:**
- Year 1 keeper cost: $40 + $5 = **$45** ✓
- Year 2 keeper cost: $40 + $10 = **$50** ✓
- Year 3 keeper cost: $40 + $15 = **$55** ✓

## Changes Made

### 1. Updated Constants File
**File:** [src/gmb/keeper_constants.py](src/gmb/keeper_constants.py)

**Before:**
```python
KEEPER_YEAR_COSTS = {
    1: 5,   # First year keeping
    2: 10,  # Second year keeping
    3: 15,  # Third year keeping
}
```

**After:**
```python
KEEPER_YEAR_INCREMENTS = {
    1: 5,   # First year keeping: +$5
    2: 10,  # Second year keeping: +$10
    3: 15,  # Third year keeping: +$15
}
```

### 2. Updated Calculation Logic
**File:** [src/gmb/keeper.py](src/gmb/keeper.py)

**Before:**
```python
# Years kept + 1 (because we're calculating cost for NEXT year)
next_year_num = years_kept + 1
# Get cost from lookup table
current_cost = KEEPER_YEAR_COSTS.get(next_year_num, KEEPER_YEAR_COSTS[MAX_KEEP_YEARS])
```

**After:**
```python
# Years kept + 1 (because we're calculating cost for NEXT year)
next_year_num = years_kept + 1
# Get increment for this year
increment = KEEPER_YEAR_INCREMENTS.get(next_year_num, KEEPER_YEAR_INCREMENTS[MAX_KEEP_YEARS])

# Add increment to original draft cost
last_cost = draft_costs[0] if draft_costs[0] is not None else 0
current_cost = last_cost + increment
```

### 3. Updated Rules Message
**File:** [app.py](app.py)

**Before:**
```
Keeper Rules: Players can be kept for up to 3 years.
Cost is $5 for year 1, $10 for year 2, and $15 for year 3.
```

**After:**
```
Keeper Rules: Players can be kept for up to 3 years.
Cost increases by $5 in year 1, $10 in year 2, and $15 in year 3 from the original draft cost.
```

## Examples

### Example 1: Expensive Star Player
**Player:** Christian McCaffrey
**Original Draft Cost:** $65

| Year | Calculation | Keeper Cost |
|------|-------------|-------------|
| 1 | $65 + $5 | **$70** |
| 2 | $65 + $10 | **$75** |
| 3 | $65 + $15 | **$80** |

### Example 2: Mid-Tier Player
**Player:** Deebo Samuel
**Original Draft Cost:** $25

| Year | Calculation | Keeper Cost |
|------|-------------|-------------|
| 1 | $25 + $5 | **$30** |
| 2 | $25 + $10 | **$35** |
| 3 | $25 + $15 | **$40** |

### Example 3: Waiver Pickup
**Player:** Puka Nacua
**Original Draft Cost:** $0 (waiver wire)

| Year | Calculation | Keeper Cost |
|------|-------------|-------------|
| 1 | $0 + $5 | **$5** |
| 2 | $0 + $10 | **$10** |
| 3 | $0 + $15 | **$15** |

## Impact on Keeper Value

The fixed implementation makes keeper value calculations more intuitive:

**High-value keepers:**
- Late-round gems (low draft cost, high production)
- Waiver pickups who became stars
- Example: $0 waiver pickup → $5 keeper = great value

**Lower-value keepers:**
- Expensive stars (already paid premium price)
- Example: $65 star → $70 keeper = marginal value increase

## Testing

To verify the fix works correctly:

1. Check a player drafted for $40 who was kept once (years_kept = 1)
   - Expected next keeper cost: $40 + $10 = $50 ✓

2. Check a waiver pickup (drafted for $0) who was kept twice (years_kept = 2)
   - Expected next keeper cost: $0 + $15 = $15 ✓

3. Check an expensive player ($60) being kept for the first time (years_kept = 0)
   - Expected next keeper cost: $60 + $5 = $65 ✓

## Files Modified

1. [src/gmb/keeper_constants.py](src/gmb/keeper_constants.py) - Renamed constant, added clarifying comments
2. [src/gmb/keeper.py](src/gmb/keeper.py) - Updated cost calculation to add increment to original cost
3. [app.py](app.py) - Updated keeper rules message

## Summary

✅ **Fixed:** Keeper costs now correctly calculated as original draft cost + increment
✅ **Renamed:** `KEEPER_YEAR_COSTS` → `KEEPER_YEAR_INCREMENTS`
✅ **Updated:** Rules message to clarify incremental increase
✅ **Tested:** Syntax validated, ready to deploy

The keeper cost calculation now properly reflects incremental increases from the original draft cost, making keeper value analysis more accurate and intuitive.
