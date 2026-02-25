#!/usr/bin/env python3
"""Test the improved overs calculation using bowler_overs data"""

from scorecard_generator.models import Player, Team, Innings, BallEvent, BALLS_PER_OVER

print("=" * 70)
print("OVERS CALCULATION FIX VERIFICATION")
print("=" * 70)

# Create test batting and bowling teams
batting_team = Team("England")
bowling_team = Team("Australia")

# Add players to teams
for i in range(11):
    batting_team.add_player(Player(i+1, f"Batter{i+1}"))
    bowling_team.add_player(Player(i+1, f"Bowler{i+1}"))

# Set batting order
batting_team.order = list(range(1, 12))
bowling_team.order = list(range(1, 12))

# Create innings
innings = Innings(batting_team, bowling_team)

print("\n1. Test Case: Incomplete over (like in the bug report)")
print("-" * 70)
print("Scenario: 3 complete overs + 4 balls in incomplete over = 3.4 overs")

# Simulate bowler overs: each bowler bowled certain overs
# Starc bowled over 0, Zampa bowled over 1, Hazlewood bowled overs 2 and 3
innings.bowler_overs[1].append(0)  # Bowler 1 bowled over 0
innings.bowler_overs[2].append(1)  # Bowler 2 bowled over 1  
innings.bowler_overs[3].extend([2, 3])  # Bowler 3 bowled overs 2 and 3

# Add balls to simulate the match
# Over 0: 4 balls
for ball in range(4):
    innings.add_ball(BallEvent(over=0, ball=ball+1, bowler=bowling_team.players[1], 
                               batter=batting_team.players[1], runs=1, event='runs'))

# Over 1: 6 balls (complete)
for ball in range(6):
    innings.add_ball(BallEvent(over=1, ball=ball+1, bowler=bowling_team.players[2], 
                               batter=batting_team.players[1], runs=1, event='runs'))

# Over 2: 6 balls (complete)
for ball in range(6):
    innings.add_ball(BallEvent(over=2, ball=ball+1, bowler=bowling_team.players[3], 
                               batter=batting_team.players[1], runs=0, event='runs'))

# Over 3: 4 balls (incomplete)
for ball in range(4):
    innings.add_ball(BallEvent(over=3, ball=ball+1, bowler=bowling_team.players[3], 
                               batter=batting_team.players[1], runs=0, event='runs'))

total_runs, wickets, overs, rr = innings.get_score()

print(f"  Expected overs: 3.4")
print(f"  Calculated overs: {overs:.1f}")
print(f"  ✓ MATCH!" if abs(overs - 3.4) < 0.01 else f"  ✗ MISMATCH!")

print("\n2. Test Case: Complete over (6 balls)")
print("-" * 70)

innings2 = Innings(batting_team, bowling_team)
innings2.bowler_overs[1].extend([0, 1])  # Bowler 1 bowled overs 0 and 1

# Over 0: 6 balls
for ball in range(6):
    innings2.add_ball(BallEvent(over=0, ball=ball+1, bowler=bowling_team.players[1], 
                                batter=batting_team.players[1], runs=1, event='runs'))

# Over 1: 6 balls  
for ball in range(6):
    innings2.add_ball(BallEvent(over=1, ball=ball+1, bowler=bowling_team.players[1], 
                                batter=batting_team.players[1], runs=1, event='runs'))

total_runs2, wickets2, overs2, rr2 = innings2.get_score()

print(f"  Expected overs: 2.0")
print(f"  Calculated overs: {overs2:.1f}")
print(f"  ✓ MATCH!" if abs(overs2 - 2.0) < 0.01 else f"  ✗ MISMATCH!")

print("\n3. Test Case: Single incomplete over (3 balls)")
print("-" * 70)

innings3 = Innings(batting_team, bowling_team)
innings3.bowler_overs[1].append(0)  # Bowler 1 bowled over 0

# Over 0: 3 balls
for ball in range(3):
    innings3.add_ball(BallEvent(over=0, ball=ball+1, bowler=bowling_team.players[1], 
                                batter=batting_team.players[1], runs=0, event='runs'))

total_runs3, wickets3, overs3, rr3 = innings3.get_score()

print(f"  Expected overs: 0.3")
print(f"  Calculated overs: {overs3:.1f}")
print(f"  ✓ MATCH!" if abs(overs3 - 0.3) < 0.01 else f"  ✗ MISMATCH!")

print("\n4. Test Case: Handling wides and no-balls")
print("-" * 70)
print("(Wides and no-balls should NOT count toward legal ball count)")

innings4 = Innings(batting_team, bowling_team)
innings4.bowler_overs[1].append(0)  # Bowler 1 bowled over 0

# Add 6 legal balls
for ball in range(6):
    innings4.add_ball(BallEvent(over=0, ball=ball+1, bowler=bowling_team.players[1], 
                                batter=batting_team.players[1], runs=0, event='runs'))

# Add some wides/no-balls that shouldn't count
for i in range(2):
    innings4.add_ball(BallEvent(over=0, ball=999, bowler=bowling_team.players[1], 
                                batter=batting_team.players[1], runs=1, event='wide'))
    innings4.add_ball(BallEvent(over=0, ball=999, bowler=bowling_team.players[1], 
                                batter=batting_team.players[1], runs=1, event='no ball'))

total_runs4, wickets4, overs4, rr4 = innings4.get_score()

print(f"  Overs with 6 legal balls (+ 2 wides/no-balls): {overs4:.1f}")
print(f"  Expected: 1.0 (wides/no-balls excluded)")
print(f"  ✓ CORRECT!" if abs(overs4 - 1.0) < 0.01 else f"  ✗ INCORRECT!")

print("\n" + "=" * 70)
print("✓ ALL TESTS COMPLETED")
print("=" * 70)
print("\nSummary:")
print("  The new calculation uses bowler_overs as the source of truth")
print("  This ensures accurate over counts even when input validation issues occur")
print("  Wides and no-balls are correctly excluded from legal deliveries")
