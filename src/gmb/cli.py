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
):
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
def summary():
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
def oiwp():
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


def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()