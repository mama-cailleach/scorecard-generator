#!/usr/bin/env python
"""Test that wicket data is properly extracted for ball-by-ball export"""

from scorecard_generator.models import Innings, BallEvent, Team, Player
from scorecard_generator.scorecard_export import export_ball_by_ball_csv

# Create test teams
team1 = Team("England")
team2 = Team("Australia")

for i in range(1, 4):
    p1 = Player(i, f"England Player {i}")
    p2 = Player(i, f"Australia Player {i}")
    team1.players[i] = p1
    team2.players[i] = p2
    team1.order.append(i)
    team2.order.append(i)

# Create test innings with various dismissal types
innings = Innings(team1, team2)

# Normal run
innings.balls.append(BallEvent(0, 1, "3 Bowler C", "1 Batter A", 1, "normal", []))

# Bowled
innings.balls.append(BallEvent(0, 2, "3 Bowler C", "2 Batter B", 0, "wicket", ["3 Bowler C"]))

# Caught (tuple format)
innings.balls.append(BallEvent(0, 3, "3 Bowler C", "3 Batter C", 0, "wicket", 
    [("2 Fielder B", None, False)]))

# Caught & Bowled (tuple format)
innings.balls.append(BallEvent(1, 1, "2 Bowler B", "1 Batter A", 0, "wicket", 
    [("2 Bowler B", None, True)]))

# LBW
innings.balls.append(BallEvent(1, 2, "2 Bowler B", "2 Batter B", 0, "wicket", 
    ["lbw", None]))

# Run out
innings.balls.append(BallEvent(1, 3, "2 Bowler B", "3 Batter C", 0, "run out", []))

innings2 = Innings(team2, team1)
innings2.balls.append(BallEvent(0, 1, "1 Bowler A", "1 Batter A", 2, "normal", []))

# Export and check
try:
    export_ball_by_ball_csv("scorecard_generator/exports/test_wickets.csv", team1, team2, innings, innings2)
    
    # Read and display
    with open("scorecard_generator/exports/test_wickets.csv", "r") as f:
        lines = f.readlines()
    
    print("✓ Export successful!\n")
    print("Ball-by-ball data with wickets:")
    print("-" * 120)
    
    # Print header
    print(lines[0].rstrip())
    
    # Print data lines
    for i, line in enumerate(lines[1:], 1):
        print(f"Ball {i}: {line.rstrip()}")
        # Extract and highlight wicket info
        parts = line.rstrip().split(',')
        wicket_type = parts[18] if len(parts) > 18 else ''
        player_dismissed = parts[19] if len(parts) > 19 else ''
        if wicket_type:
            print(f"  → WICKET: {player_dismissed} ({wicket_type})")
    
except Exception as e:
    print(f"✗ Export failed: {e}")
    import traceback
    traceback.print_exc()
