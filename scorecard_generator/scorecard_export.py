import openpyxl

def export_scorecard_excel(filename, team1, team2, first_innings, second_innings, match_result):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Match Summary"

    # Match summary
    ws.append([f"{team1.name}: {first_innings.get_score()[0]}/{first_innings.get_score()[1]}"])
    ws.append([f"{team2.name}: {second_innings.get_score()[0]}/{second_innings.get_score()[1]}"])
    ws.append([match_result])
    ws.append([])

    # --- First Innings Batting ---
    ws.append([f"{team1.name} Batting"])
    ws.append(["Player", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"])
    for num in team1.order:
        p = team1.players[num]
        bat = p.batting
        ws.append([
            p.name, bat['dismissal'], bat['runs'], bat['balls'],
            bat['4s'], bat['6s'],
            f"{(bat['runs']/bat['balls']*100):.2f}" if bat['balls'] else "0.00"
        ])
    ws.append([])

    # --- First Innings Bowling ---
    ws.append([f"{team2.name} Bowling"])
    ws.append(["Player", "Overs", "Maidens", "Runs", "Wickets", "Dots", "4s", "6s", "Wides", "No Balls"])
    for num in team2.order:
        p = team2.players[num]
        bowl = p.bowling
        # Only show bowlers who bowled at least one ball
        if bowl['balls'] > 0:
            overs = f"{bowl['balls']//6}.{bowl['balls']%6}"
            ws.append([
                p.name, overs, bowl['maidens'], bowl['runs'], bowl['wickets'],
                bowl['dots'], bowl['4s'], bowl['6s'], bowl['wides'], bowl['noballs']
            ])
    ws.append([])

    # --- Second Innings Batting ---
    ws.append([f"{team2.name} Batting"])
    ws.append(["Player", "Dismissal", "Runs", "Balls", "4s", "6s", "SR"])
    for num in team2.order:
        p = team2.players[num]
        bat = p.batting
        ws.append([
            p.name, bat['dismissal'], bat['runs'], bat['balls'],
            bat['4s'], bat['6s'],
            f"{(bat['runs']/bat['balls']*100):.2f}" if bat['balls'] else "0.00"
        ])
    ws.append([])

    # --- Second Innings Bowling ---
    ws.append([f"{team1.name} Bowling"])
    ws.append(["Player", "Overs", "Maidens", "Runs", "Wickets", "Dots", "4s", "6s", "Wides", "No Balls"])
    for num in team1.order:
        p = team1.players[num]
        bowl = p.bowling
        if bowl['balls'] > 0:
            overs = f"{bowl['balls']//6}.{bowl['balls']%6}"
            ws.append([
                p.name, overs, bowl['maidens'], bowl['runs'], bowl['wickets'],
                bowl['dots'], bowl['4s'], bowl['6s'], bowl['wides'], bowl['noballs']
            ])
    ws.append([])

    wb.save(filename)
    print(f"Scorecard exported to {filename}")