import os
import csv
import re

def get_teams_dir():
    teams_dir = os.path.join(os.path.dirname(__file__), "../teams")
    os.makedirs(teams_dir, exist_ok=True)
    return teams_dir

def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty.")

def input_number(prompt):
    while True:
        val = input(prompt).strip()
        if val.isdigit():
            return val
        print("Please input a number.")

def input_name(prompt):
    while True:
        val = input(prompt).strip()
        if re.fullmatch(r"[A-Za-z ]+", val):
            return val
        print("Please input a valid name (letters and spaces only).")

def create_team():
    name = input_name("Enter team name: ")
    squad = []
    print("Enter players for squad (minimum 11, can add more).")
    while True:
        number = input_number(f"Player {len(squad)+1} shirt number: ")
        if any(p['number'] == number for p in squad):
            print("Shirt number already used.")
            continue
        pname = input_name("Player name and surname: ")
        squad.append({'number': number, 'name': pname})
        if len(squad) >= 11:
            more = input("Add another player? (y/n): ").strip().lower()
            if more != 'y':
                break
    save_team(name, squad)
    print(f"Team '{name}' saved.")
    return name, squad

def save_team(name, squad):
    teams_dir = get_teams_dir()
    filename = f"{name}_squad.csv"
    filepath = os.path.join(teams_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["number", "name"])
        writer.writeheader()
        writer.writerows(squad)

def load_team(name):
    teams_dir = get_teams_dir()
    filename = f"{name}_squad.csv"
    filepath = os.path.join(teams_dir, filename)
    if not os.path.isfile(filepath):
        print("Team not found.")
        return None, None
    squad = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            squad.append({'number': row['number'], 'name': row['name']})
    return name, squad

def list_teams():
    teams_dir = get_teams_dir()
    return [f[:-10] for f in os.listdir(teams_dir) if f.endswith("_squad.csv")]

def edit_team(name):
    tname, squad = load_team(name)
    if not squad:
        return
    while True:
        print(f"\nCurrent squad for {tname}:")
        for i, p in enumerate(squad):
            print(f"{i+1}. {p['number']} {p['name']}")
        print("Options: [a]dd, [e]dit, [d]elete, [b]ack")
        choice = input("Choose: ").strip().lower()
        if choice == 'a':
            number = input_number("New player shirt number: ")
            if any(p['number'] == number for p in squad):
                print("Shirt number already used.")
                continue
            pname = input_name("Player name and surname: ")
            squad.append({'number': number, 'name': pname})
        elif choice == 'e':
            idx_str = input_number("Player number to edit: ")
            idx = int(idx_str) - 1
            if idx < 0 or idx >= len(squad):
                print("Invalid index.")
                continue
            number = input_number("New shirt number: ")
            pname = input_name("New name: ")
            squad[idx] = {'number': number, 'name': pname}
        elif choice == 'd':
            if len(squad) <= 11:
                print("Cannot have fewer than 11 players!")
                continue
            idx_str = input_number("Player number to delete: ")
            idx = int(idx_str) - 1
            if idx < 0 or idx >= len(squad):
                print("Invalid index.")
                continue
            squad.pop(idx)
        elif choice == 'b':
            break
        else:
            print("Unknown option.")
    save_team(tname, squad)
    print(f"Team '{tname}' updated.")

def select_team(name):
    tname, squad = load_team(name)
    if not squad:
        return
    print(f"Select starting XI for {tname}:")
    for i, p in enumerate(squad):
        print(f"{i+1}. {p['number']} {p['name']}")
    selected = []
    while len(selected) < 11:
        idx_str = input_number(f"Select player {len(selected)+1} by number: ")
        idx = int(idx_str) - 1
        if idx < 0 or idx >= len(squad):
            print("Invalid index.")
            continue
        if idx in selected:
            print("Already selected.")
            continue
        selected.append(idx)
    # Assign captain and wicket keeper
    print("Selected XI:")
    for i, idx in enumerate(selected):
        print(f"{i+1}. {squad[idx]['number']} {squad[idx]['name']}")
    cap_idx = int(input_number("Select Captain by number (1-11): ")) - 1
    wk_idx = int(input_number("Select Wicket Keeper by number (1-11): ")) - 1
    xi = []
    for i, idx in enumerate(selected):
        role = []
        if i == cap_idx:
            role.append("c")
        if i == wk_idx:
            role.append("wk")
        xi.append({'number': squad[idx]['number'], 'name': squad[idx]['name'], 'role': ",".join(role)})
    print("\nFinal XI:")
    for p in xi:
        role_str = f"({p['role']})" if p['role'] else ""
        print(f"{p['number']} {p['name']} {role_str}")
    confirm = input("Confirm this XI? (y/n): ").strip().lower()
    if confirm == 'y':
        save_match_xi(tname, xi)
        print(f"XI saved as {tname}_XI.csv")
    else:
        print("Selection cancelled.")

def save_match_xi(name, xi):
    teams_dir = get_teams_dir()
    filename = f"{name}_XI.csv"
    filepath = os.path.join(teams_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["number", "name", "role"])
        writer.writeheader()
        writer.writerows(xi)

def run_team_manager():
    """Run the interactive team manager CLI."""
    while True:
        print("\n" + "="*70)
        print("TEAM MANAGER")
        print("="*70)
        print("1. Create new team")
        print("2. Edit team")
        print("3. Select XI for match")
        print("4. List teams")
        print("5. Quit")
        choice = input("Choose: ").strip()
        if choice == '1':
            create_team()
        elif choice == '2':
            teams = list_teams()
            if not teams:
                print("No teams available. Create one first!")
                continue
            print("Available teams:", teams)
            tname = input_nonempty("Team to edit: ")
            edit_team(tname)
        elif choice == '3':
            teams = list_teams()
            if not teams:
                print("No teams available. Create one first!")
                continue
            print("Available teams:")
            for idx, t in enumerate(teams, 1):
                print(f"{idx}. {t}")
            while True:
                sel = input_number("Select team by number: ")
                sel_idx = int(sel) - 1
                if 0 <= sel_idx < len(teams):
                    tname = teams[sel_idx]
                    break
                else:
                    print("Invalid selection.")
            select_team(tname)
        elif choice == '4':
            teams = list_teams()
            if teams:
                print("Available teams:", teams)
            else:
                print("No teams available. Create one first!")
        elif choice == '5':
            print("Returning to main menu...")
            break
        else:
            print("Unknown option.")

# Example CLI for team management
if __name__ == "__main__":
    run_team_manager()
