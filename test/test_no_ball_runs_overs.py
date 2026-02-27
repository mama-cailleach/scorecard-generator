"""
Test to verify overs calculation with no_ball_runs and other variants
Bug: When no ball with runs happens (event_type="no ball_runs"), it was being
counted as a legal delivery instead of excluded.
"""

import sys
sys.path.insert(0, 'scorecard_generator')

from models import Player, Team, Innings, BallEvent, BALLS_PER_OVER


def test_no_ball_with_runs():
    """Test that no_ball_runs is correctly excluded from legal balls count"""
    batting_team = Team("Batting")
    batting_team.add_player(Player(1, "Batter1"))
    batting_team.add_player(Player(2, "Batter2"))
    
    bowling_team = Team("Bowling")
    bowling_team.add_player(Player(1, "Bowler1"))
    
    innings = Innings(batting_team, bowling_team)
    innings.bowler_overs[1] = [0]  # Bowler 1 bowled over 0
    
    # Create 6 normal deliveries + 1 no ball with runs (should not count)
    batter = batting_team.players[1]
    bowler = bowling_team.players[1]
    
    # 5 normal deliveries (6 legal balls total = 1 over)
    for i in range(5):
        innings.add_ball(BallEvent(over=0, ball=i+1, bowler=bowler, batter=batter, runs=1, event="normal"))
    
    # 1 no ball with 1 run (should NOT be counted as legal delivery)
    innings.add_ball(BallEvent(over=0, ball=6, bowler=bowler, batter=batter, runs=2, event="no ball_runs"))
    
    # Total: 5 normal (legal) + 1 no ball_runs (not legal) = 5 legal balls = 0.5 overs
    # But we need 6 legal balls for 1.0 overs
    # Add one more normal delivery
    innings.add_ball(BallEvent(over=0, ball=6, bowler=bowler, batter=batter, runs=1, event="normal"))
    
    total_runs, wickets, overs, rr = innings.get_score()
    
    print(f"\nTest: No Ball With Runs")
    print(f"Expected overs: 1.0")
    print(f"Calculated overs: {overs:.1f}")
    
    assert abs(overs - 1.0) < 0.01, f"Expected 1.0 overs, got {overs}"
    print("✓ PASSED: No ball runs correctly excluded from overs count")


def test_wide_boundary():
    """Test that wide_boundary is correctly excluded from legal balls count"""
    batting_team = Team("Batting")
    batting_team.add_player(Player(1, "Batter1"))
    batting_team.add_player(Player(2, "Batter2"))
    
    bowling_team = Team("Bowling")
    bowling_team.add_player(Player(1, "Bowler1"))
    
    innings = Innings(batting_team, bowling_team)
    innings.bowler_overs[1] = [0]  # Bowler 1 bowled over 0
    
    batter = batting_team.players[1]
    bowler = bowling_team.players[1]
    
    # 5 normal deliveries
    for i in range(5):
        innings.add_ball(BallEvent(over=0, ball=i+1, bowler=bowler, batter=batter, runs=1, event="normal"))
    
    # 1 wide with boundary (4 runs) - should NOT be counted
    innings.add_ball(BallEvent(over= 0, ball=6, bowler=bowler, batter=batter, runs=4, event="wide_boundary"))
    
    # 1 more normal delivery to complete the over
    innings.add_ball(BallEvent(over=0, ball=6, bowler=bowler, batter=batter, runs=1, event="normal"))
    
    total_runs, wickets, overs, rr = innings.get_score()
    
    print(f"\nTest: Wide Boundary")
    print(f"Expected overs: 1.0")
    print(f"Calculated overs: {overs:.1f}")
    
    assert abs(overs - 1.0) < 0.01, f"Expected 1.0 overs, got {overs}"
    print("✓ PASSED: Wide boundary correctly excluded from overs count")


def test_wide_with_byes():
    """Test that wide_bye is correctly excluded"""
    batting_team = Team("Batting")
    batting_team.add_player(Player(1, "Batter1"))
    batting_team.add_player(Player(2, "Batter2"))
    
    bowling_team = Team("Bowling")
    bowling_team.add_player(Player(1, "Bowler1"))
    
    innings = Innings(batting_team, bowling_team)
    innings.bowler_overs[1] = [0]
    
    batter = batting_team.players[1]
    bowler = bowling_team.players[1]
    
    # 5 normal + 1 wide_bye + 1 normal = 6 legal
    for i in range(5):
        innings.add_ball(BallEvent(over=0, ball=i+1, bowler=bowler, batter=batter, runs=1, event="normal"))
    
    innings.add_ball(BallEvent(over=0, ball=6, bowler=bowler, batter=batter, runs=2, event="wide_bye"))
    innings.add_ball(BallEvent(over=0, ball=6, bowler=bowler, batter=batter, runs=1, event="normal"))
    
    total_runs, wickets, overs, rr = innings.get_score()
    
    print(f"\nTest: Wide With Byes")
    print(f"Expected overs: 1.0")
    print(f"Calculated overs: {overs:.1f}")
    
    assert abs(overs - 1.0) < 0.01, f"Expected 1.0 overs, got {overs}"
    print("✓ PASSED: Wide with byes correctly excluded from overs count")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING OVERS CALCULATION FIX - WIDE/NO BALL VARIANTS")
    print("="*70)
    
    test_no_ball_with_runs()
    test_wide_boundary()
    test_wide_with_byes()
    
    print("\n" + "="*70)
    print("✅ ALL OVERS CALCULATION TESTS PASSED")
    print("="*70 + "\n")
