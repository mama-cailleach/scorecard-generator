#!/usr/bin/env python3

import csv
import os
from scorecard_generator.models import Player, Team, Innings, BallEvent
from scorecard_generator.game_logic import process_ball_event
from scorecard_generator.scorecard import print_batting_scorecard, print_bowling_scorecard

def load_team_from_file(filename):
    """Load team from CSV file"""
    team_name = filename.split('_')[0]
    team = Team(team_name)
    file_path = os.path.join('teams', filename)
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            player = Player(row[0], row[1])
            team.add_player(player)
            team.order.append(row[0])
    return team

def simulate_innings(batting_team, bowling_team, target=None, match_data=None):
    """
    Simulate one innings
    
    Args:
        batting_team: Team object for batting side
        bowling_team: Team object for bowling side
        target: Optional run target for second innings
        match_data: Optional list of ball-by-ball data to follow
                   Each ball should be a dict with:
                   {
                       'over': int,
                       'ball': int,
                       'bowler': str,
                       'batter': str,
                       'event_type': str,
                       'runs': int,
                       'fielders': list  # For wickets
                   }
    """
    innings = Innings(batting_team, bowling_team)
    
    # Set up openers
    striker = batting_team.players[batting_team.order[0]]
    non_striker = batting_team.players[batting_team.order[1]]
    current_batters = [striker, non_striker]
    batters_yet = batting_team.order[2:]
    
    # Set up first bowler
    bowler = bowling_team.players[bowling_team.order[0]]
    bowler.bowled = True
    
    wickets = 0
    over = 0
    ball_num = 1
    over_runs = 0
    legal_balls = 0
    ball_number = 1
    
    if match_data:
        # Follow actual match data
        for ball in match_data:
            if wickets >= 10 or (target and innings.get_score()[0] > target):
                break
                
            event_type = ball['event_type']
            runs = ball['runs']
            fielders = ball.get('fielders', [])
            swapped = ball.get('swapped', False)
            
            striker = current_batters[0]
            bowler = bowling_team.players[ball['bowler']]  # Use specified bowler
            
            event = BallEvent(over, ball_num, bowler, striker, runs, event_type, fielders)
            innings.add_ball(event)
            striker.batted = True
            bowler.bowled = True
            
            result = process_ball_event(
                event_type, runs, fielders, swapped, innings, bowler, striker,
                current_batters, wickets, over, ball_num, batting_team,
                over_runs, legal_balls, ball_number, batters_yet
            )
            
            wickets, over_runs, legal_balls, ball_number, current_batters, batters_yet, over_ended_early = result
            
            if legal_balls == 6:
                over += 1
                legal_balls = 0
                if current_batters[0] and current_batters[1]:
                    current_batters.reverse()
    else:
        # Example simulation data - modify this with your preferred events
        test_events = [
            ("normal", 4, [], False),  # Boundary 4
            ("normal", 1, [], True),   # Single
            ("wide", 1, [], False),    # Wide
            ("no ball_runs", 2, [], True),  # No ball + runs
            ("wicket", 0, [("Test Slip", bowler.name, "caught")], False),  # Caught
            ("normal", 6, [], False),  # Boundary 6
            ("leg bye", 1, [], True),  # Leg bye
            ("bowled", 0, [], False),  # Bowled
            ("lbw", 0, [], False),     # LBW
            ("stumped", 0, [(bowling_team.players[bowling_team.order[1]].name, None, False)], False)  # Stumped
        ]
        
        for event_type, runs, fielders, swapped in test_events:
            if wickets >= 10 or (target and innings.get_score()[0] > target):
                break
                
            striker = current_batters[0]
            event = BallEvent(over, ball_num, bowler, striker, runs, event_type, fielders)
            innings.add_ball(event)
            striker.batted = True
            
            result = process_ball_event(
                event_type, runs, fielders, swapped, innings, bowler, striker,
                current_batters, wickets, over, ball_num, batting_team,
                over_runs, legal_balls, ball_number, batters_yet
            )
            
            wickets, over_runs, legal_balls, ball_number, current_batters, batters_yet, over_ended_early = result
            
            if legal_balls == 6:
                over += 1
                legal_balls = 0
                if current_batters[0] and current_batters[1]:
                    current_batters.reverse()
    
    return innings

def main():
    # Load teams
    team1_name = input("Enter first team's file name (e.g., England_XI.csv): ")
    team2_name = input("Enter second team's file name (e.g., India_XI.csv): ")
    
    team1 = load_team_from_file(team1_name)
    team2 = load_team_from_file(team2_name)
    
    # First innings
    print(f"\n=== First Innings ({team1.name} batting) ===")
    first_innings = simulate_innings(team1, team2)
    print_batting_scorecard(first_innings)
    print_bowling_scorecard(first_innings)
    
    # Second innings
    target = first_innings.get_score()[0] + 1
    print(f"\n=== Second Innings ({team2.name} batting, Target: {target}) ===")
    second_innings = simulate_innings(team2, team1, target)
    print_batting_scorecard(second_innings)
    print_bowling_scorecard(second_innings)
    
    # Match result
    team1_score = first_innings.get_score()[0]
    team2_score = second_innings.get_score()[0]
    team1_wickets = first_innings.get_score()[1]
    team2_wickets = second_innings.get_score()[1]
    
    print("\n=== Match Result ===")
    print(f"{team1.name}: {team1_score}/{team1_wickets}")
    print(f"{team2.name}: {team2_score}/{team2_wickets}")
    
    if team2_score > team1_score:
        print(f"{team2.name} won by {10-team2_wickets} wickets")
    elif team1_score > team2_score:
        print(f"{team1.name} won by {team1_score - team2_score} runs")
    else:
        print("Match tied!")

if __name__ == "__main__":
    main()
