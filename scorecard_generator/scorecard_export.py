import csv
import os
import re

def extract_player_name(player_str):
    """Extract player name from format like '16 Jos Buttler' -> 'Jos Buttler'."""
    if not player_str or player_str == 'N/A':
        return 'N/A'
    # Split on first space to separate number from name
    parts = str(player_str).split(' ', 1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1]
    return str(player_str)

def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    # Replace spaces with underscores, remove special chars except underscores and hyphens
    sanitized = re.sub(r'[^\w\-]', '', name.replace(' ', '_'))
    return sanitized

def get_export_filename(team1, team2, export_type):
    """Generate filename in format: Team1vTeam2_exporttype.csv"""
    team1_clean = sanitize_filename(team1.name)
    team2_clean = sanitize_filename(team2.name)
    return f"scorecard_generator/exports/{team1_clean}v{team2_clean}_{export_type}.csv"

def export_scorecard_csv(filename, team1, team2, first_innings, second_innings, match_result):
    """Export traditional scorecard format to CSV."""
    # Use innings.batting_team/bowling_team to get correct ordering
    batting_team_1 = first_innings.batting_team
    bowling_team_1 = first_innings.bowling_team
    batting_team_2 = second_innings.batting_team
    bowling_team_2 = second_innings.bowling_team
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Match summary
        writer.writerow([f"{batting_team_1.name}: {first_innings.get_score()[0]}/{first_innings.get_score()[1]}"])
        writer.writerow([f"{batting_team_2.name}: {second_innings.get_score()[0]}/{second_innings.get_score()[1]}"])
        writer.writerow([match_result])
        writer.writerow([])
        
        # --- First Innings Batting ---
        writer.writerow([f"{batting_team_1.name} Batting"])
        writer.writerow(["Player", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"])
        for num in batting_team_1.order:
            p = batting_team_1.players[num]
            bat = p.batting
            writer.writerow([
                p.name, bat['dismissal'], bat['runs'], bat['balls'],
                bat['4s'], bat['6s'],
                f"{(bat['runs']/bat['balls']*100):.2f}" if bat['balls'] else "0.00"
            ])
        writer.writerow([])
        
        # --- First Innings Bowling ---
        writer.writerow([f"{bowling_team_1.name} Bowling"])
        writer.writerow(["Player", "Overs", "Maidens", "Runs", "Wickets", "Dots", "4s", "6s", "Wides", "No Balls"])
        for num in bowling_team_1.order:
            p = bowling_team_1.players[num]
            bowl = p.bowling
            # Only show bowlers who bowled at least one ball
            if bowl['balls'] > 0:
                overs = f"{bowl['balls']//6}.{bowl['balls']%6}"
                writer.writerow([
                    p.name, overs, bowl['maidens'], bowl['runs'], bowl['wickets'],
                    bowl['dots'], bowl['4s'], bowl['6s'], bowl['wides'], bowl['noballs']
                ])
        writer.writerow([])
        
        # --- Second Innings Batting ---
        writer.writerow([f"{batting_team_2.name} Batting"])
        writer.writerow(["Player", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"])
        for num in batting_team_2.order:
            p = batting_team_2.players[num]
            bat = p.batting
            writer.writerow([
                p.name, bat['dismissal'], bat['runs'], bat['balls'],
                bat['4s'], bat['6s'],
                f"{(bat['runs']/bat['balls']*100):.2f}" if bat['balls'] else "0.00"
            ])
        writer.writerow([])
        
        # --- Second Innings Bowling ---
        writer.writerow([f"{bowling_team_2.name} Bowling"])
        writer.writerow(["Player", "Overs", "Maidens", "Runs", "Wickets", "Dots", "4s", "6s", "Wides", "No Balls"])
        for num in bowling_team_2.order:
            p = bowling_team_2.players[num]
            bowl = p.bowling
            if bowl['balls'] > 0:
                overs = f"{bowl['balls']//6}.{bowl['balls']%6}"
                writer.writerow([
                    p.name, overs, bowl['maidens'], bowl['runs'], bowl['wickets'],
                    bowl['dots'], bowl['4s'], bowl['6s'], bowl['wides'], bowl['noballs']
                ])
        writer.writerow([])
    
    print(f"Scorecard exported to {filename}")

def export_match_info_csv(filename, team1, team2, first_innings, second_innings, match_result):
    """Export match info in Cricsheet format."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Cricsheet format header
        writer.writerow(['version', '2.2.0'])
        writer.writerow(['info', 'match_id', 'N/A'])
        writer.writerow(['info', 'season', 'N/A'])
        writer.writerow(['info', 'team_type', 'international'])
        writer.writerow(['info', 'match_type', 'T20'])
        writer.writerow(['info', 'gender', 'male'])
        writer.writerow(['info', 'date', 'N/A'])
        writer.writerow(['info', 'teams', team1.name, team2.name])
        writer.writerow(['info', 'venue', 'N/A'])
        writer.writerow(['info', 'city', 'N/A'])
        writer.writerow(['info', 'toss_winner', 'N/A'])
        writer.writerow(['info', 'toss_decision', 'N/A'])
        
        # Player registry
        for num in team1.order:
            p = team1.players[num]
            writer.writerow(['info', 'player', p.name, team1.name])
        for num in team2.order:
            p = team2.players[num]
            writer.writerow(['info', 'player', p.name, team2.name])
        
        # Match outcome
        writer.writerow(['info', 'outcome', match_result])
    
    print(f"Match info exported to {filename}")


def export_ball_by_ball_csv(filename, team1, team2, first_innings, second_innings):
    """Export ball-by-ball data in Cricsheet format."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Cricsheet ball-by-ball header
        writer.writerow([
            'match_id', 'season', 'start_date', 'venue', 'innings', 'ball', 'batting_team',
            'bowling_team', 'striker', 'non_striker', 'bowler', 'runs_off_bat', 'extras',
            'wides', 'noballs', 'byes', 'legbyes', 'penalty', 'wicket_type', 'player_dismissed', 'other_wicket_type', 'other_player_dismissed'
        ])
        
        # Helper function to classify runs from event type
        def classify_runs(event_type, runs):
            """Classify runs into runs_off_bat and extra types based on event type."""
            runs_off_bat = 0
            extras = 0
            wides = 0
            noballs = 0
            byes = 0
            legbyes = 0
            
            if event_type == 'normal':
                runs_off_bat = runs
            elif 'wide' in event_type:
                wides = 1  # Mark as wide occurred
                if 'boundary' in event_type:
                    runs_off_bat = 4
                    extras = 1
                else:
                    extras = runs
            elif 'no ball' in event_type:
                noballs = 1
                if 'runs' in event_type:
                    # No ball with runs
                    if runs > 1:
                        runs_off_bat = runs - 1
                    extras = 1
                else:
                    extras = 1
            elif event_type == 'bye':
                byes = runs
                extras = runs
            elif 'leg bye' in event_type:
                legbyes = runs if runs > 0 else 0
                extras = runs if runs > 0 else 0
            elif 'run out' in event_type:
                # Run outs usually have runs
                if 'bye' in event_type:
                    byes = runs
                    extras = runs
                elif 'leg' in event_type:
                    legbyes = runs
                    extras = runs
                else:
                    runs_off_bat = runs
            elif 'wicket' in event_type:
                # Wicket with no associated runs
                runs_off_bat = 0
            
            return runs_off_bat, extras, wides, noballs, byes, legbyes
        
        def write_ball_row(innings_num, inches, event, non_striker_name):
            """Helper to write a ball row."""
            # Calculate ball number (over.ball)
            ball_num = f"{event.over}.{event.ball}"
            
            # Classify the runs
            runs_off_bat, extras, wides, noballs, byes, legbyes = classify_runs(event.event, event.runs)
            
            # Wicket info extraction - fielders is a list with complex structure
            wicket_type = ''
            player_dismissed = ''  # Only populate if a wicket occurred
            
            if 'wicket' in event.event and event.fielders:
                # The dismissed player is the batter when a wicket occurs
                player_dismissed = extract_player_name(event.batter)
                # Parse fielders list to determine dismissal type
                if isinstance(event.fielders, list) and len(event.fielders) > 0:
                    first_elem = event.fielders[0]
                    
                    # LBW case: fielders = ["lbw", ...]
                    if first_elem == "lbw":
                        wicket_type = "lbw"
                    
                    # Caught & Bowled or Caught or Run out: first element contains the info
                    elif isinstance(first_elem, tuple):
                        # Tuple format: (fielder_name, something, is_c_and_b)
                        if len(first_elem) >= 3 and first_elem[2]:
                            wicket_type = "caught and bowled"
                        else:
                            wicket_type = "caught"
                    
                    # String format - could be bowler name (bowled) or fielder name (run out)
                    elif isinstance(first_elem, str):
                        bowler_name = extract_player_name(event.bowler)
                        fielder_name = extract_player_name(first_elem)
                        
                        if first_elem == event.bowler:
                            wicket_type = "bowled"
                        else:
                            wicket_type = "run out"
                    
                    # Handle stumped case: fielders = [wicketkeeper_name, ...]
                    elif len(event.fielders) >= 2:
                        wicket_type = "stumped"
            
            # Handle "run out" event type (not stored as "wicket")
            elif event.event in ["run out", "bye_run_out", "leg_bye_run_out", "wide_run_out", "no ball_run_out"]:
                wicket_type = "run out"
                player_dismissed = extract_player_name(event.batter)
            
            # Extract clean player names
            striker_name = extract_player_name(event.batter)
            bowler_name = extract_player_name(event.bowler)
            
            writer.writerow([
                'N/A',  # match_id
                'N/A',  # season
                'N/A',  # start_date
                'N/A',  # venue
                innings_num,
                ball_num,
                inches.batting_team.name,
                inches.bowling_team.name,
                striker_name,
                non_striker_name,
                bowler_name,
                runs_off_bat,
                extras,
                wides,
                noballs,
                byes,
                legbyes,
                0,      # penalty
                wicket_type,
                player_dismissed,
                '',     # other_wicket_type
                ''      # other_player_dismissed
            ])
        
        # Process first innings with non_striker tracking
        batting_order = list(first_innings.batting_team.order)
        non_striker_idx = 1  # Track current non-striker index in batting order
        
        for event in first_innings.balls:
            # Try to maintain non_striker tracking
            # Get names of current batting pair
            if non_striker_idx < len(batting_order):
                non_striker_num = batting_order[non_striker_idx]
                non_striker_name = extract_player_name(
                    f"{non_striker_num} {first_innings.batting_team.players[non_striker_num].name}"
                )
            else:
                non_striker_name = 'N/A'
            
            write_ball_row(1, first_innings, event, non_striker_name)
        
        # Process second innings
        batting_order = list(second_innings.batting_team.order)
        non_striker_idx = 1
        
        for event in second_innings.balls:
            # Get non_striker
            if non_striker_idx < len(batting_order):
                non_striker_num = batting_order[non_striker_idx]
                non_striker_name = extract_player_name(
                    f"{non_striker_num} {second_innings.batting_team.players[non_striker_num].name}"
                )
            else:
                non_striker_name = 'N/A'
            
            write_ball_row(2, second_innings, event, non_striker_name)
    
    print(f"Ball-by-ball data exported to {filename}")

def export_all(team1, team2, first_innings, second_innings, match_result):
    """Export all three CSV formats: scorecard, info, and ball-by-ball."""
    # Ensure exports directory exists
    os.makedirs("scorecard_generator/exports", exist_ok=True)
    
    # Generate filenames based on team names
    scorecard_file = get_export_filename(team1, team2, "scorecard")
    info_file = get_export_filename(team1, team2, "info")
    ballbyball_file = get_export_filename(team1, team2, "ballbyball")
    
    # Export all formats
    export_scorecard_csv(scorecard_file, team1, team2, first_innings, second_innings, match_result)
    export_match_info_csv(info_file, team1, team2, first_innings, second_innings, match_result)
    export_ball_by_ball_csv(ballbyball_file, team1, team2, first_innings, second_innings)
    
    print(f"\nAll exports completed successfully!")
    print(f"  - Scorecard: {scorecard_file}")
    print(f"  - Match Info: {info_file}")
    print(f"  - Ball-by-ball: {ballbyball_file}")