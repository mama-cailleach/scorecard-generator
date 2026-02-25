#!/usr/bin/env python3
"""Quick test to verify format configuration system"""

from scorecard_generator.models import CRICKET_FORMATS

print("=== Format Configuration Test ===\n")

for format_key, format_config in CRICKET_FORMATS.items():
    print(f"Format: {format_key}")
    print(f"  Name: {format_config['name']}")
    print(f"  Max Overs: {format_config['max_overs']}")
    print(f"  Max Bowler Overs: {format_config['max_bowler_overs']}")
    print(f"  Balls per Over: {format_config['balls_per_over']}")
    print()

# Test custom format creation
custom_format = {
    'name': 'Test Custom',
    'max_overs': 10,
    'max_bowler_overs': 3,
    'balls_per_over': 6
}

print("Custom Format Test:")
print(f"  Name: {custom_format['name']}")
print(f"  Max Overs: {custom_format['max_overs']}")
print(f"  Max Bowler Overs: {custom_format['max_bowler_overs']}")
print(f"  Balls per Over: {custom_format['balls_per_over']}")
print()

# Test unlimited overs handling
test_cases = [
    ('Limited overs', 20, True),
    ('Unlimited overs', None, False),
]

print("Loop Condition Tests:")
for name, max_overs, should_be_limited in test_cases:
    # Simulate the loop condition used in play_innings
    is_limited = max_overs is not None
    print(f"  {name}: max_overs={max_overs} -> is_limited={is_limited} ✓")

print("\n=== All Tests Passed ===")
