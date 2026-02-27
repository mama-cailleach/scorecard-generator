from .models import BallEvent, Innings, Player, Team, Partnership, get_current_phase
from .scorecard import print_batting_scorecard, print_bowling_scorecard
from .input_handlers import input_ball, select_openers, select_bowler, get_display_name

def handle_no_ball_outcome(outcome, batters, bowler, team, over_num, ball_num):
    runs = 1
    event_type = "no ball"
    fielders = []
    swapped = False

    if outcome in ['0', '']:
        return runs, event_type, fielders, swapped
    elif outcome.isdigit() and int(outcome) in range(1, 7):
        bat_runs = int(outcome)
        return (runs + bat_runs), "no ball_runs", fielders, (bat_runs % 2 == 1)
    elif outcome == 'bye':
        print("How many byes?")
        bye_runs = int(input("> "))
        swapped = (bye_runs % 2 == 1)
        return (runs + bye_runs), "no ball_bye", fielders, swapped
    elif outcome in ['leg bye', 'leg byes']:
        print("How many leg byes?")
        lb_runs = int(input("> "))
        swapped = (lb_runs % 2 == 1)
        return (runs + lb_runs), "no ball_leg_bye", fielders, swapped
    elif outcome == 'run out':
        print("How many runs completed before run out?")
        completed_runs = int(input("> "))
        swapped = (completed_runs % 2 == 1)
        print("Which batter was run out? (striker/non-striker)")
        out_batter = input("> ").strip().lower()
        if out_batter == 'striker':
            fielders = [batters[0].name]
        elif out_batter == 'non-striker':
            fielders = [batters[1].name]
        else:
            print("Invalid input.")
            return handle_no_ball_outcome(outcome, batters, bowler, team, over_num, ball_num)
        return (runs + completed_runs), "no ball_run_out", fielders, swapped
    else:
        print("Invalid input, please try again.")
        print("Valid options: 0-6, bye, leg bye, run out")
        new_outcome = input("> ").strip().lower()
        return handle_no_ball_outcome(new_outcome, batters, bowler, team, over_num, ball_num)

