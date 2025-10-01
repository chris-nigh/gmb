"""GMB Fantasy Football Dashboard main script."""
import streamlit as st

from gmb.config import DashboardConfig
from gmb.espn import ESPNFantasyLeague
from gmb.oiwp import calculate_oiwp_stats
from gmb.viz import FantasyDashboard


def apply_vermont_styling():
    """Apply Vermont Green Mountains theme with custom CSS."""
    st.markdown("""
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
    """, unsafe_allow_html=True)


def main():
    """Main entry point for the dashboard application."""
    st.set_page_config(
        page_title="🏔️ Green Mountain Boys",
        layout="wide",
        page_icon="🏔️"
    )

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
                    # Display OIWP table with color formatting
                    display_df = oiwp_stats.copy()

                    # Format numeric columns first
                    display_df['wp'] = display_df['wp'].apply(lambda x: f"{x:.3f}")
                    display_df['oiwp'] = display_df['oiwp'].apply(lambda x: f"{x:.3f}")
                    display_df['luck'] = display_df['luck'].apply(lambda x: f"{x:+.3f}")
                    display_df['schedule_wins'] = display_df['schedule_wins'].apply(lambda x: f"{x:+d}")

                    # Rename columns
                    display_df.columns = ['Team Name', 'Record', 'Predicted Record', 'Win %', 'OIWP', 'Luck', 'Schedule Wins']

                    # Define color function for styled values
                    def color_numeric_value(val):
                        """Apply color based on positive/negative values."""
                        try:
                            # Extract numeric value from formatted string
                            num_str = str(val).replace('+', '')
                            num_val = float(num_str)

                            if num_val > 0:
                                return 'color: #28a745; font-weight: bold;'  # Standard green for positive
                            elif num_val < 0:
                                return 'color: #dc3545; font-weight: bold;'  # Standard red for negative
                            else:
                                return 'color: #6c757d;'  # Gray for neutral
                        except (ValueError, AttributeError):
                            return ''

                    # Apply styling to Luck and Schedule Wins columns
                    styled_df = display_df.style.map(
                        color_numeric_value,
                        subset=['Luck', 'Schedule Wins']
                    )

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

    except ValueError as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please run `gmb setup` to configure your league settings.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()