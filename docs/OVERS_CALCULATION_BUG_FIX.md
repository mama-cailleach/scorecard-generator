# Bug Fix: Incorrect Overs Count with No Ball and Wide Variants

## Problem
When a match had wides or no balls followed by additional deliveries, the overs count was displayed incorrectly. For example:
- **Expected:** `1 Ov` (1 complete over)
- **Observed:** `1.1 Ov` (1 over + 1 extra ball)

This affected displays like:
- Match Summary: "1st Innings: Australia | 1.1 Ov | 23/0"
- Scorecard Total Line: "Total: 1.0 Ov" (conflicting display)

## Root Cause

The `Innings.get_score()` method in [models.py](scorecard_generator/models.py) was using exact string matching to filter out wide and no-ball deliveries:

```python
balls_in_last_over = sum(
    1 for be in self.balls 
    if be.over == max_over and be.event not in ['wide', 'no ball']
)
```

**Problem:** This only excluded events exactly matching `'wide'` and `'no ball'`, but NOT their variants:
- `'wide_boundary'` - wide with 4 or 6 runs
- `'wide_bye'` - wide followed by byes
- `'wide_leg_bye'` - wide followed by leg byes
- `'no ball_runs'` - no ball followed by batter runs (1-6)
- `'no ball_bye'` - no ball followed by byes
- `'no ball_leg_bye'` - no ball followed by leg byes

When a no ball was followed by runs (e.g., user enters "1" after "nb"), the event type was set to `'no ball_runs'`, which was **not** filtered out. This extra delivery was counted as a legal ball, inflating the overs count by 0.1.

## Solution

Changed the filtering logic to use `startswith()` like the scorecard display does:

**Before:**
```python
balls_in_last_over = sum(
    1 for be in self.balls 
    if be.over == max_over and be.event not in ['wide', 'no ball']
)
```

**After:**
```python
balls_in_last_over = sum(
    1 for be in self.balls 
    if be.over == max_over and not (
        be.event.startswith('wide') or 
        be.event.startswith('no ball')
    )
)
```

This correctly excludes all wide and no-ball variants:
- `be.event.startswith('wide')` → filters out: `'wide'`, `'wide_boundary'`, `'wide_bye'`, `'wide_leg_bye'`, `'wide_run_out'`
- `be.event.startswith('no ball')` → filters out: `'no ball'`, `'no ball_runs'`, `'no ball_bye'`, `'no ball_leg_bye'`, `'no ball_run_out'`

Also applied the same fix to the fallback calculation when bowler_overs data is unavailable.

## Impact

- ✅ **Match Summary** now displays correct overs (e.g., `1 Ov` instead of `1.1 Ov`)
- ✅ **Scorecard totals** consistent with fall of wickets and bowler statistics
- ✅ **Run rate calculations** accurate (uses correct overs denominator)
- ✅ **All existing tests** pass with no regressions

## Files Modified

- **scorecard_generator/models.py**
  - Updated `Innings.get_score()` method (lines 130-143)
  - Changed exact match to `startswith()` for both primary and fallback overs calculations

## Test Coverage

Created comprehensive test in `test/test_no_ball_runs_overs.py`:
- ✅ No ball with runs (`no ball_runs`) correctly excluded
- ✅ Wide with boundary (`wide_boundary`) correctly excluded
- ✅ Wide with byes (`wide_bye`) correctly excluded

All tests pass with the fix applied.

## Example Scenario

**First Innings (from bug report):**
```
Balls bowled:
0.1: 1 run (normal)
0.2: 1 run (normal)
0.3: 2 runs (normal)
0.4: wide (penalty only)
0.4: 6 runs (normal) - after wide
0.5: 4 runs (normal)
0.6: no ball (penalty only)
0.6: 6 runs (normal) - after no ball

Legal deliveries: 6 (0.1, 0.2, 0.3, 0.4 after wide, 0.5, 0.6 after no ball)
Overs: 1.0 ✓
```

**Before Fix:**
- The '0.6 after no ball' was recorded as event_type=`'no ball_runs'`
- Event type `'no ball_runs'` was NOT filtered out
- Total counted: 7 deliveries → 1.1 overs ✗

**After Fix:**
- Event type `'no ball_runs'` is filtered out (starts with 'no ball')
- Total counted: 6 deliveries → 1.0 overs ✓
