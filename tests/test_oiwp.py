"""Tests for OIWP calculation module."""
import pandas as pd  # type: ignore[import-untyped]
import pytest

from gmb.oiwp import TeamOIWP, calculate_oiwp_stats


class TestTeamOIWP:
    """Test suite for TeamOIWP class."""

    def test_init(self):
        """Test TeamOIWP initialization."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)

        assert team.name == "Team A"
        assert team._current_week == 4
        assert team._total_teams == 12
        assert team._wins == 0
        assert team._oiwins == 0

    def test_wp_calculation(self):
        """Test winning percentage calculation."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)
        team.add_win()
        team.add_win()
        team.add_win()

        assert team.wp == 0.75  # 3 wins / 4 weeks

    def test_oiwp_calculation(self):
        """Test OIWP calculation."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)

        # In 4 weeks with 12 teams, can beat at most 11 teams per week
        # Total possible wins = 11 * 4 = 44
        team.add_oiwins(8)
        team.add_oiwins(9)
        team.add_oiwins(7)
        team.add_oiwins(10)

        # Total: 34 out of 44
        assert team.oiwp == pytest.approx(34 / 44)

    def test_oiwp_zero_weeks(self):
        """Test OIWP with zero weeks (edge case)."""
        team = TeamOIWP("Team A", current_week=0, total_teams=12)

        assert team.oiwp == 0.0

    def test_luck_calculation(self):
        """Test luck calculation (wp - oiwp)."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)

        # 3 actual wins out of 4 weeks
        team.add_win()
        team.add_win()
        team.add_win()

        # 30 OIWP wins out of 44 possible
        team.add_oiwins(30)

        wp = 3 / 4  # 0.75
        oiwp = 30 / 44  # ~0.682
        expected_luck = wp - oiwp

        assert team.luck == pytest.approx(expected_luck)

    def test_positive_luck(self):
        """Test positive luck (winning more than expected)."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)

        # Win 3 actual games
        for _ in range(3):
            team.add_win()

        # But only beat 20 teams in OIWP (out of 44 possible)
        team.add_oiwins(20)

        assert team.luck > 0

    def test_negative_luck(self):
        """Test negative luck (winning less than expected)."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)

        # Win 1 actual game
        team.add_win()

        # But beat 30 teams in OIWP (out of 44 possible)
        team.add_oiwins(30)

        assert team.luck < 0

    def test_repr(self):
        """Test string representation."""
        team = TeamOIWP("Team A", current_week=4, total_teams=12)
        team.add_win()
        team.add_win()
        team.add_oiwins(20)

        repr_str = repr(team)
        assert "Team A" in repr_str
        assert "wp=" in repr_str
        assert "oiwp=" in repr_str
        assert "luck=" in repr_str


