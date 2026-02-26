#!/usr/bin/env python3
"""
Cricsheet CSV Replay Script

Loads Cricsheet info and ball-by-ball CSV files, replays the match 
ball-by-ball in the terminal, and exports using the existing export system.
"""

import sys
import os
import csv
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scorecard_generator.models import Player, Team, Innings, BallEvent
from scorecard_generator.scorecard import print_batting_scorecard, print_bowling_scorecard
from scorecard_generator.scorecard_export import export_all


def get_csv_paths():
    """Get paths to Cricsheet CSV files from CLI args or interactive prompts."""
    if len(sys.argv) >= 3:
        info_path = sys.argv[1]
        ballbyball_path = sys.argv[2]
        print(f"Using CSV files from command line:")
        print(f"  Info: {info_path}")
        print(f"  Ball-by-ball: {ballbyball_path}")
    else:
        print("Cricsheet CSV Replay")
        print("=" * 70)
        info_path = input("Enter path to info CSV file: ").strip()
        ballbyball_path = input("Enter path to ball-by-ball CSV file: ").strip()
    
    # Validate paths exist
    if not os.path.exists(info_path):
        print(f"Error: Info CSV file not found: {info_path}")
        sys.exit(1)
    if not os.path.exists(ballbyball_path):
        print(f"Error: Ball-by-ball CSV file not found: {ballbyball_path}")
        sys.exit(1)
    
    return info_path, ballbyball_path


