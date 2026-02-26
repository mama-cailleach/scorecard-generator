#!/usr/bin/env python3
"""Run overs-related regression tests with PYTHONPATH configured."""

import os
import subprocess
import sys
from pathlib import Path


def run_test(script_path, env, cwd):
    print(f"\nRunning: {script_path}")
    result = subprocess.run([sys.executable, script_path], env=env, cwd=cwd)
    return result.returncode


def main():
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root)

    scripts = [
        "test/test_overs_calculation.py",
        "test/test_total_line_runout.py",
    ]

    failures = 0
    for script in scripts:
        failures += 1 if run_test(script, env, repo_root) != 0 else 0

    if failures:
        print(f"\n{failures} test(s) failed.")
        return 1

    print("\nAll overs tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
