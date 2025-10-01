"""Visualization components for GMB fantasy football dashboard."""
import pandas as pd  # type: ignore[import-untyped]
import plotly.express as px  # type: ignore[import-untyped]
import streamlit as st

from .espn import ESPNFantasyLeague


class FantasyDashboard:
    """Dashboard for visualizing fantasy football league data."""

    def __init__(self, league: ESPNFantasyLeague):
        """Initialize dashboard with league instance."""
        self.league = league
        self.teams_df: pd.DataFrame | None = None
        self.matchups_df: pd.DataFrame | None = None

    def load_data(self) -> None:
        """Load team and matchup data from ESPN."""
        self.teams_df = self.league.get_teams()
        try:
            self.matchups_df = self.league.get_matchups()
        except Exception as e:
            print(f"Failed to load matchups: {e}")
            self.matchups_df = None

    def create_standings_chart(self) -> None:
        """Create standings visualization."""
        if self.teams_df is None:
            self.load_data()
        if self.teams_df is None:
            raise ValueError("Failed to load teams data")

        fig = px.bar(
            self.teams_df.sort_values("wins", ascending=False),
            x="team_name",
            y="wins",
            title="League Standings",
        )
        fig.update_layout(
            xaxis_title="Team",
            yaxis_title="Wins",
        )
        st.plotly_chart(fig)

    def create_weekly_scores_line(self) -> None:
        """Create weekly scoring trends visualization."""
        if self.matchups_df is None:
            self.load_data()
        if self.matchups_df is None:
            raise ValueError("Failed to load required data")

        # Extract team scores by week
        # The matchups_df has columns: week, team_name, points, opponent_name, opponent_points
        # Each row represents one team's perspective of a matchup
        scores_df = self.matchups_df[['week', 'team_name', 'points']].copy()
        scores_df.rename(columns={'points': 'score'}, inplace=True)

        fig = px.line(
            scores_df,
            x="week",
            y="score",
            color="team_name",
            title="Weekly Scoring Trends",
        )
        st.plotly_chart(fig)

    def create_points_scatter(self) -> None:
        """Create points for vs points against scatter plot."""
        if self.teams_df is None:
            self.load_data()
        if self.teams_df is None:
            raise ValueError("Failed to load teams data")

        fig = px.scatter(
            self.teams_df,
            x="points_for",
            y="points_against",
            text="team_name",
            title="Points For vs Points Against",
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig)

    def generate_power_rankings(self) -> pd.DataFrame:
        """Generate power rankings based on recent performance."""
        if self.teams_df is None:
            self.load_data()
        if self.teams_df is None:
            raise ValueError("Failed to load teams data")

        self.teams_df["power_score"] = (
            self.teams_df["wins"] * 0.6
            + (self.teams_df["points_for"] / self.teams_df["points_for"].max()) * 0.4
        )

        return self.teams_df.sort_values("power_score", ascending=False)[
            ["team_name", "wins", "points_for", "power_score"]
        ]

    def create_oiwp_chart(self, oiwp_stats: pd.DataFrame) -> None:
        """Create OIWP comparison bar chart.

        Args:
            oiwp_stats: DataFrame with OIWP statistics
        """
        fig = px.bar(
            oiwp_stats,
            x="team_name",
            y=["wp", "oiwp"],
            title="Win Percentage vs OIWP",
            labels={
                "value": "Percentage",
                "team_name": "Team",
                "variable": "Metric"
            },
            barmode="group",
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            legend_title_text="Metric",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        # Rename legend labels
        fig.for_each_trace(lambda t: t.update(name="Win %" if t.name == "wp" else "OIWP"))
        st.plotly_chart(fig, use_container_width=True)

    def create_luck_chart(self, oiwp_stats: pd.DataFrame) -> None:
        """Create luck visualization bar chart.

        Args:
            oiwp_stats: DataFrame with OIWP statistics
        """
        # Sort by luck value
        sorted_stats = oiwp_stats.sort_values("luck", ascending=False)

        fig = px.bar(
            sorted_stats,
            x="team_name",
            y="luck",
            title="Team Luck Factor (Win % - OIWP)",
            labels={
                "luck": "Luck Factor",
                "team_name": "Team"
            },
            color="luck",
            color_continuous_scale=["red", "white", "green"],
            color_continuous_midpoint=0,
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)