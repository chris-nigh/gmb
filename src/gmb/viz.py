"""Visualization components for GMB fantasy football dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

        fig = px.scatter(
            self.teams_df,
            x="wins",
            y="points_for",
            text="team_name",
            title="League Standings: Wins vs Total Points",
            labels={"wins": "Wins", "points_for": "Total Points Scored"},
            color_discrete_sequence=["#2D5F3F"],  # Vermont forest green
        )
        fig.update_traces(
            textposition="top center", marker=dict(size=12, line=dict(width=2, color="#1A3329"))
        )
        fig.update_layout(
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def create_weekly_scores_line(self) -> None:
        """Create weekly scoring trends visualization."""
        if self.matchups_df is None:
            self.load_data()
        if self.matchups_df is None:
            raise ValueError("Failed to load required data")

        # Extract team scores by week
        # The matchups_df has columns: week, team_name, points, opponent_name, opponent_points
        # Each row represents one team's perspective of a matchup
        scores_df = self.matchups_df[["week", "team_name", "points"]].copy()
        scores_df.rename(columns={"points": "score"}, inplace=True)

        fig = px.line(
            scores_df,
            x="week",
            y="score",
            color="team_name",
            title="Weekly Scoring Trends",
            color_discrete_sequence=[
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",  # Matplotlib default colors
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",  # More muted tones
                "#bcbd22",
                "#17becf",
                "#aec7e8",
                "#ffbb78",  # Pastel variants
                "#98df8a",
                "#ff9896",
                "#c5b0d5",
                "#c49c94",  # Additional pastels
            ],
        )
        fig.update_layout(
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
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
            color_discrete_sequence=["#4A7C59"],  # Mountain green
        )
        fig.update_traces(
            textposition="top center", marker=dict(size=12, line=dict(width=2, color="#2D5F3F"))
        )
        fig.update_layout(
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
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
            labels={"value": "Percentage", "team_name": "Team", "variable": "Metric"},
            barmode="group",
            color_discrete_sequence=["#4A7C59", "#2D5F3F"],  # Mountain and forest greens
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            legend_title_text="Metric",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
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
            labels={"luck": "Luck Factor", "team_name": "Team"},
            color="luck",
            color_continuous_scale=[
                "#dc3545",  # Standard red (negative luck)
                "#f8f9fa",  # Light gray (neutral)
                "#28a745",  # Standard green (positive luck)
            ],
            color_continuous_midpoint=0,
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        fig.add_hline(y=0, line_dash="dash", line_color="#6c757d", opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)

    def create_keeper_summary_table(
        self, keeper_data: pd.DataFrame, team_filter: str | None = None
    ) -> None:
        """Display keeper eligibility summary table.

        Args:
            keeper_data: DataFrame with keeper eligibility data
            team_filter: Optional team name to filter by
        """
        if keeper_data.empty:
            st.warning("No keeper data available")
            return

        display_df = keeper_data.copy()

        # Filter by team if specified
        if team_filter and team_filter != "All Teams":
            display_df = display_df[display_df["team_name"] == team_filter]

        # Calculate position rank based on total points scored (higher points = higher rank)
        # Only rank among players with scoring data
        if "total_points" in display_df.columns:
            # Debug: Show what we have
            # st.write("Debug - Position rank calculation:")
            # st.write(f"Total players: {len(display_df)}")
            # st.write(f"Players with points > 0: {(display_df['total_points'] > 0).sum()}")

            # Create a clean copy for ranking
            rank_df = display_df[
                display_df["total_points"].notna() & (display_df["total_points"] > 0)
            ].copy()

            if not rank_df.empty:
                # Rank by total points within each position (descending - higher points = rank 1)
                rank_df["pos_rank"] = rank_df.groupby("position")["total_points"].rank(
                    method="min", ascending=False
                )

                # Merge ranks back to display_df
                display_df = display_df.merge(
                    rank_df[["player_name", "pos_rank"]],
                    on="player_name",
                    how="left",
                    suffixes=("", "_new"),
                )
                # Use the new rank if it exists
                if "pos_rank_new" in display_df.columns:
                    display_df["pos_rank"] = display_df["pos_rank_new"]
                    display_df = display_df.drop("pos_rank_new", axis=1)
        else:
            # Fallback: rank by keeper cost if no scoring data available
            display_df["cost_numeric"] = pd.to_numeric(display_df["keeper_cost"], errors="coerce")
            display_df["pos_rank"] = display_df.groupby("position")["cost_numeric"].rank(
                method="min", ascending=True
            )

        # For ineligible players, clear the rank
        display_df.loc[~display_df["eligible"], "pos_rank"] = None

        # Create numeric cost for sorting (999 becomes large number for proper sorting)
        display_df["cost_numeric"] = pd.to_numeric(display_df["keeper_cost"], errors="coerce")
        display_df.loc[display_df["cost_numeric"] == 999, "cost_numeric"] = float(
            "inf"
        )  # Sort ineligible to end

        # Format cost display (999 = ineligible, show as "-")
        display_df["cost_display"] = display_df.apply(
            lambda x: "-" if x["keeper_cost"] == 999 else f"${int(x['keeper_cost'])}", axis=1
        )

        # Format rank display
        display_df["rank_display"] = display_df["pos_rank"].apply(
            lambda x: f"{int(x)}" if pd.notna(x) else "-"
        )

        # Select and rename columns for display
        cols_to_show = [
            "player_name",
            "team_name",
            "position",
            "rank_display",
            "eligible",
            "cost_numeric",
            "cost_display",
            "years_kept",
            "years_remaining",
        ]
        display_df = display_df[cols_to_show]

        display_df.columns = [
            "Player",
            "Team",
            "Position",
            "Pos Rank",
            "Eligible",
            "Cost_Numeric",
            "Cost",
            "Years Kept",
            "Years Left",
        ]

        # Hide the numeric column but keep it for sorting
        display_df = display_df[
            [
                "Player",
                "Team",
                "Position",
                "Pos Rank",
                "Eligible",
                "Cost",
                "Years Kept",
                "Years Left",
            ]
        ]

        # Format the display
        def highlight_eligible(row: pd.Series) -> list[str]:
            if row["Eligible"]:
                return ["background-color: #D4E7DD"] * len(row)
            else:
                return ["background-color: #F5E6E6"] * len(row)

        styled_df = display_df.style.apply(highlight_eligible, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)

    def create_keeper_cost_chart(self, keeper_data: pd.DataFrame) -> None:
        """Create visualization of keeper costs by team.

        Args:
            keeper_data: DataFrame with keeper eligibility data
        """
        if keeper_data.empty:
            return

        # Filter to eligible keepers only
        eligible = keeper_data[keeper_data["eligible"]].copy()

        if eligible.empty:
            st.info("No eligible keepers found")
            return

        # Convert cost to numeric, replacing 'N/A' with 0
        eligible["cost_numeric"] = pd.to_numeric(eligible["keeper_cost"], errors="coerce").fillna(0)

        # Group by team and sum costs
        team_costs = (
            eligible.groupby("team_name")
            .agg({"cost_numeric": "sum", "player_name": "count"})
            .reset_index()
        )
        team_costs.columns = ["Team", "Total Cost", "Eligible Players"]

        # Sort by total cost
        team_costs = team_costs.sort_values("Total Cost", ascending=False)

        fig = px.bar(
            team_costs,
            x="Team",
            y="Total Cost",
            title="Total Keeper Cost by Team",
            color="Eligible Players",
            color_continuous_scale=[[0, "#98df8a"], [1, "#2D5F3F"]],  # Light to dark green
            hover_data=["Eligible Players"],
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def create_draft_cost_distribution(self, draft_data: pd.DataFrame) -> None:
        """Create distribution of draft costs by team (stars and scrubs analysis).

        Args:
            draft_data: DataFrame with draft pick information including cost
        """
        if draft_data.empty:
            st.warning("No draft data available")
            return

        # Create box plot showing cost distribution per team
        fig = px.box(
            draft_data,
            x="team_name",
            y="cost",
            title="Draft Cost Distribution by Team (Stars & Scrubs Analysis)",
            labels={"cost": "Player Cost ($)", "team_name": "Team"},
            color_discrete_sequence=["#2D5F3F"],
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add interpretation
        st.info(
            "**Stars & Scrubs Strategy**: Wide distribution (tall box, long whiskers) indicates "
            "a mix of expensive stars and cheap players. "
            "**Balanced Strategy**: Narrow distribution indicates more evenly priced roster."
        )

    def create_keeper_cost_vs_draft(self, draft_data: pd.DataFrame) -> None:
        """Compare keeper costs vs drafted player costs.

        Args:
            draft_data: DataFrame with draft picks and keeper information
        """
        if draft_data.empty:
            st.warning("No draft data available")
            return

        # Separate keepers from drafted players
        draft_data_copy = draft_data.copy()
        draft_data_copy["player_type"] = draft_data_copy["keeper"].apply(
            lambda x: "Keeper" if x else "Drafted"
        )

        # Calculate summary stats
        summary = (
            draft_data_copy.groupby(["team_name", "player_type"])["cost"]
            .agg(["mean", "sum", "count"])
            .reset_index()
        )

        # Create grouped bar chart showing keeper vs drafted costs
        fig = go.Figure()

        for player_type in ["Keeper", "Drafted"]:
            type_data = summary[summary["player_type"] == player_type]
            if not type_data.empty:
                fig.add_trace(
                    go.Bar(
                        name=player_type,
                        x=type_data["team_name"],
                        y=type_data["sum"],
                        text=type_data["count"].apply(lambda x: f"{int(x)} players"),
                        textposition="auto",
                        marker_color="#4A7C59" if player_type == "Keeper" else "#8B4513",
                    )
                )

        fig.update_layout(
            title="Total Draft Cost: Keepers vs Drafted Players",
            xaxis_title="Team",
            yaxis_title="Total Cost ($)",
            barmode="group",
            xaxis_tickangle=-45,
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def create_keeper_selection_summary(self, draft_data: pd.DataFrame) -> None:
        """Show which teams kept players and summary statistics.

        Args:
            draft_data: DataFrame with draft picks and keeper information
        """
        if draft_data.empty:
            st.warning("No draft data available")
            return

        # Calculate keeper stats per team
        keepers_only = draft_data[draft_data["keeper"]]
        if keepers_only.empty:
            st.info("No keepers selected in this draft")
            return

        keeper_summary = (
            keepers_only.groupby("team_name")
            .agg({"player_name": "count", "cost": ["sum", "mean", "max"]})
            .reset_index()
        )

        # Flatten column names
        keeper_summary.columns = ["Team", "Keepers", "Total Cost", "Avg Cost", "Max Cost"]

        # Add teams with no keepers
        all_teams = pd.DataFrame({"Team": draft_data["team_name"].unique()})
        keeper_summary = all_teams.merge(keeper_summary, on="Team", how="left").fillna(0)

        # Format for display
        keeper_summary["Total Cost"] = keeper_summary["Total Cost"].apply(
            lambda x: f"${int(x)}" if x > 0 else "-"
        )
        keeper_summary["Avg Cost"] = keeper_summary["Avg Cost"].apply(
            lambda x: f"${int(x)}" if x > 0 else "-"
        )
        keeper_summary["Max Cost"] = keeper_summary["Max Cost"].apply(
            lambda x: f"${int(x)}" if x > 0 else "-"
        )
        keeper_summary["Keepers"] = keeper_summary["Keepers"].astype(int)

        # Sort by number of keepers
        keeper_summary = keeper_summary.sort_values("Keepers", ascending=False)

        st.dataframe(keeper_summary, use_container_width=True, hide_index=True)

    def create_keeper_value_chart(self, keeper_data: pd.DataFrame) -> None:
        """Create scatter plot of keeper values (cost vs years remaining).

        Args:
            keeper_data: DataFrame with keeper eligibility data
        """
        if keeper_data.empty:
            return

        # Filter to eligible keepers only
        eligible = keeper_data[keeper_data["eligible"]].copy()

        if eligible.empty:
            return

        # Convert cost to numeric
        eligible["cost_numeric"] = pd.to_numeric(eligible["keeper_cost"], errors="coerce").fillna(0)

        fig = px.scatter(
            eligible,
            x="cost_numeric",
            y="years_remaining",
            color="team_name",
            size="cost_numeric",
            hover_data=["player_name", "position"],
            title="Keeper Value Analysis",
            labels={"cost_numeric": "Keeper Cost ($)", "years_remaining": "Years Remaining"},
            color_discrete_sequence=[
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",  # Matplotlib default colors
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",  # More muted tones
                "#bcbd22",
                "#17becf",
                "#aec7e8",
                "#ffbb78",  # Pastel variants
                "#98df8a",
                "#ff9896",
                "#c5b0d5",
                "#c49c94",  # Additional pastels
            ],
        )
        fig.update_layout(
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def create_schedule_strength_chart(self) -> None:
        """Create schedule strength visualization based on opponent quality."""
        if self.matchups_df is None or self.teams_df is None:
            st.warning("Insufficient data for schedule strength analysis")
            return

        # Get opponent scores for each team (one row per matchup)
        schedule_data = self.matchups_df[["team_name", "opponent_points"]].copy()

        # Calculate average opponent score per team
        team_avg_opponents = (
            schedule_data.groupby("team_name")["opponent_points"].mean().reset_index()
        )
        team_avg_opponents.columns = ["team_name", "avg_opponent"]

        fig = px.box(
            schedule_data,
            x="team_name",
            y="opponent_points",
            title="Schedule Strength (Opponent Score Distribution)",
            labels={"opponent_points": "Opponent Score", "team_name": "Team"},
            color_discrete_sequence=["#DC143C"],  # Crimson color
        )

        # Add scatter points for team averages on top of box plot
        for _, row in team_avg_opponents.iterrows():
            fig.add_scatter(
                x=[row["team_name"]],
                y=[row["avg_opponent"]],
                mode="markers",
                marker=dict(size=10, color="#2D5F3F", symbol="diamond"),
                name="Team Avg",
                showlegend=False,
                hovertemplate=f"Avg: {row['avg_opponent']:.1f}<extra></extra>",
            )

        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def create_consistency_chart(self) -> None:
        """Create boom/bust consistency analysis showing scoring variance."""
        if self.matchups_df is None:
            st.warning("Matchup data required for consistency analysis")
            return

        # Calculate standard deviation and mean for each team
        consistency = (
            self.matchups_df.groupby("team_name")["points"].agg(["mean", "std"]).reset_index()
        )
        consistency.columns = ["team_name", "avg_score", "std_dev"]

        # Calculate coefficient of variation (lower = more consistent)
        consistency["cv"] = consistency["std_dev"] / consistency["avg_score"]

        fig = px.scatter(
            consistency,
            x="avg_score",
            y="std_dev",
            text="team_name",
            title="Scoring Consistency (Boom/Bust Analysis)",
            labels={
                "avg_score": "Average Score",
                "std_dev": "Standard Deviation (Higher = More Volatile)",
            },
            color="cv",
            color_continuous_scale="RdYlGn_r",  # Red = volatile, Green = consistent
            size="std_dev",
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )

        # Add quadrant lines
        avg_mean = consistency["avg_score"].mean()
        avg_std = consistency["std_dev"].mean()
        fig.add_hline(y=avg_std, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=avg_mean, line_dash="dash", line_color="gray", opacity=0.5)

        st.plotly_chart(fig, use_container_width=True)

        # Add interpretation guide
        st.info(
            "**Top-Right**: High scoring but inconsistent (boom/bust)  \n"
            "**Top-Left**: Low scoring and inconsistent (struggling)  \n"
            "**Bottom-Right**: High scoring and consistent (elite)  \n"
            "**Bottom-Left**: Low scoring but consistent (predictable but weak)"
        )

    def create_draft_value_analysis(
        self, draft_data: pd.DataFrame, player_stats: pd.DataFrame
    ) -> None:
        """Analyze best and worst draft picks based on cost vs performance.

        Args:
            draft_data: DataFrame with draft picks
            player_stats: DataFrame with player statistics including position ranks
        """
        if draft_data.empty:
            st.warning("No draft data available for value analysis")
            return

        if player_stats.empty:
            st.warning("No player statistics available for value analysis")
            return

        # Debug info
        # st.write(f"Draft data shape: {draft_data.shape}")
        # st.write(f"Player stats shape: {player_stats.shape}")
        # st.write(f"Draft columns: {draft_data.columns.tolist()}")
        # st.write(f"Stats columns: {player_stats.columns.tolist()}")

        from .position_map import get_position_name

        # First, calculate position ranks from ALL rostered players (not just drafted)
        stats_with_position = player_stats.copy()
        stats_with_position["position"] = stats_with_position["position_id"].apply(
            get_position_name
        )

        # Calculate league-wide position rank
        stats_with_rank = stats_with_position[stats_with_position["total_points"] > 0].copy()
        stats_with_rank["pos_rank"] = stats_with_rank.groupby("position")["total_points"].rank(
            method="min", ascending=False
        )

        # Now merge draft data with player stats AND position rank
        analysis = draft_data.merge(
            stats_with_rank[["player_name", "total_points", "position_id", "position", "pos_rank"]],
            on="player_name",
            how="left",
        )

        # st.write(f"After merge shape: {analysis.shape}")
        # st.write(f"Players with points: {analysis['total_points'].notna().sum()}")

        # Filter to players with stats and exclude D/ST
        analysis = analysis[
            (analysis["total_points"].notna())
            & (analysis["total_points"] > 0)
            & (analysis["position"] != "D/ST")
        ].copy()

        if analysis.empty:
            st.info(
                "No scoring data available for draft value analysis. Players may not have played yet."
            )
            return

        # Calculate value score (lower rank number and lower cost = better value)
        # Normalize cost and rank to 0-1 scale
        analysis["cost_normalized"] = (analysis["cost"] - analysis["cost"].min()) / (
            analysis["cost"].max() - analysis["cost"].min() + 1
        )
        analysis["rank_normalized"] = (analysis["pos_rank"] - 1) / (analysis["pos_rank"].max())

        # Value score: low rank (good) - high cost (bad)
        # Positive = good value (low rank, low cost), Negative = poor value (high rank, high cost)
        analysis["value_score"] = (1 - analysis["rank_normalized"]) - analysis["cost_normalized"]

        # Find best and worst picks
        best_picks = analysis.nlargest(5, "value_score")[
            [
                "player_name",
                "team_name",
                "position",
                "cost",
                "total_points",
                "pos_rank",
                "value_score",
            ]
        ].copy()

        worst_picks = analysis.nsmallest(5, "value_score")[
            [
                "player_name",
                "team_name",
                "position",
                "cost",
                "total_points",
                "pos_rank",
                "value_score",
            ]
        ].copy()

        # Format for display
        for df in [best_picks, worst_picks]:
            df["cost"] = df["cost"].apply(lambda x: f"${int(x)}")
            df["total_points"] = df["total_points"].apply(lambda x: f"{x:.1f}")
            df["pos_rank"] = df["pos_rank"].apply(lambda x: f"{int(x)}")
            df["value_score"] = df["value_score"].apply(lambda x: f"{x:+.3f}")

        best_picks.columns = ["Player", "Team", "Pos", "Cost", "Points", "Rank", "Value Score"]
        worst_picks.columns = ["Player", "Team", "Pos", "Cost", "Points", "Rank", "Value Score"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🏆 Best Draft Picks**")
            st.markdown("*High performance relative to draft cost*")
            st.dataframe(best_picks, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**💸 Worst Draft Picks**")
            st.markdown("*Poor performance relative to draft cost*")
            st.dataframe(worst_picks, use_container_width=True, hide_index=True)

        st.info(
            "**Value Score**: Measures draft pick value based on position rank and cost. "
            "Positive scores indicate good value (high performance, low cost). "
            "Negative scores indicate poor value (low performance, high cost)."
        )

    def create_taylor_eras_chart(self, era_stats: pd.DataFrame) -> None:
        """Create interactive Taylor Swift Eras winning percentage visualization with hierarchical clustering.

        Args:
            era_stats: DataFrame with columns: owner, era, games, wins, losses, win_pct
        """
        if era_stats.empty:
            st.warning("No era statistics available")
            return

        import dash_bio

        # Get chronological era order from taylor_eras module
        from .taylor_eras import TAYLOR_ERAS

        era_order = [era["era"] for era in TAYLOR_ERAS]
        era_dates = {era["era"]: era["start_date"].strftime("%b %Y") for era in TAYLOR_ERAS}

        # Create a pivot table for the heatmap
        pivot_data = era_stats.pivot(index="owner", columns="era", values="win_pct")

        # Sort columns chronologically
        available_eras = [era for era in era_order if era in pivot_data.columns]
        pivot_data = pivot_data[available_eras]

        # Create column labels with era name and date
        col_labels = [f"{era}<br>({era_dates[era]})" for era in pivot_data.columns]

        # Fill NaN values with a special marker for clustering
        # Use -0.5 so we can identify them (must be between -1 and 1 for normalization)
        pivot_data_filled = pivot_data.fillna(-0.0001)  # Slightly below 0 to distinguish from 0%

        # Create clustergram with proper formatting
        fig = dash_bio.Clustergram(
            data=pivot_data_filled.values,
            row_labels=list(pivot_data_filled.index),
            column_labels=col_labels,
            cluster="row",  # Only cluster rows (owners)
            standardize="none",  # Don't apply z-score normalization
            center_values=False,
            color_map=[
                [0, "#dc3545"],  # Red for low win%
                [0.5, "#ffc107"],  # Yellow for 50%
                [1, "#28a745"],  # Green for high win%
            ],
            height=max(600, len(pivot_data.index) * 50),
            width=max(900, len(pivot_data.columns) * 90),
            display_ratio=0.15,  # dendrogram ratio
            color_threshold={"row": 0},
            line_width=2,
        )

        # Add percentage text annotations to the heatmap
        for trace in fig.data:
            if isinstance(trace, go.Heatmap):
                # The trace.z already contains the clustered data
                # We just need to convert the values to percentage strings
                # The issue is that trace.z may have standardized values, so we need
                # to use the original data in the correct clustered order

                # Since center_values=False and standardize="none", trace.z should contain
                # the original percentage values (with 0.5 for NaN)
                # We need to convert back: if value is 0.5 and was originally NaN, show "-"

                text_annotations = []
                for row_vals in trace.z:
                    row_text = []
                    for val in row_vals:
                        # Check if this is a NaN marker (-1)
                        if val < 0:
                            row_text.append("-")
                        else:
                            row_text.append(f"{val:.1%}")
                    text_annotations.append(row_text)

                # Create a custom colorscale that includes gray for NaN
                # Map: -0.5 (NaN) → gray, 0 (0%) → red, 0.5 (50%) → yellow, 1.0 (100%) → green
                custom_colorscale = [
                    [0, "#e0e0e0"],  # Gray for -0.5 (NaN) - normalized to 0
                    [0.0001, "#e0e0e0"],  # Keep gray until just before 0%
                    [0.0002, "#dc3545"],  # Red for 0% win
                    [0.1, "#dc3545"],  # Red for 10% win
                    [0.5, "#ffc107"],  # Yellow for 50% win
                    [0.9, "#28a745"],  # Green for 90% win
                    [1, "#28a745"],  # Green for 100% win
                ]

                # Update the trace with text annotations and custom colorscale
                # Use zmin=-0.5 to include NaN values, but colorbar only shows 0-100%
                trace.update(
                    text=text_annotations,
                    texttemplate="%{text}",
                    textfont={"size": 10, "color": "white"},
                    colorscale=custom_colorscale,
                    zmin=-0.0001,  # Include NaN marker in color scale
                    zmax=1.0,
                    colorbar=dict(
                        title="Win %",
                        tickformat=".1%",
                        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
                        ticktext=["0.0%", "25.0%", "50.0%", "75.0%", "100.0%"],
                        tick0=0,
                        dtick=0.25,
                    ),
                )

        # Update layout
        fig.update_layout(
            title={
                "text": "Winning Percentage by Taylor Swift Era (Hierarchically Clustered)",
                "x": 0.5,
                "xanchor": "center",
            },
            xaxis={"tickangle": -45},
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )

        st.plotly_chart(fig, use_container_width=True)

    def compute_h2h_matrix(self, historical_matchups: pd.DataFrame | None = None) -> pd.DataFrame:
        """Compute head-to-head win record matrix for all teams.

        Args:
            historical_matchups: Optional DataFrame with historical matchup data.
                If None, uses current season data from self.matchups_df.
                Expected columns: team_name, opponent_name, points, opponent_points

        Returns:
            Matrix where rows/cols are team names and values are win percentages
            (wins / total_games) for each head-to-head matchup
        """
        if historical_matchups is not None:
            matchups = historical_matchups.copy()
        else:
            if self.matchups_df is None:
                self.load_data()
            if self.matchups_df is None:
                raise ValueError("Failed to load matchup data")
            matchups = self.matchups_df.copy()

        # Get unique team names
        teams = sorted(list(matchups["team_name"].unique()))

        # Build win and count matrices using dictionaries
        wins: dict[tuple[str, str], float] = {(t1, t2): 0.0 for t1 in teams for t2 in teams}
        counts: dict[tuple[str, str], int] = {(t1, t2): 0 for t1 in teams for t2 in teams}

        # For each matchup, record the result
        for _, row in matchups.iterrows():
            team = str(row["team_name"])
            opponent = str(row["opponent_name"])
            team_score = float(row["points"])
            opponent_score = float(row["opponent_points"])

            # Only count if both teams exist
            if team in teams and opponent in teams:
                # Team wins if score is higher
                if team_score > opponent_score:
                    wins[(team, opponent)] += 1
                counts[(team, opponent)] += 1

        # Create result matrix with win percentages
        h2h_matrix = pd.DataFrame(None, index=teams, columns=teams)

        for team in teams:
            for opponent in teams:
                if team == opponent:
                    h2h_matrix.loc[team, opponent] = None  # No self-matchups
                elif counts[(team, opponent)] > 0:
                    h2h_matrix.loc[team, opponent] = (
                        wins[(team, opponent)] / counts[(team, opponent)]
                    )
                else:
                    h2h_matrix.loc[team, opponent] = None

        return h2h_matrix

    def compute_h2h_history(
        self, historical_matchups: pd.DataFrame | None = None
    ) -> dict[str, pd.DataFrame]:
        """Compute head-to-head records over time, grouped by league year.

        Args:
            historical_matchups: Optional DataFrame with historical matchup data.
                If None, uses current season data from self.matchups_df.
                Expected columns: team_name, opponent_name, points, opponent_points

        Returns:
            Dictionary mapping team names to DataFrames with columns:
            - opponent: opponent team name
            - wins: wins vs that opponent
            - losses: losses vs that opponent
            - win_pct: winning percentage vs that opponent
        """
        if historical_matchups is not None:
            matchups = historical_matchups.copy()
        else:
            if self.matchups_df is None:
                self.load_data()
            if self.matchups_df is None:
                raise ValueError("Failed to load matchup data")
            matchups = self.matchups_df.copy()

        # Group by team and compute h2h records
        h2h_history = {}
        teams = sorted(matchups["team_name"].unique())

        for team in teams:
            team_matchups = matchups[matchups["team_name"] == team].copy()
            h2h_records = []

            for opponent in teams:
                if team == opponent:
                    continue

                opponent_matchups = team_matchups[team_matchups["opponent_name"] == opponent]

                if opponent_matchups.empty:
                    continue

                wins = (opponent_matchups["points"] > opponent_matchups["opponent_points"]).sum()
                losses = (opponent_matchups["points"] < opponent_matchups["opponent_points"]).sum()
                total = wins + losses

                if total > 0:
                    win_pct = wins / total
                    h2h_records.append(
                        {
                            "opponent": opponent,
                            "wins": wins,
                            "losses": losses,
                            "win_pct": win_pct,
                        }
                    )

            if h2h_records:
                h2h_history[team] = pd.DataFrame(h2h_records)

        return h2h_history

    def create_h2h_heatmap(self, historical_matchups: pd.DataFrame | None = None) -> None:
        """Create heatmap visualization of head-to-head records.

        Args:
            historical_matchups: Optional historical matchup data. If None, uses current season.
        """
        h2h_matrix = self.compute_h2h_matrix(historical_matchups)

        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=h2h_matrix.values,
                x=h2h_matrix.columns,
                y=h2h_matrix.index,
                colorscale=[
                    [0, "#dc3545"],  # Red for 0% win
                    [0.5, "#ffc107"],  # Yellow for 50% win
                    [1, "#28a745"],  # Green for 100% win
                ],
                zmin=0,
                zmax=1,
                text=h2h_matrix.values,
                texttemplate="%{text:.1%}",
                textfont={"size": 11, "color": "white"},
                colorbar=dict(
                    title="Win %",
                    tickformat=".0%",
                ),
                hovertemplate="<b>%{y} vs %{x}</b><br>Win %: %{text:.1%}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Head-to-Head Win Percentage Matrix",
            xaxis_title="Opponent",
            yaxis_title="Team",
            height=600,
            width=800,
            xaxis={"tickangle": -45},
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_h2h_line_chart(
        self, selected_team: str, historical_matchups: pd.DataFrame | None = None
    ) -> None:
        """Create line chart of winning percentage vs all opponents for a selected team.

        Args:
            selected_team: Team name to analyze
            historical_matchups: Optional historical matchup data. If None, uses current season.
        """
        h2h_history = self.compute_h2h_history(historical_matchups)

        if selected_team not in h2h_history or h2h_history[selected_team].empty:
            st.warning(f"No head-to-head data available for {selected_team}")
            return

        # Get h2h data for selected team
        team_h2h = h2h_history[selected_team].copy()

        # Sort by opponent name for consistency
        team_h2h = team_h2h.sort_values("opponent")

        # Create line chart
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=team_h2h["opponent"],
                y=team_h2h["win_pct"],
                mode="lines+markers",
                name="Win %",
                line=dict(color="#2D5F3F", width=3),
                marker=dict(size=8, color="#4A7C59", line=dict(width=2, color="#2D5F3F")),
                fill="tozeroy",
                fillcolor="rgba(45, 95, 63, 0.2)",
                hovertemplate="<b>%{x}</b><br>Win %: %{y:.1%}<extra></extra>",
            )
        )

        # Add 50% reference line
        fig.add_hline(
            y=0.5,
            line_dash="dash",
            line_color="#6c757d",
            opacity=0.5,
            annotation_text="50% (Break-even)",
            annotation_position="right",
        )

        fig.update_layout(
            title=f"Head-to-Head Winning Percentage: {selected_team}",
            xaxis_title="Opponent",
            yaxis_title="Win Percentage",
            height=500,
            xaxis={"tickangle": -45},
            yaxis=dict(tickformat=".0%", range=[0, 1]),
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)

    def compute_h2h_matrix_by_owner(
        self, historical_matchups: pd.DataFrame | None = None
    ) -> pd.DataFrame:
        """Compute head-to-head win record matrix organized by owner.

        Args:
            historical_matchups: Optional DataFrame with historical matchup data.
                Expected columns: owner, opponent_owner, points, opponent_points

        Returns:
            Matrix where rows/cols are owner names and values are win percentages
        """
        if historical_matchups is not None:
            matchups = historical_matchups.copy()
        else:
            if self.matchups_df is None:
                self.load_data()
            if self.matchups_df is None:
                raise ValueError("Failed to load matchup data")
            matchups = self.matchups_df.copy()

        # Get unique owner names
        owners = sorted(list(matchups["owner"].unique()))

        # Build win and count matrices using dictionaries
        wins: dict[tuple[str, str], float] = {(o1, o2): 0.0 for o1 in owners for o2 in owners}
        counts: dict[tuple[str, str], int] = {(o1, o2): 0 for o1 in owners for o2 in owners}

        # For each matchup, record the result
        for _, row in matchups.iterrows():
            owner = str(row["owner"])
            opponent_owner = str(row["opponent_owner"])
            owner_score = float(row["points"])
            opponent_score = float(row["opponent_points"])

            # Only count if both owners exist
            if owner in owners and opponent_owner in owners:
                # Owner wins if score is higher
                if owner_score > opponent_score:
                    wins[(owner, opponent_owner)] += 1
                counts[(owner, opponent_owner)] += 1

        # Create result matrix with win percentages
        h2h_matrix = pd.DataFrame(None, index=owners, columns=owners)

        for owner in owners:
            for opponent_owner in owners:
                if owner == opponent_owner:
                    h2h_matrix.loc[owner, opponent_owner] = None  # No self-matchups
                elif counts[(owner, opponent_owner)] > 0:
                    h2h_matrix.loc[owner, opponent_owner] = (
                        wins[(owner, opponent_owner)] / counts[(owner, opponent_owner)]
                    )
                else:
                    h2h_matrix.loc[owner, opponent_owner] = None

        return h2h_matrix

    def create_h2h_heatmap_by_owner(self, historical_matchups: pd.DataFrame | None = None) -> None:
        """Create heatmap visualization of head-to-head records organized by owner.

        Args:
            historical_matchups: Optional historical matchup data. If None, uses current season.
        """
        if historical_matchups is not None:
            matchups = historical_matchups.copy()
        else:
            if self.matchups_df is None:
                self.load_data()
            if self.matchups_df is None:
                raise ValueError("Failed to load matchup data")
            matchups = self.matchups_df.copy()

        h2h_matrix = self.compute_h2h_matrix_by_owner(historical_matchups)

        # Build record matrix (wins-losses) for hover text
        owners = sorted(list(matchups["owner"].unique()))
        wins_dict: dict[tuple[str, str], int] = {(o1, o2): 0 for o1 in owners for o2 in owners}
        losses_dict: dict[tuple[str, str], int] = {(o1, o2): 0 for o1 in owners for o2 in owners}

        for _, row in matchups.iterrows():
            owner = str(row["owner"])
            opponent_owner = str(row["opponent_owner"])
            owner_score = float(row["points"])
            opponent_score = float(row["opponent_points"])

            if owner in owners and opponent_owner in owners:
                if owner_score > opponent_score:
                    wins_dict[(owner, opponent_owner)] += 1
                else:
                    losses_dict[(owner, opponent_owner)] += 1

        record_matrix = pd.DataFrame(None, index=owners, columns=owners)
        for owner in owners:
            for opponent_owner in owners:
                if owner == opponent_owner:
                    record_matrix.loc[owner, opponent_owner] = ""
                else:
                    w = wins_dict[(owner, opponent_owner)]
                    losses = losses_dict[(owner, opponent_owner)]
                    record_matrix.loc[owner, opponent_owner] = f"{w}-{losses}"

        # Create heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=h2h_matrix.values,
                x=h2h_matrix.columns,
                y=h2h_matrix.index,
                colorscale=[
                    [0, "#dc3545"],  # Red for 0% win
                    [0.5, "#ffc107"],  # Yellow for 50% win
                    [1, "#28a745"],  # Green for 100% win
                ],
                zmin=0,
                zmax=1,
                text=h2h_matrix.values,
                texttemplate="%{text:.1%}",
                textfont={"size": 11, "color": "white"},
                customdata=record_matrix.values,
                colorbar=dict(
                    title="Win %",
                    tickformat=".0%",
                ),
                hovertemplate="<b>%{y} vs %{x}</b><br>Win %: %{text:.1%}<br>Record: %{customdata}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Head-to-Head Win Percentage Matrix (by Owner)",
            xaxis_title="Opponent",
            yaxis_title="Owner",
            height=600,
            width=800,
            xaxis={"tickangle": -45},
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_h2h_season_line_chart(
        self, selected_owner: str, historical_matchups: pd.DataFrame | None = None
    ) -> None:
        """Create line chart showing owner's winning percentage vs each opponent by season.

        Args:
            selected_owner: Owner name to analyze
            historical_matchups: Optional historical matchup data. Expected to have 'year' column.
        """
        if historical_matchups is not None:
            matchups = historical_matchups.copy()
        else:
            if self.matchups_df is None:
                self.load_data()
            if self.matchups_df is None:
                raise ValueError("Failed to load matchup data")
            matchups = self.matchups_df.copy()

        # Filter to selected owner's matchups
        owner_matchups = matchups[matchups["owner"] == selected_owner].copy()

        if owner_matchups.empty:
            st.warning(f"No head-to-head data available for {selected_owner}")
            return

        # Get unique opponents
        opponents = sorted(owner_matchups["opponent_owner"].unique())

        # Calculate cumulative win percentage over time for each opponent
        fig = go.Figure()

        for opponent in opponents:
            opponent_matchups = owner_matchups[owner_matchups["opponent_owner"] == opponent].copy()

            # Sort by year and week to get chronological order
            if "year" in opponent_matchups.columns:
                opponent_matchups = opponent_matchups.sort_values(["year", "week"]).reset_index(
                    drop=True
                )

                # Calculate wins/losses per game
                opponent_matchups["win"] = (
                    opponent_matchups["points"] > opponent_matchups["opponent_points"]
                ).astype(int)
                opponent_matchups["loss"] = (
                    opponent_matchups["points"] < opponent_matchups["opponent_points"]
                ).astype(int)

                # Calculate cumulative wins and losses
                opponent_matchups["cum_wins"] = opponent_matchups["win"].cumsum()
                opponent_matchups["cum_losses"] = opponent_matchups["loss"].cumsum()
                opponent_matchups["cum_total"] = (
                    opponent_matchups["cum_wins"] + opponent_matchups["cum_losses"]
                )
                opponent_matchups["cum_win_pct"] = (
                    opponent_matchups["cum_wins"] / opponent_matchups["cum_total"]
                )

                if len(opponent_matchups) > 0:
                    # Create a year-week label for each point
                    opponent_matchups["label"] = (
                        opponent_matchups["year"].astype(str)
                        + "-W"
                        + opponent_matchups["week"].astype(str)
                    )
                    # Create record string (wins-losses)
                    opponent_matchups["record"] = (
                        opponent_matchups["cum_wins"].astype(str)
                        + "-"
                        + opponent_matchups["cum_losses"].astype(str)
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=opponent_matchups["year"],
                            y=opponent_matchups["cum_win_pct"],
                            mode="lines+markers",
                            name=opponent,
                            line=dict(width=2),
                            marker=dict(size=6),
                            hovertemplate="<b>"
                            + opponent
                            + "</b><br>Season: %{x}<br>Record: %{customdata[0]}<br>Cumulative Win %: %{y:.1%}<extra></extra>",
                            customdata=opponent_matchups[["record"]],
                        )
                    )

        # Add 50% reference line
        if not owner_matchups.empty and "year" in owner_matchups.columns:
            fig.add_hline(
                y=0.5,
                line_dash="dash",
                line_color="#6c757d",
                opacity=0.5,
                annotation_text="50% (Break-even)",
                annotation_position="right",
            )

        fig.update_layout(
            title=f"Cumulative Head-to-Head Record: {selected_owner}",
            xaxis_title="Season (Year)",
            yaxis_title="Cumulative Win Percentage",
            height=500,
            yaxis=dict(tickformat=".0%", range=[0, 1]),
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            font=dict(color="#1A3329"),
            hovermode="closest",
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
            ),
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_win_pct_by_points_chart(
        self, historical_matchups: pd.DataFrame | None = None
    ) -> None:
        """Create chart showing winning percentage by points scored, with one line per year.

        Args:
            historical_matchups: DataFrame with historical matchup data including year, points, and opponent_points
        """
        if historical_matchups is None or historical_matchups.empty:
            st.warning("No historical matchup data available for this analysis.")
            return

        # Add win indicator
        historical_matchups = historical_matchups.copy()
        historical_matchups["won"] = (
            historical_matchups["points"] > historical_matchups["opponent_points"]
        ).astype(int)

        # Get all unique years
        years = sorted(historical_matchups["year"].unique())

        # Create figure
        fig = go.Figure()

        # Color palette - use Vermont theme colors cycling through years
        colors = [
            "#2D5F3F",  # Forest green
            "#4A7C59",  # Sage green
            "#8B4513",  # Saddle brown
            "#CD853F",  # Peru
            "#6B8E23",  # Olive drab
            "#556B2F",  # Dark olive green
            "#8FBC8F",  # Dark sea green
            "#A0522D",  # Sienna
        ]

        # Process each year
        for idx, year in enumerate(years):
            year_data = historical_matchups[historical_matchups["year"] == year].copy()

            # Create point bins (round to nearest 5)
            year_data["point_bin"] = (year_data["points"] // 5) * 5

            # Calculate win percentage for each point bin
            win_pct_by_points = (
                year_data.groupby("point_bin")
                .agg(
                    games=("won", "count"),
                    wins=("won", "sum"),
                )
                .reset_index()
            )
            win_pct_by_points["win_pct"] = (
                win_pct_by_points["wins"] / win_pct_by_points["games"]
            ) * 100

            # Filter to bins with at least 3 games for statistical relevance
            win_pct_by_points = win_pct_by_points[win_pct_by_points["games"] >= 3]

            # Sort by points for smooth line
            win_pct_by_points = win_pct_by_points.sort_values("point_bin")

            # Add trace for this year
            fig.add_trace(
                go.Scatter(
                    x=win_pct_by_points["point_bin"],
                    y=win_pct_by_points["win_pct"],
                    mode="lines+markers",
                    name=str(year),
                    line=dict(width=2, color=colors[idx % len(colors)]),
                    marker=dict(size=6),
                    hovertemplate="<b>%{fullData.name}</b><br>"
                    + "Points: %{x}<br>"
                    + "Win %: %{y:.1f}%<br>"
                    + "<extra></extra>",
                )
            )

        # Update layout
        fig.update_layout(
            title="Winning Percentage by Points Scored (Per Year)",
            xaxis_title="Points Scored",
            yaxis_title="Winning Percentage (%)",
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            hovermode="closest",
            showlegend=True,
            legend=dict(
                title="Year",
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
            ),
            xaxis=dict(
                gridcolor="#E8E5DC",
                showgrid=True,
                zeroline=False,
            ),
            yaxis=dict(
                gridcolor="#E8E5DC",
                showgrid=True,
                zeroline=False,
                range=[0, 105],  # Show 0-100% with slight padding
            ),
        )

        st.plotly_chart(fig, use_container_width=True)
