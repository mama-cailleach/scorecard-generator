"""
Test to verify scorecard formatting for reports
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scorecard_generator.models import Player, Team, Innings
from scorecard_generator.match_stats import format_scorecard_data


def test_scorecard_formatting():
    """Test that format_scorecard_data produces correct structure"""
    
    # Create teams
    batting_team = Team("Australia")
    batting_team.add_player(Player(1, "David Warner"))
    batting_team.add_player(Player(2, "Travis Head"))
    batting_team.add_player(Player(3, "Steve Smith"))
    batting_team.order = [1, 2, 3]
    batting_team.captain_number = None
    batting_team.wicketkeeper_number = None
    
    bowling_team = Team("England")
    bowling_team.add_player(Player(1, "Mark Wood"))
    
    innings = Innings(batting_team, bowling_team)
    
    # Simulate some batting
    batter1 = batting_team.players[1]
    batter1.batted = True
    batter1.batting['runs'] = 45
    batter1.batting['balls'] = 30
    batter1.batting['4s'] = 4
    batter1.batting['6s'] = 2
    batter1.batting['dismissal'] = 'b Wood'
    
    batter2 = batting_team.players[2]
    batter2.batted = True
    batter2.batting['runs'] = 15
    batter2.batting['balls'] = 20
    batter2.batting['4s'] = 1
    batter2.batting['6s'] = 0
    batter2.batting['dismissal'] = 'not out'
    
    # Extras
    innings.extras['wides'] = 3
    innings.extras['byes'] = 2
    
    # Fall of wickets
    innings.fall_of_wickets.append((45, "David Warner", "Wood", 5.2))
    
    # Bowling
    bowler = bowling_team.players[1]
    bowler.bowled = True
    bowler.bowling['balls'] = 36
    bowler.bowling['runs'] = 65
    bowler.bowling['wickets'] = 1
    bowler.bowling['dots'] = 15
    bowler.bowling['maidens'] = 0
    bowler.bowling['wides'] = 3
    bowler.bowling['noballs'] = 0
    bowler.bowling['4s'] = 5
    bowler.bowling['6s'] = 2
    
    # Format scorecard
    scorecard = format_scorecard_data(innings)
    
    # Verify structure
    assert scorecard['team_name'] == 'Australia', "Team name incorrect"
    assert len(scorecard['batters']) == 2, "Should have 2 batters"
    assert scorecard['batters'][0]['name'] == 'David Warner', "First batter name incorrect"
    assert scorecard['batters'][0]['runs'] == 45, "First batter runs incorrect"
    assert scorecard['batters'][1]['not_out'] == '*', "Second batter should be not out"
    assert scorecard['extras'] == 5, "Extras total incorrect"
    assert 'b 2' in scorecard['extras_detail'], "Extras detail should include byes"
    assert 'w 3' in scorecard['extras_detail'], "Extras detail should include wides"
    assert len(scorecard['did_not_bat']) == 1, "Should have 1 player who didn't bat"
    assert scorecard['did_not_bat'][0] == 'Steve Smith', "Did not bat list incorrect"
    assert len(scorecard['fall_of_wickets']) == 1, "Should have 1 fall of wicket"
    assert scorecard['fall_of_wickets'][0]['batsman'] == 'David Warner', "Fall of wicket batsman incorrect"
    assert len(scorecard['bowlers']) == 1, "Should have 1 bowler"
    assert scorecard['bowlers'][0]['name'] == 'Mark Wood', "Bowler name incorrect"
    assert scorecard['bowlers'][0]['overs'] == '6.0', "Bowler overs incorrect"
    assert scorecard['bowlers'][0]['wickets'] == 1, "Bowler wickets incorrect"
    assert scorecard['bowling_team'] == 'England', "Bowling team name incorrect"
    
    print("✓ Scorecard formatting test PASSED")
    print(f"  - Batters formatted: {len(scorecard['batters'])}")
    print(f"  - Bowlers formatted: {len(scorecard['bowlers'])}")
    print(f"  - Fall of wickets: {len(scorecard['fall_of_wickets'])}")
    print(f"  - Did not bat: {len(scorecard['did_not_bat'])}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING SCORECARD FORMATTING FOR REPORTS")
    print("="*70 + "\n")
    
    test_scorecard_formatting()
    
    print("\n" + "="*70)
    print("✅ ALL SCORECARD FORMATTING TESTS PASSED")
    print("="*70 + "\n")
