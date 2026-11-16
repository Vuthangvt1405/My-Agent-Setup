"""Run the same checks every time and compare them with the baseline.

Run it from the repository root, with the project's own Python (so the project's tools are found):

    .venv/bin/python <skill>/scripts/verify.py baseline   # Phase 0: record the starting state
    .venv/bin/python <skill>/scripts/verify.py compare    # Phase 2: after every batch; exit 1 on any regression

Checks: compileall, import smoke test, ruff, mypy (only if configured), vulture, pytest.
Optional settings in .maintenance/checks.toml:

    packages = ["researchchat", "app"]   # importable names; default: top-level packages found
    pytest_args = ["-q"]                 # default: ["-q"]; add ["-m", "not docker"] to skip slow suites
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

MAINTENANCE_DIR = Path(".maintenance")
BASELINE_PATH = MAINTENANCE_DIR / "baseline.json"
SETTINGS_PATH = MAINTENANCE_DIR / "checks.toml"
DEFAULT_PYTEST_ARGS = ["-q"]
IGNORED_TOP_LEVEL_DIRS = {"tests", "test", "docs", "scripts", "node_modules", "build", "dist"}
PYTEST_COUNT = re.compile(r"(\d+) (passed|failed|errors?|skipped|deselected)")
RUFF_LINE = re.compile(r"^(?P<path>[^:]+):\d+:\d+: (?P<rest>.+)$")
MAX_LISTED_NEW_ISSUES = 20


@dataclass
class CheckResults:
    compile_ok: bool = False
    imports_ok: bool = False
    ruff_issues: list[str] = field(default_factory=list)
    mypy_errors: int | None = None
    vulture_findings: int = 0
    tests: dict[str, int] = field(default_factory=dict)


def main() -> int:
    mode = parse_mode()
    settings = load_settings()
    current = run_all_checks(settings)
    if mode == "baseline":
        save_baseline(current)
        print_table(None, current)
        return 0
    baseline = load_baseline()
    print_table(baseline, current)
    regressions = find_regressions(baseline, current)
    for regression in regressions:
        print(f"REGRESSION: {regression}")
    return 1 if regressions else 0


def parse_mode() -> str:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=["baseline", "compare"])
    return parser.parse_args().mode


def load_settings() -> dict:
    settings = tomllib.loads(SETTINGS_PATH.read_text(encoding="utf-8")) if SETTINGS_PATH.is_file() else {}
    settings.setdefault("packages", find_top_level_packages())
    settings.setdefault("pytest_args", DEFAULT_PYTEST_ARGS)
    return settings


def find_top_level_packages() -> list[str]:
    packages = [
        folder.name for folder in sorted(Path(".").iterdir())
        if folder.is_dir() and (folder / "__init__.py").is_file() and folder.name not in IGNORED_TOP_LEVEL_DIRS
    ]
    return packages or [path.stem for path in sorted(Path(".").glob("*.py"))]


def run_all_checks(settings: dict) -> CheckResults:
    packages: list[str] = settings["packages"]
    return CheckResults(
        compile_ok=run_quietly(["-m", "compileall", "-q", *existing_paths(packages)]).returncode == 0,
        imports_ok=run_quietly(["-c", "; ".join(f"import {package}" for package in packages)]).returncode == 0,
        ruff_issues=collect_ruff_issues(),
        mypy_errors=count_mypy_errors() if is_mypy_configured() else None,
        vulture_findings=len(run_quietly(["-m", "vulture"]).stdout.splitlines()),
        tests=collect_test_counts(settings["pytest_args"]),
    )


def run_quietly(python_arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *python_arguments], capture_output=True, text=True, check=False)


def existing_paths(packages: list[str]) -> list[str]:
    candidates = [Path(package) for package in packages] + [Path(f"{package}.py") for package in packages]
    return [str(path) for path in candidates if path.exists()]


def collect_ruff_issues() -> list[str]:
    """Issues as 'path: CODE message', line numbers dropped, so moved lines don't count as new issues."""
    output = run_quietly(["-m", "ruff", "check", ".", "--output-format", "concise", "-q"]).stdout
    return sorted(f"{match['path']}: {match['rest']}" for line in output.splitlines() if (match := RUFF_LINE.match(line)))


