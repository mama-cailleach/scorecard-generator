# Export System Overhaul

## Overview

The export system has been completely rewritten to generate three CSV files in Cricsheet-compatible format, replacing the previous Excel-based export.

## Implementation Date

February 25, 2026

## Problem Statement

The original export system had several critical issues:

1. **Innings Ordering Bug**: Assumed `team1` always batted first, causing incorrect scorecard display when `team2` batted first
2. **Format Limitations**: Excel-only format not compatible with cricket data standards
3. **Limited Metadata**: No structured match information format
4. **No Ball-by-Ball Data**: Missing detailed event-level export capability

## Solution

### New Export Functions

The new `scorecard_export.py` provides four main functions:

1. **`export_scorecard_csv()`** - Traditional scorecard format
   - Shows batting and bowling statistics for both innings
   - Uses `innings.batting_team` and `innings.bowling_team` for correct ordering
   - CSV format for easy parsing

2. **`export_match_info_csv()`** - Cricsheet info format
   - Version 2.2.0 compatible
   - Stores match metadata (teams, players, outcome)
   - Placeholder "N/A" values for unimplemented fields (match_id, season, venue, etc.)

3. **`export_ball_by_ball_csv()`** - Cricsheet ball-by-ball format
   - 21-column format matching Cricsheet specification
   - Tracks every delivery with runs, extras, wickets
   - Separates runs_off_bat from extras (wides, noballs, byes, legbyes)

4. **`export_all()`** - Main export function
   - Calls all three export functions
   - Generates dynamic filenames: `Team1vTeam2_exporttype.csv`
   - Creates exports directory if needed

### Helper Functions

- **`sanitize_filename(name)`** - Removes invalid filename characters
- **`get_export_filename(team1, team2, export_type)`** - Generates standardized filenames

## Key Bug Fix: Innings Ordering

### The Problem

Original code (WRONG):
```python
def export_scorecard_excel(filename, team1, team2, first_innings, second_innings, match_result):
    # ...
    ws.append([f"{team1.name} Batting"])  # ❌ Assumes team1 batted first
    for num in team1.order:  # ❌ Wrong when team2 batted first
```

When `team2` won the toss and batted first:
- `first_innings.batting_team = team2`
- But export showed `team1` batting first
- Scorecard displayed in wrong order

### The Solution

New code (CORRECT):
```python
def export_scorecard_csv(filename, team1, team2, first_innings, second_innings, match_result):
    # Use innings.batting_team/bowling_team for correct ordering
    batting_team_1 = first_innings.batting_team  # ✓ Actual batting team
    bowling_team_1 = first_innings.bowling_team  # ✓ Actual bowling team
    
    writer.writerow([f"{batting_team_1.name} Batting"])  # ✓ Correct order
    for num in batting_team_1.order:  # ✓ Correct team's batters
```

Now the export always reflects the actual innings order, regardless of parameter order.

## Cricsheet Format Compatibility

### Info CSV Format

```csv
version,2.2.0
info,match_id,N/A
info,season,N/A
info,team_type,international
info,match_type,T20
info,gender,male
info,teams,Team1,Team2
info,player,Player Name,Team Name
info,outcome,Team1 wins by 5 wickets
```

### Ball-by-Ball CSV Format

21-column header:
```csv
match_id,season,start_date,venue,innings,ball,batting_team,bowling_team,striker,non_striker,bowler,runs_off_bat,extras,wides,noballs,byes,legbyes,penalty,wicket_type,player_dismissed,other_wicket_type,other_player_dismissed
```

Each ball event is recorded with:
- Over.ball number (e.g., "1.3")
- Batting/bowling team names
- Striker, non-striker, bowler
- Runs separated: runs_off_bat vs extras
- Breakdown of extras by type (wides, noballs, byes, legbyes)
- Wicket information if applicable

## Export Filenames

Dynamic filenames based on team names:
- Scorecard: `Team1vTeam2_scorecard.csv`
- Info: `Team1vTeam2_info.csv`
- Ball-by-ball: `Team1vTeam2_ballbyball.csv`

Special characters are sanitized (spaces → underscores, special chars removed).

## Testing

### Test Suite: `test/test_export_format.py`

Comprehensive test coverage including:

1. **`test_sanitize_filename()`** - Filename cleaning
2. **`test_get_export_filename()`** - Filename generation
3. **`test_innings_ordering()`** - **Critical**: Verifies bug fix for innings ordering
4. **`test_scorecard_csv_format()`** - Traditional scorecard structure
5. **`test_match_info_csv_format()`** - Cricsheet info compatibility
6. **`test_ball_by_ball_csv_format()`** - Cricsheet ball-by-ball compatibility
7. **`test_export_all()`** - Integration test for all exports

### Test Verification

The innings ordering test specifically validates:
- When team2 bats first, Team B appears first in scorecard
- Bowling sections match correct opposing teams
- All sections use `innings.batting_team`/`innings.bowling_team`

## Migration Notes

### Breaking Changes

1. **Import change** in `main.py`:
   ```python
   # Old:
   from .scorecard_export import export_scorecard_excel
   
   # New:
   from .scorecard_export import export_all
   ```

2. **Function call change**:
   ```python
   # Old:
   export_scorecard_excel("scorecard_generator/exports/scorecard.xlsx", 
                          team1, team2, innings1, innings2, match_result)
   
   # New:
   export_all(team1, team2, innings1, innings2, match_result)
   ```

3. **Dependency change**:
   - No longer requires `openpyxl`
   - Uses only Python stdlib (`csv`, `os`, `re`)

### File Outputs

Old: Single Excel file `exports/scorecard.xlsx`

New: Three CSV files:
- `exports/Team1vTeam2_scorecard.csv`
- `exports/Team1vTeam2_info.csv`
- `exports/Team1vTeam2_ballbyball.csv`

## Future Enhancements

Current "N/A" placeholders can be replaced with real data:

1. **match_id** - Generate UUID or sequential ID
2. **season** - Add season field to match input
3. **start_date** - Add date selection
4. **venue, city** - Add venue selection
5. **toss_winner, toss_decision** - Already tracked in game logic, needs plumbing
6. **non_striker** - Track in ball events (currently not stored)

## References

- Cricsheet format specification: https://cricsheet.org
- Example files: `cricsheet_info/1432444.csv`, `cricsheet_info/1432444_info.csv`
- Test suite: `test/test_export_format.py`

## Related Files

- `scorecard_generator/scorecard_export.py` - Implementation (281 lines)
- `scorecard_generator/main.py` - Integration (lines 4, 89)
- `test/test_export_format.py` - Test suite (365 lines)
- `.github/copilot-instructions.md` - AI guidance (updated with export info)
