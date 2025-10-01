import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px

# Configuration - Replace with your league details
LEAGUE_ID = 294338  # Replace with your league ID
YEAR = 2024
ESPN_S2 = "AEArMPrD3zaAx8sODtZz5mCeGrICQ%2FoIRXm8ZoaeaVRnulKIfBk5gTGUOk4capIwiiD%2BrhgJRuMkhdWUDEIKVs4WcR2toJNiEzvBtI7Ni2N8RaZWT7j6mutxpfu%2B6L96HZTtx5OeT9cmDNxe2O7M7qfirvXCxQqB9WeDR3sc0JIbf51LOrAGzu%2FElWJbo4L8lIm7tM5L6tQQvhwhk%2BfFuMtCqSIHcKiCyPGzKJt%2BkkoEI%2F56RENsfo9YI0thh81%2FIOw%2F5ER%2BgAFQkWS9LLbEFagA78bpUpZNGh4IzvlyYDtC7g%3D%3D"
SWID = "{53CA2B64-EB4D-4443-AE3F-9A0E6D1A6654}"



class ESPNFantasyLeague:
    def __init__(
        self, league_id: int, year: int = 2024, espn_s2: str | None = None, swid: str | None = None
    ):
        """
        Initialize ESPN Fantasy League API client

        Args:
            league_id: Your ESPN league ID
            year: Fantasy season year
            espn_s2: ESPN session cookie (for private leagues)
            swid: ESPN user ID cookie (for private leagues)
        """
        self.league_id = league_id
        self.year = year
        self.base_url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"

        # Cookies for private league access
        self.cookies = {}
        if espn_s2:
            self.cookies["espn_s2"] = espn_s2
        if swid:
            self.cookies["SWID"] = swid

    def get_league_info(self) -> dict:
        """Get basic league information"""
        url = f"{self.base_url}?view=mSettings"
        response = requests.get(url, cookies=self.cookies)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch league info: {response.status_code}")

    def get_teams(self) -> pd.DataFrame:
        """Get all teams in the league"""
        url = f"{self.base_url}?view=mTeam"
        response = requests.get(url, cookies=self.cookies)
        data = response.json()

        teams_data = []
        for team in data["teams"]:
            teams_data.append(
                {
                    "team_id": team["id"],
                    "team_name": team["name"],
                    "owner": team["primaryOwner"],
                    "wins": team["record"]["overall"]["wins"],
                    "losses": team["record"]["overall"]["losses"],
                    "points_for": team["record"]["overall"]["pointsFor"],
                    "points_against": team["record"]["overall"]["pointsAgainst"],
                }
            )

        return pd.DataFrame(teams_data)

    def get_matchups(self, week: int | None = None) -> pd.DataFrame:
        """Get matchup data for specific week or all weeks"""
        if week:
            url = f"{self.base_url}?view=mMatchup&scoringPeriodId={week}"
        else:
            url = f"{self.base_url}?view=mMatchup"

        response = requests.get(url, cookies=self.cookies)
        data = response.json()

        matchups_data = []
        for matchup in data["schedule"]:
            try:
                matchups_data.append(
                    {
                        "week": matchup["matchupPeriodId"],
                        "home_team_id": matchup["home"]["teamId"],
                        "home_score": matchup["home"]["totalPoints"],
                        "away_team_id": matchup["away"]["teamId"],
                        "away_score": matchup["away"]["totalPoints"],
                    }
                )
            except KeyError:
                continue  # Skip if matchup data is incomplete

        return pd.DataFrame(matchups_data)

    def get_roster(self, team_id: int, week: int) -> pd.DataFrame:
        """Get roster for specific team and week"""
        url = f"{self.base_url}?view=mRoster&scoringPeriodId={week}"
        response = requests.get(url, cookies=self.cookies)
        data = response.json()

        roster_data = []
        for team in data["teams"]:
            if team["id"] == team_id:
                for player in team["roster"]["entries"]:
                    roster_data.append(
                        {
                            "player_name": player["playerPoolEntry"]["player"]["fullName"],
                            "position": player["playerPoolEntry"]["player"]["defaultPositionId"],
                            "points": player["playerPoolEntry"]["player"]["stats"][0][
                                "appliedTotal"
                            ]
                            if player["playerPoolEntry"]["player"]["stats"]
                            else 0,
                            "slot": player["lineupSlotId"],
                        }
                    )

        return pd.DataFrame(roster_data)


