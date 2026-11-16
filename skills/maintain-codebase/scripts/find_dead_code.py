"""Run Vulture and collect the evidence for every finding in one triage table.

The script does the searching; the AI only fills in the Classification column
(Remove / False positive / Uncertain). Run it from the repository root:

    python <skill>/scripts/find_dead_code.py [--min-confidence 60] [--out .maintenance/triage.md]

Vulture's paths, excludes and whitelist come from [tool.vulture] in pyproject.toml.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MIN_CONFIDENCE = 60
DEFAULT_REPORT_PATH = Path(".maintenance/triage.md")
VULTURE_LINE = re.compile(r"^(?P<path>[^:]+):(?P<line>\d+): (?P<message>.+?) \((?P<confidence>\d+)% confidence")
QUOTED_NAME = re.compile(r"'([^']+)'")
DYNAMIC_ACCESS = re.compile(r"getattr|setattr|hasattr|import_module|globals\(\)|__all__")
IMPLICIT_CALLER_DECORATORS = ("@pytest.fixture", "@app.", "@router.", "@cl.", "@click.", "@property", "@abstractmethod", "@override")
MAX_SHOWN_REFERENCES = 5
DEFINITION_SPAN_LINES = 4  # Vulture reports a decorated def at its first decorator line


@dataclass
class Finding:
    path: str
    line: int
    message: str
    confidence: int
    name: str


@dataclass
class Evidence:
    python_references: list[str] = field(default_factory=list)
    other_references: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)


def main() -> int:
    options = parse_options()
    findings = run_vulture(options.min_confidence)
    rows = [(finding, gather_evidence(finding)) for finding in findings]
    write_triage_table(rows, options.out)
    print(f"{len(findings)} findings -> {options.out}")
    return 0


def parse_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-confidence", type=int, default=DEFAULT_MIN_CONFIDENCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


def run_vulture(min_confidence: int) -> list[Finding]:
    completed = subprocess.run(
        [sys.executable, "-m", "vulture", "--min-confidence", str(min_confidence)],
        capture_output=True, text=True, check=False,
    )
    has_bad_input = completed.returncode in (1, 2)
    if has_bad_input:
        sys.exit(f"vulture failed:\n{completed.stderr or completed.stdout}")
    return [finding for line in completed.stdout.splitlines() if (finding := parse_vulture_line(line))]


def parse_vulture_line(line: str) -> Finding | None:
    match = VULTURE_LINE.match(line)
    if match is None:
        return None
    quoted = QUOTED_NAME.search(match["message"])
    name = quoted.group(1) if quoted else ""
    return Finding(match["path"], int(match["line"]), match["message"], int(match["confidence"]), name)


def gather_evidence(finding: Finding) -> Evidence:
    evidence = Evidence()
    for reference in search_repository(finding.name):
        if is_own_definition(reference, finding):
            continue
        target = evidence.python_references if reference.split(":", 1)[0].endswith(".py") else evidence.other_references
        target.append(reference)
    evidence.hints = implicit_use_hints(finding, evidence)
    return evidence


def is_own_definition(reference: str, finding: Finding) -> bool:
    path, line_text, content = reference.split(":", 2)
    is_near_reported_line = path == finding.path and 0 <= int(line_text) - finding.line < DEFINITION_SPAN_LINES
    defines_the_name = re.search(rf"\b(def|class)\s+{re.escape(finding.name)}\b|^\s*{re.escape(finding.name)}\s*[:=]", content)
    return is_near_reported_line and (int(line_text) == finding.line or defines_the_name is not None)


def search_repository(name: str) -> list[str]:
    if not name:
        return []
    completed = subprocess.run(["git", "grep", "-n", "-w", "-I", "--", name, ":(exclude).maintenance"], capture_output=True, text=True, check=False)
    return completed.stdout.splitlines()


def implicit_use_hints(finding: Finding, evidence: Evidence) -> list[str]:
    hints: list[str] = []
    if finding.name.startswith("__") and finding.name.endswith("__"):
        hints.append("dunder")
    decorator = decorator_above(Path(finding.path), finding.line)
    if decorator:
        hints.append(f"decorated {decorator}")
    if any(DYNAMIC_ACCESS.search(reference) for reference in evidence.python_references):
        hints.append("dynamic access nearby")
    if finding.path.endswith("__init__.py"):
        hints.append("package __init__ (re-export?)")
    if evidence.other_references:
        hints.append("named outside Python")
    return hints


def decorator_above(source_path: Path, line_number: int) -> str:
    try:
        lines = source_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    nearby_lines = [line.strip() for line in lines[max(line_number - 2, 0):line_number + DEFINITION_SPAN_LINES - 1]]
    return next((prefix for line in nearby_lines for prefix in IMPLICIT_CALLER_DECORATORS if line.startswith(prefix)), "")


def write_triage_table(rows: list[tuple[Finding, Evidence]], report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Vulture triage",
        "",
        "Fill in Classification: Remove / False positive / Uncertain. Evidence columns are filled by the script.",
        "",
        "| # | Location | Finding | Conf. | .py refs | Other refs | Hints | Classification |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for number, (finding, evidence) in enumerate(rows, start=1):
        lines.append(
            f"| {number} | `{finding.path}:{finding.line}` | {finding.message} | {finding.confidence}% "
            f"| {format_references(evidence.python_references)} | {format_references(evidence.other_references)} "
            f"| {', '.join(evidence.hints) or '-'} | |"
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_references(references: list[str]) -> str:
    if not references:
        return "0"
    shown = "<br>".join(f"`{reference.split(':', 2)[0]}:{reference.split(':', 2)[1]}`" for reference in references[:MAX_SHOWN_REFERENCES])
    more = f"<br>+{len(references) - MAX_SHOWN_REFERENCES} more" if len(references) > MAX_SHOWN_REFERENCES else ""
    return f"{len(references)}: {shown}{more}"


if __name__ == "__main__":
    sys.exit(main())