def parse_info_csv(info_path):
    """
    Parse Cricsheet info CSV and extract match metadata.
    
    Returns:
        dict with keys: teams, players, venue, date, match_id, etc.
    """
    info = {
        'teams': [],
        'players': defaultdict(list),  # team_name -> [player_names]
        'venue': 'Unknown',
        'date': 'Unknown',
        'match_id': 'Unknown',
        'season': 'Unknown',
        'toss_winner': 'Unknown',
        'toss_decision': 'Unknown',
        'match_result': 'Unknown'
    }
    
    with open(info_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            
            key = row[0]
            value = row[1] if len(row) > 1 else ''
            
            if key == 'info' and len(row) >= 3:
                info_key = row[1]
                info_value = row[2] if len(row) > 2 else ''
                
                if info_key == 'team':
                    info['teams'].append(info_value)
                elif info_key == 'venue':
                    info['venue'] = info_value
                elif info_key == 'date':
                    info['date'] = info_value
                elif info_key == 'season':
                    info['season'] = info_value
                elif info_key == 'toss_winner':
                    info['toss_winner'] = info_value
                elif info_key == 'toss_decision':
                    info['toss_decision'] = info_value
                elif info_key == 'winner':
                    winner = info_value
                    # Look for winner_runs or winner_wickets in subsequent rows
                    info['match_result'] = f"{winner} won"
                elif info_key == 'player' and len(row) >= 4:
                    team_name = row[2]
                    player_name = row[3]
                    info['players'][team_name].append(player_name)
    
    # Extract match_id from filename if not in CSV
    if info['match_id'] == 'Unknown':
        match_id = Path(info_path).stem.replace('_info', '')
        info['match_id'] = match_id
    
    return info


def create_teams_from_info(info):
    """
    Create Team objects with Player objects from Cricsheet info.
    Auto-assigns player numbers 1-11 in listed order.
    
    Returns:
        tuple of (team1, team2)
    """
    teams = []
    
    for team_name in info['teams']:
        team = Team(team_name)
        player_names = info['players'].get(team_name, [])
        
        # Auto-assign numbers 1-11 in order
        for i, player_name in enumerate(player_names, start=1):
            player = Player(i, player_name)
            team.add_player(player)
            team.order.append(i)
            team.bowler_order.append(i)
        
        # Set placeholders for captain and wicketkeeper (not in Cricsheet data)
        team.captain_number = None
        team.wicketkeeper_number = None
        
        teams.append(team)
    
    if len(teams) != 2:
        print(f"Error: Expected 2 teams, found {len(teams)}")
        sys.exit(1)
    
    return teams[0], teams[1]


def parse_ball_by_ball_csv(ballbyball_path):
    """
    Parse Cricsheet ball-by-ball CSV into innings data.
    
    Returns:
        dict with innings numbers as keys, each containing list of ball dicts
    """
    innings_data = defaultdict(list)
    
    with open(ballbyball_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            innings_num = int(row['innings'])
            innings_data[innings_num].append(row)
    
    return innings_data


def cricsheet_to_event_type(row):
    """
    Convert Cricsheet ball row to internal event type and parameters.
    
    Returns:
        tuple: (event_type, runs, fielders_info)
    """
    runs_off_bat = int(row['runs_off_bat']) if row['runs_off_bat'] else 0
    extras = int(row['extras']) if row['extras'] else 0
    wides = int(row['wides']) if row['wides'] else 0
    noballs = int(row['noballs']) if row['noballs'] else 0
    byes = int(row['byes']) if row['byes'] else 0
    legbyes = int(row['legbyes']) if row['legbyes'] else 0
    wicket_type = row['wicket_type']
    player_dismissed = row['player_dismissed']
    
    # Determine event type
    if wicket_type:
        # Wicket occurred
        if wicket_type == 'run out':
            return 'run out', runs_off_bat, ['Unknown', 0, runs_off_bat]  # fielder, batter_idx, runs
        else:
            # Regular wicket (caught, bowled, lbw, stumped)
            return 'wicket', runs_off_bat, [wicket_type]
    elif wides > 0:
        # Wide
        if extras > wides:
            # Wide with extra runs (byes/legbyes)
            return 'wide_bye', extras, []
        else:
            return 'wide', extras, []
    elif noballs > 0:
        # No ball
        if runs_off_bat > 0:
            return 'no ball_runs', noballs + runs_off_bat, []
        elif byes > 0:
            return 'no ball_bye', noballs + byes, []
        elif legbyes > 0:
            return 'no ball_leg_bye', noballs + legbyes, []
        else:
            return 'no ball', noballs, []
    elif byes > 0:
        return 'bye', byes, []
    elif legbyes > 0:
        return 'leg bye', legbyes, []
    else:
        # Normal delivery
        return 'normal', runs_off_bat, []


def get_player_by_name(team, name):
    """Find player in team by name (case-insensitive)."""
    name_lower = name.lower()
    for player in team.players.values():
        if player.name.lower() == name_lower:
            return player
    return None


def replay_innings(innings_num, balls_data, batting_team, bowling_team, info):
    """
    Replay a single innings from Cricsheet ball data.
    
    Returns:
        Innings object
    """
    innings = Innings(batting_team, bowling_team)
    
    print(f"\n{'='*70}")
    print(f"Innings {innings_num}: {batting_team.name} batting")
    print(f"{'='*70}\n")
    
    current_striker = None
    current_non_striker = None
    wickets = 0
    
    for ball_data in balls_data:
        over = int(float(ball_data['ball']))
        ball = int((float(ball_data['ball']) % 1) * 10 + 0.5)  # Extract decimal part
        
        striker_name = ball_data['striker']
        non_striker_name = ball_data['non_striker']
        bowler_name = ball_data['bowler']
        
        # Get player objects
        striker = get_player_by_name(batting_team, striker_name)
        non_striker = get_player_by_name(batting_team, non_striker_name)
        bowler = get_player_by_name(bowling_team, bowler_name)
        
        if not striker or not bowler:
            print(f"Warning: Could not find player - Striker: {striker_name}, Bowler: {bowler_name}")
            continue
        
        # Convert to internal event type
        event_type, runs, fielders = cricsheet_to_event_type(ball_data)
        
        # Create BallEvent
        ball_event = BallEvent(over, ball, bowler, striker, runs, event_type, fielders)
        innings.add_ball(ball_event)
        
        # Update stats based on event type
        update_stats_for_ball(striker, bowler, event_type, runs, innings)
        
        # Print ball information
        print_ball_commentary(over, ball, striker_name, bowler_name, event_type, runs, ball_data)
        
        # Track wickets
        if ball_data['wicket_type']:
            wickets += 1
            dismissed_player = get_player_by_name(batting_team, ball_data['player_dismissed'])
            if dismissed_player:
                dismissed_player.batting['dismissal'] = format_dismissal(ball_data, bowler_name)
                innings.fall_of_wickets.append((
                    get_innings_total(innings),
                    dismissed_player.name,
                    bowler_name,
                    float(ball_data['ball'])
                ))
    
    return innings


def update_stats_for_ball(striker, bowler, event_type, runs, innings):
    """Update player and innings stats for a ball."""
    # Update batter stats
    if event_type == 'normal':
        striker.batting['runs'] += runs
        striker.batting['balls'] += 1
        if runs == 4:
            striker.batting['4s'] += 1
        elif runs == 6:
            striker.batting['6s'] += 1
        bowler.bowling['balls'] += 1
        bowler.bowling['runs'] += runs
        if runs == 0:
            bowler.bowling['dots'] += 1
        if runs == 4:
            bowler.bowling['4s'] += 1
        elif runs == 6:
            bowler.bowling['6s'] += 1
    elif event_type == 'wicket':
        striker.batting['balls'] += 1
        bowler.bowling['balls'] += 1
        bowler.bowling['wickets'] += 1
    elif event_type in ['bye', 'leg bye']:
        striker.batting['balls'] += 1
        bowler.bowling['balls'] += 1
        if event_type == 'bye':
            innings.extras['byes'] += runs
        else:
            innings.extras['leg byes'] += runs
    elif event_type == 'wide':
        innings.extras['wides'] += runs
        bowler.bowling['wides'] += runs
        bowler.bowling['runs'] += runs
    elif 'no ball' in event_type:
        striker.batting['balls'] += 1
        innings.extras['no balls'] += 1
        bowler.bowling['noballs'] += 1
        if event_type == 'no ball_runs':
            bat_runs = runs - 1  # Subtract penalty
            striker.batting['runs'] += bat_runs
            bowler.bowling['runs'] += runs
            if bat_runs == 4:
                striker.batting['4s'] += 1
            elif bat_runs == 6:
                striker.batting['6s'] += 1
        elif event_type == 'no ball_bye':
            bye_runs = runs - 1
            innings.extras['byes'] += bye_runs
            bowler.bowling['runs'] += 1
        elif event_type == 'no ball_leg_bye':
            leg_bye_runs = runs - 1
            innings.extras['leg byes'] += leg_bye_runs
            bowler.bowling['runs'] += 1
        else:
            bowler.bowling['runs'] += 1


def print_ball_commentary(over, ball, striker, bowler, event_type, runs, ball_data):
    """Print commentary for a single ball."""
    ball_ref = f"{over}.{ball}"
    
    if ball_data['wicket_type']:
        wicket_desc = f"{ball_data['wicket_type']}"
        print(f"  {ball_ref} - {bowler} to {striker} - WICKET! {wicket_desc} - {ball_data['player_dismissed']}")
    elif event_type == 'normal':
        if runs == 0:
            print(f"  {ball_ref} - {bowler} to {striker} - dot ball")
        elif runs == 4:
            print(f"  {ball_ref} - {bowler} to {striker} - FOUR!")
        elif runs == 6:
            print(f"  {ball_ref} - {bowler} to {striker} - SIX!")
        else:
            print(f"  {ball_ref} - {bowler} to {striker} - {runs} run(s)")
    elif 'wide' in event_type:
        print(f"  {ball_ref} - {bowler} to {striker} - WIDE ({runs} extra)")
    elif 'no ball' in event_type:
        print(f"  {ball_ref} - {bowler} to {striker} - NO BALL ({runs} total)")
    elif 'bye' in event_type or 'leg bye' in event_type:
        extra_type = 'byes' if 'bye' in event_type else 'leg byes'
        print(f"  {ball_ref} - {bowler} to {striker} - {runs} {extra_type}")


def format_dismissal(ball_data, bowler_name):
    """Format dismissal string from Cricsheet data."""
    wicket_type = ball_data['wicket_type']
    bowler_surname = bowler_name.split()[-1] if bowler_name else 'Unknown'
    
    if wicket_type == 'caught':
        return f"c Unknown b {bowler_surname}"
    elif wicket_type == 'bowled':
        return f"b {bowler_surname}"
    elif wicket_type == 'lbw':
        return f"lbw b {bowler_surname}"
    elif wicket_type == 'stumped':
        return f"st Unknown b {bowler_surname}"
    elif wicket_type == 'run out':
        return "run out (Unknown)"
    else:
        return wicket_type


def get_innings_total(innings):
    """Calculate current innings total from player runs and extras."""
    total = 0
    for player in innings.batting_team.players.values():
        total += player.batting['runs']
    total += sum(innings.extras.values())
    return total

def export_cricsheet_data(team1, team2, innings1, innings2, match_result, info, innings_data):
    """
    Export match data using original Cricsheet data to preserve accuracy.
    This avoids issues with non-striker inference and metadata.
    """
    from scorecard_generator.scorecard_export import get_export_filename, export_scorecard_csv, export_match_info_csv

    # Export scorecard (batting/bowling stats) - this works fine
    scorecard_file = get_export_filename(team1, team2, "scorecard")
    export_scorecard_csv(scorecard_file, team1, team2, innings1, innings2, match_result)
    print(f"Scorecard exported to {scorecard_file}")

    # Export match info CSV with actual metadata
    info_file = get_export_filename(team1, team2, "info")
    export_match_info_csv(info_file, team1, team2, innings1, innings2, match_result)
    print(f"Match info exported to {info_file}")

    def normalize_optional(value):
        if value is None:
            return ''
        if value == '' or value == '0':
            return ''
        return value

    # Export ball-by-ball using original Cricsheet data
    ballbyball_file = get_export_filename(team1, team2, "ballbyball")
    with open(ballbyball_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "match_id", "season", "start_date", "venue", "innings", "ball",
            "batting_team", "bowling_team", "striker", "non_striker", "bowler",
            "runs_off_bat", "extras", "wides", "noballs", "byes", "legbyes", "penalty",
            "wicket_type", "player_dismissed", "other_wicket_type", "other_player_dismissed"
        ])

        # Write all balls from both innings using original Cricsheet data
        for innings_num in sorted(innings_data.keys()):
            for ball_data in innings_data[innings_num]:
                match_id = ball_data.get('match_id') or info['match_id']
                season = ball_data.get('season') or info['season']
                start_date = ball_data.get('start_date') or info['date']
                venue = ball_data.get('venue') or info['venue']

                writer.writerow([
                    match_id,
                    season,
                    start_date,
                    venue,
                    ball_data['innings'],
                    ball_data['ball'],
                    ball_data['batting_team'],
                    ball_data['bowling_team'],
                    ball_data['striker'],
                    ball_data['non_striker'],  # Preserved from Cricsheet
                    ball_data['bowler'],
                    ball_data['runs_off_bat'],
                    ball_data['extras'],
                    normalize_optional(ball_data.get('wides')),
                    normalize_optional(ball_data.get('noballs')),
                    normalize_optional(ball_data.get('byes')),
                    normalize_optional(ball_data.get('legbyes')),
                    normalize_optional(ball_data.get('penalty')),
                    normalize_optional(ball_data.get('wicket_type')),
                    normalize_optional(ball_data.get('player_dismissed')),
                    normalize_optional(ball_data.get('other_wicket_type')),
                    normalize_optional(ball_data.get('other_player_dismissed'))
                ])

    print(f"Ball-by-ball data exported to {ballbyball_file}")

    print("\nAll exports completed successfully!")
    print(f"  - Scorecard: {scorecard_file}")
    print(f"  - Match Info: {info_file}")
    print(f"  - Ball-by-ball: {ballbyball_file}")


def main():
    """Main entry point for Cricsheet replay."""
    print("\n" + "="*70)
    print("CRICSHEET CSV REPLAY")
    print("="*70 + "\n")
    
    # Get CSV paths
    info_path, ballbyball_path = get_csv_paths()
    
    # Parse info CSV
    print("\nParsing match info...")
    info = parse_info_csv(info_path)
    print(f"  Match: {info['teams'][0]} vs {info['teams'][1]}")
    print(f"  Venue: {info['venue']}")
    print(f"  Date: {info['date']}")
    
    # Create teams
    print("\nCreating teams...")
    team1, team2 = create_teams_from_info(info)
    print(f"  {team1.name}: {len(team1.players)} players")
    print(f"  {team2.name}: {len(team2.players)} players")
    
    # Parse ball-by-ball data
    print("\nParsing ball-by-ball data...")
    innings_data = parse_ball_by_ball_csv(ballbyball_path)
    print(f"  Found {len(innings_data)} innings")
    
    # Determine which team bats first from ball-by-ball data
    first_innings_batting = innings_data[1][0]['batting_team']
    if first_innings_batting == team1.name:
        first_batting, first_bowling = team1, team2
    else:
        first_batting, first_bowling = team2, team1
    
    # Replay innings 1
    innings1 = replay_innings(1, innings_data[1], first_batting, first_bowling, info)
    print_batting_scorecard(innings1)
    print_bowling_scorecard(innings1)
    
    # Replay innings 2 if exists
    innings2 = None
    if 2 in innings_data:
        second_batting = first_bowling
        second_bowling = first_batting
        innings2 = replay_innings(2, innings_data[2], second_batting, second_bowling, info)
        print_batting_scorecard(innings2)
        print_bowling_scorecard(innings2)
    
    # Export results
    print("\n" + "="*70)
    print("EXPORTING MATCH DATA")
    print("="*70 + "\n")
    
    match_result = info['match_result']
    # Use custom export that preserves Cricsheet data accuracy
    export_cricsheet_data(team1, team2, innings1, innings2, match_result, info, innings_data)
    
    print("\n✓ Replay complete! Check scorecard_generator/exports/ for CSV files.")


if __name__ == "__main__":
    main()
