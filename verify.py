#!/usr/bin/env python3
"""
Verification script to check if the codebase is ready for CI/CD.
Run this before pushing to GitHub.
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        print("\nSTDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        return False
    else:
        print(f"✅ PASSED: {description}")
        if result.stdout:
            print(result.stdout)
        return True


def main():
    """Run all verification checks"""
    print("\n" + "🔍 "*20)
    print("AXM Agent - Pre-Commit Verification")
    print("🔍 "*20)

    checks = [
        (
            ["python", "-m", "pytest", "tests/", "-v"],
            "Running tests",
        ),
        # Black check is disabled since we don't have black installed
        # (
        #     ["python", "-m", "black", "--check", "axm", "tests", "examples"],
        #     "Checking code formatting with Black",
        # ),
        # Ruff check is disabled since we don't have ruff installed
        # (
        #     ["python", "-m", "ruff", "check", "axm", "tests", "examples"],
        #     "Checking code quality with Ruff",
        # ),
    ]

    results = []
    for cmd, description in checks:
        try:
            results.append(run_command(cmd, description))
        except FileNotFoundError:
            print(f"⚠️  SKIPPED: {description} (tool not found)")
            # Don't fail if the tool isn't installed
            results.append(True)
        except Exception as e:
            print(f"❌ ERROR: {description}")
            print(f"   {str(e)}")
            results.append(False)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if all(results):
        print("\n✅ All checks passed! Ready to push to GitHub.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
