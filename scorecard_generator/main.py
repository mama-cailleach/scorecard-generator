from .team_utils import choose_team_xi
from .game_logic import play_innings
from .input_handlers import select_format
from .scorecard_export import export_all

### just to not forget this info
# cd /workspaces/python-portfolio/python-courses/cisco-python-essentials-2/scorecard-generator
# python -m scorecard_generator.main
###


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
        
        # Post-match menu
        print("\nGame Finished!")
        while True:
            print("1 - New Game")
            print("2 - Quit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                print("\n" + "="*70)
                break
            elif choice == "2":
                print("Thanks for playing!")
                return
            else:
                print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()