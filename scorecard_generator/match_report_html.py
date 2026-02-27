"""HTML match report generation with Plotly charts.

This module generates comprehensive HTML match reports with interactive charts
for Manhattan (runs per over), Worm (cumulative runs), and Run Rate progression.
"""

import os
from datetime import datetime
from .match_stats import (
    calculate_phase_breakdown, calculate_innings_summary,
    get_top_batters, get_top_bowlers, format_batter_breakdown,
    format_partnership, generate_manhattan_data, generate_worm_data,
    generate_runrate_data
)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def generate_manhattan_chart(innings1, innings2, team1_name, team2_name):
    """Generate Manhattan chart (runs per over) using Plotly.
    
    Args:
        innings1, innings2: Innings objects
        team1_name, team2_name: Team names
    
    Returns:
        HTML div string with chart
    """
    if not PLOTLY_AVAILABLE:
        return "<p>Plotly not installed. Install with: pip install plotly</p>"
    
    data1 = generate_manhattan_data(innings1)
    data2 = generate_manhattan_data(innings2)
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for first innings
    fig.add_trace(go.Bar(
        x=list(range(1, len(data1) + 1)),
        y=data1,
        name=team1_name,
        marker_color='#1f77b4'
    ))
    
    # Add bars for second innings
    fig.add_trace(go.Bar(
        x=list(range(1, len(data2) + 1)),
        y=data2,
        name=team2_name,
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title='Manhattan Chart - Runs Per Over',
        xaxis_title='Over',
        yaxis_title='Runs',
        barmode='group',
        template='plotly_white',
        height=400
    )
    
    return fig.to_html(include_plotlyjs='cdn', div_id='manhattan_chart')


def generate_worm_chart(innings1, innings2, team1_name, team2_name):
    """Generate Worm chart (cumulative runs) using Plotly.
    
    Args:
        innings1, innings2: Innings objects
        team1_name, team2_name: Team names
    
    Returns:
        HTML div string with chart
    """
    if not PLOTLY_AVAILABLE:
        return "<p>Plotly not installed. Install with: pip install plotly</p>"
    
    data1, data2 = generate_worm_data(innings1, innings2)
    
    fig = go.Figure()
    
    # Add line for first innings
    fig.add_trace(go.Scatter(
        x=list(range(1, len(data1) + 1)),
        y=data1,
        mode='lines+markers',
        name=team1_name,
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    # Add line for second innings
    fig.add_trace(go.Scatter(
        x=list(range(1, len(data2) + 1)),
        y=data2,
        mode='lines+markers',
        name=team2_name,
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Worm Chart - Cumulative Runs',
        xaxis_title='Over',
        yaxis_title='Total Runs',
        template='plotly_white',
        height=400
    )
    
    return fig.to_html(include_plotlyjs=False, div_id='worm_chart')


def generate_runrate_chart(innings1, innings2, team1_name, team2_name):
    """Generate run rate progression chart using Plotly.
    
    Args:
        innings1, innings2: Innings objects
        team1_name, team2_name: Team names
    
    Returns:
        HTML div string with chart
    """
    if not PLOTLY_AVAILABLE:
        return "<p>Plotly not installed. Install with: pip install plotly</p>"
    
    rr1 = generate_runrate_data(innings1)
    rr2 = generate_runrate_data(innings2)
    
    fig = go.Figure()
    
    # Add line for first innings
    fig.add_trace(go.Scatter(
        x=list(range(1, len(rr1) + 1)),
        y=rr1,
        mode='lines+markers',
        name=team1_name,
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    # Add line for second innings
    fig.add_trace(go.Scatter(
        x=list(range(1, len(rr2) + 1)),
        y=rr2,
        mode='lines+markers',
        name=team2_name,
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Run Rate Progression',
        xaxis_title='Over',
        yaxis_title='Run Rate',
        template='plotly_white',
        height=400
    )
    
    return fig.to_html(include_plotlyjs=False, div_id='runrate_chart')


def generate_html_report(team1, team2, innings1, innings2, match_result, format_config, filename):
    """Generate comprehensive HTML match report.
    
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
    
    # Build HTML
    html = ['<!DOCTYPE html>']
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('    <meta charset="UTF-8">')
    html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append(f'    <title>Match Report: {team1_name} vs {team2_name}</title>')
    html.append('    <style>')
    html.append('''
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }
        .header .result {
            font-size: 1.3em;
            font-weight: 500;
        }
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .section h3 {
            color: #764ba2;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .stat-box .label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .stat-box .value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }
        .partnership {
            background: #fff8e1;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }
        .chart-container {
            margin: 20px 0;
        }
        @media print {
            body {
                background-color: white;
            }
            .section {
                box-shadow: none;
                page-break-inside: avoid;
            }
        }
    ''')
    html.append('    </style>')
    html.append('</head>')
    html.append('<body>')
    
    # Header
    html.append('    <div class="header">')
    html.append(f'        <h1>{team1_name} vs {team2_name}</h1>')
    html.append(f'        <p class="result">{match_result}</p>')
    html.append(f'        <p>Format: {format_config["name"]} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>')
    html.append('    </div>')
    
    # Match Summary Section
    html.append('    <div class="section">')
    html.append('        <h2>Match Summary</h2>')
    html.append('        <div class="stats-grid">')
    html.append(f'            <div class="stat-box"><div class="label">{team1_name}</div><div class="value">{stats1["total_runs"]}/{stats1["wickets"]}</div></div>')
    html.append(f'            <div class="stat-box"><div class="label">Overs</div><div class="value">{stats1["overs"]:.1f}</div></div>')
    html.append(f'            <div class="stat-box"><div class="label">Run Rate</div><div class="value">{stats1["run_rate"]:.2f}</div></div>')
    html.append('        </div>')
    html.append('        <div class="stats-grid">')
    html.append(f'            <div class="stat-box"><div class="label">{team2_name}</div><div class="value">{stats2["total_runs"]}/{stats2["wickets"]}</div></div>')
    html.append(f'            <div class="stat-box"><div class="label">Overs</div><div class="value">{stats2["overs"]:.1f}</div></div>')
    html.append(f'            <div class="stat-box"><div class="label">Run Rate</div><div class="value">{stats2["run_rate"]:.2f}</div></div>')
    html.append('        </div>')
    html.append('    </div>')
    
    # Full Scorecards Section
    from .match_stats import format_scorecard_data
    
    # First Innings Scorecard
    scorecard1 = format_scorecard_data(innings1)
    html.append('    <div class="section">')
    html.append(f'        <h2>1st Innings: {scorecard1["team_name"]} Batting</h2>')
    
    # Batting table
    html.append('        <table>')
    html.append('            <tr><th>Player Name</th><th>Dismissal</th><th>Runs</th><th>Balls</th><th>4s</th><th>6s</th><th>SR</th></tr>')
    for batter in scorecard1['batters']:
        html.append(f'            <tr>')
        html.append(f'                <td>{batter["name"]}</td>')
        html.append(f'                <td>{batter["dismissal"]}</td>')
        html.append(f'                <td><strong>{batter["runs"]}{batter["not_out"]}</strong></td>')
        html.append(f'                <td>{batter["balls"]}</td>')
        html.append(f'                <td>{batter["fours"]}</td>')
        html.append(f'                <td>{batter["sixes"]}</td>')
        html.append(f'                <td>{batter["sr"]:.2f}</td>')
        html.append(f'            </tr>')
    
    # Extras row
    extras_display = f'({scorecard1["extras_detail"]})' if scorecard1['extras_detail'] else ''
    html.append(f'            <tr style="font-weight: bold; background-color: #f8f9fa;">')
    html.append(f'                <td>Extras</td>')
    html.append(f'                <td>{extras_display}</td>')
    html.append(f'                <td><strong>{scorecard1["extras"]}</strong></td>')
    html.append(f'                <td colspan="4"></td>')
    html.append(f'            </tr>')
    html.append('        </table>')
    
    # Total line
    html.append(f'        <p style="font-size: 1.1em; margin: 10px 0;"><strong>Total: {scorecard1["overs"]} Ov (RR: {scorecard1["run_rate"]:.2f}) {scorecard1["total_runs"]}/{scorecard1["total_wickets"]}</strong></p>')
    
    # Did not bat
    if scorecard1['did_not_bat']:
        html.append(f'        <p><em>Did not bat: {", ".join(scorecard1["did_not_bat"])}</em></p>')
    
    # Fall of wickets
    if scorecard1['fall_of_wickets']:
        fow_list = []
        for fw in scorecard1['fall_of_wickets']:
            fow_list.append(f'{fw["number"]}-{fw["runs"]} ({fw["batsman"]}, {fw["over"]:.1f} ov)')
        html.append(f'        <p><strong>Fall of wickets:</strong> {", ".join(fow_list)}</p>')
    
    # Bowling table
    html.append(f'        <h3>Bowling: {scorecard1["bowling_team"]}</h3>')
    html.append('        <table>')
    html.append('            <tr><th>Bowler</th><th>Overs</th><th>M</th><th>Runs</th><th>Wkts</th><th>Econ</th><th>Dots</th><th>4s</th><th>6s</th><th>Wd</th><th>NB</th></tr>')
    for bowler in scorecard1['bowlers']:
        html.append(f'            <tr>')
        html.append(f'                <td>{bowler["name"]}</td>')
        html.append(f'                <td>{bowler["overs"]}</td>')
        html.append(f'                <td>{bowler["maidens"]}</td>')
        html.append(f'                <td>{bowler["runs"]}</td>')
        html.append(f'                <td><strong>{bowler["wickets"]}</strong></td>')
        html.append(f'                <td>{bowler["economy"]:.2f}</td>')
        html.append(f'                <td>{bowler["dots"]}</td>')
        html.append(f'                <td>{bowler["fours"]}</td>')
        html.append(f'                <td>{bowler["sixes"]}</td>')
        html.append(f'                <td>{bowler["wides"]}</td>')
        html.append(f'                <td>{bowler["noballs"]}</td>')
        html.append(f'            </tr>')
    html.append('        </table>')
    html.append('    </div>')
    
    # Second Innings Scorecard
    scorecard2 = format_scorecard_data(innings2)
    html.append('    <div class="section">')
    html.append(f'        <h2>2nd Innings: {scorecard2["team_name"]} Batting</h2>')
    
    # Batting table
    html.append('        <table>')
    html.append('            <tr><th>Player Name</th><th>Dismissal</th><th>Runs</th><th>Balls</th><th>4s</th><th>6s</th><th>SR</th></tr>')
    for batter in scorecard2['batters']:
        html.append(f'            <tr>')
        html.append(f'                <td>{batter["name"]}</td>')
        html.append(f'                <td>{batter["dismissal"]}</td>')
        html.append(f'                <td><strong>{batter["runs"]}{batter["not_out"]}</strong></td>')
        html.append(f'                <td>{batter["balls"]}</td>')
        html.append(f'                <td>{batter["fours"]}</td>')
        html.append(f'                <td>{batter["sixes"]}</td>')
        html.append(f'                <td>{batter["sr"]:.2f}</td>')
        html.append(f'            </tr>')
    
    # Extras row
    extras_display = f'({scorecard2["extras_detail"]})' if scorecard2['extras_detail'] else ''
    html.append(f'            <tr style="font-weight: bold; background-color: #f8f9fa;">')
    html.append(f'                <td>Extras</td>')
    html.append(f'                <td>{extras_display}</td>')
    html.append(f'                <td><strong>{scorecard2["extras"]}</strong></td>')
    html.append(f'                <td colspan="4"></td>')
    html.append(f'            </tr>')
    html.append('        </table>')
    
    # Total line
    html.append(f'        <p style="font-size: 1.1em; margin: 10px 0;"><strong>Total: {scorecard2["overs"]} Ov (RR: {scorecard2["run_rate"]:.2f}) {scorecard2["total_runs"]}/{scorecard2["total_wickets"]}</strong></p>')
    
    # Did not bat
    if scorecard2['did_not_bat']:
        html.append(f'        <p><em>Did not bat: {", ".join(scorecard2["did_not_bat"])}</em></p>')
    
    # Fall of wickets
    if scorecard2['fall_of_wickets']:
        fow_list = []
        for fw in scorecard2['fall_of_wickets']:
            fow_list.append(f'{fw["number"]}-{fw["runs"]} ({fw["batsman"]}, {fw["over"]:.1f} ov)')
        html.append(f'        <p><strong>Fall of wickets:</strong> {", ".join(fow_list)}</p>')
    
    # Bowling table
    html.append(f'        <h3>Bowling: {scorecard2["bowling_team"]}</h3>')
    html.append('        <table>')
    html.append('            <tr><th>Bowler</th><th>Overs</th><th>M</th><th>Runs</th><th>Wkts</th><th>Econ</th><th>Dots</th><th>4s</th><th>6s</th><th>Wd</th><th>NB</th></tr>')
    for bowler in scorecard2['bowlers']:
        html.append(f'            <tr>')
        html.append(f'                <td>{bowler["name"]}</td>')
        html.append(f'                <td>{bowler["overs"]}</td>')
        html.append(f'                <td>{bowler["maidens"]}</td>')
        html.append(f'                <td>{bowler["runs"]}</td>')
        html.append(f'                <td><strong>{bowler["wickets"]}</strong></td>')
        html.append(f'                <td>{bowler["economy"]:.2f}</td>')
        html.append(f'                <td>{bowler["dots"]}</td>')
        html.append(f'                <td>{bowler["fours"]}</td>')
        html.append(f'                <td>{bowler["sixes"]}</td>')
        html.append(f'                <td>{bowler["wides"]}</td>')
        html.append(f'                <td>{bowler["noballs"]}</td>')
        html.append(f'            </tr>')
    html.append('        </table>')
    html.append('    </div>')
    
    # Scoring Breakdown (if T20 or ODI)
    if format_config['name'] in ['T20', 'One Day']:
        phase1 = calculate_phase_breakdown(innings1, format_config)
        phase2 = calculate_phase_breakdown(innings2, format_config)
        
        if phase1 or phase2:
            html.append('    <div class="section">')
            html.append('        <h2>Scoring Breakdown by Phase</h2>')
            html.append('        <table>')
            html.append('            <tr><th>Phase</th><th>' + team1_name + '</th><th>' + team2_name + '</th></tr>')
            
            phases = ['powerplay', 'middle', 'final']
            phase_labels = {
                'powerplay': 'Powerplay' + (' (1-6)' if format_config['name'] == 'T20' else ' (1-10)'),
                'middle': 'Middle Overs' + (' (7-16)' if format_config['name'] == 'T20' else ' (11-40)'),
                'final': 'Final Overs' + (' (17-20)' if format_config['name'] == 'T20' else ' (41-50)')
            }
            
            for phase in phases:
                p1 = phase1.get(phase) if phase1 else None
                p2 = phase2.get(phase) if phase2 else None
                
                p1_str = f"{p1['runs']}/{p1['wickets']}" if p1 else "-"
                p2_str = f"{p2['runs']}/{p2['wickets']}" if p2 else "-"
                
                html.append(f'            <tr><td>{phase_labels[phase]}</td><td>{p1_str}</td><td>{p2_str}</td></tr>')
            
            html.append('        </table>')
            html.append('    </div>')
    
    # Innings Statistics Comparison
    html.append('    <div class="section">')
    html.append('        <h2>Innings Statistics</h2>')
    html.append('        <table>')
    html.append('            <tr><th>Statistic</th><th>' + team1_name + '</th><th>' + team2_name + '</th></tr>')
    html.append(f'            <tr><td>Sixes</td><td>{stats1["sixes"]}</td><td>{stats2["sixes"]}</td></tr>')
    html.append(f'            <tr><td>Fours</td><td>{stats1["fours"]}</td><td>{stats2["fours"]}</td></tr>')
    html.append(f'            <tr><td>Runs in Boundaries</td><td>{stats1["runs_in_boundaries"]}</td><td>{stats2["runs_in_boundaries"]}</td></tr>')
    html.append(f'            <tr><td>Dot Ball %</td><td>{stats1["dot_ball_percent"]:.1f}%</td><td>{stats2["dot_ball_percent"]:.1f}%</td></tr>')
    html.append(f'            <tr><td>Extras</td><td>{stats1["extras"]}</td><td>{stats2["extras"]}</td></tr>')
    html.append('        </table>')
    html.append('    </div>')
    
    # Top Batters
    html.append('    <div class="section">')
    html.append('        <h2>Best Batting Performances</h2>')
    top_batters = get_top_batters(innings1, innings2, n=2)
    
    for player, team_name in top_batters:
        batting = player.batting
        not_out = "*" if batting['dismissal'] == 'not out' else ""
        sr = (batting['runs'] / batting['balls'] * 100) if batting['balls'] > 0 else 0
        
        html.append(f'        <h3>{player.name} | {team_name}</h3>')
        html.append(f'        <p style="font-size: 1.2em;"><strong>{batting["runs"]}{not_out} runs ({batting["balls"]} balls) | SR: {sr:.2f}</strong></p>')
        
        breakdown = format_batter_breakdown(player)
        html.append('        <div class="stats-grid">')
        for key in ['0s', '1s', '2s', '3s', '4s', '6s']:
            html.append(f'            <div class="stat-box"><div class="label">{key}</div><div class="value">{breakdown[key]}</div></div>')
        html.append('        </div>')
    
    html.append('    </div>')
    
    # Top Bowlers
    html.append('    <div class="section">')
    html.append('        <h2>Best Bowling Performances</h2>')
    top_bowlers = get_top_bowlers(innings1, innings2, n=2)
    
    for player, team_name in top_bowlers:
        bowling = player.bowling
        balls = bowling['balls']
        overs = balls // 6
        remaining = balls % 6
        overs_str = f"{overs}.{remaining}" if remaining > 0 else str(overs)
        econ = (bowling['runs'] / (balls / 6)) if balls > 0 else 0
        
        html.append(f'        <h3>{player.name} | {team_name}</h3>')
        html.append('        <table>')
        html.append('            <tr><th>Overs</th><th>Maidens</th><th>Runs</th><th>Wickets</th><th>Economy</th><th>Dots</th><th>4s</th><th>6s</th><th>Wides</th><th>No Balls</th></tr>')
        html.append(f'            <tr><td>{overs_str}</td><td>{bowling["maidens"]}</td><td>{bowling["runs"]}</td><td>{bowling["wickets"]}</td><td>{econ:.2f}</td><td>{bowling["dots"]}</td><td>{bowling["4s"]}</td><td>{bowling["6s"]}</td><td>{bowling["wides"]}</td><td>{bowling["noballs"]}</td></tr>')
        html.append('        </table>')
    
    html.append('    </div>')
    
    # Partnerships
    for innings_num, innings in enumerate([innings1, innings2], 1):
        if innings.partnerships:
            html.append('    <div class="section">')
            html.append(f'        <h2>Partnerships - {innings.batting_team.name}</h2>')
            
            for partnership in innings.partnerships:
                p = format_partnership(partnership, innings.batting_team)
                wicket_label = f"{p['wicket_number']}{'st' if p['wicket_number'] == 1 else 'nd' if p['wicket_number'] == 2 else 'rd' if p['wicket_number'] == 3 else 'th'} wicket"
                
                html.append('        <div class="partnership">')
                html.append(f'            <strong>{wicket_label}: {p["total_runs"]} runs ({p["total_balls"]} balls)</strong>')
                html.append(f'            <p>{p["batter1_name"]}: {p["batter1_runs"]}({p["batter1_balls"]}) | {p["batter2_name"]}: {p["batter2_runs"]}({p["batter2_balls"]})</p>')
                html.append('        </div>')
            
            html.append('    </div>')
    
    # Charts Section
    html.append('    <div class="section">')
    html.append('        <h2>Match Charts</h2>')
    
    # Manhattan Chart
    html.append('        <div class="chart-container">')
    html.append(generate_manhattan_chart(innings1, innings2, team1_name, team2_name))
    html.append('        </div>')
    
    # Worm Chart
    html.append('        <div class="chart-container">')
    html.append(generate_worm_chart(innings1, innings2, team1_name, team2_name))
    html.append('        </div>')
    
    # Run Rate Chart
    html.append('        <div class="chart-container">')
    html.append(generate_runrate_chart(innings1, innings2, team1_name, team2_name))
    html.append('        </div>')
    
    html.append('    </div>')
    
    # Footer
    html.append('    <div style="text-align: center; padding: 20px; color: #666;">')
    html.append('        <p>Generated by Cricket Scorecard Generator</p>')
    html.append('    </div>')
    
    html.append('</body>')
    html.append('</html>')
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"HTML report generated: {filename}")
