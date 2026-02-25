#!/usr/bin/env python3
"""Import test to verify all modules load correctly"""

try:
    print("Testing imports...")
    
    from scorecard_generator.models import (
        Player, Team, Innings, BallEvent, 
        CRICKET_FORMATS, BALLS_PER_OVER, MAX_OVERS, MAX_BOWLER_OVERS
    )
    print("✓ models.py imports successful")
    
    from scorecard_generator.input_handlers import (
        safe_int, safe_choice, get_display_name, 
        select_openers, select_bowler, select_format
    )
    print("✓ input_handlers.py imports successful")
    
    from scorecard_generator.game_logic import play_innings
    print("✓ game_logic.py imports successful")
    
    from scorecard_generator.team_utils import choose_team_xi
    print("✓ team_utils.py imports successful")
    
    from scorecard_generator.scorecard import print_batting_scorecard, print_bowling_scorecard
    print("✓ scorecard.py imports successful")
    
    from scorecard_generator.scorecard_export import export_scorecard_excel
    print("✓ scorecard_export.py imports successful")
    
    print("\n=== All imports successful ===")
    print("\nFormat constants loaded:")
    print(f"  CRICKET_FORMATS keys: {list(CRICKET_FORMATS.keys())}")
    print(f"  BALLS_PER_OVER: {BALLS_PER_OVER}")
    print(f"  MAX_OVERS (legacy): {MAX_OVERS}")
    print(f"  MAX_BOWLER_OVERS (legacy): {MAX_BOWLER_OVERS}")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)

print("\n=== Import Test Passed ===")
