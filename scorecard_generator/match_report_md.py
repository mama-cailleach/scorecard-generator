"""Markdown match report generation.

This module generates comprehensive Markdown match reports with tables
and formatted statistics. Markdown files are ideal for GitHub and other
documentation systems.
"""

from datetime import datetime
from .match_stats import (
    calculate_phase_breakdown, calculate_innings_summary,
    get_top_batters, get_top_bowlers, format_batter_breakdown,
    format_partnership
)


def generate_markdown_report(team1, team2, innings1, innings2, match_result, format_config, filename):
    """Generate comprehensive Markdown match report.
    
    Args:
        team1, team2: Team objects
        innings1, innings2: Innings objects
        match_result: String describing match outcome
        format_config: Dict with format configuration
        filename: Output filename
    """
    # Get team names
    team1_name = innings1.batting_team.name
    team2_name = innings2.batting_team.name
    
    # Calculate statistics
    stats1 = calculate_innings_summary(innings1)
    stats2 = calculate_innings_summary(innings2)
    
    # Build Markdown content
    md = []
    
    # Header
    md.append(f"# Match Report: {team1_name} vs {team2_name}")
    md.append("")
    md.append(f"**Result:** {match_result}")
    md.append(f"**Format:** {format_config['name']}")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("")
    md.append("---")
    md.append("")
    
    # Match Summary
    md.append("## Match Summary")
    md.append("")
    md.append("| Team | Score | Overs | Run Rate |")
    md.append("|------|-------|-------|----------|")
    md.append(f"| {team1_name} | {stats1['total_runs']}/{stats1['wickets']} | {stats1['overs']:.1f} | {stats1['run_rate']:.2f} |")
    md.append(f"| {team2_name} | {stats2['total_runs']}/{stats2['wickets']} | {stats2['overs']:.1f} | {stats2['run_rate']:.2f} |")
    md.append("")
    
    # Full Scorecards Section
    from .match_stats import format_scorecard_data
    
    # First Innings Scorecard
    scorecard1 = format_scorecard_data(innings1)
    md.append("## 1st Innings Scorecard")
    md.append("")
    md.append(f"### {scorecard1['team_name']} Batting")
    md.append("")
    md.append("| Player Name | Dismissal | Runs | Balls | 4s | 6s | SR |")
    md.append("|-------------|-----------|------|-------|----|----|-----|")
    
    for batter in scorecard1['batters']:
        md.append(f"| {batter['name']} | {batter['dismissal']} | **{batter['runs']}{batter['not_out']}** | {batter['balls']} | {batter['fours']} | {batter['sixes']} | {batter['sr']:.2f} |")
    
    # Extras
    extras_display = f"({scorecard1['extras_detail']})" if scorecard1['extras_detail'] else ""
    md.append(f"| **Extras** | {extras_display} | **{scorecard1['extras']}** | | | | |")
    md.append("")
    md.append(f"**Total: {scorecard1['overs']} Ov (RR: {scorecard1['run_rate']:.2f}) {scorecard1['total_runs']}/{scorecard1['total_wickets']}**")
    md.append("")
    
    if scorecard1['did_not_bat']:
        md.append(f"*Did not bat: {', '.join(scorecard1['did_not_bat'])}*")
        md.append("")
    
    if scorecard1['fall_of_wickets']:
        fow_list = []
        for fw in scorecard1['fall_of_wickets']:
            fow_list.append(f"{fw['number']}-{fw['runs']} ({fw['batsman']}, {fw['over']:.1f} ov)")
        md.append(f"**Fall of wickets:** {', '.join(fow_list)}")
        md.append("")
    
    # Bowling
    md.append(f"### Bowling: {scorecard1['bowling_team']}")
    md.append("")
    md.append("| Bowler | Overs | M | Runs | Wkts | Econ | Dots | 4s | 6s | Wd | NB |")
    md.append("|--------|-------|---|------|------|------|------|----|----|----|----|")
    
    for bowler in scorecard1['bowlers']:
        md.append(f"| {bowler['name']} | {bowler['overs']} | {bowler['maidens']} | {bowler['runs']} | **{bowler['wickets']}** | {bowler['economy']:.2f} | {bowler['dots']} | {bowler['fours']} | {bowler['sixes']} | {bowler['wides']} | {bowler['noballs']} |")
    
    md.append("")
    md.append("---")
    md.append("")
    
    # Second Innings Scorecard
    scorecard2 = format_scorecard_data(innings2)
    md.append("## 2nd Innings Scorecard")
    md.append("")
    md.append(f"### {scorecard2['team_name']} Batting")
    md.append("")
    md.append("| Player Name | Dismissal | Runs | Balls | 4s | 6s | SR |")
    md.append("|-------------|-----------|------|-------|----|----|-----|")
    
    for batter in scorecard2['batters']:
        md.append(f"| {batter['name']} | {batter['dismissal']} | **{batter['runs']}{batter['not_out']}** | {batter['balls']} | {batter['fours']} | {batter['sixes']} | {batter['sr']:.2f} |")
    
    # Extras
    extras_display = f"({scorecard2['extras_detail']})" if scorecard2['extras_detail'] else ""
    md.append(f"| **Extras** | {extras_display} | **{scorecard2['extras']}** | | | | |")
    md.append("")
    md.append(f"**Total: {scorecard2['overs']} Ov (RR: {scorecard2['run_rate']:.2f}) {scorecard2['total_runs']}/{scorecard2['total_wickets']}**")
    md.append("")
    
    if scorecard2['did_not_bat']:
        md.append(f"*Did not bat: {', '.join(scorecard2['did_not_bat'])}*")
        md.append("")
    
    if scorecard2['fall_of_wickets']:
        fow_list = []
        for fw in scorecard2['fall_of_wickets']:
            fow_list.append(f"{fw['number']}-{fw['runs']} ({fw['batsman']}, {fw['over']:.1f} ov)")
        md.append(f"**Fall of wickets:** {', '.join(fow_list)}")
        md.append("")
    
    # Bowling
    md.append(f"### Bowling: {scorecard2['bowling_team']}")
    md.append("")
    md.append("| Bowler | Overs | M | Runs | Wkts | Econ | Dots | 4s | 6s | Wd | NB |")
    md.append("|--------|-------|---|------|------|------|------|----|----|----|----|")
    
    for bowler in scorecard2['bowlers']:
        md.append(f"| {bowler['name']} | {bowler['overs']} | {bowler['maidens']} | {bowler['runs']} | **{bowler['wickets']}** | {bowler['economy']:.2f} | {bowler['dots']} | {bowler['fours']} | {bowler['sixes']} | {bowler['wides']} | {bowler['noballs']} |")
    
    md.append("")
    md.append("---")
    md.append("")
    
    # Scoring Breakdown (if T20 or ODI)
    if format_config['name'] in ['T20', 'One Day']:
        phase1 = calculate_phase_breakdown(innings1, format_config)
        phase2 = calculate_phase_breakdown(innings2, format_config)
        
        if phase1 or phase2:
            md.append("## Scoring Breakdown by Phase")
            md.append("")
            md.append(f"| Phase | {team1_name} | {team2_name} |")
            md.append("|-------|" + "-" * (len(team1_name) + 2) + "|" + "-" * (len(team2_name) + 2) + "|")
            
            phases = ['powerplay', 'middle', 'final']
            phase_labels = {
                'powerplay': 'Powerplay' + (' (1-6)' if format_config['name'] == 'T20' else ' (1-10)'),
                'middle': 'Middle Overs' + (' (7-16)' if format_config['name'] == 'T20' else ' (11-40)'),
                'final': 'Final Overs' + (' (17-20)' if format_config['name'] == 'T20' else ' (41-50)')
            }
            
            for phase in phases:
                p1 = phase1.get(phase) if phase1 else None
                p2 = phase2.get(phase) if phase2 else None
                
                p1_str = f"{p1['runs']}/{p1['wickets']} in {p1['overs']} ov" if p1 else "-"
                p2_str = f"{p2['runs']}/{p2['wickets']} in {p2['overs']} ov" if p2 else "-"
                
                md.append(f"| {phase_labels[phase]} | {p1_str} | {p2_str} |")
            
            md.append("")
    
    # Innings Statistics Comparison
    md.append("## Innings Statistics")
    md.append("")
    md.append(f"| Statistic | {team1_name} | {team2_name} |")
    md.append("|-----------|" + "-" * (len(team1_name) + 2) + "|" + "-" * (len(team2_name) + 2) + "|")
    md.append(f"| Sixes | {stats1['sixes']} | {stats2['sixes']} |")
    md.append(f"| Fours | {stats1['fours']} | {stats2['fours']} |")
    md.append(f"| Runs in Boundaries | {stats1['runs_in_boundaries']} | {stats2['runs_in_boundaries']} |")
    md.append(f"| Dot Ball % | {stats1['dot_ball_percent']:.1f}% | {stats2['dot_ball_percent']:.1f}% |")
    md.append(f"| Extras | {stats1['extras']} | {stats2['extras']} |")
    md.append("")
    
    # Top Batters
    md.append("## Best Batting Performances")
    md.append("")
    top_batters = get_top_batters(innings1, innings2, n=2)
    
    for i, (player, team_name) in enumerate(top_batters, 1):
        batting = player.batting
        not_out = "*" if batting['dismissal'] == 'not out' else ""
        sr = (batting['runs'] / batting['balls'] * 100) if batting['balls'] > 0 else 0
        
        md.append(f"### {i}. {player.name} | {team_name}")
        md.append("")
        md.append(f"**{batting['runs']}{not_out} runs ({batting['balls']} balls) | Strike Rate: {sr:.2f}**")
        md.append("")
        
        breakdown = format_batter_breakdown(player)
        md.append("| 0s | 1s | 2s | 3s | 4s | 6s |")
        md.append("|----|----|----|----|----|---|")
        md.append(f"| {breakdown['0s']} | {breakdown['1s']} | {breakdown['2s']} | {breakdown['3s']} | {breakdown['4s']} | {breakdown['6s']} |")
        md.append("")
    
    # Top Bowlers
    md.append("## Best Bowling Performances")
    md.append("")
    top_bowlers = get_top_bowlers(innings1, innings2, n=2)
    
    for i, (player, team_name) in enumerate(top_bowlers, 1):
        bowling = player.bowling
        balls = bowling['balls']
        overs = balls // 6
        remaining = balls % 6
        overs_str = f"{overs}.{remaining}" if remaining > 0 else str(overs)
        econ = (bowling['runs'] / (balls / 6)) if balls > 0 else 0
        
        md.append(f"### {i}. {player.name} | {team_name}")
        md.append("")
        md.append("| Overs | Maidens | Runs | Wickets | Economy | Dots | 4s | 6s | Wides | No Balls |")
        md.append("|-------|---------|------|---------|---------|------|----|----|-------|----------|")
        md.append(f"| {overs_str} | {bowling['maidens']} | {bowling['runs']} | {bowling['wickets']} | {econ:.2f} | {bowling['dots']} | {bowling['4s']} | {bowling['6s']} | {bowling['wides']} | {bowling['noballs']} |")
        md.append("")
    
    # Partnerships
    for innings_num, innings in enumerate([innings1, innings2], 1):
        if innings.partnerships:
            md.append(f"## Partnerships - {innings.batting_team.name}")
            md.append("")
            md.append("| Wicket | Partnership | Batter 1 | Batter 2 |")
            md.append("|--------|-------------|----------|----------|")
            
            for partnership in innings.partnerships:
                p = format_partnership(partnership, innings.batting_team)
                wicket_label = f"{p['wicket_number']}{'st' if p['wicket_number'] == 1 else 'nd' if p['wicket_number'] == 2 else 'rd' if p['wicket_number'] == 3 else 'th'}"
                partnership_str = f"{p['total_runs']}({p['total_balls']})"
                batter1_str = f"{p['batter1_name']}: {p['batter1_runs']}({p['batter1_balls']})"
                batter2_str = f"{p['batter2_name']}: {p['batter2_runs']}({p['batter2_balls']})"
                
                md.append(f"| {wicket_label} | {partnership_str} | {batter1_str} | {batter2_str} |")
            
            md.append("")
    
    # Charts Note (since Markdown can't embed interactive charts)
    md.append("## Match Charts")
    md.append("")
    md.append("📊 **Interactive charts (Manhattan, Worm, Run Rate) are available in the HTML report.**")
    md.append("")
    md.append("**Runs per Over (Manhattan):**")
    md.append("")
    md.append(f"| Over | {team1_name} | {team2_name} |")
    md.append("|------|" + "-" * (len(team1_name) + 2) + "|" + "-" * (len(team2_name) + 2) + "|")
    
    # Display up to 20 overs or max available
    max_overs = max(len(innings1.over_totals), len(innings2.over_totals))
    for i in range(min(max_overs, 20)):
        over_num = i + 1
        runs1 = innings1.over_totals[i] if i < len(innings1.over_totals) else "-"
        runs2 = innings2.over_totals[i] if i < len(innings2.over_totals) else "-"
        md.append(f"| {over_num} | {runs1} | {runs2} |")
    
    if max_overs > 20:
        md.append(f"| ... | ... | ... |")
        md.append(f"*({max_overs - 20} more overs not shown)*")
    
    md.append("")
    
    # Footer
    md.append("---")
    md.append("")
    md.append("*Generated by Cricket Scorecard Generator*")
    md.append("")
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))
    
    print(f"Markdown report generated: {filename}")
