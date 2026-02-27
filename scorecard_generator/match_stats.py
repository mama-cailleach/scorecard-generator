"""Match statistics calculation and display module.

This module provides functions to calculate and display comprehensive match statistics
including phase breakdowns, partnerships, top performers, and chart data.
"""

from collections import defaultdict


def calculate_phase_breakdown(innings, format_config):
    """Calculate runs, wickets, and overs by phase (powerplay/middle/final).
    
    Args:
        innings: Innings object with phase_stats
        format_config: Dict with format configuration
    
    Returns:
        Dict with phase names as keys and stats as values
    """
    if format_config['name'] not in ['T20', 'One Day']:
        return None
    
    breakdown = {}
    for phase, stats in innings.phase_stats.items():
        if stats['balls'] > 0:  # Only include phases that were played
            balls = stats['balls']
            overs = balls // 6
            remaining_balls = balls % 6
            overs_str = f"{overs}.{remaining_balls}" if remaining_balls > 0 else str(overs)
            
            breakdown[phase] = {
                'runs': stats['runs'],
                'wickets': stats['wickets'],
                'balls': stats['balls'],
                'overs': overs_str
            }
    
    return breakdown


def calculate_innings_summary(innings):
    """Calculate summary statistics for an innings.
    
    Args:
        innings: Innings object
    
    Returns:
        Dict with summary stats
    """
    total_runs, wickets, overs, rr = innings.get_score()
    
    # Count dot balls (0 runs off bat on legal deliveries)
    total_legal_balls = 0
    dot_balls = 0
    
    for ball in innings.balls:
        # Count legal deliveries (not wides or no-balls)
        if ball.event not in ['wide', 'wide_boundary', 'wide_bye', 'wide_leg_bye']:
            total_legal_balls += 1
            # Check if it's a dot ball (0 runs off bat)
            if ball.event in ['normal', 'wicket', 'bye', 'leg bye', 'run out'] and ball.runs == 0:
                dot_balls += 1
            elif ball.event == 'bye':  # Byes are dot balls for batters
                dot_balls += 1
            elif ball.event == 'leg bye':  # Leg byes are dot balls for batters
                dot_balls += 1
    
    dot_ball_percent = (dot_balls / total_legal_balls * 100) if total_legal_balls> 0 else 0
    
    # Count boundaries
    total_fours = sum(p.batting['4s'] for p in innings.batting_team.players.values())
    total_sixes = sum(p.batting['6s'] for p in innings.batting_team.players.values())
    runs_in_boundaries = (total_fours * 4) + (total_sixes * 6)
    
    # Total extras
    total_extras = sum(innings.extras.values())
    
    return {
        'total_runs': total_runs,
        'wickets': wickets,
        'overs': overs,
        'run_rate': rr,
        'dot_ball_percent': dot_ball_percent,
        'sixes': total_sixes,
        'fours': total_fours,
        'runs_in_boundaries': runs_in_boundaries,
        'extras': total_extras
    }


def get_top_batters(innings1, innings2, n=2):
    """Get top n batters across both innings.
    
    Args:
        innings1: First Innings object
        innings2: Second Innings object
        n: Number of top batters to return
    
    Returns:
        List of (player, team_name) tuples sorted by runs
    """
    all_batters = []
    
    # Collect batters from both innings
    for innings in [innings1, innings2]:
        for player in innings.batting_team.players.values():
            if player.batted and player.batting['balls'] > 0:
                all_batters.append((player, innings.batting_team.name))
    
    # Sort by runs (descending)
    all_batters.sort(key=lambda x: x[0].batting['runs'], reverse=True)
    
    return all_batters[:n]


def get_top_bowlers(innings1, innings2, n=2):
    """Get top n bowlers across both innings.
    
    Args:
        innings1: First Innings object
        innings2: Second Innings object
        n: Number of top bowlers to return
    
    Returns:
        List of (player, team_name) tuples sorted by wickets then runs
    """
    all_bowlers = []
    
    # Collect bowlers from both innings
    for innings in [innings1, innings2]:
        for player in innings.bowling_team.players.values():
            if player.bowled and player.bowling['balls'] > 0:
                all_bowlers.append((player, innings.bowling_team.name))
    
    # Sort by wickets (descending), then by runs (ascending)
    all_bowlers.sort(key=lambda x: (-x[0].bowling['wickets'], x[0].bowling['runs']))
    
    return all_bowlers[:n]


