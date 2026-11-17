"""Create and update the maintenance report with a fixed layout: what the user must reply to comes first.

    python <skill>/scripts/report.py init [--new-pass]        # reuse the newest report, or create one from the template
    python <skill>/scripts/report.py path                     # print the newest report's path
    python <skill>/scripts/report.py set-section "<Heading>" < body.md   # replace one "## <Heading>" section in place
    python <skill>/scripts/report.py check                    # exit 1 on any layout problem

"init" never starts a second report while one exists; --new-pass is only for a new, separate maintenance pass.
"set-section" replaces the section's body (everything up to the next "## " heading). A section that is not
in the report yet is inserted at its fixed position. An empty body removes an optional section, so a report
only contains sections that have something to say. Headings may carry a suffix: "SOLID review (scope: core)".
"""

from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

MAINTENANCE_DIR = Path(".maintenance")
REPORT_GLOB = "maintenance-report-*.md"
GIT_EXCLUDE_PATH = Path(".git/info/exclude")
SECTION_PREFIX = "## "
REPLY_SECTION = "Needs your reply"
SECTION_ORDER = [
    "Summary",
    REPLY_SECTION,
    "What changed",
    "Dead code",
    "Verification",
    "Maintenance rules added",
    "SOLID review",
    "Folder structure",
    "Tech debt",
    "Action rounds",
    "Commits",
]
REQUIRED_SECTIONS = ["Summary", REPLY_SECTION, "What changed", "Verification", "Commits"]
REPLY_SUBSECTIONS = ["### Decide", "### Approve", "### Answer"]
MAX_TABLE_COLUMNS = 6
PLACEHOLDER = "_Not filled in yet._"
REPLY_TEMPLATE = "\n\n".join(f"{subsection}\nNone." for subsection in REPLY_SUBSECTIONS)

Section = tuple[str, str]  # (heading text after "## ", body)


def main() -> int:
    options = parse_options()
    if options.command == "init":
        print(init_report(options.new_pass))
    elif options.command == "path":
        print(require_newest_report())
    elif options.command == "set-section":
        report_path = require_newest_report()
        write_report(report_path, replace_section(read_report(report_path), options.heading, sys.stdin.read()))
        print(f"updated '{options.heading}' in {report_path}")
    elif options.command == "check":
        return print_layout_problems(layout_problems(read_report(require_newest_report())))
    return 0


def parse_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--new-pass", action="store_true")
    commands.add_parser("path")
    set_section = commands.add_parser("set-section")
    set_section.add_argument("heading")
    commands.add_parser("check")
    return parser.parse_args()


def newest_report() -> Path | None:
    reports = sorted(MAINTENANCE_DIR.glob(REPORT_GLOB), key=lambda path: path.stat().st_mtime)
    return reports[-1] if reports else None


def require_newest_report() -> Path:
    report_path = newest_report()
    if report_path is None:
        sys.exit("no report yet; run 'report.py init'")
    return report_path


def init_report(is_new_pass: bool) -> Path:
    existing = newest_report()
    if existing is not None and not is_new_pass:
        return existing
    MAINTENANCE_DIR.mkdir(exist_ok=True)
    exclude_maintenance_dir_from_git()
    report_path = MAINTENANCE_DIR / f"maintenance-report-{datetime.date.today().isoformat()}.md"
    write_report(report_path, render_template(project_name()))
    return report_path


def exclude_maintenance_dir_from_git() -> None:
    if not GIT_EXCLUDE_PATH.parent.is_dir():
        return
    rule = f"{MAINTENANCE_DIR}/"
    current_rules = GIT_EXCLUDE_PATH.read_text(encoding="utf-8") if GIT_EXCLUDE_PATH.is_file() else ""
    if rule not in current_rules.splitlines():
        GIT_EXCLUDE_PATH.write_text(current_rules.rstrip("\n") + f"\n{rule}\n", encoding="utf-8")


def project_name() -> str:
    completed = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    return Path(completed.stdout.strip() or ".").resolve().name


