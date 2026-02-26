#!/usr/bin/env python3
"""Regression test for Total line overs after run out in the over."""

import io
from contextlib import redirect_stdout

from scorecard_generator.models import Player, Team, Innings, BallEvent
from scorecard_generator.scorecard import print_batting_scorecard


def create_team(name):
    team = Team(name)
    for i in range(1, 12):
        team.add_player(Player(i, f"{name} Player {i}"))
    team.order = list(range(1, 12))
    team.bowler_order = list(range(1, 12))
    return team


def test_total_line_overs_after_run_out():
    batting_team = create_team("England")
    bowling_team = create_team("Australia")
    innings = Innings(batting_team, bowling_team)

    # Simulate one over with 6 legal deliveries, including a run out at ball 5.
    # Ball events are legal because they are not wides/no-balls.
    striker = batting_team.players[1]
    bowler = bowling_team.players[1]

    innings.add_ball(BallEvent(0, 1, bowler, striker, 1, "normal"))
    innings.add_ball(BallEvent(0, 2, bowler, striker, 1, "normal"))
    innings.add_ball(BallEvent(0, 3, bowler, striker, 1, "leg bye"))
    innings.add_ball(BallEvent(0, 4, bowler, striker, 6, "normal"))
    innings.add_ball(BallEvent(0, 5, bowler, striker, 2, "run out"))
    innings.add_ball(BallEvent(0, 6, bowler, striker, 6, "normal"))

    # Set batting and extras to match 15/1.
    batting_team.players[1].batting["runs"] = 1
    batting_team.players[2].batting["runs"] = 7
    batting_team.players[3].batting["runs"] = 6
    batting_team.players[2].batting["dismissal"] = "run out"
    innings.extras["leg byes"] = 1
    innings.fall_of_wickets.append((9, "Batter 2", "Bowler 1", 0.5))

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_batting_scorecard(innings)
    output = buffer.getvalue()

    assert "Total: 1 Ov" in output, f"Expected Total line to show 1 Ov. Output was:\n{output}"


if __name__ == "__main__":
    test_total_line_overs_after_run_out()
    print("\n\u2713 Total line overs regression test passed")
