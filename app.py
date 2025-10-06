"""GMB Fantasy Football Dashboard main script."""

import pandas as pd
import streamlit as st

from gmb.config import DashboardConfig
from gmb.espn import ESPNFantasyLeague
from gmb.espn_keeper import ESPNKeeperLeague
from gmb.keeper import KeeperAnalyzer
from gmb.keeper_constants import GO_BACK_YEARS
from gmb.oiwp import calculate_oiwp_stats
from gmb.viz import FantasyDashboard


def apply_vermont_styling():
    """Apply Vermont Green Mountains theme with custom CSS."""
    st.markdown(
        """
        <style>
        /* Vermont Green Mountains Theme */

        /* Main background with subtle texture */
        .main {
            background: linear-gradient(135deg, #F5F3EE 0%, #E8E5DC 100%);
        }

        /* Streamlit headers with mountain-inspired colors */
        h1, h2, h3 {
            color: #1A3329 !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
        }

        h1 {
            border-bottom: 3px solid #2D5F3F;
            padding-bottom: 10px;
        }

        /* Metric cards with forest green accents */
        [data-testid="stMetricValue"] {
            color: #2D5F3F !important;
            font-weight: 700;
        }

        [data-testid="stMetricLabel"] {
            color: #4A7C59 !important;
            font-weight: 600;
        }

        /* Tabs with autumn-inspired colors */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #E8E5DC;
            border-radius: 8px 8px 0 0;
            padding: 5px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 5px;
            padding: 10px 20px;
            color: #4A7C59;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2D5F3F 0%, #4A7C59 100%);
            color: #F5F3EE !important;
        }

        /* Info boxes with mountain meadow colors */
        .stAlert {
            background-color: #D4E7DD !important;
            border-left: 4px solid #2D5F3F !important;
            color: #1A3329 !important;
        }

        /* Dataframes with subtle borders */
        [data-testid="stDataFrame"] {
            border: 2px solid #C5D5CC !important;
            border-radius: 8px;
        }

        /* Buttons with forest green */
        .stButton>button {
            background: linear-gradient(135deg, #2D5F3F 0%, #4A7C59 100%);
            color: #F5F3EE;
            border: none;
            border-radius: 5px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #1A3329 0%, #2D5F3F 100%);
            box-shadow: 0 4px 12px rgba(45, 95, 63, 0.3);
        }

        /* Sidebar with darker forest theme */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2D5F3F 0%, #1A3329 100%);
        }

        [data-testid="stSidebar"] * {
            color: #E8E5DC !important;
        }

        /* Charts and plots with subtle backgrounds */
        [data-testid="stPlotlyChart"] {
            background-color: #FAFAF8;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 8px rgba(26, 51, 41, 0.1);
        }

        /* Subheaders with accent color */
        .stSubheader {
            color: #4A7C59 !important;
            border-bottom: 2px solid #C5D5CC;
            padding-bottom: 5px;
        }

        /* Add subtle mountain silhouette to top */
        .main::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 150px;
            background: linear-gradient(to bottom, rgba(45, 95, 63, 0.05) 0%, transparent 100%);
            pointer-events: none;
            z-index: -1;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Main entry point for the dashboard application."""
    st.set_page_config(page_title="🏔️ Green Mountain Boys", layout="wide", page_icon="🏔️")

    # Apply Vermont styling
    apply_vermont_styling()

    st.title("🏔️ Green Mountain Boys")

    try:
        # Load configuration from environment variables
        print("Loading configuration...")
        config = DashboardConfig.load()
        print(f"Loaded config: {config.to_dict()}")

        # Initialize league client
        league = ESPNFantasyLeague(**config.to_dict())

        # Create dashboard instance
        dashboard = FantasyDashboard(league)

        # Load initial data
        dashboard.load_data()

        # Create metrics row
        col1, col2, col3 = st.columns(3)

        if dashboard.teams_df is not None:
            with col1:
                st.metric("Total Teams", len(dashboard.teams_df))
            with col2:
                st.metric("Avg Points/Game", f"{dashboard.teams_df['points_for'].mean():.1f}")
            with col3:
                highest_scorer = dashboard.teams_df.loc[
                    dashboard.teams_df["points_for"].idxmax(), "team_name"
                ]
                st.metric("Highest Scorer", str(highest_scorer))

        # Create tabs for different views
        tab1, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            [
                "📊 Overview",
                "🎯 OIWP Analysis",
                "🔒 Keepers",
                "🎲 Keeper What-If",
                "📋 Draft Analysis",
                "✨ Taylor's Eras",
            ]
        )

        with tab1:
            # Standings section
            st.subheader("Current Standings")
            if dashboard.teams_df is not None:
                standings = dashboard.teams_df[
                    ["team_name", "wins", "losses", "points_for", "points_against"]
                ].sort_values(["wins", "points_for"], ascending=[False, False])
                st.dataframe(standings, use_container_width=True, hide_index=True)

            st.subheader("League Standings Chart")
            dashboard.create_standings_chart()

            # Analytics section
            if dashboard.matchups_df is not None:
                st.subheader("Weekly Scoring Trends")
                dashboard.create_weekly_scores_line()

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Points For vs Points Against")
                    dashboard.create_points_scatter()
                with col2:
                    st.subheader("Schedule Strength")
                    dashboard.create_schedule_strength_chart()

                st.subheader("Scoring Consistency Analysis")
                dashboard.create_consistency_chart()
            else:
                st.warning("Matchup data not available for analytics")

        # Power Rankings tab (hidden for now, keeping code)
        # with tab2:
        #     st.subheader("Power Rankings")
        #     if dashboard.teams_df is not None:
        #         rankings = dashboard.generate_power_rankings()
        #         st.dataframe(rankings, use_container_width=True)
        #
        #         st.info(
        #             "Power rankings are calculated using a weighted formula: "
        #             "60% wins + 40% normalized points scored"
        #         )

        with tab3:
            st.subheader("Opponent-Independent Winning Percentage (OIWP)")

            if dashboard.matchups_df is not None and not dashboard.matchups_df.empty:
                # Calculate OIWP stats
                oiwp_stats = calculate_oiwp_stats(dashboard.matchups_df)

                if not oiwp_stats.empty:
                    # Display OIWP table with color formatting
                    display_df = oiwp_stats.copy()

                    # Format numeric columns first
                    display_df["wp"] = display_df["wp"].apply(lambda x: f"{x:.3f}")
                    display_df["oiwp"] = display_df["oiwp"].apply(lambda x: f"{x:.3f}")
                    display_df["luck"] = display_df["luck"].apply(lambda x: f"{x:+.3f}")
                    display_df["schedule_wins"] = display_df["schedule_wins"].apply(
                        lambda x: f"{x:+d}"
                    )

                    # Rename columns
                    display_df.columns = [
                        "Team Name",
                        "Record",
                        "OIWP Predicted Record",
                        "Win %",
                        "OIWP",
                        "Luck",
                        "Schedule Wins",
                    ]

                    # Define color function for styled values
                    def color_numeric_value(val):
                        """Apply color based on positive/negative values."""
                        try:
                            # Extract numeric value from formatted string
                            num_str = str(val).replace("+", "")
                            num_val = float(num_str)

                            if num_val > 0:
                                return "color: #28a745; font-weight: bold;"  # Standard green for positive
                            elif num_val < 0:
                                return "color: #dc3545; font-weight: bold;"  # Standard red for negative
                            else:
                                return "color: #6c757d;"  # Gray for neutral
                        except (ValueError, AttributeError):
                            return ""

                    # Apply styling to Luck and Schedule Wins columns
                    styled_df = display_df.style.map(
                        color_numeric_value, subset=["Luck", "Schedule Wins"]
                    ).hide(axis="index")

                    st.dataframe(styled_df, use_container_width=True)

                    # Explanation
                    st.info(
                        "**OIWP (Opponent-Independent Winning Percentage)** measures how well each team "
                        "would perform if they played against *every* other team in the league each week.\n\n"
                        "- **Record**: Actual win-loss record from head-to-head matchups\n"
                        "- **Predicted Record**: What your record would be based on OIWP\n"
                        "- **Win %**: Actual winning percentage from head-to-head matchups\n"
                        "- **OIWP**: Winning percentage against all teams (not just your opponent)\n"
                        "- **Luck**: Difference between Win % and OIWP\n"
                        "  - **Positive luck** (green): You're winning more than your scores suggest (favorable matchups)\n"
                        "  - **Negative luck** (red): You're losing more than your scores suggest (tough matchups)\n"
                        "- **Schedule Wins**: Actual wins minus predicted wins\n"
                        "  - **Positive** (+): Extra wins from favorable schedule\n"
                        "  - **Negative** (-): Lost wins from tough schedule"
                    )

                    # Visualizations
                    dashboard.create_oiwp_chart(oiwp_stats)
                    dashboard.create_luck_chart(oiwp_stats)
                else:
                    st.warning("Unable to calculate OIWP statistics")
            else:
                st.warning("Matchup data not available for OIWP calculation")

        with tab4:
            st.subheader("Keeper Eligibility Summary")

            # Add a cache for keeper data to avoid reloading
            @st.cache_data(ttl=3600)
            def load_keeper_data(league_id: int, year: int, espn_s2: str | None, swid: str | None):
                """Load keeper data for all teams."""
                try:
                    keeper_league = ESPNKeeperLeague(
                        league_id=league_id,
                        year=year,
                        espn_s2=espn_s2,
                        swid=swid,
                    )

                    # Collect historical data
                    draft_history = []
                    transaction_history = []

                    with st.spinner(f"Loading keeper data ({GO_BACK_YEARS} years of history)..."):
                        for hist_year in range(year, year - GO_BACK_YEARS, -1):
                            draft_df = keeper_league.get_draft_picks(hist_year)
                            trans_df = keeper_league.get_transactions(hist_year)
                            draft_history.append(draft_df)
                            transaction_history.append(trans_df)

                    # Get all teams and rosters
                    teams_df = keeper_league.get_teams()
                    analyzer = KeeperAnalyzer(draft_history, transaction_history)

                    # Get player stats for position ranking
                    with st.spinner("Loading player statistics..."):
                        player_stats = keeper_league.get_player_stats(year)

                    all_keeper_data = []
                    for _, team in teams_df.iterrows():
                        team_id = team["team_id"]
                        team_name = team["team_name"]
                        roster_df = keeper_league.get_roster(team_id, year)
                        team_keeper_data = analyzer.analyze_roster(roster_df, team_name)
                        all_keeper_data.append(team_keeper_data)

                    keeper_df = (
                        pd.concat(all_keeper_data, ignore_index=True)
                        if all_keeper_data
                        else pd.DataFrame()
                    )

                    # Merge with player stats to get scoring data
                    if not keeper_df.empty and not player_stats.empty:
                        # Merge on player_name
                        keeper_df = keeper_df.merge(
                            player_stats[["player_name", "total_points", "position_id"]],
                            on="player_name",
                            how="left",
                            suffixes=("", "_stats"),
                        )

                    return keeper_df

                except Exception as e:
                    st.error(f"Error loading keeper data: {e}")
                    import traceback

                    st.error(traceback.format_exc())
                    return pd.DataFrame()

            # Load keeper data
            keeper_data = load_keeper_data(
                config.league_id, config.year, config.espn_s2, config.swid
            )

            if not keeper_data.empty:
                # Team filter
                teams_list = ["All Teams"] + sorted(keeper_data["team_name"].unique().tolist())
                selected_team = st.selectbox("Filter by Team", teams_list)

                # Display keeper summary table
                st.subheader("Keeper Eligible Players")
                dashboard.create_keeper_summary_table(keeper_data, selected_team)

                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_eligible = keeper_data["eligible"].sum()
                    st.metric("Total Eligible Keepers", total_eligible)
                with col2:
                    avg_years = keeper_data[keeper_data["eligible"]]["years_remaining"].mean()
                    st.metric(
                        "Avg Years Remaining",
                        f"{avg_years:.1f}" if not pd.isna(avg_years) else "N/A",
                    )
                with col3:
                    eligible_with_cost = keeper_data[keeper_data["eligible"]].copy()
                    eligible_with_cost["cost_numeric"] = pd.to_numeric(
                        eligible_with_cost["keeper_cost"], errors="coerce"
                    )
                    avg_cost = eligible_with_cost["cost_numeric"].mean()
                    st.metric(
                        "Avg Keeper Cost", f"${avg_cost:.0f}" if not pd.isna(avg_cost) else "N/A"
                    )

                # Visualizations
                st.subheader("Keeper Analytics")
                dashboard.create_keeper_value_chart(keeper_data)

                max_years = int(
                    keeper_data["years_remaining"].max() + keeper_data["years_kept"].max()
                )
                st.info(
                    f"**Keeper Rules**: Players can be kept for up to {max_years} years. "
                    "Cost increases by \\$5 in year 1, \\$10 in year 2, and \\$15 in year 3 from the original draft cost."
                )
            else:
                st.warning(
                    "No keeper data available. Make sure your league has keeper settings enabled."
                )

        with tab5:
            st.subheader("Keeper What-If Tool")
            st.write(
                "Experiment with different keeper combinations to see their impact on your draft budget and roster."
            )

            # Reuse the keeper data from tab4
            keeper_data = load_keeper_data(
                config.league_id, config.year, config.espn_s2, config.swid
            )

            if not keeper_data.empty:
                # Team selection
                teams_list = sorted(keeper_data["team_name"].unique().tolist())
                selected_team = st.selectbox("Select Your Team", teams_list, key="whatif_team")

                # Filter to selected team's eligible keepers
                team_keepers = keeper_data[
                    (keeper_data["team_name"] == selected_team) & (keeper_data["eligible"])
                ].copy()

                if not team_keepers.empty:
                    # League settings (these would ideally come from ESPN API)
                    col1, col2 = st.columns(2)
                    with col1:
                        auction_budget = st.number_input(
                            "Auction Budget", min_value=0, value=200, step=10
                        )
                    with col2:
                        roster_size = st.number_input("Roster Size", min_value=1, value=15, step=1)

                    st.subheader("Select Your Keepers")

                    # Create multiselect for keeper selection
                    team_keepers["display_name"] = team_keepers.apply(
                        lambda x: f"{x['player_name']} ({x['position']}) - ${x['keeper_cost']}",
                        axis=1,
                    )

                    selected_keepers = st.multiselect(
                        "Choose players to keep",
                        team_keepers["display_name"].tolist(),
                        help="Select as many keepers as you want",
                    )

                    # Calculate impacts
                    if selected_keepers:
                        # Get costs for selected keepers
                        selected_df = team_keepers[
                            team_keepers["display_name"].isin(selected_keepers)
                        ].copy()
                        selected_df["cost_numeric"] = pd.to_numeric(
                            selected_df["keeper_cost"], errors="coerce"
                        ).fillna(0)
                        total_keeper_cost = selected_df["cost_numeric"].sum()
                        remaining_budget = auction_budget - total_keeper_cost
                        roster_spots_to_fill = roster_size - len(selected_keepers)
                        avg_per_player = (
                            remaining_budget / roster_spots_to_fill
                            if roster_spots_to_fill > 0
                            else 0
                        )

                        # Calculate max bid (need to leave $1 for each remaining spot)
                        max_bid = (
                            remaining_budget - roster_spots_to_fill
                            if roster_spots_to_fill > 0
                            else remaining_budget
                        )

                        # Display impacts
                        st.subheader("Draft Impact")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Keepers Selected", len(selected_keepers))
                            st.metric("Remaining Roster Spots", roster_spots_to_fill)
                        with col2:
                            st.metric("Total Keeper Cost", f"${total_keeper_cost:.0f}")
                            st.metric("Remaining Budget", f"${remaining_budget:.0f}")
                        with col3:
                            st.metric("Avg $/Player", f"${avg_per_player:.2f}")
                            st.metric(
                                "Maximum Single Bid", f"${max_bid:.0f}" if max_bid > 0 else "$0"
                            )

                        # Show selected keepers in roster format
                        st.subheader("Your Keeper Roster")

                        # Organize by position
                        position_order = ["QB", "RB", "WR", "TE", "K", "D/ST"]
                        selected_df["cost_display"] = selected_df["keeper_cost"].apply(
                            lambda x: f"${int(x)}"
                        )

                        # Group by position
                        grouped = selected_df.groupby("position")

                        for pos in position_order:
                            if pos in grouped.groups:
                                pos_players = grouped.get_group(pos)
                                st.markdown(f"**{pos}**")

                                for _, player in pos_players.iterrows():
                                    col1, col2, col3 = st.columns([3, 1, 1])
                                    with col1:
                                        st.write(f"• {player['player_name']}")
                                    with col2:
                                        st.write(f"{player['cost_display']}")
                                    with col3:
                                        years_left = int(player["years_remaining"])
                                        st.write(
                                            f"{years_left} yr{'s' if years_left != 1 else ''} left"
                                        )

                        # Show any other positions not in the standard list
                        other_positions = set(selected_df["position"].unique()) - set(
                            position_order
                        )
                        for pos in sorted(other_positions):
                            if pos in grouped.groups:
                                pos_players = grouped.get_group(pos)
                                st.markdown(f"**{pos}**")

                                for _, player in pos_players.iterrows():
                                    col1, col2, col3 = st.columns([3, 1, 1])
                                    with col1:
                                        st.write(f"• {player['player_name']}")
                                    with col2:
                                        st.write(f"${int(player['keeper_cost'])}")
                                    with col3:
                                        years_left = int(player["years_remaining"])
                                        st.write(
                                            f"{years_left} yr{'s' if years_left != 1 else ''} left"
                                        )

                        # Show summary of open roster spots by position
                        st.markdown("---")
                        st.markdown(f"**Open Roster Spots**: {roster_spots_to_fill}")

                        # Draft strategy insight
                        if remaining_budget < roster_spots_to_fill:
                            st.error(
                                "⚠️ Budget issue: You don't have enough money to fill remaining roster spots ($1 minimum per player)!"
                            )
                        elif avg_per_player < 5:
                            st.warning(
                                "⚠️ Low budget: You'll have limited flexibility in the draft with less than $5 per remaining player."
                            )
                        elif avg_per_player > 15:
                            st.success(
                                "✅ Good position: You have solid budget flexibility for the draft!"
                            )
                        else:
                            st.info(
                                "📊 Moderate budget: You'll need to balance stars and value picks."
                            )

                    else:
                        st.info("Select players above to see draft impact analysis.")

                else:
                    st.info(f"No eligible keepers found for {selected_team}")
            else:
                st.warning("No keeper data available for what-if analysis.")

        with tab6:
            st.subheader("Draft Analysis")

            # Cache draft data
            @st.cache_data(ttl=3600)
            def load_draft_data(league_id: int, year: int, espn_s2: str | None, swid: str | None):
                """Load draft data for analysis."""
                try:
                    keeper_league = ESPNKeeperLeague(
                        league_id=league_id,
                        year=year,
                        espn_s2=espn_s2,
                        swid=swid,
                    )
                    return keeper_league.get_draft_picks(year)
                except Exception as e:
                    st.error(f"Error loading draft data: {e}")
                    return pd.DataFrame()

            draft_data = load_draft_data(config.league_id, config.year, config.espn_s2, config.swid)

            # Load player stats for best/worst picks analysis
            @st.cache_data(ttl=3600)
            def load_player_stats_for_draft(
                league_id: int, year: int, espn_s2: str | None, swid: str | None
            ):
                try:
                    keeper_league = ESPNKeeperLeague(
                        league_id=league_id,
                        year=year,
                        espn_s2=espn_s2,
                        swid=swid,
                    )
                    # Use get_all_player_stats to get ALL active players for accurate position rankings
                    return keeper_league.get_all_player_stats(year)
                except Exception as e:
                    st.error(f"Error loading player stats: {e}")
                    return pd.DataFrame()

            # Use same year as draft for stats (current season stats)
            player_stats = load_player_stats_for_draft(
                config.league_id, config.year, config.espn_s2, config.swid
            )

            if not draft_data.empty:
                # Best/Worst draft picks analysis
                if not player_stats.empty:
                    st.subheader("Best & Worst Draft Picks")
                    dashboard.create_draft_value_analysis(draft_data, player_stats)

                # Keeper selection summary
                st.subheader("Keeper Selection Summary")
                dashboard.create_keeper_selection_summary(draft_data)

                # Keeper vs Drafted cost comparison
                st.subheader("Keeper vs Drafted Costs")
                dashboard.create_keeper_cost_vs_draft(draft_data)

                # Stars and Scrubs analysis
                st.subheader("Draft Strategy Analysis")
                dashboard.create_draft_cost_distribution(draft_data)

                # Additional metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_keepers = draft_data["keeper"].sum()
                    st.metric("Total Keepers", int(total_keepers))
                with col2:
                    avg_keeper_cost = draft_data[draft_data["keeper"]]["cost"].mean()
                    st.metric(
                        "Avg Keeper Cost",
                        f"${avg_keeper_cost:.1f}" if not pd.isna(avg_keeper_cost) else "N/A",
                    )
                with col3:
                    avg_draft_cost = draft_data[~draft_data["keeper"]]["cost"].mean()
                    st.metric(
                        "Avg Drafted Cost",
                        f"${avg_draft_cost:.1f}" if not pd.isna(avg_draft_cost) else "N/A",
                    )

            else:
                st.warning("No draft data available for analysis.")

        with tab7:
            st.subheader("🎤 Winning Percentage by Taylor Swift Era")

            st.info(
                "Each Taylor Swift album release marks a new era. "
                "This analysis shows how each owner performed during different Taylor Swift eras since 2006."
            )

            # Cache historical data loading
            @st.cache_data(ttl=3600)
            def load_historical_data(
                league_id: int,
                start_year: int,
                end_year: int,
                espn_s2: str | None,
                swid: str | None,
            ):
                """Load historical matchup data for era analysis."""
                from gmb.taylor_eras import get_historical_matchups_data

                return get_historical_matchups_data(league_id, start_year, end_year, espn_s2, swid)

            # Year range selection
            col1, col2 = st.columns(2)
            with col1:
                start_year = st.number_input(
                    "Start Year",
                    min_value=2006,
                    max_value=config.year,
                    value=2006,
                    step=1,
                    help="Taylor Swift's debut album was released in 2006",
                )
            with col2:
                end_year = st.number_input(
                    "End Year",
                    min_value=2006,
                    max_value=config.year,
                    value=config.year,
                    step=1,
                )

            if start_year > end_year:
                st.error("Start year must be before or equal to end year")
            else:
                with st.spinner(f"Loading {end_year - start_year + 1} years of historical data..."):
                    historical_data = load_historical_data(
                        config.league_id, start_year, end_year, config.espn_s2, config.swid
                    )

                if historical_data:
                    from gmb.taylor_eras import calculate_era_win_percentages

                    era_stats = calculate_era_win_percentages(historical_data)

                    # Display the data table
                    st.subheader("Era Statistics")

                    # Format for display
                    display_df = era_stats.copy()
                    display_df["win_pct"] = display_df["win_pct"].apply(lambda x: f"{x:.1%}")
                    display_df.columns = ["Owner", "Era", "Games", "Wins", "Losses", "Win %"]

                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                    # Visualizations
                    dashboard.create_taylor_eras_chart(era_stats)

                    # Fun facts
                    st.subheader("🎵 Era Insights")

                    # Most dominant owner-era combo
                    best_owner_era = era_stats.loc[era_stats["win_pct"].idxmax()]

                    st.metric(
                        "Most Dominant Performance",
                        f"{best_owner_era['owner']} in {best_owner_era['era']}",
                        f"{best_owner_era['win_pct']:.1%}",
                    )

                    st.markdown(
                        """
                        ---
                        **About the Eras**: Each era begins on the original album release date and ends when the next album is released.
                        This analysis uses the original album releases only and does not include Taylor's Version re-recordings as separate eras.
                        """
                    )
                else:
                    st.warning(
                        f"No historical data available for years {start_year}-{end_year}. "
                        "This could be due to API access issues or the league not existing in those years."
                    )

    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please run `gmb setup` to configure your league settings.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
