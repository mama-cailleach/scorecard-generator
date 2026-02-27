from .team_utils import choose_team_xi
from .game_logic import play_innings
from .input_handlers import select_format
from .scorecard_export import export_all, sanitize_filename
from .teams_manager import run_team_manager
from .match_stats import generate_terminal_summary
from .match_report_html import generate_html_report
from .match_report_md import generate_markdown_report
import os

### just to not forget this info
# python -m scorecard_generator.main
###


def print_innings_summary(innings1, innings2):
    """Print a quick summary of both innings with top performers."""
    print("\n" + "="*70)
    print("MATCH SUMMARY")
    print("="*70)
    
    # First Innings Summary
    score1, wickets1, overs1, _ = innings1.get_score()
    
    # Format overs display
    overs1_int = int(overs1)
    overs1_frac = int((overs1 - overs1_int) * 10)
    if overs1_frac > 0:
        overs1_str = f"{overs1_int}.{overs1_frac} Ov"
    else:
        overs1_str = f"{overs1_int} Ov"
    
    print(f"\n1st Innings: {innings1.batting_team.name:<20} |  {overs1_str:<6} | {score1}/{wickets1}")
    print()
    
    # Get all batters who batted and sort by runs
    batters1 = [p for p in innings1.batting_team.players.values() if p.batted]
    batters1.sort(key=lambda x: x.batting['runs'], reverse=True)
    batters1 = batters1[:4]  # Max 4
    
    # Get all bowlers who bowled and sort by wickets (desc), then runs (asc)
    bowlers1 = [p for p in innings1.bowling_team.players.values() if p.bowled]
    bowlers1.sort(key=lambda x: (-x.bowling['wickets'], x.bowling['runs']))
    bowlers1 = bowlers1[:4]  # Max 4
    
    # Print headers for columns
    print(f"Top Batters:                   | Top Bowlers:")
    
    # Print batters and bowlers side by side
    for i in range(4):
        batter_str = ""
        if i < len(batters1):
            batter = batters1[i]
            runs = batter.batting['runs']
            balls = batter.batting['balls']
            not_out = "*" if batter.batting['dismissal'] == 'not out' else ""
            batter_str = f"  {batter.name}: {runs}{not_out}({balls})"
        
        bowler_str = ""
        if i < len(bowlers1):
            bowler = bowlers1[i]
            wickets = bowler.bowling['wickets']
            runs = bowler.bowling['runs']
            bowler_str = f"  {bowler.name}: {wickets}-{runs}"
        
        # Print with fixed column widths
        print(f"{batter_str:<30} | {bowler_str}")
    
    # Second Innings Summary
    score2, wickets2, overs2, _ = innings2.get_score()
    
    # Format overs display
    overs2_int = int(overs2)
    overs2_frac = int((overs2 - overs2_int) * 10)
    if overs2_frac > 0:
        overs2_str = f"{overs2_int}.{overs2_frac} Ov"
    else:
        overs2_str = f"{overs2_int} Ov"
    
    print(f"\n{'-'*70}")
    print(f"\n2nd Innings: {innings2.batting_team.name:<20} |  {overs2_str:<6} | {score2}/{wickets2}")
    print()
    
    # Get all batters who batted and sort by runs
    batters2 = [p for p in innings2.batting_team.players.values() if p.batted]
    batters2.sort(key=lambda x: x.batting['runs'], reverse=True)
    batters2 = batters2[:4]  # Max 4
    
    # Get all bowlers who bowled and sort by wickets (desc), then runs (asc)
    bowlers2 = [p for p in innings2.bowling_team.players.values() if p.bowled]
    bowlers2.sort(key=lambda x: (-x.bowling['wickets'], x.bowling['runs']))
    bowlers2 = bowlers2[:4]  # Max 4
    
    # Print headers for columns
    print(f"Top Batters:                   | Top Bowlers:")
    
    # Print batters and bowlers side by side
    for i in range(4):
        batter_str = ""
        if i < len(batters2):
            batter = batters2[i]
            runs = batter.batting['runs']
            balls = batter.batting['balls']
            not_out = "*" if batter.batting['dismissal'] == 'not out' else ""
            batter_str = f"  {batter.name}: {runs}{not_out}({balls})"
        
        bowler_str = ""
        if i < len(bowlers2):
            bowler = bowlers2[i]
            wickets = bowler.bowling['wickets']
            runs = bowler.bowling['runs']
            bowler_str = f"  {bowler.name}: {wickets}-{runs}"
        
        # Print with fixed column widths
        print(f"{batter_str:<30} | {bowler_str}")
    
    print("\n" + "="*70)