class TestCalculateOIWPStats:
    """Test suite for calculate_oiwp_stats function."""

    def test_basic_calculation(self):
        """Test basic OIWP calculation with simple data."""
        # Create sample matchup data
        matchups_df = pd.DataFrame({
            'week': [1, 1, 1, 1],
            'team_name': ['Team A', 'Team B', 'Team A', 'Team B'],
            'points': [100, 90, 100, 90],
            'opponent_name': ['Team B', 'Team A', 'Team B', 'Team A'],
            'opponent_points': [90, 100, 90, 100]
        })

        stats = calculate_oiwp_stats(matchups_df)

        assert isinstance(stats, pd.DataFrame)
        assert len(stats) == 2
        assert 'team_name' in stats.columns
        assert 'wp' in stats.columns
        assert 'oiwp' in stats.columns
        assert 'luck' in stats.columns

    def test_sorted_by_oiwp(self):
        """Test that results are sorted by OIWP descending."""
        matchups_df = pd.DataFrame({
            'week': [1, 1, 1, 1, 2, 2, 2, 2],
            'team_name': ['Team A', 'Team B', 'Team A', 'Team B', 'Team A', 'Team B', 'Team A', 'Team B'],
            'points': [120, 80, 120, 80, 130, 85, 130, 85],
            'opponent_name': ['Team B', 'Team A', 'Team B', 'Team A', 'Team B', 'Team A', 'Team B', 'Team A'],
            'opponent_points': [80, 120, 80, 120, 85, 130, 85, 130]
        })

        stats = calculate_oiwp_stats(matchups_df)

        # Team A should have higher OIWP than Team B
        assert stats.iloc[0]['team_name'] == 'Team A'
        assert stats.iloc[1]['team_name'] == 'Team B'
        assert stats.iloc[0]['oiwp'] > stats.iloc[1]['oiwp']

    def test_multiple_teams(self):
        """Test OIWP with multiple teams."""
        matchups_df = pd.DataFrame({
            'week': [1, 1, 1, 1, 1, 1],
            'team_name': ['Team A', 'Team B', 'Team C', 'Team A', 'Team B', 'Team C'],
            'points': [120, 100, 80, 120, 100, 80],
            'opponent_name': ['Team B', 'Team A', 'Team B', 'Team B', 'Team A', 'Team B'],
            'opponent_points': [100, 120, 100, 100, 120, 100]
        })

        stats = calculate_oiwp_stats(matchups_df)

        assert len(stats) == 3
        # Team A scored highest, so should have highest OIWP
        assert stats.iloc[0]['team_name'] == 'Team A'

    def test_empty_dataframe(self):
        """Test handling of empty matchup data."""
        matchups_df = pd.DataFrame({
            'week': [],
            'team_name': [],
            'points': [],
            'opponent_name': [],
            'opponent_points': []
        })

        stats = calculate_oiwp_stats(matchups_df)

        assert isinstance(stats, pd.DataFrame)
        assert len(stats) == 0

    def test_zero_scores_filtered(self):
        """Test that weeks with zero scores are excluded."""
        matchups_df = pd.DataFrame({
            'week': [1, 1, 2, 2],
            'team_name': ['Team A', 'Team B', 'Team A', 'Team B'],
            'points': [100, 90, 0, 0],  # Week 2 has zero scores
            'opponent_name': ['Team B', 'Team A', 'Team B', 'Team A'],
            'opponent_points': [90, 100, 0, 0]
        })

        stats = calculate_oiwp_stats(matchups_df)

        # Should only calculate based on week 1
        # Each team played 1 week with 1 opponent
        assert stats.iloc[0]['wp'] in [0.0, 1.0]  # Either 0-1 or 1-0

    def test_actual_wins_counted(self):
        """Test that actual wins are counted correctly."""
        matchups_df = pd.DataFrame({
            'week': [1, 1],
            'team_name': ['Team A', 'Team B'],
            'points': [100, 90],
            'opponent_name': ['Team B', 'Team A'],
            'opponent_points': [90, 100]
        })

        stats = calculate_oiwp_stats(matchups_df)

        team_a = stats[stats['team_name'] == 'Team A'].iloc[0]
        team_b = stats[stats['team_name'] == 'Team B'].iloc[0]

        assert team_a['wp'] == 1.0  # Won 1 of 1
        assert team_b['wp'] == 0.0  # Won 0 of 1

    def test_oiwp_vs_wp_relationship(self):
        """Test that luck is calculated correctly as wp - oiwp."""
        matchups_df = pd.DataFrame({
            'week': [1, 1, 1, 1],
            'team_name': ['Team A', 'Team B', 'Team A', 'Team B'],
            'points': [100, 90, 100, 90],
            'opponent_name': ['Team B', 'Team A', 'Team B', 'Team A'],
            'opponent_points': [90, 100, 90, 100]
        })

        stats = calculate_oiwp_stats(matchups_df)

        for _, row in stats.iterrows():
            assert row['luck'] == pytest.approx(row['wp'] - row['oiwp'])

    def test_three_teams_oiwp(self):
        """Test OIWP calculation with three teams to verify logic."""
        # Week 1: A=120, B=100, C=80
        # Team A beats 2 teams (B and C)
        # Team B beats 1 team (C)
        # Team C beats 0 teams
        matchups_df = pd.DataFrame({
            'week': [1, 1, 1, 1, 1, 1],
            'team_name': ['Team A', 'Team B', 'Team C', 'Team A', 'Team B', 'Team C'],
            'points': [120, 100, 80, 120, 100, 80],
            'opponent_name': ['Team B', 'Team A', 'Team C', 'Team B', 'Team A', 'Team C'],
            'opponent_points': [100, 120, 80, 100, 120, 80]
        })

        stats = calculate_oiwp_stats(matchups_df)

        # With 3 teams and 1 week, max possible wins = 2 * 1 = 2
        team_a = stats[stats['team_name'] == 'Team A'].iloc[0]
        team_b = stats[stats['team_name'] == 'Team B'].iloc[0]
        team_c = stats[stats['team_name'] == 'Team C'].iloc[0]

        assert team_a['oiwp'] == pytest.approx(2 / 2)  # Beat 2 out of 2 possible
        assert team_b['oiwp'] == pytest.approx(1 / 2)  # Beat 1 out of 2 possible
        assert team_c['oiwp'] == pytest.approx(0 / 2)  # Beat 0 out of 2 possible


