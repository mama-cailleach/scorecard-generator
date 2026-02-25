"""
Test the export functionality to ensure correct formatting and innings ordering.
"""
import os
import sys
import csv
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scorecard_generator.models import Player, Team, Innings, BallEvent
from scorecard_generator.scorecard_export import (
    export_scorecard_csv,
    export_match_info_csv,
    export_ball_by_ball_csv,
    export_all,
    sanitize_filename,
    get_export_filename
)


def create_test_team(name, player_count=11):
    """Create a test team with specified number of players."""
    team = Team(name)
    for i in range(1, player_count + 1):
        player = Player(i, f"{name} Player {i}")
        team.players[i] = player
        team.order.append(i)
        team.bowler_order.append(i)
    
    # Set captain and wicketkeeper
    team.captain_number = 1
    team.wicketkeeper_number = 2
    
    return team


def create_test_innings(batting_team, bowling_team):
    """Create a test innings with some sample ball events."""
    innings = Innings(batting_team, bowling_team)
    
    # Add some test ball events
    # Over 0
    innings.balls.append(BallEvent(0, 1, "Bowler A", "Batter 1", 1, "runs", None))
    innings.balls.append(BallEvent(0, 2, "Bowler A", "Batter 2", 0, "runs", None))
    innings.balls.append(BallEvent(0, 3, "Bowler A", "Batter 2", 4, "runs", None))
    innings.balls.append(BallEvent(0, 4, "Bowler A", "Batter 2", 0, "runs", None))
    innings.balls.append(BallEvent(0, 5, "Bowler A", "Batter 2", 1, "runs", None))
    innings.balls.append(BallEvent(0, 6, "Bowler A", "Batter 1", 6, "runs", None))
    
    # Over 1
    innings.balls.append(BallEvent(1, 1, "Bowler B", "Batter 1", 0, "runs", None))
    innings.balls.append(BallEvent(1, 2, "Bowler B", "Batter 1", 1, "wide", None))
    innings.balls.append(BallEvent(1, 2, "Bowler B", "Batter 1", 2, "runs", None))
    innings.balls.append(BallEvent(1, 3, "Bowler B", "Batter 2", 0, "wicket", {"dismissal_type": "caught", "dismissed_player": "Batter 2"}))
    innings.balls.append(BallEvent(1, 4, "Bowler B", "Batter 3", 0, "runs", None))
    innings.balls.append(BallEvent(1, 5, "Bowler B", "Batter 3", 1, "bye", None))
    innings.balls.append(BallEvent(1, 6, "Bowler B", "Batter 1", 0, "runs", None))
    
    # Simulate some batting stats
    for i in range(1, 4):
        player = batting_team.players[i]
        player.batting['runs'] = i * 10
        player.batting['balls'] = i * 8
        player.batting['4s'] = i
        player.batting['6s'] = i - 1 if i > 1 else 0
        player.batting['dismissal'] = "not out" if i == 1 else f"c Fielder b Bowler {i}"
    
    # Simulate some bowling stats
    for i in range(1, 3):
        player = bowling_team.players[i]
        player.bowling['balls'] = 6
        player.bowling['runs'] = 10 + i
        player.bowling['wickets'] = i - 1 if i > 1 else 0
        player.bowling['maidens'] = 0
        player.bowling['dots'] = 2
        player.bowling['4s'] = 1
        player.bowling['6s'] = 0
        player.bowling['wides'] = i - 1 if i > 1 else 0
        player.bowling['noballs'] = 0
    
    # Track bowler overs for accurate overs calculation
    innings.bowler_overs = {
        "Bowler A": 6,
        "Bowler B": 6
    }
    
    return innings


def test_sanitize_filename():
    """Test filename sanitization."""
    print("Testing filename sanitization...")
    
    assert sanitize_filename("Team Name") == "Team_Name"
    assert sanitize_filename("Team's Name!") == "Teams_Name"  # Apostrophe and ! removed, space becomes _
    assert sanitize_filename("Team-Name_123") == "Team-Name_123"
    
    print("✓ Filename sanitization works correctly")


def test_get_export_filename():
    """Test export filename generation."""
    print("\nTesting export filename generation...")
    
    team1 = Team("New Zealand")
    team2 = Team("South Africa")
    
    scorecard_file = get_export_filename(team1, team2, "scorecard")
    assert "New_ZealandvSouth_Africa_scorecard.csv" in scorecard_file
    assert scorecard_file.startswith("scorecard_generator/exports/")
    
    print("✓ Export filename generation works correctly")


