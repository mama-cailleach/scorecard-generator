from .input_handlers import get_display_name

def print_batting_scorecard(innings):
    team = innings.batting_team
    print(f"\nBatting: {team.name}")
    columns = ["Player Name", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"]
    print("{:<20}{:<25}{:>5}{:>6}{:>4}{:>4}{:>7}".format(*columns))
    did_not_bat = []
    for num in team.order:
        p = team.players[num]
        bat = p.batting
        # Show batter if they have batted (faced balls/scored/got out) OR if they are currently batting (p.batted is True)
        if bat['balls'] > 0 or bat['runs'] > 0 or bat['dismissal'] != 'not out' or p.batted:
            player_name = get_display_name(team, num)
            dismissal = bat['dismissal']
            print("{:<20}{:<25}{:>5}{:>6}{:>4}{:>4}{:>7.2f}".format(
                player_name, dismissal, bat['runs'], bat['balls'],
                bat.get('4s', 0), bat.get('6s', 0),
                (bat['runs'] / bat['balls'] * 100) if bat['balls'] > 0 else 0.0
            ))
        else:
            did_not_bat.append(get_display_name(team, num))
    extras_total = sum(innings.extras.values())
    # Build extras breakdown string
    extras_parts = []
    if innings.extras['byes']:
        extras_parts.append(f"b {innings.extras['byes']}")
    if innings.extras['leg byes']:
        extras_parts.append(f"lb {innings.extras['leg byes']}")
    if innings.extras['wides']:
        extras_parts.append(f"w {innings.extras['wides']}")
    if innings.extras['no balls']:
        extras_parts.append(f"nb {innings.extras['no balls']}")
    extras_str = ', '.join(extras_parts)
    print("{:<20}{:<25}{:>5}".format("Extras", f"({extras_str})" if extras_str else '', extras_total))
    runs, wickets, overs, rr = innings.get_score()
    # Calculate balls for overs: count only legal deliveries (exclude wides and no balls)
    balls = sum(
        1
        for be in innings.balls
        if not (be.event.startswith('wide') or be.event.startswith('no ball'))
    )
    full_overs = balls // 6
    rem_balls = balls % 6
    overs_str = f"{full_overs}.{rem_balls} Ov" if rem_balls else f"{full_overs} Ov"
    print(f"\nTotal: {overs_str} (RR: {rr:.2f}) {runs}/{wickets}")
    if did_not_bat:
        print("Did not bat: " + ", ".join(did_not_bat))
    print("Fall of wickets:")
    for i, fw in enumerate(innings.fall_of_wickets, 1):
        runs, batsman, bowler, over = fw
        print(f" {i}-{runs} ({batsman}, {over:.1f} ov)", end=",")
    print("\n")

def print_bowling_scorecard(innings):
    team = innings.bowling_team
    columns = ["Bowler", "Overs", "M", "Runs", "Wkts", "Econ", "Dots", "4s", "6s", "Wd", "NB"]
    print("{:<20}{:>6}{:>8}{:>6}{:>6}{:>7}{:>6}{:>4}{:>4}{:>7}{:>8}".format(*columns))
    for num, p in team.players.items():
        if p.bowling['balls'] == 0:
            continue
        balls = p.bowling['balls']
        full_overs = balls // 6
        rem_balls = balls % 6
        overs = f"{full_overs}.{rem_balls}" if rem_balls else f"{full_overs}.0"
        maidens = p.bowling['maidens']
        # Calculate runs conceded (excluding byes/leg byes)
        runs = p.bowling['runs']  # This will now only include runs off bat, wides, and no balls
        wkts = p.bowling['wickets']
        econ = (runs / (balls/6)) if balls else 0
        dots = p.bowling['dots']
        wides = p.bowling['wides']
        noballs = p.bowling['noballs']
        print("{:<20}{:>6}{:>8}{:>6}{:>6}{:>7.2f}{:>6}{:>4}{:>4}{:>7}{:>8}".format(
            p.name, overs, maidens, runs, wkts, econ, dots, p.bowling.get('4s', 0), p.bowling.get('6s', 0), wides, noballs
        ))
    print()