def render_template(project: str) -> str:
    """Only the required sections; optional ones appear when 'set-section' gives them content."""
    sections = [
        f"{SECTION_PREFIX}{heading}\n{REPLY_TEMPLATE if heading == REPLY_SECTION else PLACEHOLDER}\n"
        for heading in REQUIRED_SECTIONS
    ]
    return f"# Maintenance report: {project}\n\n" + "\n".join(sections)


def read_report(report_path: Path) -> str:
    return report_path.read_text(encoding="utf-8")


def write_report(report_path: Path, text: str) -> None:
    report_path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")


def split_sections(text: str) -> tuple[str, list[Section]]:
    """(title block, [(heading, body)]) where heading is the text after '## '."""
    title, *chunks = text.split(f"\n{SECTION_PREFIX}")
    sections = []
    for chunk in chunks:
        heading, _, body = chunk.partition("\n")
        sections.append((heading.strip(), body))
    return title, sections


def join_sections(title: str, sections: list[Section]) -> str:
    return title.rstrip("\n") + "\n\n" + "\n".join(f"{SECTION_PREFIX}{heading}\n{body.strip(chr(10))}\n" for heading, body in sections)


def canonical_name(heading: str) -> str:
    """'SOLID review (scope: core)' -> 'SOLID review'. A heading outside the fixed layout is its own name."""
    return next((name for name in SECTION_ORDER if heading.startswith(name)), heading)


def layout_rank(heading: str) -> int:
    """Position in the fixed layout. Headings outside the layout sort after every known section."""
    name = canonical_name(heading)
    return SECTION_ORDER.index(name) if name in SECTION_ORDER else len(SECTION_ORDER)


def find_section(sections: list[Section], heading: str) -> int | None:
    wanted = canonical_name(heading)
    return next((index for index, (name, _) in enumerate(sections) if canonical_name(name) == wanted), None)


def replace_section(text: str, heading: str, new_body: str) -> str:
    title, sections = split_sections(text)
    index = find_section(sections, heading)
    is_empty = not new_body.strip()
    if is_empty and canonical_name(heading) in REQUIRED_SECTIONS:
        sys.exit(f"'{heading}' is a required section and cannot be empty")
    if index is not None and is_empty:
        del sections[index]
    elif index is not None:
        sections[index] = (heading, new_body)
    elif not is_empty:
        later_sections = (position for position, (name, _) in enumerate(sections) if layout_rank(name) > layout_rank(heading))
        sections.insert(next(later_sections, len(sections)), (heading, new_body))
    return join_sections(title, sections)


def layout_problems(text: str) -> list[str]:
    _, sections = split_sections(text)
    problems = [f"missing section: {heading}" for heading in REQUIRED_SECTIONS if find_section(sections, heading) is None]
    ranks = [layout_rank(name) for name, _ in sections]
    if ranks != sorted(ranks):
        problems.append(f"sections are out of order; the fixed order is: {', '.join(SECTION_ORDER)}")
    reply_index = find_section(sections, REPLY_SECTION)
    if reply_index is not None:
        if reply_index != 1:
            problems.append(f"'{REPLY_SECTION}' must be the second section, directly after Summary")
        reply_body = sections[reply_index][1]
        problems += [f"'{REPLY_SECTION}' lacks '{subsection}' (write 'None.' under it if empty)" for subsection in REPLY_SUBSECTIONS if subsection not in reply_body]
    for name, body in sections:
        if PLACEHOLDER in body:
            problems.append(f"section not filled in: {name}")
        widest = widest_table(body)
        if widest > MAX_TABLE_COLUMNS:
            problems.append(f"table with {widest} columns in '{name}' (max {MAX_TABLE_COLUMNS}); move detail below the table")
    return problems


def widest_table(body: str) -> int:
    """Largest column count of any markdown table row outside code fences."""
    widest = 0
    is_in_code_fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            is_in_code_fence = not is_in_code_fence
        elif not is_in_code_fence and stripped.startswith("|") and stripped.endswith("|"):
            widest = max(widest, stripped.replace("\\|", "").count("|") - 1)
    return widest


def print_layout_problems(problems: list[str]) -> int:
    for problem in problems:
        print(f"LAYOUT: {problem}")
    print("layout ok" if not problems else f"{len(problems)} layout problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
