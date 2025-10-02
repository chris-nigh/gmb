# GMB Dashboard - New Features Summary

## 🎉 What's New

### 1. 🔒 Keeper Summary Tab
A comprehensive view of keeper eligibility across all teams in your league.

**Features:**
- **Team Filter**: View keeper data for all teams or filter by specific team
- **Eligibility Table**: Shows all players with their keeper status, cost, years kept, and years remaining
  - Green highlighting for eligible keepers
  - Red highlighting for ineligible players
- **Summary Metrics**:
  - Total eligible keepers league-wide
  - Average years remaining
  - Average keeper cost
- **Visual Analytics**:
  - Total keeper cost by team (bar chart)
  - Keeper value scatter plot (cost vs. years remaining)

**How to Use:**
1. Navigate to the "🔒 Keepers" tab
2. Use the team filter dropdown to focus on specific teams
3. Review the color-coded eligibility table
4. Analyze keeper distribution across the league with charts

---

### 2. 🎲 Keeper What-If Tool
Interactive tool to experiment with keeper selections and see their impact on your draft strategy.

**Features:**
- **Team Selection**: Choose your team from the dropdown
- **Configurable Settings**:
  - Auction budget (default: $200)
  - Roster size (default: 16)
  - Max keepers allowed (default: 3)
- **Interactive Keeper Selection**: Multi-select interface showing player name, position, and cost
- **Real-time Draft Impact Metrics**:
  - Number of keepers selected
  - Total keeper cost
  - Remaining auction budget
  - Average dollars per remaining roster spot
- **Smart Alerts**:
  - ⚠️ Budget warnings if you can't afford remaining roster spots
  - ⚠️ Low flexibility warnings for tight budgets
  - ✅ Success indicators for good draft position
- **Scenario Comparison**: Expandable table showing all possible keeper combinations and their impacts

**How to Use:**
1. Go to the "🎲 Keeper What-If" tab
2. Select your team
3. Adjust league settings if needed (budget, roster size, max keepers)
4. Select players to keep using the multi-select dropdown
5. View real-time impact on your draft budget
6. Expand "Compare All Keeper Scenarios" to see alternative strategies

---

### 3. 📈 Enhanced Analytics Tab
New advanced analytics to help understand team performance beyond wins and losses.

**New Visualizations:**

#### Schedule Strength
- Bar chart showing average opponent score faced by each team
- Identifies which teams have had easy or tough schedules
- Color-coded: Red = tougher opponents, lighter = easier opponents

#### Scoring Consistency (Boom/Bust Analysis)
- Scatter plot comparing average score vs. standard deviation
- Teams positioned in quadrants:
  - **Top-Right**: High scoring but volatile (boom/bust teams)
  - **Bottom-Right**: High scoring and consistent (elite teams)
  - **Top-Left**: Low scoring and volatile (struggling teams)
  - **Bottom-Left**: Low scoring but consistent (predictably weak)
- Helps identify reliable vs. unpredictable teams

**How to Use:**
1. Visit the "📈 Analytics" tab
2. Scroll down to see schedule strength and consistency charts
3. Use insights to evaluate playoff readiness and trade targets

---

## 🎨 Design Philosophy

All new features follow the **Vermont Green Mountains** theme:
- Forest green color palette
- Clean, readable tables
- Data-driven insights without fluff
- Practical tools for league decision-making

---

## 🔧 Technical Details

### Performance Optimizations
- **Caching**: Keeper data is cached for 1 hour to reduce API calls
- **Lazy Loading**: Keeper tab only loads data when accessed
- **Efficient Queries**: Historical data fetched once and reused across features

### Data Requirements
- Keeper features require **3 years of historical data** (configurable in `keeper_constants.py`)
- Supports both draft and transaction history from ESPN
- Works with auction and snake draft formats

---

## 💡 Additional Analytics Suggestions

Here are some ideas for future enhancements:

### 1. **Playoff Probability Calculator**
- Simulate remaining games to calculate playoff odds
- Show magic numbers for clinching/elimination
- Account for schedule strength

### 2. **Trade Analyzer**
- Input proposed trade
- Calculate fair value based on recent performance
- Show positional scarcity impact
- Predict post-trade power rankings

### 3. **Waiver Wire Optimizer**
- Track available players and their trends
- Suggest waiver pickups based on team needs
- Show projected keeper value of FA pickups

### 4. **Draft Pick Value Calculator**
- For keeper leagues: show value of draft picks you'll gain/lose
- Compare keeper costs vs. expected draft position value
- Help decide whether to keep or release players

### 5. **Matchup Predictor**
- Use historical data to predict future matchup outcomes
- Show win probability for upcoming weeks
- Factor in bye weeks and injuries (if data available)

### 6. **Position Scarcity Analysis**
- Show league-wide roster construction
- Identify which positions are hoarded
- Suggest trade targets based on scarcity

---

## 🐛 Known Limitations

1. **Keeper Rules**: The app assumes standard keeper rules (max 3 years, $5 increment). These are configurable in `keeper_constants.py`.
2. **ESPN API**: Some keeper data may not be available for all league types or older seasons.
3. **Transaction Timing**: Waiver clearing detection uses a 7-day window, which may need adjustment for your league.

---

## 📝 Configuration

### Keeper Constants
Edit `src/gmb/keeper_constants.py` to adjust:
- `MAX_KEEP_YEARS`: Maximum years a player can be kept (default: 3)
- `YEAR_COST_INCR`: Cost increase per year (default: $5)
- `GO_BACK_YEARS`: Years of history to analyze (default: 3)
- `DROP_TO_PICKUP`: Time window for waiver clearing (default: 7 days)

---

## 🚀 Getting Started

1. Make sure you've run `gmb setup` to configure your league
2. Launch the dashboard: `streamlit run app.py`
3. Navigate to the new tabs:
   - **🔒 Keepers**: View league-wide keeper eligibility
   - **🎲 Keeper What-If**: Plan your keeper strategy
   - **📈 Analytics**: Enhanced analytics with schedule and consistency data

---

## 📊 Screenshots

*(Consider adding screenshots here after running the app)*

---

## 🤝 Contributing

Have ideas for new analytics or features? The codebase is structured to make adding new visualizations easy:

1. Add new chart methods to `src/gmb/viz.py` in the `FantasyDashboard` class
2. Call them from `app.py` in the appropriate tab
3. Follow the Vermont theme color palette for consistency

---

**Happy drafting! 🏔️**