def test_innings_ordering():
    """Test that innings are exported in the correct order regardless of team parameter order."""
    print("\nTesting innings ordering (critical bug fix)...")
    
    # Create two teams
    team1 = create_test_team("Team A")
    team2 = create_test_team("Team B")
    
    # Scenario 1: Team 2 bats first (this was the bug scenario)
    innings1 = create_test_innings(team2, team1)  # Team B batting
    innings2 = create_test_innings(team1, team2)  # Team A batting
    
    # Export
    test_file = "scorecard_generator/exports/test_innings_order_scorecard.csv"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    export_scorecard_csv(test_file, team1, team2, innings1, innings2, "Test Match")
    
    # Read and verify
    with open(test_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # First batting section should be Team B (innings1.batting_team)
    assert "Team B Batting" in rows[4][0], f"Expected 'Team B Batting' but got '{rows[4][0]}'"
    
    # First bowling section should be Team A (innings1.bowling_team)
    batting_section_end = None
    for i, row in enumerate(rows):
        if row and "Bowling" in row[0] and "Team A" in row[0]:
            batting_section_end = i
            break
    
    assert batting_section_end is not None, "Could not find Team A Bowling section"
    assert "Team A Bowling" in rows[batting_section_end][0]
    
    # Second batting section should be Team A (innings2.batting_team)
    second_batting_section = None
    for i in range(batting_section_end + 1, len(rows)):
        if rows[i] and "Batting" in rows[i][0] and "Team A" in rows[i][0]:
            second_batting_section = i
            break
    
    assert second_batting_section is not None, "Could not find second Team A Batting section"
    assert "Team A Batting" in rows[second_batting_section][0]
    
    # Clean up
    os.remove(test_file)
    
    print("✓ Innings ordering is correct (uses innings.batting_team/bowling_team)")


def test_scorecard_csv_format():
    """Test the scorecard CSV export format."""
    print("\nTesting scorecard CSV format...")
    
    team1 = create_test_team("Team One")
    team2 = create_test_team("Team Two")
    innings1 = create_test_innings(team1, team2)
    innings2 = create_test_innings(team2, team1)
    
    test_file = "scorecard_generator/exports/test_scorecard.csv"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    export_scorecard_csv(test_file, team1, team2, innings1, innings2, "Team One wins by 5 wickets")
    
    # Verify file exists and has content
    assert os.path.exists(test_file)
    
    with open(test_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Check that we have content
    assert len(rows) > 10, "Scorecard should have multiple rows"
    
    # Check for match result
    assert any("Team One wins by 5 wickets" in str(row) for row in rows[:5])
    
    # Check for batting headers
    batting_headers = ["Player", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"]
    assert any(row == batting_headers for row in rows), "Missing batting header row"
    
    # Check for bowling headers
    bowling_headers = ["Player", "Overs", "Maidens", "Runs", "Wickets", "Dots", "4s", "6s", "Wides", "No Balls"]
    assert any(row == bowling_headers for row in rows), "Missing bowling header row"
    
    # Clean up
    os.remove(test_file)
    
    print("✓ Scorecard CSV format is correct")


def test_match_info_csv_format():
    """Test the match info CSV export format (Cricsheet)."""
    print("\nTesting match info CSV format...")
    
    team1 = create_test_team("Team One")
    team2 = create_test_team("Team Two")
    innings1 = create_test_innings(team1, team2)
    innings2 = create_test_innings(team2, team1)
    
    test_file = "scorecard_generator/exports/test_info.csv"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    export_match_info_csv(test_file, team1, team2, innings1, innings2, "Team One wins")
    
    assert os.path.exists(test_file)
    
    with open(test_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Check version
    assert rows[0] == ['version', '2.2.0'], "First row should be version 2.2.0"
    
    # Check info rows
    info_rows = [row for row in rows if row[0] == 'info']
    assert len(info_rows) > 10, "Should have multiple info rows"
    
    # Check for teams
    team_rows = [row for row in rows if len(row) >= 2 and row[1] == 'teams']
    assert len(team_rows) > 0, "Should have teams info"
    
    # Check for players
    player_rows = [row for row in rows if len(row) >= 2 and row[1] == 'player']
    assert len(player_rows) >= 22, "Should have at least 22 player registrations (11 per team)"
    
    # Check for outcome
    outcome_rows = [row for row in rows if len(row) >= 2 and row[1] == 'outcome']
    assert len(outcome_rows) > 0, "Should have outcome info"
    
    # Clean up
    os.remove(test_file)
    
    print("✓ Match info CSV format is correct (Cricsheet compatible)")


def test_ball_by_ball_csv_format():
    """Test the ball-by-ball CSV export format (Cricsheet)."""
    print("\nTesting ball-by-ball CSV format...")
    
    team1 = create_test_team("Team One")
    team2 = create_test_team("Team Two")
    innings1 = create_test_innings(team1, team2)
    innings2 = create_test_innings(team2, team1)
    
    test_file = "scorecard_generator/exports/test_ballbyball.csv"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    export_ball_by_ball_csv(test_file, team1, team2, innings1, innings2)
    
    assert os.path.exists(test_file)
    
    with open(test_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Check header
    expected_header = [
        'match_id', 'season', 'start_date', 'venue', 'innings', 'ball', 'batting_team',
        'bowling_team', 'striker', 'non_striker', 'bowler', 'runs_off_bat', 'extras',
        'wides', 'noballs', 'byes', 'legbyes', 'penalty', 'wicket_type', 'player_dismissed',
        'other_wicket_type', 'other_player_dismissed'
    ]
    assert rows[0] == expected_header, "Header should match Cricsheet format"
    
    # Check that we have ball data
    ball_rows = rows[1:]
    assert len(ball_rows) > 0, "Should have ball-by-ball data"
    
    # Check innings numbers
    innings_1_balls = [row for row in ball_rows if row[4] == '1']
    innings_2_balls = [row for row in ball_rows if row[4] == '2']
    assert len(innings_1_balls) > 0, "Should have innings 1 balls"
    assert len(innings_2_balls) > 0, "Should have innings 2 balls"
    
    # Check ball numbering format
    for row in ball_rows[:5]:
        ball_num = row[5]
        assert '.' in ball_num, f"Ball number should be in format 'over.ball', got {ball_num}"
    
    # Check that teams are correct for each innings
    for row in innings_1_balls:
        assert row[6] == "Team One", f"Innings 1 batting team should be Team One, got {row[6]}"
        assert row[7] == "Team Two", f"Innings 1 bowling team should be Team Two, got {row[7]}"
    
    for row in innings_2_balls:
        assert row[6] == "Team Two", f"Innings 2 batting team should be Team Two, got {row[6]}"
        assert row[7] == "Team One", f"Innings 2 bowling team should be Team One, got {row[7]}"
    
    # Clean up
    os.remove(test_file)
    
    print("✓ Ball-by-ball CSV format is correct (Cricsheet compatible)")


def test_export_all():
    """Test the export_all function that creates all 3 files."""
    print("\nTesting export_all function...")
    
    team1 = create_test_team("New Zealand")
    team2 = create_test_team("South Africa")
    innings1 = create_test_innings(team1, team2)
    innings2 = create_test_innings(team2, team1)
    
    # Run export_all
    export_all(team1, team2, innings1, innings2, "New Zealand wins by 6 wickets")
    
    # Check all 3 files were created
    expected_files = [
        "scorecard_generator/exports/New_ZealandvSouth_Africa_scorecard.csv",
        "scorecard_generator/exports/New_ZealandvSouth_Africa_info.csv",
        "scorecard_generator/exports/New_ZealandvSouth_Africa_ballbyball.csv"
    ]
    
    for file_path in expected_files:
        assert os.path.exists(file_path), f"Expected file {file_path} was not created"
        
        # Verify file has content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 0, f"File {file_path} should not be empty"
    
    # Clean up
    for file_path in expected_files:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    print("✓ export_all creates all 3 CSV files successfully")


def run_all_tests():
    """Run all export tests."""
    print("="*70)
    print("EXPORT FORMAT TESTS")
    print("="*70)
    
    test_sanitize_filename()
    test_get_export_filename()
    test_innings_ordering()
    test_scorecard_csv_format()
    test_match_info_csv_format()
    test_ball_by_ball_csv_format()
    test_export_all()
    
    print("\n" + "="*70)
    print("ALL EXPORT TESTS PASSED ✓")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()
