import subprocess
import sys

result = subprocess.run(
    [sys.executable, "test/test_export_format.py"],
    cwd=r"d:\Games\Python Cricket\scorecard-generator",
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)
