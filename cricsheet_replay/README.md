# Cricsheet CSV Replay

This module allows you to "reverse engineer" Cricsheet CSV files into a live ball-by-ball match replay with full scorecard generation and export.

## Overview

The replay script reads Cricsheet's standardized info and ball-by-ball CSV files, reconstructs the match in memory, displays it ball-by-ball in the terminal, and exports it using the same export system as the interactive match simulator.

## Usage

### Command Line (Recommended)

```powershell
python cricsheet_replay/replay.py <info_csv_path> <ballbyball_csv_path>
```

**Example:**
```powershell
python cricsheet_replay/replay.py cricsheet_info/1432444_info.csv cricsheet_info/1432444.csv
```

### Interactive Mode

Run without arguments to be prompted for file paths:

```powershell
python cricsheet_replay/replay.py
```

## Features

### What it does:
- ✅ Parses Cricsheet info CSV for match metadata and player lists
- ✅ Auto-assigns player numbers (1-11) based on info CSV order
- ✅ Reads ball-by-ball CSV and converts to internal BallEvent format
- ✅ Displays live ball-by-ball commentary in terminal
- ✅ Shows full batting and bowling scorecards after each innings
- ✅ Exports match data to CSV files (scorecard, info, ball-by-ball)

### Limitations (Cricsheet data gaps):
- ❌ Captain/wicketkeeper not specified → set to placeholders
- ❌ Fielder names for catches → shown as "Unknown"
- ❌ Some wicket details may be generic

## Output

### Terminal Display

The script prints:
1. Match header (teams, venue, date)
2. Ball-by-ball commentary for each innings
3. Batting scorecard (runs, balls, 4s, 6s, SR, dismissals)
4. Bowling scorecard (overs, maidens, runs, wickets, economy, extras)

### Exported Files

All files are saved to `scorecard_generator/exports/`:

- `{Team1}v{Team2}_scorecard.csv` - Batting/bowling stats
- `{Team1}v{Team2}_info.csv` - Match metadata
- `{Team1}v{Team2}_ballbyball.csv` - Ball-by-ball data

## Example Output

```
======================================================================
Innings 1: New Zealand batting
======================================================================

  0.1 - M Kapp to SW Bates - 1 run(s)
  0.2 - M Kapp to GE Plimmer - dot ball
  0.3 - M Kapp to GE Plimmer - dot ball
  0.4 - M Kapp to GE Plimmer - FOUR!
  ...

Batting: New Zealand
Player Name         Dismissal                 Runs Balls  4s  6s     SR
SW Bates            b Mlaba                     32    30   3   0 106.67
GE Plimmer          c Unknown b Khaka            9     7   2   0 128.57
...

Total: 20 Ov (RR: 7.78) 158/5
```

## Data Format

The script expects Cricsheet "Ashwin" CSV format (version 2+):

### Info CSV columns:
- `version`, `info`, metadata keys/values
- Player lists: `info,player,{team},{player_name}`

### Ball-by-ball CSV columns:
- `match_id`, `season`, `start_date`, `venue`, `innings`, `ball`
- `batting_team`, `bowling_team`, `striker`, `non_striker`, `bowler`
- `runs_off_bat`, `extras`, `wides`, `noballs`, `byes`, `legbyes`, `penalty`
- `wicket_type`, `player_dismissed`, `other_wicket_type`, `other_player_dismissed`

## Integration

The replay script integrates with existing scorecard-generator modules:

- [scorecard_generator/models.py](../scorecard_generator/models.py) - Uses Team, Player, Innings, BallEvent
- [scorecard_generator/scorecard.py](../scorecard_generator/scorecard.py) - Calls display functions
- [scorecard_generator/scorecard_export.py](../scorecard_generator/scorecard_export.py) - Uses export_all()

## Requirements

- Python 3.7+
- Standard library only (csv, collections, pathlib)
- scorecard-generator package installed (parent directory)

## Notes

- Player numbers are auto-assigned 1-11 in the order they appear in the info CSV
- Missing fielder/captain/keeper info is filled with placeholders ("Unknown" or None)
- The replay is non-interactive (no prompts during ball-by-ball)
- Exports match the same format as the interactive match simulator

## Getting Cricsheet Data

Download Cricsheet CSV files from: https://cricsheet.org/

Look for matches in the "Ashwin" CSV format (version 2+).
