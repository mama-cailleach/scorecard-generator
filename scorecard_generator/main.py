from .team_utils import choose_team_xi
from .game_logic import play_innings
from .input_handlers import select_format
from .scorecard_export import export_all

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
    print(f"\n1st Innings: {innings1.batting_team.name}")
    print(f"Score: {score1}/{wickets1}")
    print(f"\nTop Batters:")
    
    # Get all batters who batted and sort by runs
    batters1 = [p for p in innings1.batting_team.players.values() if p.batted]
    batters1.sort(key=lambda x: x.batting['runs'], reverse=True)
    
    for i, batter in enumerate(batters1[:4]):  # Show max 4
        runs = batter.batting['runs']
        balls = batter.batting['balls']
        print(f"  {batter.name}: {runs}({balls})")
    
    print(f"\nTop Bowlers:")
    # Get all bowlers who bowled and sort by wickets (desc), then runs (asc)
    bowlers1 = [p for p in innings1.bowling_team.players.values() if p.bowled]
    bowlers1.sort(key=lambda x: (-x.bowling['wickets'], x.bowling['runs']))
    
    for i, bowler in enumerate(bowlers1[:4]):  # Show max 4
        wickets = bowler.bowling['wickets']
        runs = bowler.bowling['runs']
        print(f"  {bowler.name}: {wickets}-{runs}")
    
    # Second Innings Summary
    score2, wickets2, overs2, _ = innings2.get_score()
    print(f"\n{'-'*70}")
    print(f"\n2nd Innings: {innings2.batting_team.name}")
    print(f"Score: {score2}/{wickets2}")
    print(f"\nTop Batters:")
    
    # Get all batters who batted and sort by runs
    batters2 = [p for p in innings2.batting_team.players.values() if p.batted]
    batters2.sort(key=lambda x: x.batting['runs'], reverse=True)
    
    for i, batter in enumerate(batters2[:4]):  # Show max 4
        runs = batter.batting['runs']
        balls = batter.batting['balls']
        print(f"  {batter.name}: {runs}({balls})")
    
    print(f"\nTop Bowlers:")
    # Get all bowlers who bowled and sort by wickets (desc), then runs (asc)
    bowlers2 = [p for p in innings2.bowling_team.players.values() if p.bowled]
    bowlers2.sort(key=lambda x: (-x.bowling['wickets'], x.bowling['runs']))
    
    for i, bowler in enumerate(bowlers2[:4]):  # Show max 4
        wickets = bowler.bowling['wickets']
        runs = bowler.bowling['runs']
        print(f"  {bowler.name}: {wickets}-{runs}")
    
    print("="*70)


def main():
    print("Cricket T20 Scorecard Creator/Analyzer\n")
    ready = input("Do you have your starting XIs ready? (y/n): ").strip().lower()
    if ready != "y":
        print("Please use the team manager (team_utils.py) to create/select your teams and starting XIs before running the scorecard generator.")
        return

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
        
        # Post-match menu
        print("\nScoring Finished!")
        while True:
            print("1 - Match Stats")
            print("2 - New Game")
            print("3 - Quit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                print("\nMatch Stats feature coming soon...")
                return
                # TODO: Implement match stats functionality
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