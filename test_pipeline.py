"""
test_pipeline.py — Headless smoke tests for the pipeline (no GUI required).

Runs three test suites against the synthetic data in test_data/:
  1. Validation-only pass  — confirms all files are readable and well-formed
  2. Full pipeline run     — exercises the complete progress report workflow
  3. Semester groups run   — verifies the semester-configured groups path
                             (bypasses control file entirely)

Usage:
    python test_pipeline.py
    python generate_test_data.py && python test_pipeline.py  # regenerate first
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from processors.pipeline_controller import PipelineController, PipelineInputs
from utils.logging_utils import setup_logger

logger = setup_logger("test_pipeline")

TEST_DIR = Path(__file__).parent / "test_data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PASS = "✅ PASS"
FAIL = "❌ FAIL"

results = []


def run_test(name: str, fn) -> bool:
    print(f"\n{'─' * 55}")
    print(f"  {name}")
    print(f"{'─' * 55}")
    try:
        ok = fn()
        tag = PASS if ok else FAIL
        print(f"\n  Result: {tag}")
        results.append((name, ok))
        return ok
    except Exception:
        print(f"\n  Uncaught exception:")
        traceback.print_exc()
        results.append((name, False))
        return False


def log_cb(msg: str) -> None:
    print(f"    → {msg}")


# ---------------------------------------------------------------------------
# Shared inputs (control-file path)
# ---------------------------------------------------------------------------
def base_inputs(**overrides) -> PipelineInputs:
    defaults = dict(
        progress_report=TEST_DIR / "progress_report.xlsx",
        contact_report=TEST_DIR / "contact_report.xlsx",
        control_file=TEST_DIR / "control.txt",
        group_dir=TEST_DIR / "groups",
        output_dir=OUTPUT_DIR,
    )
    defaults.update(overrides)
    return PipelineInputs(**defaults)


# ---------------------------------------------------------------------------
# Test 1 — Validation only
# ---------------------------------------------------------------------------
def test_validation():
    result = PipelineController(progress_callback=log_cb).validate_only(base_inputs())
    if result.errors:
        for e in result.errors:
            print(f"    ERROR: {e}")
    for w in result.warnings:
        print(f"    WARN:  {w}")
    return result.success


# ---------------------------------------------------------------------------
# Test 2 — Full pipeline run (control file path)
# ---------------------------------------------------------------------------
def test_full_run():
    result = PipelineController(progress_callback=log_cb).run(base_inputs())
    if result.success:
        print(f"    Output: {result.output_path}")
        print("    Metrics:")
        for k, v in result.metrics.items():
            print(f"      {k}: {v}")
    else:
        print(f"    FAILED: {result.message}")
        for e in result.errors:
            print(f"    ERROR: {e}")
    return result.success


# ---------------------------------------------------------------------------
# Test 3 — Semester groups path (no control file)
# Reads the same group Excel files but passes them as [{name, file_path}]
# dicts, bypassing the control.txt entirely.
# ---------------------------------------------------------------------------
def test_semester_groups():
    groups_dir = TEST_DIR / "groups"
    semester_groups = [
        {"name": "Athletes", "file_path": str(groups_dir / "athletes.xlsx")},
        {"name": "Probation", "file_path": str(groups_dir / "probation.xlsx")},
        {"name": "Honors", "file_path": str(groups_dir / "honors.xlsx")},
        {"name": "International", "file_path": str(groups_dir / "international.xlsx")},
    ]

    inputs = PipelineInputs(
        progress_report=TEST_DIR / "progress_report.xlsx",
        contact_report=TEST_DIR / "contact_report.xlsx",
        control_file=Path("."),  # unused — semester_groups takes precedence
        group_dir=Path("."),  # unused
        output_dir=OUTPUT_DIR,
        semester_groups=semester_groups,
    )

    result = PipelineController(progress_callback=log_cb).run(inputs)
    if result.success:
        print(f"    Output: {result.output_path}")
        assigned = result.metrics.get("total_assigned", "?")
        unmatched = result.metrics.get("total_unmatched", "?")
        print(f"    Assigned: {assigned}  |  Unmatched: {unmatched}")
    else:
        print(f"    FAILED: {result.message}")
        for e in result.errors:
            print(f"    ERROR: {e}")
    return result.success


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 55)
    print("  Academic Intervention Sorter — Pipeline Tests")
    print("=" * 55)

    if not TEST_DIR.exists():
        print(
            f"\n⚠  test_data/ not found. Run first:\n"
            f"       python generate_test_data.py\n"
        )
        return 1

    run_test("1. Validation-only pass", test_validation)
    run_test("2. Full pipeline run", test_full_run)
    run_test("3. Semester groups (no control file)", test_semester_groups)

    # Summary
    print(f"\n{'=' * 55}")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"  Results: {passed}/{total} passed")
    for name, ok in results:
        print(f"    {'✅' if ok else '❌'}  {name}")
    print("=" * 55)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