def process_ball_event(
    event_type, runs, fielders, swapped, innings, bowler, batter,
    current_batters, wickets, over, ball_num, batting_team, over_runs,
    legal_balls, ball_number, batters_yet, format_config
):
    over_ended_early = False
    
    # Determine current phase for stats tracking
    phase = get_current_phase(over, format_config)
    

    def handle_wicket_fall(out_batter_idx=0, out_batter=None):
        nonlocal wickets, current_batters, over_ended_early, batters_yet
        runs_total, _, _, _ = innings.get_score()
        print(f"Set dismissal for {out_batter.name}: {out_batter.batting['dismissal']}") # delete
        print(f"\nWICKET! Score: {runs_total}-{wickets+1} | {out_batter.name} {out_batter.batting['runs']}({out_batter.batting['balls']})")
        wickets += 1
        innings.fall_of_wickets.append((runs_total, out_batter.name, bowler.name, over + ball_number / 10))
        
        # Track wicket in phase stats
        if phase:
            innings.phase_stats[phase]['wickets'] += 1
        
        # Close current partnership
        if innings.current_partnership:
            innings.current_partnership.end_score = runs_total
            innings.partnerships.append(innings.current_partnership)
            innings.current_partnership = None
        
        if wickets == 10:
            current_batters[0] = None
            current_batters[1] = None
            over_ended_early = True
            return True

        # Replace out batter with new one if available
        non_out_idx = 1 - out_batter_idx
        survivor = current_batters[non_out_idx]
        batters_batted = [
            b.number for b in batting_team.players.values()
            if b.batting['balls'] > 0 or b.batting['dismissal'] != 'not out'
        ]
        batters_yet = [
            num for num in batting_team.order
            if num not in batters_batted and (survivor is None or num != survivor.number)
        ]
        if batters_yet:
            print("Choose next batter in from:")
            for idx, num in enumerate(batters_yet, 1):
                print(f"{idx}: {num} {get_display_name(batting_team, num)}")
            while True:
                try:
                    next_batter_idx = int(input("Enter order number of next batter: "))
                    if not (1 <= next_batter_idx <= len(batters_yet)):
                        print("you can't do that try again.")
                        continue
                    next_batter_num = batters_yet[next_batter_idx-1]
                    break
                except:
                    print("you can't do that try again.")
            current_batters[out_batter_idx] = batting_team.players[next_batter_num]
            # Start new partnership
            new_batter = batting_team.players[next_batter_num]
            survivor = current_batters[1 - out_batter_idx]
            runs_total, _, _, _ = innings.get_score()
            innings.current_partnership = Partnership(survivor, new_batter, wickets + 1, runs_total)
        else:
            current_batters[0] = None
            current_batters[1] = None
            over_ended_early = True
            return True
        return False

    # Normal scoring ball
    if event_type == "normal":
        batter.batting['runs'] += runs
        batter.batting['balls'] += 1
        batter.batting['scoring_distribution'][runs] += 1  # Track scoring distribution
        if runs == 4:
            batter.batting['4s'] += 1
            bowler.bowling['4s'] += 1
        if runs == 6:
            batter.batting['6s'] += 1
            bowler.bowling['6s'] += 1
        if runs == 0:
            bowler.bowling['dots'] += 1
        bowler.bowling['balls'] += 1
        bowler.bowling['runs'] += runs
        over_runs += runs
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['runs'] += runs
            innings.phase_stats[phase]['balls'] += 1
        
        # Track partnership stats
        if innings.current_partnership:
            innings.current_partnership.runs += runs
            innings.current_partnership.balls += 1
            if batter == current_batters[0]:
                innings.current_partnership.batter1_runs += runs
                innings.current_partnership.batter1_balls += 1
            else:
                innings.current_partnership.batter2_runs += runs
                innings.current_partnership.batter2_balls += 1
        
        if runs % 2 == 1:
            current_batters.reverse()
        legal_balls += 1
        ball_number += 1

    # Wide ball variants
    elif event_type in ["wide", "wide_boundary", "wide_bye", "wide_leg_bye"]:
        if event_type == "wide":
            innings.extras['wides'] += runs
            bowler.bowling['wides'] += 1
            bowler.bowling['runs'] += runs
        elif event_type == "wide_boundary":
            innings.extras['wides'] += runs
            bowler.bowling['wides'] += 1
            bowler.bowling['runs'] += runs
        elif event_type == "wide_bye":
            innings.extras['wides'] += 1
            innings.extras['byes'] += runs - 1
            bowler.bowling['wides'] += 1
            bowler.bowling['runs'] += 1
        elif event_type == "wide_leg_bye":
            innings.extras['wides'] += 1
            innings.extras['leg byes'] += runs - 1
            bowler.bowling['wides'] += 1
            bowler.bowling['runs'] += 1
        over_runs += runs
        
        # Track phase stats for wides
        if phase:
            innings.phase_stats[phase]['runs'] += runs
        
        # Track partnership stats for wides
        if innings.current_partnership:
            innings.current_partnership.runs += runs
        
        if swapped:
            current_batters.reverse()

    # No ball variants
    elif event_type == "no ball":
        innings.extras['no balls'] += 1
        bowler.bowling['noballs'] += 1
        bowler.bowling['runs'] += 1
        batter.batting['balls'] += 1

    elif event_type == "no ball_runs":
        penalty = 1
        bat_runs = runs - penalty
        innings.extras['no balls'] += penalty
        bowler.bowling['noballs'] += penalty
        bowler.bowling['runs'] += runs
        batter.batting['runs'] += bat_runs
        batter.batting['balls'] += 1
        batter.batting['scoring_distribution'][bat_runs] += 1  # Track scoring
        if bat_runs == 4:
            batter.batting['4s'] += 1
            bowler.bowling['4s'] += 1
        if bat_runs == 6:
            batter.batting['6s'] += 1
            bowler.bowling['6s'] += 1
        over_runs += runs
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['runs'] += runs
        
        # Track partnership stats
        if innings.current_partnership:
            innings.current_partnership.runs += runs
            if batter == current_batters[0]:
                innings.current_partnership.batter1_runs += bat_runs
                innings.current_partnership.batter1_balls += 1
            else:
                innings.current_partnership.batter2_runs += bat_runs
                innings.current_partnership.batter2_balls += 1
        
        if bat_runs % 2 == 1:
            current_batters.reverse()

    elif event_type == "no ball_bye":
        penalty = 1
        bye_runs = runs - penalty
        innings.extras['no balls'] += penalty
        innings.extras['byes'] += bye_runs
        bowler.bowling['noballs'] += penalty
        bowler.bowling['runs'] += penalty
        batter.batting['balls'] += 1
        over_runs += runs
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['runs'] += runs
        
        # Track partnership stats
        if innings.current_partnership:
            innings.current_partnership.runs += runs
        
        if swapped:
            current_batters.reverse()

    elif event_type == "no ball_leg_bye":
        penalty = 1
        leg_bye_runs = runs - penalty
        innings.extras['no balls'] += penalty
        innings.extras['leg byes'] += leg_bye_runs
        bowler.bowling['noballs'] += penalty
        bowler.bowling['runs'] += penalty
        batter.batting['balls'] += 1
        over_runs += runs
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['runs'] += runs
        
        # Track partnership stats
        if innings.current_partnership:
            innings.current_partnership.runs += runs
        
        if swapped:
            current_batters.reverse()

    elif event_type == "bye":
        innings.extras['byes'] += runs
        batter.batting['balls'] += 1
        batter.batting['scoring_distribution'][0] += 1  # Count as dot ball for batter
        bowler.bowling['balls'] += 1
        bowler.bowling['dots'] += 1  # Byes are dots for bowlers (no runs off bat)
        over_runs += runs
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['runs'] += runs
            innings.phase_stats[phase]['balls'] += 1
        
        # Track partnership stats
        if innings.current_partnership:
            innings.current_partnership.runs += runs
            innings.current_partnership.balls += 1
        
        if swapped:
            current_batters.reverse()
        legal_balls += 1
        ball_number += 1

    elif event_type == "leg bye":
        innings.extras['leg byes'] += runs
        batter.batting['balls'] += 1
        batter.batting['scoring_distribution'][0] += 1  # Count as dot ball for batter
        bowler.bowling['balls'] += 1
        bowler.bowling['dots'] += 1  # Leg byes are dots for bowlers (no runs off bat)
        over_runs += runs
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['runs'] += runs
            innings.phase_stats[phase]['balls'] += 1
        
        # Track partnership stats
        if innings.current_partnership:
            innings.current_partnership.runs += runs
            innings.current_partnership.balls += 1
        
        if swapped:
            current_batters.reverse()
        legal_balls += 1
        ball_number += 1

    elif event_type in ["run out", "bye_run_out", "leg_bye_run_out", "wide_run_out", "no ball_run_out"]:
        fielder = fielders[0]
        out_batter_idx = fielders[1]
        completed_runs = fielders[2]
        out_batter = current_batters[out_batter_idx]
        handle_run_out(out_batter, fielder)
        if handle_wicket_fall(out_batter_idx=out_batter_idx, out_batter=out_batter):
            return wickets, over_runs, legal_balls, ball_number, current_batters, batters_yet, over_ended_early
        out_batter.batting['balls'] += 1
        bowler.bowling['balls'] += 1
        over_runs += completed_runs
        if swapped:
            current_batters.reverse()
        legal_balls += 1
        ball_number += 1

    elif event_type == "wicket":
        batter.batting['balls'] += 1
        batter.batting['scoring_distribution'][0] += 1  # Wicket counts as dot for scoring distribution
        bowler.bowling['balls'] += 1
        bowler.bowling['wickets'] += 1
        bowler.bowling['dots'] += 1  # Wickets are dots for bowlers
        
        # Track phase stats
        if phase:
            innings.phase_stats[phase]['balls'] += 1
        
        # Track partnership stats (balls only, runs already tracked)
        if innings.current_partnership:
            innings.current_partnership.balls += 1
            if batter == current_batters[0]:
                innings.current_partnership.batter1_balls += 1
            else:
                innings.current_partnership.batter2_balls += 1
        
        bowler_surname = bowler.name.split()[-1]
        dismissal_set = False

        if len(fielders) == 1:
            f = fielders[0]
            # Caught & Bowled or Caught
            if isinstance(f, tuple):
                fielder, _, is_c_and_b = f
                fielder_surname = fielder.split()[-1]
                if is_c_and_b:
                    batter.batting['dismissal'] = f"c & b {bowler_surname}"
                else:
                    batter.batting['dismissal'] = f"c {fielder_surname} b {bowler_surname}"
                dismissal_set = True
            # Bowled
            elif isinstance(f, str) and f == bowler.name:
                batter.batting['dismissal'] = f"b {bowler_surname}"
                dismissal_set = True
            # Run out
            elif isinstance(f, str):
                fielder_surname = f.split()[-1]
                batter.batting['dismissal'] = f"run out ({fielder_surname})"
                dismissal_set = True

        # LBW
        elif len(fielders) == 2 and fielders[0] == "lbw":
            batter.batting['dismissal'] = f"lbw b {bowler_surname}"
            dismissal_set = True

        # Stumped
        elif len(fielders) == 2:
            wicketkeeper, _ = fielders
            keeper_surname = wicketkeeper.split()[-1]
            batter.batting['dismissal'] = f"st †{keeper_surname} b {bowler_surname}"
            dismissal_set = True

        # Fallback
        if not dismissal_set:
            batter.batting['dismissal'] = f"b {bowler_surname}"

        if handle_wicket_fall(out_batter_idx=0, out_batter=batter):
            return wickets, over_runs, legal_balls, ball_number, current_batters, batters_yet, over_ended_early
        legal_balls += 1
        ball_number += 1

    return wickets, over_runs, legal_balls, ball_number, current_batters, batters_yet, over_ended_early

