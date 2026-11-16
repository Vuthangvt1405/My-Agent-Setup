"""Measure every package folder against the three folder limits and list what breaks them.

    python <skill>/scripts/folder_sizes.py <package_root> [<package_root> ...] [--ignore <glob> ...]

--ignore skips folders whose layout a framework decides (for example '*/migrations/versions').

Limits (references/structure-and-debt.md, "Size limits"):
  width   5-9 entries per folder is healthy; over 12 is a finding
  rule of three   a subfolder needs at least 3 Python files
  depth   at most 4 levels below the package root
Exit code 1 when any folder breaks a limit, 0 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_HEALTHY_WIDTH = 9
MAX_WIDTH = 12
MIN_FILES_PER_SUBFOLDER = 3
MAX_DEPTH = 4
IGNORED_NAMES = {"__pycache__", "node_modules", ".venv", ".git", ".mypy_cache", ".ruff_cache", ".pytest_cache"}


@dataclass
class FolderMeasure:
    path: Path
    entries: int
    python_files: int
    depth: int


def main() -> int:
    options = parse_options()
    measures = [
        measure for root in options.package_roots for measure in measure_tree(root)
        if not any(measure.path.match(pattern) for pattern in options.ignore)
    ]
    findings = [finding for measure in measures for finding in limit_findings(measure)]
    print_measures(measures)
    print_findings(findings)
    return 1 if findings else 0


def parse_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("package_roots", nargs="+", type=Path)
    parser.add_argument("--ignore", action="append", default=[], help="glob of folders to skip")
    return parser.parse_args()


def measure_tree(root: Path) -> list[FolderMeasure]:
    folders = [root, *sorted(path for path in root.rglob("*") if path.is_dir() and not is_ignored(path))]
    return [measure_folder(folder, root) for folder in folders]


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_NAMES or part.startswith(".") for part in path.parts)


def measure_folder(folder: Path, root: Path) -> FolderMeasure:
    entries = [entry for entry in folder.iterdir() if not is_ignored(entry) and entry.name != "__init__.py"]
    python_files = [entry for entry in entries if entry.suffix == ".py"]
    return FolderMeasure(folder, len(entries), len(python_files), len(folder.relative_to(root).parts))


def limit_findings(measure: FolderMeasure) -> list[str]:
    findings: list[str] = []
    if measure.entries > MAX_WIDTH:
        findings.append(f"{measure.path}: {measure.entries} entries (width limit {MAX_WIDTH})")
    is_subfolder = measure.depth > 0
    holds_only_files = measure.entries == measure.python_files
    if is_subfolder and holds_only_files and measure.python_files < MIN_FILES_PER_SUBFOLDER:
        findings.append(f"{measure.path}: {measure.python_files} Python files (rule of three)")
    if measure.depth > MAX_DEPTH:
        findings.append(f"{measure.path}: depth {measure.depth} (limit {MAX_DEPTH})")
    return findings


def print_measures(measures: list[FolderMeasure]) -> None:
    print("| Folder | Entries | .py files | Depth | Width |\n|---|---|---|---|---|")
    for measure in measures:
        print(f"| `{measure.path}` | {measure.entries} | {measure.python_files} | {measure.depth} | {width_label(measure.entries)} |")


def width_label(entries: int) -> str:
    if entries > MAX_WIDTH:
        return "over limit"
    return "wide" if entries > MAX_HEALTHY_WIDTH else "ok"


def print_findings(findings: list[str]) -> None:
    print("\nFindings:" if findings else "\nAll folders within limits.")
    for finding in findings:
        print(f"- {finding}")


if __name__ == "__main__":
    sys.exit(main())
