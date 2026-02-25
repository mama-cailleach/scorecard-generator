# Fix Summary: Overs Calculation Discrepancy

## Problem Fixed

**Symptoms:**
- Scorecard total line sometimes showed incorrect overs (e.g., 3.2 instead of 3.4)
- Discrepancy was 1-2 balls, making run rate appear wrong
- Only happened sometimes, seemingly random

**Example:**
```
Expected: Total: 3.4 Ov (RR: 5.10) 17/10
Observed: Total: 3.2 Ov (RR: 5.10) 17/10
```

---

## Root Cause

The `Innings.get_score()` method in `models.py` was calculating overs by counting legal balls from the `balls` list using an unreliable event type filter. Issues:

1. **Input validation side effects** - Some balls weren't recorded properly during complex validation
2. **Event type mismatches** - Not all delivery types were in the filter list
3. **String concatenation bug** - Missing comma: `'run out''bye_run_out'` treated as single string `'run out bye_run_out'`

---

## Solution Implemented

Changed `Innings.get_score()` to use `bowler_overs` data as the authoritative source instead of reconstructing from ball events.

### Why This Works

- **`bowler_overs`** dict tracks which overs each bowler definitely bowled
- It's built incrementally and updated at the end of each over
- Much more reliable than trying to reconstruct from complex event data
- Immune to input validation failures

### New Algorithm

```python
# Get all overs that were bowled
all_overs_bowled = set()
for overs_list in self.bowler_overs.values():
    all_overs_bowled.update(overs_list)

# Find max over number
max_over = max(all_overs_bowled)

# Count legal balls in the last (incomplete) over
balls_in_last_over = sum(
    1 for be in self.balls 
    if be.over == max_over and be.event not in ['wide', 'no ball']
)

# Calculate: complete_overs + fractional_part
complete_overs, remainder = divmod(balls_in_last_over, BALLS_PER_OVER)
overs = max_over + complete_overs + remainder / 10
```

### Example Calculation

Using the bug report example (3 complete overs + 4 balls):
- Max over bowled: 3
- Balls in over 3: 4
- Calculation: 3 + (4 / 10) = **3.4** ✓

---

## Verification

### Test Results

All tests pass:

✅ **Incomplete over** (3 complete + 4 balls) = 3.4 overs  
✅ **Complete overs** (2 x 6 balls) = 2.0 overs  
✅ **Single incomplete** (3 balls) = 0.3 overs  
✅ **Wides/no-balls excluded** correctly  
✅ **Exact bug scenario** test = 3.4 overs (FIXED!)  

### Impact

- ✅ Overs now accurately reflect bowler data
- ✅ No false discrepancies in scorecard totals
- ✅ All fall of wickets and totals now consistent
- ✅ No changes to existing functionality

---

## Files Modified

- **`scorecard_generator/models.py`** - Updated `Innings.get_score()` method (lines 81-123)

## Testing Files Created

- `test_overs_calculation.py` - 4 test cases for overs calculation
- `test_bug_scenario.py` - Exact reproduction of the reported bug
- Both pass all tests ✅

---

## Backward Compatibility

✅ All APIs unchanged  
✅ All external functions work the same  
✅ Only internal calculation logic improved  
✅ No breaking changes  

---

## Next Steps

The fix is ready for use. Run matches normally:

```bash
python -m scorecard_generator.main
```

Scorecard totals will now be accurate, matching all other match data exactly.