def format_batter_breakdown(player):
    """Format a batter's scoring distribution (0s, 1s, 2s, 3s, 4s, 6s).
    
    Args:
        player: Player object
    
    Returns:
        Dict with scoring distribution
    """
    dist = player.batting.get('scoring_distribution', defaultdict(int))
    return {
        '0s': dist[0],
        '1s': dist[1],
        '2s': dist[2],
        '3s': dist[3],
        '4s': dist[4],
        '5s': dist.get(5, 0),
        '6s': dist[6]
    }


def format_partnership(partnership, team):
    """Format partnership information for display.
    
    Args:
        partnership: Partnership object
        team: Team object to get player names
    
    Returns:
        Dict with formatted partnership data
    """
    # Get the display order - batter1 is the one who came in first for this partnership
    batter1_name = partnership.batter1.name if partnership.batter1 else "Unknown"
    batter2_name = partnership.batter2.name if partnership.batter2 else "Unknown"
    
    return {
        'wicket_number': partnership.wicket_number,
        'batter1_name': batter1_name,
        'batter1_runs': partnership.batter1_runs,
        'batter1_balls': partnership.batter1_balls,
        'batter2_name': batter2_name,
        'batter2_runs': partnership.batter2_runs,
        'batter2_balls': partnership.batter2_balls,
        'total_runs': partnership.runs,
        'total_balls': partnership.balls
    }


def generate_terminal_summary(innings1, innings2, match_result, format_config):
    """Generate a brief terminal summary of match stats.
    
    Args:
        innings1: First Innings object
        innings2: Second Innings object
        match_result: String describing match outcome
        format_config: Dict with format configuration
    
    Returns:
        String with formatted terminal output
    """
    summary = []
    summary.append("\n" + "="*70)
    summary.append("MATCH STATISTICS SUMMARY")
    summary.append("="*70)
    
    # Innings summaries
    for i, innings in enumerate([innings1, innings2], 1):
        stats = calculate_innings_summary(innings)
        summary.append(f"\n{i}{'st' if i == 1 else 'nd'} Innings: {innings.batting_team.name}")
        summary.append(f"  Score: {stats['total_runs']}/{stats['wickets']} in {stats['overs']:.1f} overs")
        summary.append(f"  Boundaries: {stats['fours']} fours, {stats['sixes']} sixes")
        summary.append(f"  Dot ball %: {stats['dot_ball_percent']:.1f}%")
    
    # Top performers
    summary.append("\n" + "-"*70)
    summary.append("TOP PERFORMERS")
    summary.append("-"*70)
    
    top_batters = get_top_batters(innings1, innings2, n=2)
    if top_batters:
        summary.append("\nBatting:")
        for player, team_name in top_batters:
            runs = player.batting['runs']
            balls = player.batting['balls']
            sr = (runs / balls * 100) if balls > 0 else 0
            not_out = "*" if player.batting['dismissal'] == 'not out' else ""
            summary.append(f"  {player.name} ({team_name}): {runs}{not_out}({balls}) SR: {sr:.2f}")
    
    top_bowlers = get_top_bowlers(innings1, innings2, n=2)
    if top_bowlers:
        summary.append("\nBowling:")
        for player, team_name in top_bowlers:
            wickets = player.bowling['wickets']
            runs = player.bowling['runs']
            balls = player.bowling['balls']
            overs = balls // 6
            remaining = balls % 6
            overs_str = f"{overs}.{remaining}" if remaining > 0 else str(overs)
            econ = (runs / (balls / 6)) if balls > 0 else 0
            summary.append(f"  {player.name} ({team_name}): {wickets}-{runs} in {overs_str} overs, Econ: {econ:.2f}")
    
    summary.append("\n" + "="*70)
    summary.append(f"Result: {match_result}")
    summary.append("="*70)
    summary.append("\nDetailed match report with graphs exported to:")
    
    return "\n".join(summary)


def generate_manhattan_data(innings):
    """Generate data for Manhattan chart (runs per over).
    
    Args:
        innings: Innings object
    
    Returns:
        List of runs scored in each over
    """
    return innings.over_totals


def generate_worm_data(innings1, innings2):
    """Generate data for Worm chart (cumulative runs progression).
    
    Args:
        innings1: First Innings object
        innings2: Second Innings object
    
    Returns:
        Tuple of (innings1_cumulative, innings2_cumulative)
    """
    return innings1.cumulative_runs, innings2.cumulative_runs


def generate_runrate_data(innings):
    """Generate run rate progression data for an innings.
    
    Args:
        innings: Innings object
    
    Returns:
        List of run rates at the end of each over
    """
    run_rates = []
    cumulative_runs = innings.cumulative_runs
    
    for over_num, total_runs in enumerate(cumulative_runs, 1):
        run_rate = total_runs / over_num
        run_rates.append(run_rate)
    
    return run_rates
