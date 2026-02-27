import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scorecard_generator.models import Player, Team, Innings, Partnership
from scorecard_generator.game_logic import process_ball_event
from scorecard_generator.match_stats import format_scorecard_data


def make_teams():
    batting = Team("Bat")
    for i, name in [(1, "A"), (2, "B"), (3, "C")]:
        batting.add_player(Player(i, name))
    batting.order = [1, 2, 3]

    bowling = Team("Bowl")
    bowling.add_player(Player(1, "Bowler"))
    bowling.order = [1]
    bowling.bowler_order = [1]
    return batting, bowling


def test_partnership_attribution_uses_player_identity():
    batting, bowling = make_teams()
    innings = Innings(batting, bowling)
    striker = batting.players[1]
    non_striker = batting.players[2]
    bowler = bowling.players[1]

    innings.current_partnership = Partnership(striker, non_striker, 1, 0)
    current_batters = [striker, non_striker]

    # Ball 1: striker A scores 1, strike rotates
    wickets, over_runs, legal_balls, ball_num, current_batters, _, _ = process_ball_event(
        "normal", 1, [], False, innings, bowler, current_batters[0], current_batters,
        0, 0, 1, batting, 0, 0, 1, [3], {'name': 'T20', 'max_overs': 20, 'max_bowler_overs': 4, 'balls_per_over': 6}
    )

    # Ball 2: now striker is B and scores 2
    wickets, over_runs, legal_balls, ball_num, current_batters, _, _ = process_ball_event(
        "normal", 2, [], False, innings, bowler, current_batters[0], current_batters,
        wickets, 0, ball_num, batting, over_runs, legal_balls, ball_num, [3], {'name': 'T20', 'max_overs': 20, 'max_bowler_overs': 4, 'balls_per_over': 6}
    )

    p = innings.current_partnership
    assert p.batter1.name == "A"
    assert p.batter2.name == "B"
    assert p.batter1_runs == 1, f"Expected A to have 1, got {p.batter1_runs}"
    assert p.batter2_runs == 2, f"Expected B to have 2, got {p.batter2_runs}"


def test_non_striker_not_faced_shows_in_scorecard():
    batting, bowling = make_teams()
    innings = Innings(batting, bowling)

    # A and B are currently at crease, only A has faced
    a = batting.players[1]
    b = batting.players[2]
    a.batted = True
    b.batted = True
    a.batting['runs'] = 10
    a.batting['balls'] = 6
    innings.current_batters = [a, b]

    score = format_scorecard_data(innings)
    names = [x['name'] for x in score['batters']]
    assert "B" in names, "Non-striker who never faced should appear as not out 0*(0)"
    b_row = next(x for x in score['batters'] if x['name'] == "B")
    assert b_row['runs'] == 0 and b_row['balls'] == 0 and b_row['not_out'] == "*"


if __name__ == "__main__":
    test_partnership_attribution_uses_player_identity()
    test_non_striker_not_faced_shows_in_scorecard()
    print("ok")
