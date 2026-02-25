# Copilot Instructions for Scorecard Generator

## Architecture Overview

**Modular structure with clear separation of concerns:**
- `models.py` — Data classes: `Player`, `Team`, `Innings`, `BallEvent` (immutable event records)
- `team_utils.py` — CSV-based team/squad persistence and XI selection
- `game_logic.py` — Ball-by-ball match simulation and event processing (280+ lines, complex)
- `input_handlers.py` — Robust user input validation (`safe_int`, `safe_choice`, `get_display_name`)
- `scorecard.py` — Scorecard formatting and display
- `scorecard_export.py` — Excel export (openpyxl) for match records
- `main.py` — Entry point: toss → XI selection → innings loop → export

**Current scope limitations:**
- `MAX_OVERS = 2` (hardcoded for testing; target: 20 overs for T20)
- `MAX_BOWLER_OVERS = 1` (hardcoded; target: 4 overs max)
- No persistence of match records beyond Excel export

## Project Organization

**Folder structure:**
- `scorecard_generator/` — Main package with all game logic and UI modules
- `teams/` — CSV files for team data and starting XIs
- `test/` — All test files (test_*.py); place all new tests here
- `docs/` — All markdown documentation; place all new docs here
- `legacy/` — Original monolithic version (archived, not maintained)

**Documentation files in `docs/`:**
- `FORMAT_IMPLEMENTATION.md` — Cricket format selection system (T20, ODI, First Class, Custom)
- `OVERS_CALCULATION_FIX.md` — Bug fix for scorecard overs display accuracy
- `FIX_SUMMARY.md` — Summary of fixes and improvements

**Test files in `test/`:**
- `test_format_config.py` — Format configuration validation
- `test_format_verification.py` — Comprehensive format logic tests
- `test_imports.py` — Module import verification
- `test_overs_calculation.py` — Overs calculation accuracy tests
- `test_bug_scenario.py` — Reproductions of specific bugs for regression testing

## Critical Data Flow

1. **Team Loading**: `load_team()` reads CSV → populates `Team.order` (batting) & `Team.bowler_order`
2. **Player Role Marking**: Store `captain_number`, `wicketkeeper_number` in Team; use `get_display_name()` for output formatting:
   - Captain only: `(c)`
   - Wicketkeeper only: `†`
   - Both: `(c)†`
3. **Ball Events**: `BallEvent(over, ball, bowler, batter, runs, event_type, fielders)`
   - Event types: `"runs"`, `"wicket"`, `"wide"`, `"no ball"`, `"bye"`, `"leg bye"`, etc.
4. **Batting Stats**: Updated per player: `runs`, `balls`, `4s`, `6s`, `SR`, `dismissal`
5. **Bowling Stats**: Aggregated per bowler via `Innings.bowler_overs` dict
6. **Extras**: Stored in `Innings.extras` defaultdict (wides, noballs, byes, leg byes)

## Key Patterns & Conventions

### Input Validation
Always use `safe_int()` or `safe_choice()` for interactive prompts:
```python
# ❌ Don't: val = int(input(...))
# ✅ Do:
val = safe_int("Enter number: ", valid=[1, 2, 3])
choice = safe_choice("Select: ", options=["a", "b", "c"])
```
Both support `"exit"` keyword to terminate program gracefully.

### Ball-by-Ball Processing
In `game_logic.py`, `process_ball_event()` handles striker/non-striker swaps:
- Runs add to striker; swap logic: `runs % 2 == 1` triggers swap
- Wickets: Increment counter, update `fall_of_wickets`, replace with next XI batter
- No-balls return 1 penalty run **plus** extras (runs + byes); **do not count as legal delivery**
- Wide/no-ball outcomes: Complex branching in `handle_no_ball_outcome()` (study before modifying)

### Dismissal Tracking
Dismissals stored as strings in `Player.batting['dismissal']`:
- Examples: `"c Jones b Patel"`, `"lbw"`, `"bowled"`, `"run out"`, `"not out"`, `"did not bat"`
- Format follows standard cricket notation

### Innings Lifecycle
Each innings tracked via `Innings` with:
- `current_batters` — [striker, non-striker] or None if still batting
- `dismissed` — list of retired players
- `did_not_bat` — XI members not selected
- `fall_of_wickets` — [(run_total, player_name, bowler_name, over_decimal), ...]

## Critical Workflows

### Adding a Feature
1. **Modify imports**: Add to `main()` or relevant module
2. **Extend models**: Update `Player`, `Team`, or `Innings` if new data needed
3. **Add logic**: Place game-changing logic in `game_logic.py`, I/O in `input_handlers.py`
4. **Update scorecard**: Modify `scorecard.py` for display; test with both batting/bowling views
5. **Excel export**: Update `scorecard_export.py` if new stats needed (import openpyxl)
6. **Test file**: Add test_*.py to `test/` folder for verification
7. **Documentation**: Add/update markdown files in `docs/` folder with implementation details

### Debugging Common Issues
- **Striker/Non-striker confusion**: Check `swapped` flag logic in ball processing (runs % 2)
- **Extras not counting**: Verify `innings.extras[type]` is incremented; don't add to `current_batter.runs` directly
- **CSV loading fails**: Ensure `teams/` folder exists and CSV has `number`, `name`, `role` headers (role optional)
- **Wicket logic**: All 10 wickets triggers `over_ended_early = True`; verify new batter selection doesn't bypass boundaries

## Installation & Running

```bash
# Install as package (editable)
pip install -e .

# Run interactive match
python -m scorecard_generator.main

# Create/manage teams
python teams_utils.py

# Basic match simulator (prototype)
python match_simulator.py
```

## External Dependencies
- `openpyxl` — Excel export (optional; scorecard still works without it, but export fails)
- No other third-party deps; uses stdlib only (csv, collections, os, sys)

## Code Style Notes
- No type hints (legacy codebase); consider `from typing import` for new code
- CSV role field: comma-separated (`"c,wk"`) if both captain and keeper
- All player selection uses order index (1-based for user input, 0-based in arrays)
- Magic numbers in `models.py`: `BALLS_PER_OVER=6`, `MAX_OVERS=2`, `MAX_BOWLER_OVERS=1` — update together when targeting full T20
