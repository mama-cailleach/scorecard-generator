import sys, os, csv
from scorecard_generator.models import Player, Team

def list_xi_files():
    teams_dir = os.path.join(os.path.dirname(__file__), "../teams")
    if not os.path.isdir(teams_dir):
        return []
    return [f for f in os.listdir(teams_dir) if f.endswith("_XI.csv")]

def load_xi(filepath):
    players = []
    wicketkeeper_number = None
    captain_number = None
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            number = int(row['number'])
            name = row['name']
            role = row.get('role', '').strip().lower() if 'role' in row else ''
            players.append({'number': number, 'name': name})
            if 'wk' in role.split(','):
                wicketkeeper_number = number
            if 'c' in role.split(','):
                captain_number = number
    return players, wicketkeeper_number, captain_number

def choose_team_xi(label):
    xi_files = list_xi_files()
    if not xi_files:
        print("No starting XI files found. Please use the team manager to create/select your teams.")
        sys.exit(1)
    print(f"\nAvailable starting XIs for {label} team:")
    for idx, fname in enumerate(xi_files, 1):
        print(f"{idx}. {fname}")
    while True:
        sel = input(f"Select {label} team by number: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(xi_files):
            xi_file = xi_files[int(sel)-1]
            break
        print("Invalid selection.")
    team_name = xi_file[:-7]
    xi_path = os.path.join(os.path.dirname(__file__), "../teams", xi_file)
    players, wicketkeeper_number, captain_number = load_xi(xi_path)
    team = Team(team_name)
    order = []
    for p in players:
        team.add_player(Player(p['number'], p['name']))
        order.append(p['number'])
    team.order = order
    team.wicketkeeper_number = wicketkeeper_number
    team.captain_number = captain_number
    return team