class TestOIWPValidation:
    """Test suite for OIWP validation checks."""

    def test_validation_with_realistic_data(self):
        """Test that realistic data passes validation without warnings."""
        # Create realistic data: 4 teams, 3 weeks
        matchups_df = pd.DataFrame([
            # Week 1
            {'week': 1, 'team_name': 'Team A', 'points': 110, 'opponent_points': 90},
            {'week': 1, 'team_name': 'Team B', 'points': 90, 'opponent_points': 110},
            {'week': 1, 'team_name': 'Team C', 'points': 105, 'opponent_points': 95},
            {'week': 1, 'team_name': 'Team D', 'points': 95, 'opponent_points': 105},
            # Week 2
            {'week': 2, 'team_name': 'Team A', 'points': 95, 'opponent_points': 100},
            {'week': 2, 'team_name': 'Team B', 'points': 100, 'opponent_points': 95},
            {'week': 2, 'team_name': 'Team C', 'points': 110, 'opponent_points': 85},
            {'week': 2, 'team_name': 'Team D', 'points': 85, 'opponent_points': 110},
            # Week 3
            {'week': 3, 'team_name': 'Team A', 'points': 115, 'opponent_points': 105},
            {'week': 3, 'team_name': 'Team B', 'points': 105, 'opponent_points': 115},
            {'week': 3, 'team_name': 'Team C', 'points': 90, 'opponent_points': 100},
            {'week': 3, 'team_name': 'Team D', 'points': 100, 'opponent_points': 90},
        ])

        # Should not raise warnings
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # Turn warnings into errors
            stats = calculate_oiwp_stats(matchups_df)

        # Verify stats are reasonable
        assert all(0.0 <= stats['wp']) and all(stats['wp'] <= 1.0)
        assert all(0.0 <= stats['oiwp']) and all(stats['oiwp'] <= 1.0)
        assert abs(stats['wp'].mean() - 0.5) < 0.01
        assert abs(stats['oiwp'].mean() - 0.5) < 0.01
        assert abs(stats['luck'].sum()) < 0.04  # Allow margin for 4 teams

    def test_validation_warns_on_invalid_wp(self):
        """Test that validation warns when WP values are out of range."""
        # Manually create invalid results to test validation
        from gmb.oiwp import _validate_oiwp_results
        invalid_df = pd.DataFrame([
            {'team_name': 'Team A', 'wp': 1.5, 'oiwp': 0.5, 'luck': 1.0},
            {'team_name': 'Team B', 'wp': 0.5, 'oiwp': 0.5, 'luck': 0.0},
        ])

        with pytest.warns(UserWarning, match="Invalid WP values detected"):
            _validate_oiwp_results(invalid_df)

    def test_validation_warns_on_non_zero_sum_luck(self):
        """Test that validation warns when luck doesn't sum to zero."""
        # Manually create data with non-zero sum luck
        from gmb.oiwp import _validate_oiwp_results
        invalid_df = pd.DataFrame([
            {'team_name': 'Team A', 'wp': 0.8, 'oiwp': 0.5, 'luck': 0.3},
            {'team_name': 'Team B', 'wp': 0.8, 'oiwp': 0.5, 'luck': 0.3},
        ])

        with pytest.warns(UserWarning, match="Sum of luck values"):
            _validate_oiwp_results(invalid_df)

    def test_validation_warns_on_mean_wp_deviation(self):
        """Test that validation warns when mean WP deviates from 0.5."""
        # Manually create data with skewed WP
        from gmb.oiwp import _validate_oiwp_results
        invalid_df = pd.DataFrame([
            {'team_name': 'Team A', 'wp': 0.9, 'oiwp': 0.5, 'luck': 0.4},
            {'team_name': 'Team B', 'wp': 0.9, 'oiwp': 0.5, 'luck': 0.4},
        ])

        with pytest.warns(UserWarning, match="Mean WP is .*, expected ~0.500"):
            _validate_oiwp_results(invalid_df)

    def test_validation_empty_dataframe(self):
        """Test that validation handles empty dataframes gracefully."""
        # Should not raise warnings or errors with empty input
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # Turn warnings into errors
            result = calculate_oiwp_stats(pd.DataFrame(columns=['week', 'team_name', 'points', 'opponent_points']))

        # Empty result should not trigger validation warnings and should be empty
        assert result.empty
