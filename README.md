# Cricket T20 Scorecard Generator

A console-based Python application for creating and analyzing detailed cricket T20 scorecards.  
**Modular, professional Python codebase** for learning, coaching, match recording, and fun.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Team CSV File Format](#team-csv-file-format)
- [Match Simulation](#match-simulation)
- [Example Output](#example-output)
- [Changelog / Recent Improvements](#changelog--recent-improvements)
- [Legacy Version](#legacy-version)
- [To Improve / TODO](#to-improve--todo)
- [Portfolio Note](#portfolio-note)

---

## Features

### Modular Design

- **All main match logic split into dedicated Python modules** (`scorecard_generator/`):
    - `models.py` — data classes for teams, players, innings, ball events
    - `team_utils.py` — XI loading and match utility functions
    - `input_handlers.py` — all robust user input and ball-by-ball prompts
    - `game_logic.py` — match/innings logic and event processing
    - `scorecard.py` — scorecard formatting and output
    - `scorecard_export.py` — Excel export for full match scorecards (batting & bowling)
    - `main.py` — entry point for playing a match

### Team Management

- **Interactive team/squad management with `teams_utils.py` in the main folder**:
    - Create/edit teams and squads, enforce unique shirt numbers
    - Add more than 11 players per squad for flexible selection
    - Assign captain and wicketkeeper roles, saved in CSV
    - Select and save starting XIs for matches
    - Teams and XIs saved as CSVs in `teams/`

### Match Play & Scorecard Generation

- **Interactive, robust match input:**
    - Select openers and bowlers from loaded XIs
    - Input every ball (runs, wickets, extras, byes, leg byes, robust no-ball logic)
    - Accurate striker/non-striker swap logic
    - Friendly, error-resilient prompts

- **Professional scorecard output:**
    - Batting and bowling scorecards with correct cricket notation
    - Displays (c) for captain, † for wicketkeeper
    - Handles all edge cases: early over/innings ends, did-not-bat, etc.
    - **Exports full match scorecard (batting & bowling for both innings) to Excel**

### Match Simulation

- **Basic match simulator with `match_simulator.py`**:
    - Early prototype/draft for testing scorecard functionality
    - Loads teams from CSV files
    - Uses a simple preset sequence of cricket events or follows provided match data
    - Generates basic match results and scorecards

### Legacy Support

- The old monolithic script is preserved in a `legacy/` folder for historical context.

---

## Project Structure

```
scorecard-generator/
│
├── teams_utils.py                  # Interactive team/squad manager (run to create/edit teams, pick XIs)
├── match_simulator.py              # Basic match simulator prototype for testing
├── teams/                          # Folder for team and XI CSVs
│
├── scorecard_generator/
│   ├── __init__.py
│   ├── main.py                     # Main entry point for a match
│   ├── models.py                   # Data structures (Team, Player, Innings, BallEvent)
│   ├── team_utils.py               # XI loader and team utility functions (for match play only)
│   ├── input_handlers.py           # All robust user input and validation logic
│   ├── game_logic.py               # Core match/innings logic (ball-by-ball processing)
│   ├── scorecard.py                # Output and formatting for batting/bowling scorecards
│   ├── scorecard_export.py         # Excel export for match scorecards
│
├── legacy/
│   └── scorecard_generator.py      # The original all-in-one script (not maintained)
│
├── setup.py                        # Package setup configuration
├── README.md
```

---

## Installation

### Installation as a Package

The project can be installed as a Python package:

```bash
# From the scorecard-generator directory
pip install -e .
```

### Manual Setup

Alternatively, you can run scripts directly without installation:

1. Clone the repository
2. Navigate to the `scorecard-generator` directory
3. Run scripts as shown in the Usage section

---

## Usage

### 1. Team Management & Squad Selection

- **Run the team/squad manager:**
  ```bash
  python teams_utils.py
  ```
  - Create/edit teams and squads
  - Assign captains and wicketkeepers
  - Select and save starting XI for a match
  - Teams and XIs saved as CSVs in `teams/`

### 2. Run the Scorecard Generator

- **Play a match using the modular system:**
  ```bash
  # If installed as a package:
  python -m scorecard_generator.main
  
  # Or, run directly:
  python scorecard_generator/main.py
  ```
  - Loads XIs from CSV
  - Prompts for toss, openers, bowlers, and each ball
  - Shows professional scorecards at innings end
  - **Automatically exports a full match scorecard (batting & bowling for both innings) to Excel (`scorecard_generator/exports/scorecard.xlsx`)**

### 3. Run the Match Simulator

- **Run the basic match simulator:**
  ```bash
  python match_simulator.py
  ```
  - Prompts for two team CSV files
  - Simulates a basic match using predefined events
  - Displays scorecards and match result
  - Exports the match scorecard to Excel

---

## Team CSV File Format

Teams and starting XIs are stored as CSV files in the `teams/` folder.

**Format:**  
```
number,name,role
16,Jos Buttler,"c,wk"
18,Virat Kohli,"c"
7,MS Dhoni,"wk"
33,Player Name,
```
- `number`: Player's shirt number (unique within team)
- `name`: Full player name
- `role`: Optional (`c`, `wk`, or both as `c,wk`)

Roles are displayed as:
- Captain only: `(c)`
- Wicketkeeper only: `†`
- Captain & wicketkeeper: `(c)†`
- Example:  
  `16 Jos Buttler (c)†`  
  `7 MS Dhoni †`  
  `18 Virat Kohli (c)`

---

## Match Simulation

The `match_simulator.py` script provides a basic match simulation prototype:

- **Current implementation:**
  - Loads two teams from CSV files
  - Simulates two innings with predefined ball events
  - Uses the same core logic as the interactive version
  - Outputs basic match results and scorecards
  - **Exports the match scorecard (batting & bowling for both innings) to Excel**

- **Functionality:**
  - Simple sequence of test events (boundaries, wickets, extras)
  - Basic match result calculation
  - Integration with the scorecard display functions
  - Demonstrates the scorecard generator's capabilities

- **Usage:** Run `python match_simulator.py` and follow prompts to provide team file names

> Note: The match simulator is currently in early development as a proof of concept. It uses a fixed set of events rather than realistic simulation, primarily serving as a test harness for the scorecard generator.

---

## Example Output

```
Batting: Team A
Player Name         Dismissal                Runs Balls 4s  6s     SR
Jos Buttler (c)†    c Jones b Patel             35    27  4   2  129.63
...
Extras                                         11
Total: 2.0 Ov (RR: 7.80) 156/6
Did not bat: Bob, Carol, Eve
Fall of wickets:
 1-22 (Patel, 0.3 ov), 2-45 (Jones, 1.1 ov), ...
...
Bowling: Team B
Bowler              Overs Maidens Runs Wkts  Econ Dots 4s 6s Wides Noballs
Kevin Patel         1.0      0    15   2   7.50    3   1  0     1      0
...
```

**Excel Export Example:**  
After each match, a file like `scorecard_generator/exports/scorecard.xlsx` is created, containing:
- Match summary and result
- Batting and bowling scorecards for both innings

---

## Changelog / Recent Improvements

- **Excel export:** Full match scorecard (batting & bowling for both innings) exported automatically after each match
- **Bowling scorecard in Excel:** Bowling stats now included for both innings in the export
- **Full modular refactor:** Logic split into `models.py`, `team_utils.py`, `input_handlers.py`, `game_logic.py`, and `scorecard.py`
- **Robust team manager:** `teams_utils.py` for team and squad management (main folder)
- **Basic match simulator:** Added `match_simulator.py` prototype for testing the scorecard functions
- **Improved input validation:** All ball-by-ball and selection input is robust, clear, and error-resilient
- **Edge case handling:** Striker/non-striker swaps, early over/innings ends, did-not-bat, etc.
- **Package structure:** Added `setup.py` for proper Python package installation
- **Legacy support:** Original monolithic script in `legacy/`

---

## Legacy Version

- The original, all-in-one script (`legacy/scorecard_generator.py`) is included for reference and historical context.
- **All new features and improvements are in the modular version.**
- The legacy file is not maintained or recommended for use.

---

## To Improve / TODO

- Full 20-over support and automatic match result calculation
- Fine tune the correct logic for legal deliveries and possibilities
- Export scorecards to file (txt/CSV/JSON)
- Support for ODI/Test match formats
- More summary statistics and user guidance
- Optional integration with external cricket data APIs
- Unit/integration tests and CI setup
- Web interface for easier use and visualization
- **Project Independence:** Development will continue in a standalone repository separate from this portfolio

---

## Portfolio Note

This project demonstrates:
- **Refactoring from procedural to modular Python**
- **Best practices in user input, data validation, and code organization**
- **Growth as a developer, see both the monolithic and modern modular versions**
- **Python package structure and organization**

While this project was developed as part of the Cisco Python Essentials 2 course portfolio, it has grown beyond its original scope. **Future development will continue in a dedicated repository**, where it will evolve into a more comprehensive cricket statistics and simulation tool with additional features from the TODO list.

Feel free to explore the [Python Portfolio](https://github.com/mama-cailleach/python-portfolio/) for more projects and evolution of coding style.

---

*Part of the [Python Portfolio](https://github.com/mama-cailleach/python-portfolio/) — Cisco Python Essentials 2*

*Last updated: 2025-07-
