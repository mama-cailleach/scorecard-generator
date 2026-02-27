"""Test suite for match statistics functionality.

Tests phase detection, scoring distribution tracking, partnership tracking,
and statistics calculation functions.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import defaultdict
from scorecard_generator.models import Player, Team, Innings, Partnership, get_current_phase, CRICKET_FORMATS
from scorecard_generator.match_stats import (
    calculate_phase_breakdown, calculate_innings_summary,
    get_top_batters, get_top_bowlers, format_batter_breakdown,
    format_partnership
)


def test_phase_detection():
    """Test get_current_phase function for different formats."""
    print("Testing phase detection...")
    
    # T20 format
    t20_config = CRICKET_FORMATS['T20']
    assert get_current_phase(0, t20_config) == 'powerplay'
    assert get_current_phase(5, t20_config) == 'powerplay'
    assert get_current_phase(6, t20_config) == 'middle'
    assert get_current_phase(15, t20_config) == 'middle'
    assert get_current_phase(16, t20_config) == 'final'
    assert get_current_phase(19, t20_config) == 'final'
    
    # ODI format
    odi_config = CRICKET_FORMATS['ODI']
    assert get_current_phase(0, odi_config) == 'powerplay'
    assert get_current_phase(9, odi_config) == 'powerplay'
    assert get_current_phase(10, odi_config) == 'middle'
    assert get_current_phase(39, odi_config) == 'middle'
    assert get_current_phase(40, odi_config) == 'final'
    assert get_current_phase(49, odi_config) == 'final'
    
    # First Class format (no phases)
    test_config = CRICKET_FORMATS['TEST']
    assert get_current_phase(0, test_config) is None
    assert get_current_phase(50, test_config) is None
    
    print("  ✓ Phase detection tests passed")


def test_partnership_creation():
    """Test Partnership object creation and tracking."""
    print("Testing partnership creation...")
    
    # Create mock players
    player1 = Player(1, "Player One")
    player2 = Player(2, "Player Two")
    
    # Create partnership
    partnership = Partnership(player1, player2, wicket_number=1, start_score=0)
    assert partnership.batter1 == player1
    assert partnership.batter2 == player2
    assert partnership.wicket_number == 1
    assert partnership.start_score == 0
    assert partnership.runs == 0
    assert partnership.balls == 0
    
    # Simulate partnership progression
    partnership.runs = 45
    partnership.balls = 38
    partnership.batter1_runs = 25
    partnership.batter1_balls = 20
    partnership.batter2_runs = 20
    partnership.batter2_balls = 18
    partnership.end_score = 45
    
    assert partnership.runs == 45
    assert partnership.batter1_runs + partnership.batter2_runs == 45
    
    print("  ✓ Partnership creation tests passed")


def test_scoring_distribution():
    """Test scoring distribution tracking in Player batting dict."""
    print("Testing scoring distribution...")
    
    player = Player(1, "Test Batter")
    
    # Simulate scoring
    scoring_dist = player.batting['scoring_distribution']
    scoring_dist[0] = 10  # 10 dot balls
    scoring_dist[1] = 15  # 15 singles
    scoring_dist[2] = 5   # 5 twos
    scoring_dist[4] = 8   # 8 fours
    scoring_dist[6] = 3   # 3 sixes
    
    # Verify
    assert scoring_dist[0] == 10
    assert scoring_dist[1] == 15
    assert scoring_dist[4] == 8
    assert scoring_dist[6] == 3
    
    # Test format_batter_breakdown
    breakdown = format_batter_breakdown(player)
    assert breakdown['0s'] == 10
    assert breakdown['1s'] == 15
    assert breakdown['2s'] == 5
    assert breakdown['3s'] == 0
    assert breakdown['4s'] == 8
    assert breakdown['6s'] == 3
    
    print("  ✓ Scoring distribution tests passed")


def test_innings_phase_stats():
    """Test phase statistics tracking in Innings."""
    print("Testing innings phase stats...")
    
    team1 = Team("Team A")
    team2 = Team("Team B")
    innings = Innings(team1, team2)
    
    # Verify phase_stats initialized
    assert 'powerplay' in innings.phase_stats
    assert 'middle' in innings.phase_stats
    assert 'final' in innings.phase_stats
    
    # Simulate phase stats
    innings.phase_stats['powerplay']['runs'] = 55
    innings.phase_stats['powerplay']['wickets'] = 1
    innings.phase_stats['powerplay']['balls'] = 36
    
    innings.phase_stats['middle']['runs'] = 120
    innings.phase_stats['middle']['wickets'] = 4
    innings.phase_stats['middle']['balls'] = 60
    
    # Verify
    assert innings.phase_stats['powerplay']['runs'] == 55
    assert innings.phase_stats['middle']['wickets'] == 4
    
    print("  ✓ Innings phase stats tests passed")


def test_calculate_phase_breakdown():
    """Test calculate_phase_breakdown function."""
    print("Testing phase breakdown calculation...")
    
    team1 = Team("Team A")
    team2 = Team("Team B")
    innings = Innings(team1, team2)
    
    # Set some phase stats
    innings.phase_stats['powerplay']['runs'] = 48
    innings.phase_stats['powerplay']['wickets'] = 2
    innings.phase_stats['powerplay']['balls'] = 36
    
    innings.phase_stats['middle']['runs'] = 95
    innings.phase_stats['middle']['wickets'] = 3
    innings.phase_stats['middle']['balls'] = 60
    
    t20_config = CRICKET_FORMATS['T20']
    breakdown = calculate_phase_breakdown(innings, t20_config)
    
    assert breakdown is not None
    assert 'powerplay' in breakdown
    assert breakdown['powerplay']['runs'] == 48
    assert breakdown['powerplay']['wickets'] == 2
    assert breakdown['powerplay']['overs'] == "6"  # 36 balls = 6 overs exactly
    
    # Test with First Class (should return None)
    test_config = CRICKET_FORMATS['TEST']
    breakdown_test = calculate_phase_breakdown(innings, test_config)
    assert breakdown_test is None
    
    print("  ✓ Phase breakdown calculation tests passed")


def test_innings_summary():
    """Test calculate_innings_summary function."""
    print("Testing innings summary calculation...")
    
    team1 = Team("Team A")
    team2 = Team("Team B")
    
    # Add players
    for i in range(1, 12):
        team1.add_player(Player(i, f"Player {i}"))
        team1.order.append(i)
    
    innings = Innings(team1, team2)
    
    # Simulate some batting stats
    team1.players[1].batting['runs'] = 45
    team1.players[1].batting['balls'] = 30
    team1.players[1].batting['4s'] = 5
    team1.players[1].batting['6s'] = 2
    team1.players[1].batted = True
    
    team1.players[2].batting['runs'] = 30
    team1.players[2].batting['balls'] = 25
    team1.players[2].batting['4s'] = 3
    team1.players[2].batting['6s'] = 1
    team1.players[2].batted = True
    
    # Simulate extras
    innings.extras['wides'] = 5
    innings.extras['no balls'] = 2
    
    # Calculate summary
    summary = calculate_innings_summary(innings)
    
    assert 'total_runs' in summary
    assert 'wickets' in summary
    assert 'sixes' in summary
    assert 'fours' in summary
    assert summary['sixes'] == 3  # 2 + 1
    assert summary['fours'] == 8  # 5 + 3
    assert summary['extras'] == 7  # 5 + 2
    
    print("  ✓ Innings summary calculation tests passed")


def test_top_performers():
    """Test get_top_batters and get_top_bowlers functions."""
    print("Testing top performers selection...")
    
    # Create mock teams and innings
    team1 = Team("Team A")
    team2 = Team("Team B")
    
    for i in range(1, 12):
        team1.add_player(Player(i, f"Batter {i}"))
        team1.order.append(i)
        team2.add_player(Player(i, f"Bowler {i}"))
        team2.order.append(i)
    
    innings1 = Innings(team1, team2)
    innings2 = Innings(team2, team1)
    
    # Set batting stats
    team1.players[1].batting['runs'] = 85
    team1.players[1].batting['balls'] = 55
    team1.players[1].batted = True
    
    team1.players[2].batting['runs'] = 45
    team1.players[2].batting['balls'] = 30
    team1.players[2].batted = True
    
    team2.players[1].batting['runs'] = 60
    team2.players[1].batting['balls'] = 40
    team2.players[1].batted = True
    
    # Get top batters
    top_batters = get_top_batters(innings1, innings2, n=2)
    assert len(top_batters) == 2
    assert top_batters[0][0].batting['runs'] == 85  # Highest scorer first
    
    # Set bowling stats
    team2.players[1].bowling['wickets'] = 3
    team2.players[1].bowling['runs'] = 25
    team2.players[1].bowling['balls'] = 24
    team2.players[1].bowled = True
    
    team2.players[2].bowling['wickets'] = 2
    team2.players[2].bowling['runs'] = 30
    team2.players[2].bowling['balls'] = 24
    team2.players[2].bowled = True
    
    # Get top bowlers
    top_bowlers = get_top_bowlers(innings1, innings2, n=2)
    assert len(top_bowlers) == 2
    assert top_bowlers[0][0].bowling['wickets'] == 3  # Most wickets first
    
    print("  ✓ Top performers selection tests passed")


def test_format_partnership():
    """Test format_partnership function."""
    print("Testing partnership formatting...")
    
    team = Team("Test Team")
    player1 = Player(1, "Player One")
    player2 = Player(2, "Player Two")
    team.add_player(player1)
    team.add_player(player2)
    
    partnership = Partnership(player1, player2, wicket_number=2, start_score=30)
    partnership.runs = 55
    partnership.balls = 42
    partnership.batter1_runs = 30
    partnership.batter1_balls = 25
    partnership.batter2_runs = 25
    partnership.batter2_balls = 17
    partnership.end_score = 85
    
    formatted = format_partnership(partnership, team)
    
    assert formatted['wicket_number'] == 2
    assert formatted['total_runs'] == 55
    assert formatted['total_balls'] == 42
    assert formatted['batter1_name'] == "Player One"
    assert formatted['batter1_runs'] == 30
    assert formatted['batter2_name'] == "Player Two"
    assert formatted['batter2_runs'] == 25
    
    print("  ✓ Partnership formatting tests passed")


def run_all_tests():
    """Run all match stats tests."""
    print("\n" + "="*70)
    print("RUNNING MATCH STATS TESTS")
    print("="*70 + "\n")
    
    try:
        test_phase_detection()
        test_partnership_creation()
        test_scoring_distribution()
        test_innings_phase_stats()
        test_calculate_phase_breakdown()
        test_innings_summary()
        test_top_performers()
        test_format_partnership()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
