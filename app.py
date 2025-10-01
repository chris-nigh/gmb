"""GMB Fantasy Football Dashboard main script."""
import streamlit as st

from gmb.config import DashboardConfig
from gmb.espn import ESPNFantasyLeague
from gmb.oiwp import calculate_oiwp_stats
from gmb.viz import FantasyDashboard


def main():
    """Main entry point for the dashboard application."""
    st.set_page_config(page_title="GMB Fantasy Football", layout="wide")
    st.title("GMB Fantasy Football Dashboard")

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
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "🏆 Power Rankings", "🎯 OIWP Analysis"])

        with tab1:
            st.subheader("Current Standings")
            if dashboard.teams_df is not None:
                standings = dashboard.teams_df[
                    ["team_name", "wins", "losses", "points_for", "points_against"]
                ].sort_values("wins", ascending=False)
                st.dataframe(standings, use_container_width=True)

            st.subheader("League Standings Chart")
            dashboard.create_standings_chart()

        with tab2:
            if dashboard.matchups_df is not None:
                st.subheader("Weekly Scoring Trends")
                dashboard.create_weekly_scores_line()

                st.subheader("Points For vs Points Against")
                dashboard.create_points_scatter()
            else:
                st.warning("Matchup data not available")

        with tab3:
            st.subheader("Power Rankings")
            if dashboard.teams_df is not None:
                rankings = dashboard.generate_power_rankings()
                st.dataframe(rankings, use_container_width=True)

                st.info(
                    "Power rankings are calculated using a weighted formula: "
                    "60% wins + 40% normalized points scored"
                )

        with tab4:
            st.subheader("Opponent-Independent Winning Percentage (OIWP)")

            if dashboard.matchups_df is not None and not dashboard.matchups_df.empty:
                # Calculate OIWP stats
                oiwp_stats = calculate_oiwp_stats(dashboard.matchups_df)

                if not oiwp_stats.empty:
                    # Display OIWP table
                    display_df = oiwp_stats.copy()
                    display_df['wp'] = display_df['wp'].apply(lambda x: f"{x:.3f}")
                    display_df['oiwp'] = display_df['oiwp'].apply(lambda x: f"{x:.3f}")
                    display_df['luck'] = display_df['luck'].apply(lambda x: f"{x:+.3f}")
                    display_df.columns = ['Team Name', 'Win %', 'OIWP', 'Luck']
                    st.dataframe(display_df, use_container_width=True)

                    # Explanation
                    st.info(
                        "**OIWP (Opponent-Independent Winning Percentage)** measures how well each team "
                        "would perform if they played against *every* other team in the league each week.\n\n"
                        "- **Win %**: Actual winning percentage from head-to-head matchups\n"
                        "- **OIWP**: Winning percentage against all teams (not just your opponent)\n"
                        "- **Luck**: Difference between Win % and OIWP\n"
                        "  - **Positive luck** (green): You're winning more than your scores suggest (favorable matchups)\n"
                        "  - **Negative luck** (red): You're losing more than your scores suggest (tough matchups)"
                    )

                    # Visualizations
                    dashboard.create_oiwp_chart(oiwp_stats)
                    dashboard.create_luck_chart(oiwp_stats)
                else:
                    st.warning("Unable to calculate OIWP statistics")
            else:
                st.warning("Matchup data not available for OIWP calculation")

    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please run `gmb setup` to configure your league settings.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()