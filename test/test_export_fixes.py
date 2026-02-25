#!/usr/bin/env python
"""Test the fixed export functionality"""

from scorecard_generator.models import Innings, BallEvent, Team, Player
from scorecard_generator.scorecard_export import export_ball_by_ball_csv, extract_player_name

# Test name extraction
print("Testing name extraction:")
print(f"  '16 Jos Buttler' -> '{extract_player_name('16 Jos Buttler')}'")
print(f"  '38 Josh Hazlewood' -> '{extract_player_name('38 Josh Hazlewood')}'")
print(f"  'N/A' -> '{extract_player_name('N/A')}'")

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

# Create test innings with realistic ball events
innings = Innings(team1, team2)

# Add test balls with correct event types from game_logic
# Normal runs
innings.balls.append(BallEvent(0, 1, "38 Josh Hazlewood", "16 Jos Buttler", 1, "normal", []))
# More normal runs
innings.balls.append(BallEvent(0, 2, "38 Josh Hazlewood", "22 Jonny Bairstow", 4, "normal", []))
# Wide
innings.balls.append(BallEvent(0, 3, "38 Josh Hazlewood", "16 Jos Buttler", 1, "wide", []))
# No ball
innings.balls.append(BallEvent(0, 4, "38 Josh Hazlewood", "22 Jonny Bairstow", 0, "no ball", []))
# Bye
innings.balls.append(BallEvent(0, 5, "38 Josh Hazlewood", "16 Jos Buttler", 2, "bye", []))
# Wicket
innings.balls.append(BallEvent(0, 6, "38 Josh Hazlewood", "22 Jonny Bairstow", 0, "wicket", 
    [{'dismissal_type': 'bowled', 'dismissed_player': 'Jonny Bairstow'}]))

innings2 = Innings(team2, team1)
innings2.balls.append(BallEvent(0, 1, "44 Mark Wood", "31 David Warner", 2, "normal", []))

# Try exporting
try:
    export_ball_by_ball_csv("scorecard_generator/exports/test_export.csv", team1, team2, innings, innings2)
    print("\n✓ Export successful!")
    
    # Read and display the exported file
    with open("scorecard_generator/exports/test_export.csv", "r") as f:
        lines = f.readlines()
        print(f"\nExported {len(lines)} lines (including header)")
        print("First 3 lines:")
        for line in lines[:3]:
            print(f"  {line.rstrip()}")
        if len(lines) > 3:
            print(f"Sample data line:\n  {lines[1].rstrip()}")
except Exception as e:
    print(f"✗ Export failed: {e}")
    import traceback
    traceback.print_exc()
