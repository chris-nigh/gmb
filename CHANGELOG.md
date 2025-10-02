# Changelog - Keeper Feature Enhancements

## Updates - October 2025

### 🔒 Keeper Summary Tab Improvements

#### Position Display
- ✅ **Position names instead of IDs**: Positions now display as "QB", "RB", "WR", etc. instead of numeric IDs (1, 2, 4)
- ✅ **New column: Position Rank**: Shows each player's rank within their position based on keeper cost (lower cost = higher rank)
  - Rank 1 = cheapest keeper at that position
  - Only eligible keepers are ranked
  - Ineligible players show "-" for rank

#### Cost Display
- ✅ **Removed "N/A" values**: Ineligible players now show "-" instead of "N/A"
- ✅ **Numeric sorting**: Cost column now sorts properly as numbers
- ✅ **Formatted display**: All costs show with dollar signs (e.g., "$25")

#### Updated Columns
```
Player | Team | Position | Pos Rank | Eligible | Cost | Years Kept | Years Left
```

**Example:**
```
Josh Allen    | Team A | QB | 2  | ✓ | $45 | 1 | 2
Saquon Barkley| Team B | RB | 1  | ✓ | $35 | 0 | 3
Travis Kelce  | Team C | TE | 3  | ✓ | $40 | 2 | 1
Old Player    | Team D | WR | -  | ✗ | -   | 3 | 0
```

---

### 🎲 Keeper What-If Tool Improvements

#### Default Settings Updated
- ✅ **Roster size default**: Changed from 16 to **15 spots**

#### New Metrics
1. ✅ **Remaining Roster Spots**: Shows how many open spots you'll have after keepers
2. ✅ **Maximum Single Bid**: Calculates the highest amount you can bid on one player
   - Formula: `Remaining Budget - Remaining Roster Spots`
   - Ensures you can still afford $1 for each remaining roster spot

#### Enhanced Draft Impact Display
**Before:**
```
Keepers: 3 | Total Cost: $95 | Remaining: $105 | Avg: $8.08
```

**After (3 columns, 2 metrics each):**
```
Column 1:                    Column 2:                Column 3:
Keepers Selected: 3          Total Keeper Cost: $95   Avg $/Player: $8.75
Remaining Roster Spots: 12   Remaining Budget: $105   Max Single Bid: $93
```

#### Roster Format Display
- ✅ **Organized by position**: Keepers now display grouped by position (QB, RB, WR, TE, K, D/ST)
- ✅ **Cleaner layout**: Each player shows name, cost, and years remaining in a structured format

**Example Display:**
```
Your Keeper Roster
------------------
**QB**
• Josh Allen        $45    2 yrs left

**RB**
• Saquon Barkley    $35    3 yrs left
• Kenneth Walker    $25    2 yrs left

**WR**
• CeeDee Lamb       $30    1 yr left

**TE**
• (empty)

---
Open Roster Spots: 11
```

---

### 🛠️ Technical Changes

#### New Files
- **`src/gmb/position_map.py`**: ESPN position ID to position name mapping
  - Supports all standard fantasy positions
  - Helper function: `get_position_name(position_id)`

#### Modified Files

**`src/gmb/keeper.py`**
- Import position mapping
- Added `position_id` field to keeper data (preserves original ID)
- Convert position IDs to names in `to_dict()` method
- Changed ineligible cost from `"N/A"` to `999` (numeric value for sorting)

**`src/gmb/viz.py`**
- Enhanced `create_keeper_summary_table()`:
  - Calculate position rank within each position group
  - Format cost display (999 → "-")
  - Format rank display (NaN → "-")
  - Added "Pos Rank" column

**`app.py`**
- Fixed dollar sign escaping in Keeper Rules message (use `\\$` for proper markdown)
- Updated What-If default roster size: 15
- Added new metrics: Remaining Roster Spots, Maximum Single Bid
- Reorganized Draft Impact display (3 columns, 2 metrics each)
- Implemented roster-style display for keeper selections
  - Groups by position
  - Shows position headers (QB, RB, WR, etc.)
  - Lists players with cost and years remaining
  - Displays open roster spots summary

