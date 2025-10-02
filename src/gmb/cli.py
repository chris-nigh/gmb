"""Command-line interface for GMB configuration."""
import typer
from rich import print as rprint

from gmb.config import DashboardConfig, CONFIG_FILE
from gmb.espn import ESPNFantasyLeague

app = typer.Typer(help="GMB Fantasy Football Tools")


@app.command()
def setup(
    league_id: int = typer.Option(..., prompt=True, help="ESPN league ID"),
    year: int = typer.Option(2024, prompt=True, help="Season year"),
    espn_s2: str | None = typer.Option(
        None,
        prompt="Enter your ESPN_S2 cookie value (press Enter to skip)",
        help="ESPN S2 cookie for private leagues",
    ),
    swid: str | None = typer.Option(
        None,
        prompt="Enter your SWID cookie value (press Enter to skip)",
        help="SWID cookie for private leagues",
    ),
) -> None:
    """Interactive configuration setup."""
    rprint("[bold]GMB Fantasy Football Configuration Setup[/bold]")

    try:
        config = DashboardConfig(
            league_id=league_id,
            year=year,
            espn_s2=espn_s2 if espn_s2 else None,
            swid=swid if swid else None,
        )
        config.save()

        rprint("\n[green]Configuration saved successfully![/green]")
        rprint(f"League settings saved to: {CONFIG_FILE}")
        rprint("[dim]Credentials stored securely in system keyring[/dim]")
    except Exception as e:
        rprint(f"[red]Error saving configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def summary() -> None:
    """Display league summary and team standings."""
    try:
        config = DashboardConfig.load()
        league = ESPNFantasyLeague(**config.to_dict())
        teams_df = league.get_teams()
        rprint("\n[bold]Team Standings:[/bold]")
        rprint("[dim]--------------[/dim]")
        standings = teams_df.sort_values('wins', ascending=False)[
            ['team_name', 'wins', 'losses', 'points_for']
        ]
        standings['points_for'] = standings['points_for'].round(1)
        rprint(standings.to_string(index=False))
    except Exception as e:
        rprint(f"[red]Error displaying league summary: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def oiwp() -> None:
    """Show OIWP (Opponent-Independent Winning Percentage) analysis.

    OIWP measures how well each team would perform if they played against
    every other team in the league each week. Positive luck indicates
    winning more than expected; negative luck indicates underperforming.
    """
    try:
        config = DashboardConfig.load()
        league = ESPNFantasyLeague(**config.to_dict())
        matchups_df = league.get_matchups()

        if matchups_df.empty:
            rprint("[yellow]No matchup data available yet.[/yellow]")
            return

        from .oiwp import calculate_oiwp_stats
        stats = calculate_oiwp_stats(matchups_df)

        if stats.empty:
            rprint("[yellow]No OIWP data could be calculated.[/yellow]")
            return

        rprint("\n[bold]Opponent-Independent Winning Percentage (OIWP) Analysis[/bold]")
        rprint("[dim]----------------------------------------------------[/dim]")
        for _, row in stats.iterrows():
            luck_color = "green" if row['luck'] > 0 else "red"
            schedule_color = "green" if row['schedule_wins'] > 0 else "red" if row['schedule_wins'] < 0 else "dim"
            rprint(
                f"{row['team_name']}: [bold]{row['record']}[/bold] "
                f"(Predicted: {row['predicted_record']}, "
                f"OIWP: {row['oiwp']:.3f}, "
                f"Luck: [{luck_color}]{row['luck']:+.3f}[/{luck_color}], "
                f"Sched: [{schedule_color}]{row['schedule_wins']:+d}[/{schedule_color}])"
            )
    except Exception as e:
        rprint(f"[red]Error calculating OIWP: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def keepers(
    team_id: int = typer.Option(..., help="ESPN team ID to analyze"),
    year: int = typer.Option(None, help="Year to generate keeper summary for (default: current config year)"),
    output: str = typer.Option(None, help="Output CSV file path (default: gmb_keepers_<year>.csv)"),
) -> None:
    """Generate keeper eligibility summary for a team.

    Creates a CSV file showing which players are eligible to be kept,
    their keeper costs, and years remaining. Analyzes the past 3 years
    of draft and transaction history to determine eligibility.
    """
    try:
        from .espn_keeper import ESPNKeeperLeague
        from .keeper import KeeperAnalyzer
        from .keeper_constants import GO_BACK_YEARS

        config = DashboardConfig.load()

        # Use year from config if not specified
        if year is None:
            year = config.year

        # Default output filename
        if output is None:
            output = f"gmb_keepers_{year + 1}.csv"

        rprint(f"\n[bold]Generating Keeper Summary for {year + 1} Season[/bold]")
        rprint(f"[dim]Analyzing {GO_BACK_YEARS} years of history ({year - GO_BACK_YEARS + 1}-{year})[/dim]\n")

        # Create keeper league client
        league = ESPNKeeperLeague(
            league_id=config.league_id,
            year=year,
            espn_s2=config.espn_s2,
            swid=config.swid,
        )

        # Collect draft and transaction data for past GO_BACK_YEARS years
        draft_history = []
        transaction_history = []

        for hist_year in range(year, year - GO_BACK_YEARS, -1):
            rprint(f"Processing {hist_year}...")

            draft_df = league.get_draft_picks(hist_year)
            trans_df = league.get_transactions(hist_year)

            draft_history.append(draft_df)
            transaction_history.append(trans_df)

        rprint(f"\n[bold]Analyzing roster for team {team_id}...[/bold]")

        # Get current roster
        roster_df = league.get_roster(team_id, year)

        # Get team name
        teams_df = league.get_teams()
        team_row = teams_df[teams_df['team_id'] == team_id]
        team_name = team_row.iloc[0]['team_name'] if len(team_row) > 0 else f"Team {team_id}"

        # Analyze keeper eligibility
        analyzer = KeeperAnalyzer(draft_history, transaction_history)
        results_df = analyzer.analyze_roster(roster_df, team_name)

        # Save to CSV
        results_df.to_csv(output, index=False)

        rprint(f"\n[green]✓ Keeper summary saved to: {output}[/green]")
        rprint(f"[dim]Total players analyzed: {len(results_df)}[/dim]")

        # Show summary
        eligible_count = results_df['eligible'].sum()
        rprint(f"[dim]Keeper eligible: {eligible_count}[/dim]")

    except Exception as e:
        rprint(f"[red]Error generating keeper summary: {e}[/red]")
        import traceback
        rprint(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


@app.command()
def transactions(
    year: int = typer.Option(None, help="Year to fetch transactions for (default: current config year)"),
    output: str = typer.Option(None, help="Output CSV file path (default: transactions_<year>.csv)"),
) -> None:
    """Fetch and save league transactions to CSV.

    Retrieves all add/drop/waiver transactions from ESPN for the specified year.
    Useful for offline keeper analysis or record keeping.
    """
    try:
        from .espn_keeper import ESPNKeeperLeague

        config = DashboardConfig.load()

        # Use year from config if not specified
        if year is None:
            year = config.year

        # Default output filename
        if output is None:
            output = f"transactions_{year}.csv"

        rprint(f"\n[bold]Fetching Transactions for {year}[/bold]")

        # Create keeper league client
        league = ESPNKeeperLeague(
            league_id=config.league_id,
            year=year,
            espn_s2=config.espn_s2,
            swid=config.swid,
        )

        # Fetch transactions
        rprint("Retrieving transaction data from ESPN...")
        trans_df = league.get_transactions(year)

        # Save to CSV
        trans_df.to_csv(output, index=False)


        rprint(f"\n[green]✓ Transactions saved to: {output}[/green]")
        rprint(f"[dim]Total transactions: {len(trans_df)}[/dim]")

    except Exception as e:
        rprint(f"[red]Error fetching transactions: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def player_transactions(
    player_name: str = typer.Argument(..., help="Player name to filter (case-insensitive)"),
    year: int = typer.Option(None, help="Year to fetch transactions for (default: current config year)"),
    output: str = typer.Option(None, help="Output CSV file path (default: player_transactions_<year>.csv)"),
) -> None:
    """Export all transactions for a given player in a given year to CSV."""
    try:
        from .espn_keeper import ESPNKeeperLeague
        config = DashboardConfig.load()
        if year is None:
            year = config.year
        if output is None:
            output = f"player_transactions_{year}.csv"
        rprint(f"\n[bold]Fetching Transactions for {year}[/bold]")
        league = ESPNKeeperLeague(
            league_id=config.league_id,
            year=year,
            espn_s2=config.espn_s2,
            swid=config.swid,
        )
        trans_df = league.get_transactions(year)
        # Filter for player (case-insensitive substring match)
        filtered = trans_df[trans_df['player_name'].str.lower().str.contains(player_name.lower())]
        filtered.to_csv(output, index=False)
        rprint(f"\n[green]✓ Player transactions saved to: {output}[/green]")
        rprint(f"[dim]Total transactions for '{player_name}': {len(filtered)}[/dim]")
    except Exception as e:
        rprint(f"[red]Error fetching player transactions: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def show_player_transactions(
    player_name: str = typer.Argument(..., help="Player name to filter (case-insensitive)"),
    year: int = typer.Option(None, help="Year to fetch transactions for (default: current config year)"),
) -> None:
    """Print all transactions for a given player in a given year to the screen, with a check for player existence."""
    try:
        from .espn_keeper import ESPNKeeperLeague
        config = DashboardConfig.load()
        if year is None:
            year = config.year
        rprint(f"\n[bold]Fetching Transactions for {year}[/bold]")
        league = ESPNKeeperLeague(
            league_id=config.league_id,
            year=year,
            espn_s2=config.espn_s2,
            swid=config.swid,
        )
        trans_df = league.get_transactions(year)
        # Check if player exists in any transaction
        all_players = trans_df['player_name'].str.lower().unique()
        if not any(player_name.lower() in p for p in all_players):
            rprint(f"[red]No transactions found for any player matching '{player_name}' in {year}.[/red]")
            return
        filtered = trans_df[trans_df['player_name'].str.lower().str.contains(player_name.lower())]
        if filtered.empty:
            rprint(f"[yellow]No transactions found for '{player_name}' in {year}.[/yellow]")
        else:
            rprint(f"\n[bold]Transactions for '{player_name}' in {year}:[/bold]")
            rprint(filtered.to_string(index=False))
            rprint(f"[dim]Total transactions: {len(filtered)}[/dim]")
    except Exception as e:
        rprint(f"[red]Error fetching player transactions: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def show_player_draft(
    player_name: str = typer.Argument(..., help="Player name to filter (case-insensitive)"),
    year: int = typer.Option(None, help="Year to fetch draft details for (default: current config year)"),
) -> None:
    """Print draft details for a given player in a given year."""
    try:
        from .espn_keeper import ESPNKeeperLeague
        config = DashboardConfig.load()
        if year is None:
            year = config.year
        rprint(f"\n[bold]Fetching Draft Details for {year}[/bold]")
        league = ESPNKeeperLeague(
            league_id=config.league_id,
            year=year,
            espn_s2=config.espn_s2,
            swid=config.swid,
        )
        draft_df = league.get_draft_picks(year)

        # Check if player exists in draft
        all_players = draft_df['player_name'].str.lower().unique()
        if not any(player_name.lower() in p for p in all_players):
            rprint(f"[red]No draft pick found for any player matching '{player_name}' in {year}.[/red]")
            return

        # Filter for player
        filtered = draft_df[draft_df['player_name'].str.lower().str.contains(player_name.lower())]

        if filtered.empty:
            rprint(f"[yellow]No draft pick found for '{player_name}' in {year}.[/yellow]")
        else:
            rprint(f"\n[bold]Draft Details for '{player_name}' in {year}:[/bold]")
            for _, row in filtered.iterrows():
                keeper_status = "[green]Yes[/green]" if row['keeper'] else "[dim]No[/dim]"
                rprint(f"  Player: [cyan]{row['player_name']}[/cyan]")
                rprint(f"  Team: {row['team_name']}")
                rprint(f"  Round: {row['round']}, Pick: {row['pick']}")
                rprint(f"  Cost: ${row['cost']}")
                rprint(f"  Keeper: {keeper_status}")
                rprint("")
            rprint(f"[dim]Total draft picks: {len(filtered)}[/dim]")
    except Exception as e:
        rprint(f"[red]Error fetching draft details: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def draft_value(
    year: int = typer.Option(None, help="Year to analyze (default: current config year)"),
) -> None:
    """Debug draft value analysis - show best and worst picks."""
    try:
        from .espn_keeper import ESPNKeeperLeague
        from .position_map import get_position_name

        config = DashboardConfig.load()
        if year is None:
            year = config.year

        rprint(f"\n[bold]Draft Value Analysis for {year}[/bold]")
        rprint("[dim]Loading data...[/dim]")

        league = ESPNKeeperLeague(
            league_id=config.league_id,
            year=year,
            espn_s2=config.espn_s2,
            swid=config.swid,
        )

        # Get draft data
        draft_df = league.get_draft_picks(year)
        rprint(f"[green]✓[/green] Draft data loaded: {len(draft_df)} picks")

        # Get player stats (all active players for accurate league-wide rankings)
        stats_df = league.get_all_player_stats(year)
        rprint(f"[green]✓[/green] Player stats loaded: {len(stats_df)} active players\n")

        if draft_df.empty:
            rprint("[red]No draft data available[/red]")
            return

        if stats_df.empty:
            rprint("[red]No player stats available[/red]")
            return

        # Show sample data
        rprint("[bold]Sample Draft Data:[/bold]")
        rprint(f"Columns: {', '.join(draft_df.columns.tolist())}")
        rprint(f"Sample player names: {', '.join(draft_df['player_name'].head(3).tolist())}\n")

        rprint("[bold]Sample Stats Data:[/bold]")
        rprint(f"Columns: {', '.join(stats_df.columns.tolist())}")
        rprint(f"Sample player names: {', '.join(stats_df['player_name'].head(3).tolist())}\n")

        # First, calculate position ranks from ALL rostered players (not just drafted)
        stats_with_position = stats_df.copy()
        stats_with_position['position'] = stats_with_position['position_id'].apply(get_position_name)

        # Calculate league-wide position rank
        stats_with_rank = stats_with_position[stats_with_position['total_points'] > 0].copy()
        stats_with_rank['pos_rank'] = stats_with_rank.groupby('position')['total_points'].rank(method='min', ascending=False)

        # Now merge draft data with player stats AND position rank
        analysis = draft_df.merge(
            stats_with_rank[['player_name', 'total_points', 'position_id', 'position', 'pos_rank']],
            on='player_name',
            how='left'
        )

        rprint(f"[bold]After Merge:[/bold]")
        rprint(f"Total rows: {len(analysis)}")
        rprint(f"Players with stats: {analysis['total_points'].notna().sum()}")
        rprint(f"Players with points > 0: {(analysis['total_points'] > 0).sum()}\n")

        # Filter to players with stats
        analysis = analysis[analysis['total_points'].notna() & (analysis['total_points'] > 0)].copy()

        if analysis.empty:
            rprint("[yellow]No players with scoring data found[/yellow]")
            return

        # Calculate value score
        analysis['cost_normalized'] = (analysis['cost'] - analysis['cost'].min()) / (analysis['cost'].max() - analysis['cost'].min() + 1)
        analysis['rank_normalized'] = (analysis['pos_rank'] - 1) / (analysis['pos_rank'].max())
        analysis['value_score'] = (1 - analysis['rank_normalized']) - analysis['cost_normalized']

        # Best picks
        rprint("[bold green]🏆 Top 5 Best Draft Picks:[/bold green]")
        best = analysis.nlargest(5, 'value_score')[
            ['player_name', 'team_name', 'position', 'cost', 'total_points', 'pos_rank', 'value_score']
        ]
        for _, row in best.iterrows():
            rprint(
                f"  {row['player_name']:20} | {row['team_name']:15} | "
                f"{row['position']:3} | ${row['cost']:3.0f} | "
                f"{row['total_points']:6.1f} pts | Rank {int(row['pos_rank']):2} | "
                f"Value: {row['value_score']:+.3f}"
            )

        rprint("\n[bold red]💸 Top 5 Worst Draft Picks:[/bold red]")
        worst = analysis.nsmallest(5, 'value_score')[
            ['player_name', 'team_name', 'position', 'cost', 'total_points', 'pos_rank', 'value_score']
        ]
        for _, row in worst.iterrows():
            rprint(
                f"  {row['player_name']:20} | {row['team_name']:15} | "
                f"{row['position']:3} | ${row['cost']:3.0f} | "
                f"{row['total_points']:6.1f} pts | Rank {int(row['pos_rank']):2} | "
                f"Value: {row['value_score']:+.3f}"
            )

        rprint(f"\n[dim]Total players analyzed: {len(analysis)}[/dim]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
        import traceback
        rprint(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