def main():
    print("Cricket T20 Scorecard Creator/Analyzer\n")
    
    # Check if teams are ready, launch team manager if not
    while True:
        ready = input("Do you have your starting XIs ready? (y/n): ").strip().lower()
        if ready == "y":
            break
        elif ready == "n":
            print("\nLaunching Team Manager...\n")
            run_team_manager()
        else:
            print("Please enter 'y' or 'n'.")

    while True:
        print("\nChoose teams for the match:")
        team1 = choose_team_xi("first")
        team2 = choose_team_xi("second")

        # Select match format
        format_config = select_format()
        print(f"\nMatch format: {format_config['name']}")
        if format_config['max_overs']:
            print(f"  - {format_config['max_overs']} overs per innings")
        else:
            print(f"  - Unlimited overs")
        if format_config['max_bowler_overs']:
            print(f"  - {format_config['max_bowler_overs']} overs max per bowler")
        else:
            print(f"  - No bowler overs limit")

        # Toss logic
        print("\nWho won the toss?")
        print(f"1. {team1.name}")
        print(f"2. {team2.name}")
        while True:
            toss_winner = input("Enter number: ").strip()
            if toss_winner == "1":
                toss_team = team1
                toss_loser = team2
                break
            elif toss_winner == "2":
                toss_team = team2
                toss_loser = team1
                break
            else:
                print("Invalid selection.")

        print(f"\nWhat does {toss_team.name} choose?")
        print("1. Bat first")
        print("2. Bowl first")
        while True:
            toss_choice = input("Enter number: ").strip()
            if toss_choice == "1":
                batting_first = toss_team
                bowling_first = toss_loser
                break
            elif toss_choice == "2":
                batting_first = toss_loser
                bowling_first = toss_team
                break
            else:
                print("Invalid selection.")

        print(f"\nFirst Innings: {batting_first.name} Batting")
        innings1 = play_innings(batting_first, bowling_first, format_config)
        score1, wickets1, overs1, rr1 = innings1.get_score()
        target = score1 + 1

        print(f"\nSecond Innings: {bowling_first.name} Batting (Target: {target})")
        innings2 = play_innings(bowling_first, batting_first, format_config, target=target)

        # You may wish to add a basic winner logic here
        score1, wickets1, overs1, rr1 = innings1.get_score()
        score2, wickets2, overs2, rr2 = innings2.get_score()
        if score2 >= target:
            match_result = f"{bowling_first.name} win by {10 - wickets2} wicket(s)!"
        elif score2 < target - 1:
            match_result = f"{batting_first.name} win by {target - 1 - score2} runs!"
        else:
            match_result = "Match tied!"
        
        print(f"\nMatch Result: {match_result}")

        # Export to CSV files
        export_all(team1, team2, innings1, innings2, match_result)
        
        # Print match summary
        print_innings_summary(innings1, innings2)
        
        # Store data for match stats (needed later in menu)
        match_data = {
            'team1': team1,
            'team2': team2,
            'innings1': innings1,
            'innings2': innings2,
            'match_result': match_result,
            'format_config': format_config
        }
        
        # Post-match menu
        print("\nScoring Finished!")
        while True:
            print("1 - Match Stats")
            print("2 - New Game")
            print("3 - Quit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                # Generate match statistics and reports
                print("\n" + "="*70)
                print("GENERATING MATCH STATISTICS REPORT")
                print("="*70)
                
                # Display terminal summary
                summary = generate_terminal_summary(
                    match_data['innings1'],
                    match_data['innings2'],
                    match_data['match_result'],
                    match_data['format_config']
                )
                print(summary)
                
                # Generate filenames
                team1_clean = sanitize_filename(match_data['team1'].name)
                team2_clean = sanitize_filename(match_data['team2'].name)
                base_filename = f"{team1_clean}v{team2_clean}"
                
                # Ensure exports directory exists
                os.makedirs("scorecard_generator/exports", exist_ok=True)
                
                html_filename = f"scorecard_generator/exports/{base_filename}_report.html"
                md_filename = f"scorecard_generator/exports/{base_filename}_report.md"
                
                # Generate HTML report
                try:
                    generate_html_report(
                        match_data['team1'],
                        match_data['team2'],
                        match_data['innings1'],
                        match_data['innings2'],
                        match_data['match_result'],
                        match_data['format_config'],
                        html_filename
                    )
                    print(f"  📊 HTML Report: {html_filename}")
                except Exception as e:
                    print(f"  ⚠️  HTML report generation failed: {e}")
                    print("     (Tip: Install plotly with 'pip install plotly' for interactive charts)")
                
                # Generate Markdown report
                try:
                    generate_markdown_report(
                        match_data['team1'],
                        match_data['team2'],
                        match_data['innings1'],
                        match_data['innings2'],
                        match_data['match_result'],
                        match_data['format_config'],
                        md_filename
                    )
                    print(f"  📝 Markdown Report: {md_filename}")
                except Exception as e:
                    print(f"  ⚠️  Markdown report generation failed: {e}")
                
                print("\n" + "="*70)
            elif choice == "2":
                print("\n" + "="*70)
                break
            elif choice == "3":
                print("Thanks for scoring!")
                return
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()