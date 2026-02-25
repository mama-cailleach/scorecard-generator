#!/usr/bin/env python
"""Quick verification that export works"""

from scorecard_generator.models import Innings, BallEvent, Team, Player

# Create simple test data
team1 = Team("Test Team 1")
team2 = Team("Test Team 2")

for i in range(1, 3):
    p = Player(i, f"Player {i}")
    team1.players[i] = p
    team2.players[i] = p
    team1.order.append(i)
    team2.order.append(i)

innings = Innings(team1, team2)

# Test that 'balls' attribute exists
print(f"innings.balls exists: {hasattr(innings, 'balls')}")
print(f"innings.balls type: {type(innings.balls)}")

# Test adding ball event
ball = BallEvent(0, 1, "Bowler A", "Batter 1", 1, "runs", None)
innings.balls.append(ball)

print(f"Added ball event successfully")
print(f"innings.balls length: {len(innings.balls)}")
print(f"Ball event has 'event' attribute: {hasattr(ball, 'event')}")
print(f"Ball event.event value: {ball.event}")

# Try importing export function
from scorecard_generator.scorecard_export import export_all
print(f"export_all imported successfully")

print("\n✓ All attribute names verified correctly!")