def is_mypy_configured() -> bool:
    pyproject = Path("pyproject.toml")
    has_pyproject_section = pyproject.is_file() and "[tool.mypy]" in pyproject.read_text(encoding="utf-8")
    return has_pyproject_section or Path("mypy.ini").is_file()


def count_mypy_errors() -> int:
    return run_quietly(["-m", "mypy", "."]).stdout.count(": error:")


def collect_test_counts(pytest_args: list[str]) -> dict[str, int]:
    summary_line = run_quietly(["-m", "pytest", *pytest_args]).stdout.strip().splitlines()[-1:]
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "deselected": 0}
    for number, kind in PYTEST_COUNT.findall(summary_line[0] if summary_line else ""):
        counts["errors" if kind.startswith("error") else kind] = int(number)
    return counts


def save_baseline(results: CheckResults) -> None:
    MAINTENANCE_DIR.mkdir(exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(asdict(results), indent=1), encoding="utf-8")
    print(f"baseline saved to {BASELINE_PATH}")


def load_baseline() -> CheckResults:
    if not BASELINE_PATH.is_file():
        sys.exit(f"no baseline at {BASELINE_PATH}; run 'verify.py baseline' first")
    return CheckResults(**json.loads(BASELINE_PATH.read_text(encoding="utf-8")))


def find_regressions(baseline: CheckResults, current: CheckResults) -> list[str]:
    regressions: list[str] = []
    if baseline.compile_ok and not current.compile_ok:
        regressions.append("compileall now fails")
    if baseline.imports_ok and not current.imports_ok:
        regressions.append("import smoke test now fails")
    new_ruff_issues = sorted(set(current.ruff_issues) - set(baseline.ruff_issues))
    regressions += [f"new ruff issue: {issue}" for issue in new_ruff_issues[:MAX_LISTED_NEW_ISSUES]]
    if baseline.mypy_errors is not None and (current.mypy_errors or 0) > baseline.mypy_errors:
        regressions.append(f"mypy errors {baseline.mypy_errors} -> {current.mypy_errors}")
    if current.vulture_findings > baseline.vulture_findings:
        regressions.append(f"vulture findings {baseline.vulture_findings} -> {current.vulture_findings}")
    regressions += test_regressions(baseline.tests, current.tests)
    return regressions


def test_regressions(baseline_tests: dict[str, int], current_tests: dict[str, int]) -> list[str]:
    broken_before = baseline_tests.get("failed", 0) + baseline_tests.get("errors", 0)
    broken_now = current_tests.get("failed", 0) + current_tests.get("errors", 0)
    regressions = [f"failing tests {broken_before} -> {broken_now}"] if broken_now > broken_before else []
    if current_tests.get("passed", 0) < baseline_tests.get("passed", 0):
        regressions.append(f"passing tests {baseline_tests['passed']} -> {current_tests.get('passed', 0)}")
    return regressions


def print_table(baseline: CheckResults | None, current: CheckResults) -> None:
    rows = [
        ("compileall", describe_ok, "compile_ok"),
        ("imports", describe_ok, "imports_ok"),
        ("ruff issues", len, "ruff_issues"),
        ("mypy errors", describe_optional, "mypy_errors"),
        ("vulture findings", str, "vulture_findings"),
        ("pytest", describe_tests, "tests"),
    ]
    print("| Check | Baseline | Now |\n|---|---|---|")
    for label, describe, attribute in rows:
        before = describe(getattr(baseline, attribute)) if baseline else "-"
        print(f"| {label} | {before} | {describe(getattr(current, attribute))} |")


def describe_ok(is_ok: bool) -> str:
    return "ok" if is_ok else "FAIL"


def describe_optional(value: int | None) -> str:
    return "not configured" if value is None else str(value)


def describe_tests(counts: dict[str, int]) -> str:
    return ", ".join(f"{count} {kind}" for kind, count in counts.items() if count) or "no tests"


if __name__ == "__main__":
    sys.exit(main())