class FantasyDashboard:
    def __init__(self, league: ESPNFantasyLeague):
        self.league = league
        self.teams_df: pd.DataFrame | None = None
        self.matchups_df: pd.DataFrame | None = None

    def load_data(self):
        """Load all necessary data"""
        self.teams_df = self.league.get_teams()
        self.matchups_df = self.league.get_matchups()

    def create_standings_chart(self):
        """Create standings visualization"""
        if self.teams_df is None:
            self.load_data()
        if self.teams_df is None:
            raise ValueError("Failed to load teams data")

        fig = px.bar(
            self.teams_df.sort_values("wins", ascending=False),
            x="team_name",
            y="wins",
            title="League Standings - Wins",
            labels={"wins": "Wins", "team_name": "Team"},
            color="wins",
            color_continuous_scale="viridis",
        )
        fig.update_xaxis(tickangle=45)
        return fig

    def create_points_scatter(self):
        """Create points for vs points against scatter plot"""
        if self.teams_df is None:
            self.load_data()

        fig = px.scatter(
            self.teams_df,
            x="points_for",
            y="points_against",
            text="team_name",
            title="Points For vs Points Against",
            labels={"points_for": "Points For", "points_against": "Points Against"},
        )
        fig.update_traces(textposition="top center")
        return fig

    def create_weekly_scores_line(self):
        """Create weekly scoring trends"""
        if self.matchups_df is None:
            self.load_data()

        # Reshape data for line chart
        scores_data = []
        for _, match in self.matchups_df.iterrows():
            scores_data.append(
                {
                    "week": match["week"],
                    "team_id": match["home_team_id"],
                    "score": match["home_score"],
                }
            )
            scores_data.append(
                {
                    "week": match["week"],
                    "team_id": match["away_team_id"],
                    "score": match["away_score"],
                }
            )

        scores_df = pd.DataFrame(scores_data)

        # Merge with team names
        scores_df = scores_df.merge(self.teams_df[["team_id", "team_name"]], on="team_id")

        fig = px.line(
            scores_df,
            x="week",
            y="score",
            color="team_name",
            title="Weekly Scoring Trends",
            labels={"score": "Points Scored", "week": "Week"},
        )
        return fig

    def generate_power_rankings(self) -> pd.DataFrame:
        """Generate power rankings based on recent performance"""
        if self.teams_df is None:
            self.load_data()

        # Simple power ranking: weighted average of wins and points
        self.teams_df["power_score"] = (
            self.teams_df["wins"] * 0.6
            + (self.teams_df["points_for"] / self.teams_df["points_for"].max()) * 0.4
        )

        return self.teams_df.sort_values("power_score", ascending=False)[
            ["team_name", "wins", "losses", "points_for", "power_score"]
        ].reset_index(drop=True)


def create_streamlit_dashboard():
    """Create Streamlit dashboard interface"""
    st.title("🏈 Fantasy Football League Dashboard")

    if st.sidebar.button("Load League Data"):
        try:
            # Initialize league
            league = ESPNFantasyLeague(
                league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID
            )

            # Create dashboard
            dashboard = FantasyDashboard(league)
            dashboard.load_data()

            # Display league info
            st.header("League Overview")
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

            # Standings
            st.header("Current Standings")
            if dashboard.teams_df is not None:
                st.dataframe(
                    dashboard.teams_df[
                        ["team_name", "wins", "losses", "points_for", "points_against"]
                    ].sort_values("wins", ascending=False)
                )

            # Visualizations
            st.header("League Analytics")

            # Standings chart
            st.plotly_chart(dashboard.create_standings_chart(), use_container_width=True)

            # Points scatter
            st.plotly_chart(dashboard.create_points_scatter(), use_container_width=True)

            # Weekly trends
            st.plotly_chart(dashboard.create_weekly_scores_line(), use_container_width=True)

            # Power Rankings
            st.header("Power Rankings")
            power_rankings = dashboard.generate_power_rankings()
            st.dataframe(power_rankings)

        except Exception as e:
            st.error(f"Error loading league data: {str(e)}")
            st.info(
                "Make sure your League ID is correct and provide authentication for private leagues."
            )


# Example usage script
def main():
    """Example usage of the ESPN Fantasy League API"""


    # Initialize league
    league = ESPNFantasyLeague(LEAGUE_ID, YEAR, ESPN_S2, SWID)

    # Get data
    print("Fetching league data...")
    teams_df = league.get_teams()

    # Display basic info
    print("\n=== LEAGUE STANDINGS ===")
    standings = teams_df.sort_values("wins", ascending=False)
    print(standings[["team_name", "wins", "losses", "points_for"]].to_string(index=False))

    # Create visualizations
    plt.figure(figsize=(15, 10))

    # Subplot 1: Standings
    plt.subplot(2, 2, 1)
    plt.bar(range(len(standings)), standings["wins"])
    plt.xticks(range(len(standings)), standings["team_name"].tolist(), rotation=45, ha="right")
    plt.title("League Standings")
    plt.ylabel("Wins")

    # Subplot 2: Points comparison
    plt.subplot(2, 2, 2)
    plt.scatter(teams_df["points_for"], teams_df["points_against"])
    for i, row in teams_df.iterrows():
        plt.annotate(row["team_name"], (row["points_for"], row["points_against"]))
    plt.xlabel("Points For")
    plt.ylabel("Points Against")
    plt.title("Points For vs Against")

    # Show plots
    plt.tight_layout()
    plt.show()

    print("\nDashboard created successfully!")
    print("To run the interactive dashboard, use: streamlit run this_file.py")

    # except Exception as e:
    #     print(f"Error: {e}")
    #     print("\nTroubleshooting tips:")
    #     print("1. Verify your League ID is correct")
    #     print("2. For private leagues, you need ESPN_S2 and SWID cookies")
    #     print("3. Check that the season year is correct")


if __name__ == "__main__":
    # Uncomment the line below to run the Streamlit dashboard
    create_streamlit_dashboard()

    # Or run the basic example
    main()