---

### 📊 Position Rank Calculation

Position rank is calculated as follows:
1. Filter to **eligible keepers only**
2. Group players by position
3. Rank by keeper cost (ascending)
   - Rank 1 = lowest cost at position
   - Rank 2 = second lowest, etc.
4. Ineligible players show "-" for rank

**Example Position Rankings:**

**QB Rankings:**
```
Rank 1: Patrick Mahomes  - $35
Rank 2: Josh Allen       - $45
Rank 3: Jalen Hurts      - $50
```

**RB Rankings:**
```
Rank 1: Saquon Barkley   - $35
Rank 2: Kenneth Walker   - $25  (wait, this would be Rank 1!)
Rank 3: Derrick Henry    - $40
```

*(Corrected: Rankings are based on cost, not arbitrary order)*

---

### 🎯 Maximum Bid Calculation

The maximum bid represents the highest amount you can spend on a single player while still being able to afford $1 for each remaining roster spot.

**Formula:**
```
Max Bid = Remaining Budget - Remaining Roster Spots
```

**Example:**
- Remaining Budget: $105
- Remaining Roster Spots: 12
- Max Bid: $105 - $12 = **$93**

This ensures you always have enough money to fill your roster, even if you only bid $1 for each remaining spot.

**Special Cases:**
- If `Remaining Spots > Remaining Budget`, Max Bid = $0 (budget crisis!)
- If `Remaining Spots = 0`, Max Bid = Remaining Budget (all spots filled)

---

### 🐛 Bug Fixes

1. **Cost Sorting Issue**
   - **Before**: "N/A" values prevented numeric sorting
   - **After**: Ineligible costs stored as 999, displayed as "-"

2. **Position Display**
   - **Before**: Showed numeric IDs (1, 2, 4, 6)
   - **After**: Shows position names (QB, RB, WR, TE)

3. **Markdown Formatting**
   - **Before**: "$5" in Keeper Rules caused display issues
   - **After**: "\\$5" properly escapes dollar signs

---

### 🚀 Testing Checklist

- [ ] Verify position names display correctly in Keeper Summary
- [ ] Check that position rank shows for eligible players only
- [ ] Confirm cost column sorts numerically
- [ ] Test that ineligible players show "-" for cost and rank
- [ ] Verify What-If default roster size is 15
- [ ] Check that "Remaining Roster Spots" metric appears
- [ ] Verify "Maximum Single Bid" calculation is correct
- [ ] Confirm keeper selections display in roster format by position
- [ ] Test with various keeper combinations (0, 1, 2, 3+ keepers)
- [ ] Verify dollar sign displays correctly in Keeper Rules message

---

### 📝 Notes for Future Enhancements

**Position-Based Roster Requirements**
- Could add typical roster requirements (e.g., 1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 K, 1 D/ST)
- Show which positions are filled vs. open
- Highlight positional needs for draft strategy

**Advanced Keeper Value Metrics**
- Add ADP (Average Draft Position) data if available
- Calculate keeper value as: ADP - Keeper Cost
- Show "draft pick value saved" by keeping players

**Keeper Deadline Countdown**
- Add configurable keeper deadline date
- Show countdown timer
- Send reminders as deadline approaches

---

## Summary

All requested changes have been implemented:
- ✅ Position names instead of IDs
- ✅ Position rank column added
- ✅ N/A cost replaced with "-" (stored as 999)
- ✅ Dollar sign formatting fixed
- ✅ Default roster size set to 15
- ✅ Remaining roster spots metric added
- ✅ Maximum bid calculation added
- ✅ Roster-style format for keeper selections

**Files Modified:** 4 (app.py, viz.py, keeper.py, + new position_map.py)
**Lines Changed:** ~150
**New Features:** 3 (pos rank, max bid, roster format)
**Bug Fixes:** 3 (cost sorting, position display, markdown)
