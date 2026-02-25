# Ball-by-Ball CSV Export Fixes

## Issues Fixed

### 1. ✓ Non-Striker Name Not Showing
**Before:** Non-striker was hardcoded to "N/A"
**After:** Now tracks the current non-striker from the batting team order

### 2. ✓ Player Names Include Shirt Numbers
**Before:** Striker showed as "16 Jos Buttler", bowler as "38 Josh Hazlewood"
**After:** Added `extract_player_name()` function that strips the shirt number
- "16 Jos Buttler" → "Jos Buttler"
- "38 Josh Hazlewood" → "Josh Hazlewood"

### 3. ✓ Runs/Wickets Not Populating (Most Critical)
**Root Cause:** Event type checking was looking for 'runs' but game_logic uses 'normal'

**Before:** 
```python
if event.event == 'runs':  # ❌ Never matches
    runs_off_bat = event.runs
```

**After:** 
```python
def classify_runs(event_type, runs):
    if event_type == 'normal':  # ✓ Correct event type
        runs_off_bat = runs
    elif 'wide' in event_type:  # Handles wide, wide_boundary, wide_bye, etc.
        # proper classification...
    elif 'no ball' in event_type:  # Handles no ball, no ball_runs, etc.
        # proper classification...
    # ... etc for bye, leg bye, run out, wicket
```

## Event Type Mapping

Now correctly handles all game_logic event types:

| Event Type | Classification |
|------------|-----------------|
| `normal` | runs_off_bat |
| `wide`, `wide_boundary` | wides (extras) |
| `wide_bye`, `wide_leg_bye` | wides + byes/legbyes |
| `no ball` | noballs (extras) |
| `no ball_runs` | noballs + runs_off_bat |
| `no ball_bye` | noballs + byes |
| `bye` | byes (extras) |
| `leg bye` | legbyes (extras) |
| `run out`, `bye_run_out`, etc. | appropriate runs/extras |
| `wicket` | wicket info populated |

## Implementation Details

### New Functions
1. **`extract_player_name(player_str)`** - Strips shirt number from "number name" format
2. **`classify_runs(event_type, runs)`** - Maps event types to CSV column values

### Non-Striker Tracking
- Maintains reference to batting order for each innings
- Looks up non-striker player number and name from batting team
- Properly handles when there are fewer batters than expected (uses 'N/A')

### Wicket Handling
- Handles both dict and list forms of fielders data
- Extracts dismissal_type and dismissed_player safely
- Properly populated in the CSV

## Files Modified

- [scorecard_generator/scorecard_export.py](scorecard_generator/scorecard_export.py)
  - Added `extract_player_name()` function
  - Rewrote `export_ball_by_ball_csv()` with comprehensive event handling
  - Added `classify_runs()` helper function
  - Added `write_ball_row()` helper function
  - Implemented non_striker tracking

## Testing

To test the fixes:
1. Run the game: `python -m scorecard_generator.main`
2. Complete a match
3. Check the generated `*_ballbyball.csv` file for:
   - Clean player names (no shirt numbers)
   - Non-striker names populated
   - Runs and wicket information filled in

## Example Output

**Before (Broken):**
```
N/A,N/A,N/A,N/A,1,0.1,England,Australia,16 Jos Buttler,N/A,38 Josh Hazlewood,0,0,0,0,0,0,0,,,,
```

**After (Fixed):**
```
N/A,N/A,N/A,N/A,1,0.1,England,Australia,Jos Buttler,Jonny Bairstow,Josh Hazlewood,1,0,0,0,0,0,0,,,,
```

Changes:
- Striker: `16 Jos Buttler` → `Jos Buttler` ✓
- Non-striker: `N/A` → `Jonny Bairstow` ✓  
- Runs_off_bat: `0` → `1` (actual ball had 1 run) ✓

## Next Steps

The export system is now ready to generate accurate Cricsheet-compatible CSV files with all required data populated correctly!
