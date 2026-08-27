"""
Day 5, Task 1 -- Testing the Mini Project via Subprocess (CLI-level testing)

CONCEPT:
Instead of importing internal functions directly, this tests the tool the way an actual USER would use it -- running the command-line script as a separate process and checking its exit code and output. A common way to test CLI tools end-to-end.
"""

import subprocess
import sys
import os

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "day4", "09_smart_text_toolkit.py")

SAMPLE_TEXT = (
    "Priya reported that the checkout page is throwing an error for "
    "international customers. She is asking if this can be prioritized "
    "before the weekend release."
)

passed = 0
failed = 0


def check(description, condition):
    global passed, failed
    if condition:
        print(f"PASS: {description}")
        passed += 1
    else:
        print(f"FAIL: {description}")
        failed += 1


def run_cli(args):
    return subprocess.run(
        [sys.executable, SCRIPT_PATH] + args,
        capture_output=True, text=True, timeout=60,
    )


if __name__ == "__main__":
    print("=== Test: summarize task runs successfully ===")
    result = run_cli(["--task", "summarize", "--text", SAMPLE_TEXT])
    check("exit code is 0", result.returncode == 0)
    check("produced non-empty output", bool(result.stdout.strip()))

    print("\n=== Test: classify task runs successfully ===")
    result = run_cli(["--task", "classify", "--text", SAMPLE_TEXT, "--categories", "Bug Report,Feature Request,Question,Other"])
    check("exit code is 0", result.returncode == 0)
    check("output mentions 'Category:'", "Category:" in result.stdout)

    print("\n=== Test: missing --task argument fails cleanly ===")
    result = run_cli(["--text", SAMPLE_TEXT])
    check("non-zero exit code on missing required arg", result.returncode != 0)

    print("\n=== Test: missing both --text and --file fails cleanly ===")
    result = run_cli(["--task", "summarize"])
    check("script exits with an error instead of crashing unhandled", result.returncode != 0)

    print(f"\n{passed} passed, {failed} failed")

    # WHAT TO OBSERVE / NOTE DOWN:
    # - Did the "missing argument" tests fail GRACEFULLY (clean argparse
    #   error) rather than crashing with an ugly traceback?
    # - Try running the actual CLI with genuinely ambiguous input (very
    #   short text) -- does extract/classify still produce valid output?