def play_innings(batting_team, bowling_team, format_config, target=None):
    max_overs = format_config['max_overs']
    max_bowler_overs = format_config['max_bowler_overs']
    balls_per_over = format_config['balls_per_over']
    
    innings = Innings(batting_team, bowling_team)
    print(f"Players available to open the batting:")
    for idx, num in enumerate(batting_team.order, 1):
        print(f"{idx}: {num} {get_display_name(batting_team, num)}")
    openers = select_openers(batting_team)
    striker, non_striker = batting_team.players[openers[0]], batting_team.players[openers[1]]
    current_batters = [striker, non_striker]
    
    # Initialize first partnership
    innings.current_partnership = Partnership(striker, non_striker, 1, 0)
    
    batters_yet = [num for num in batting_team.order if num not in batting_team.order[:2]]
    bowler_overs = {}
    wickets = 0
    over = 0
    prev_bowler = None
    # Condition handles unlimited overs (max_overs is None) or limited overs
    while (max_overs is None or over < max_overs) and wickets < 10:
        bowler_num = select_bowler(bowling_team, over, prev_bowler, bowler_overs, max_bowler_overs)
        bowler = bowling_team.players[bowler_num]
        balls_this_over = 0
        over_runs = 0
        over_dots = 0
        legal_balls = 0
        ball_num = 1
        over_ended_early = False
        bowler_overs.setdefault(bowler_num, [])
        while legal_balls < balls_per_over:
            if wickets == 10 or current_batters[0] is None or current_batters[1] is None:
                over_ended_early = True
                break
            result = input_ball(current_batters, bowler, over, ball_num, bowling_team)
            if len(result) == 4:
                runs, event_type, fielders, swapped = result
            else:
                runs, event_type, fielders = result
                swapped = False
            if event_type == "end":
                over_ended_early = True
                break
            batter = current_batters[0]
            event = BallEvent(over, ball_num, bowler, batter, runs, event_type, fielders)
            innings.add_ball(event)
            batter.batted = True
            bowler.bowled = True
            wickets, over_runs, legal_balls, ball_num, current_batters, batters_yet, over_ended_early = process_ball_event(
                event_type, runs, fielders, swapped, innings, bowler, batter,
                current_batters, wickets, over, ball_num, batting_team, over_runs,
                legal_balls, ball_num, batters_yet, format_config
            )
            score, _, _, _ = innings.get_score()
            if target is not None and score >= target:
                print(f"\nTarget reached! {batting_team.name} win by {10 - wickets} wicket(s)!")
                over_ended_early = True
                break
            if over_ended_early:
                break
        if over_ended_early:
            print("OVER ENDED EARLY (all out, no batters, or innings ended).")
            break
        else:
            print("OVER FINISHED.")
        
        # Record over totals for charts
        innings.over_totals.append(over_runs)
        total_score, _, _, _ = innings.get_score()
        innings.cumulative_runs.append(total_score)
        
        bowler_overs[bowler_num].append(over)
        if over_runs == 0:
            bowler.bowling['maidens'] += 1
        prev_bowler = bowler_num
        over += 1
        if over > 0 and current_batters[0] and current_batters[1]:
            current_batters.reverse()
    
    # Close final partnership if still active
    if innings.current_partnership:
        total_score, _, _, _ = innings.get_score()
        innings.current_partnership.end_score = total_score
        innings.partnerships.append(innings.current_partnership)
    
    print_batting_scorecard(innings)
    print_bowling_scorecard(innings)
    return innings

def handle_run_out(batter, fielder_info):
    """Helper function to consistently handle run out dismissals"""
    fielder_name = fielder_info[0] if isinstance(fielder_info, tuple) else fielder_info
    fielder_surname = fielder_name.split()[-1]
    batter.batting['dismissal'] = f"run out ({fielder_surname})"
    return True