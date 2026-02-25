#!/usr/bin/env python3
"""
Test case simulating the exact bug scenario from the report:
Expected: Total: 3.4 Ov (RR: 5.10) 17/10
Observed: Total: 3.2 Ov (RR: 5.10) 17/10
"""

from scorecard_generator.models import Player, Team, Innings, BallEvent

print("=" * 70)
print("BUG SCENARIO TEST: Missing 2 balls in overs display")
print("=" * 70)

# Create test teams (England batting vs Australia bowling)
batting_team = Team("England")
bowling_team = Team("Australia")

# Add batters
batters = [
    (16, "Jos Buttler"),
    (17, "Jonny Bairstow"),
    (1, "Moeen Ali"),
    (8, "Ben Stokes"),
    (33, "Joe Root"),
    (11, "Liam Livingstone"),
    (15, "Sam Curran"),
    (88, "Harry Brook"),
    (30, "Reece Topley"),
    (99, "Chris Jordan"),
    (44, "Mark Wood"),
]

for num, name in batters:
    batting_team.add_player(Player(num, name))

batting_team.order = [num for num, _ in batters]

# Add bowlers
bowlers = [
    (1, "Mitch Starc"),
    (2, "Adam Zampa"),
    (3, "Josh Hazlewood"),
]

for num, name in bowlers:
    bowling_team.add_player(Player(num, name))

bowling_team.order = [num for num, _ in bowlers]

# Create innings
innings = Innings(batting_team, bowling_team)

# Set up bowler overs as in the actual match
# Starc bowled over 0
# Zampa bowled over 1
# Hazlewood bowled overs 2 and 3
innings.bowler_overs[1].append(0)  # Starc over 0
innings.bowler_overs[2].append(1)  # Zampa over 1
innings.bowler_overs[3].extend([2, 3])  # Hazlewood overs 2 and 3

print("\nBowler overs setup:")
print(f"  Mitch Starc (1): {innings.bowler_overs[1]} -> 0.4 overs")
print(f"  Adam Zampa (2): {innings.bowler_overs[2]} -> 1.0 overs")
print(f"  Josh Hazlewood (3): {innings.bowler_overs[3]} -> 2.0 overs")
print(f"  TOTAL: 0.4 + 1.0 + 2.0 = 3.4 overs")

# Simulate the balls from the actual match
print("\nSimulating ball-by-ball events...")

# Over 0 (Starc): 4 balls
print("  Over 0 (Starc): 4 balls")
for ball in range(4):
    innings.add_ball(BallEvent(over=0, ball=ball+1, bowler=bowling_team.players[1], 
                               batter=batting_team.players[batters[0][0]], 
                               runs=0, event='runs'))

# Over 1 (Zampa): 6 balls (complete)
print("  Over 1 (Zampa): 6 balls (complete)")
for ball in range(6):
    innings.add_ball(BallEvent(over=1, ball=ball+1, bowler=bowling_team.players[2], 
                               batter=batting_team.players[batters[0][0]], 
                               runs=1, event='runs'))

# Over 2 (Hazlewood): 6 balls (complete)
print("  Over 2 (Hazlewood): 6 balls (complete)")
for ball in range(6):
    innings.add_ball(BallEvent(over=2, ball=ball+1, bowler=bowling_team.players[3], 
                               batter=batting_team.players[batters[0][0]], 
                               runs=0, event='runs'))

# Over 3 (Hazlewood): 4 balls (incomplete - all out)
print("  Over 3 (Hazlewood): 4 balls (incomplete - ends at 3.4)")
for ball in range(4):
    innings.add_ball(BallEvent(over=3, ball=ball+1, bowler=bowling_team.players[3], 
                               batter=batting_team.players[batters[0][0]], 
                               runs=0, event='runs'))

# Simulate fall of wickets
innings.fall_of_wickets = [
    (0, "Jos Buttler", "Hazlewood", 0.1),
    (0, "Jonny Bairstow", "Hazlewood", 0.2),
    (4, "Ben Stokes", "Zampa", 1.1),
    (4, "Joe Root", "Zampa", 1.2),
    (13, "Moeen Ali", "Zampa", 2.1),
    (13, "Liam Livingstone", "Starc", 2.2),
    (13, "Harry Brook", "Hazlewood", 2.3),
    (13, "Reece Topley", "Hazlewood", 2.4),
    (14, "Sam Curran", "Hazlewood", 2.6),
    (17, "Mark Wood", "Starc", 3.4),
]

# Add extras
innings.extras['nb'] = 1

# Get score
total_runs, wickets, overs, rr = innings.get_score()

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

print(f"\nTotal Runs: {total_runs}")
print(f"Wickets: {wickets}")
print(f"Overs: {overs:.1f}")
print(f"Run Rate: {rr:.2f}")

print(f"\n{'='*70}")
print("SCORECARD TOTAL LINE:")
print(f"Total: {overs:.1f} Ov (RR: {rr:.2f}) {total_runs}/{wickets}")
print(f"{'='*70}")

print("\nExpected: Total: 3.4 Ov (RR: 5.10) 17/10")
print(f"Observed: Total: {overs:.1f} Ov (RR: {rr:.2f}) {total_runs}/{wickets}")

if abs(overs - 3.4) < 0.01:
    print("\n✅ BUG FIXED! The overs calculation is now correct (3.4)")
    print("   (Runs and wickets differ from actual due to test data being simulated)")
else:
    print(f"\n❌ Issue persists. Overs: {overs:.1f} (expected 3.4)")

print("\n" + "=" * 70)
print("Calculation details:")
print(f"  Max over bowled: 3")
print(f"  Balls in last over (over 3): 4")
print(f"  Total overs: 3 + 4/10 = 3.4 ✓")
print("=" * 70)
