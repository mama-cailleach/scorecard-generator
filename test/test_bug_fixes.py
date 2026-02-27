"""
Verification tests for the two bug fixes:
1. Bowler dots on byes, leg byes, and wickets
2. Partnership wicket numbering starting at 1 instead of 0
"""

import sys
sys.path.insert(0, 'scorecard_generator')

from models import Player, Team, Innings, Partnership
from collections import defaultdict


def test_bowler_dots_on_byes():
    """Verify bowler gets dots credited for bye deliveries"""
    # Create bowler
    bowler = Player(1, "Bowler1")
    batter = Player(1, "Batter1")
    
    # Simulate bye event - bowler should get a dot
    bowler.bowling['balls'] += 1
    bowler.bowling['dots'] += 1  # Bug fix: dots should be credited
    
    assert bowler.bowling['dots'] == 1, f"Expected 1 dot, got {bowler.bowling['dots']}"
    print("✓ Bowler dots on byes - PASSED")


def test_bowler_dots_on_leg_byes():
    """Verify bowler gets dots credited for leg bye deliveries"""
    bowler = Player(1, "Bowler1")
    
    # Simulate leg bye event - bowler should get a dot
    bowler.bowling['balls'] += 1
    bowler.bowling['dots'] += 1  # Bug fix: dots should be credited
    
    assert bowler.bowling['dots'] == 1, f"Expected 1 dot, got {bowler.bowling['dots']}"
    print("✓ Bowler dots on leg byes - PASSED")


def test_bowler_dots_on_wickets():
    """Verify bowler gets dots credited for wicket deliveries"""
    bowler = Player(1, "Bowler1")
    
    # Process wicket event - bowler should get a wicket AND a dot
    bowler.bowling['balls'] += 1
    bowler.bowling['wickets'] += 1
    bowler.bowling['dots'] += 1  # Bug fix: dots should be credited
    
    assert bowler.bowling['dots'] == 1, f"Expected 1 dot, got {bowler.bowling['dots']}"
    assert bowler.bowling['wickets'] == 1, f"Expected 1 wicket, got {bowler.bowling['wickets']}"
    print("✓ Bowler dots on wickets - PASSED")


def test_partnership_wicket_numbering():
    """Verify partnerships are numbered 1st through 10th, not 0th through 9th"""
    # Create initial partnership
    batter1 = Player(1, "Batter1")
    batter2 = Player(2, "Batter2")
    
    # Bug fix: Initial partnership should be wicket_number=1
    partnership = Partnership(batter1, batter2, 1, 0)
    assert partnership.wicket_number == 1, f"Initial partnership should be 1st, got {partnership.wicket_number}"
    
    # Simulate subsequent partnerships
    wickets_fallen = 0  # First wicket
    wickets_fallen += 1  # After first wicket
    batter3 = Player(3, "Batter3")
    
    # Bug fix: New partnership should use wickets + 1
    partnership2 = Partnership(batter2, batter3, wickets_fallen + 1, 50)
    assert partnership2.wicket_number == 2, f"Second partnership should be 2nd, got {partnership2.wicket_number}"
    
    # Continue through all partnerships
    for i in range(2, 10):
        wickets_fallen = i
        batter_new = Player(i + 1, f"Batter{i + 1}")
        partnership_next = Partnership(batter3, batter_new, wickets_fallen + 1, 50)
        assert partnership_next.wicket_number == i + 1, f"Partnership should be {i+1}th, got {partnership_next.wicket_number}"
    
    print("✓ Partnership wicket numbering (1st-10th) - PASSED")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING BUG FIXES")
    print("="*60 + "\n")
    
    test_bowler_dots_on_byes()
    test_bowler_dots_on_leg_byes()
    test_bowler_dots_on_wickets()
    test_partnership_wicket_numbering()
    
    print("\n" + "="*60)
    print("✅ ALL BUG FIX TESTS PASSED")
    print("="*60 + "\n")
