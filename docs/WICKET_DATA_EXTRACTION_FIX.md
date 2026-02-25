# Wicket Data Extraction Fix

## Issue
Wicket information was **not being captured** in the ball-by-ball CSV export, even though dismissals were correctly recorded in the scorecard.

**Example from test output:**
- Scorecard showed: `David Warner,b Wood` (dismissal recorded)
- Ball-by-ball CSV showed: empty wicket_type and player_dismissed columns

## Root Cause
The `fielders` data structure in `BallEvent` is a **list with complex structure**, not a simple dict. The export code was trying to extract it as a dict, which failed silently.

### Fielders Data Structure (from game_logic.py)

Depending on dismissal type:

| Dismissal Type | Fielders Structure | Example |
|---|---|---|
| Bowled | `[bowler_name]` | `["Josh Hazlewood"]` |
| Caught | `[(fielder_info, _, False)]` | `[("Alex Carey", None, False)]` |
| Caught & Bowled | `[(bowler_name, _, True)]` | `[("Josh Hazlewood", None, True)]` |
| LBW | `["lbw", something]` | `["lbw", None]` |
| Stumped | `[wicketkeeper_name, ...]` | `["Alex Carey", None]` |
| Run Out | List or empty | Varies |

## Solution
Rewrote the wicket extraction logic in `write_ball_row()` to:

1. **Check if event is a wicket**: Look for `'wicket' in event.event`
2. **Decode the fielders list** to determine dismissal type:
   ```python
   if event.fielders[0] == "lbw":
       wicket_type = "lbw"
   elif isinstance(event.fielders[0], tuple):
       # Check if caught & bowled flag (index 2)
       if event.fielders[0][2]:
           wicket_type = "caught and bowled"
       else:
           wicket_type = "caught"
   elif first_elem == event.bowler:
       wicket_type = "bowled"
   else:
       wicket_type = "run out"
   ```
3. **Extract dismissed player**: Always the batter (`extract_player_name(event.batter)`)
4. **Handle run-out events**: Also check for run-out event types that are NOT stored as "wicket"
   ```python
   elif event.event in ["run out", "bye_run_out", "leg_bye_run_out", "wide_run_out", "no ball_run_out"]:
       wicket_type = "run out"
   ```

## Code Changes

### Before (Broken)
```python
wicket_type = ''
player_dismissed = ''
if 'wicket' in event.event and event.fielders:
    if isinstance(event.fielders, dict):  # ❌ fielders is a LIST, not dict!
        wicket_type = event.fielders.get('dismissal_type', '')
        player_dismissed = event.fielders.get('dismissed_player', '')
```

### After (Fixed)
```python
wicket_type = ''
player_dismissed = extract_player_name(event.batter)

if 'wicket' in event.event and event.fielders:
    if isinstance(event.fielders, list) and len(event.fielders) > 0:
        first_elem = event.fielders[0]
        
        # LBW case
        if first_elem == "lbw":
            wicket_type = "lbw"
        
        # Caught/caught & bowled - tuple format
        elif isinstance(first_elem, tuple):
            if len(first_elem) >= 3 and first_elem[2]:
                wicket_type = "caught and bowled"
            else:
                wicket_type = "caught"
        
        # Bowled or run out - string format
        elif isinstance(first_elem, str):
            if first_elem == event.bowler:
                wicket_type = "bowled"
            else:
                wicket_type = "run out"

# Also handle run-out event types
elif event.event in ["run out", "bye_run_out", ...]:
    wicket_type = "run out"
```

## Expected Output

### Before (Broken)
```csv
...player_name,,,,,... (wicket columns empty)
```

### After (Fixed)
```csv
...Jos Buttler,bowled,... (wicket type and player_dismissed populated)
...Travis Head,caught and bowled,...
```

## Testing

To verify the fix:
1. Run: `python test_wickets_export.py`
2. Check the generated CSV for populated wicket_type columns
3. Run a full match and verify wickets appear in `*_ballbyball.csv`

## Files Modified

- [scorecard_generator/scorecard_export.py](scorecard_generator/scorecard_export.py)
  - Rewrote `write_ball_row()` function
  - Fixed wicket data extraction logic
  - Now handles all dismissal types from game_logic

## Related Documentation

- [BALLBYBALL_CSV_FIXES.md](BALLBYBALL_CSV_FIXES.md) - Previous fixes (player names, non_striker)
- [game_logic.py](../../scorecard_generator/game_logic.py#L215) - Where wicket events are created
