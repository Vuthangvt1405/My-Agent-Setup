"""Create and update the maintenance report with a fixed layout: Open questions always last.

    python <skill>/scripts/report.py init [--new-pass]        # reuse the newest report, or create one from the template
    python <skill>/scripts/report.py path                     # print the newest report's path
    python <skill>/scripts/report.py set-section "<Heading>" < body.md   # replace one "## <Heading>" section in place
    python <skill>/scripts/report.py check                    # exit 1 if a section is missing, out of order, or not last

"init" never starts a second report while one exists; --new-pass is only for a new, separate maintenance pass.
"set-section" replaces the section's body (everything up to the next "## " heading). A heading not in the
template is inserted just above "Open questions", so nothing can ever end up after it.
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
LAST_SECTION = "Open questions"
REQUIRED_SECTIONS = [
    "Summary",
    "What changed: folder tree after maintenance",
    "Dead code removed",
    "Kept (false positives - whitelisted)",
    "Needs your decision (uncertain / test-only)",
    "Verification",
    "Maintenance rules added",
    "SOLID review",
    "Folder structure",
    "Tech debt found",
    "Proposed action plan (for your review)",
    "Action rounds",
    "Commits",
    LAST_SECTION,
]
PLACEHOLDER = "_Not filled in yet._"
OPEN_QUESTIONS_TEMPLATE = "### Answered\nNone yet.\n\n### Still open\nNone."


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
    sections = [
        f"{SECTION_PREFIX}{heading}\n{OPEN_QUESTIONS_TEMPLATE if heading == LAST_SECTION else PLACEHOLDER}\n"
        for heading in REQUIRED_SECTIONS
    ]
    return f"# Maintenance report: {project}\n\n" + "\n".join(sections)


def read_report(report_path: Path) -> str:
    return report_path.read_text(encoding="utf-8")


def write_report(report_path: Path, text: str) -> None:
    report_path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(title block, [(heading, body)]) where heading is the text after '## '."""
    title, *chunks = text.split(f"\n{SECTION_PREFIX}")
    sections = []
    for chunk in chunks:
        heading, _, body = chunk.partition("\n")
        sections.append((heading.strip(), body))
    return title, sections


def join_sections(title: str, sections: list[tuple[str, str]]) -> str:
    return title.rstrip("\n") + "\n\n" + "\n".join(f"{SECTION_PREFIX}{heading}\n{body.strip(chr(10))}\n" for heading, body in sections)


def replace_section(text: str, heading: str, new_body: str) -> str:
    title, sections = split_sections(text)
    index = find_section(sections, heading)
    if index is not None:
        sections[index] = (sections[index][0], new_body)
    else:
        open_questions_index = find_section(sections, LAST_SECTION)
        insert_at = len(sections) if open_questions_index is None else open_questions_index
        sections.insert(insert_at, (heading, new_body))
    return join_sections(title, sections)


def find_section(sections: list[tuple[str, str]], heading: str) -> int | None:
    """Matches on the start of the heading, so 'SOLID review' finds 'SOLID review (scope: ...)'."""
    return next((index for index, (name, _) in enumerate(sections) if name.startswith(heading)), None)


def layout_problems(text: str) -> list[str]:
    _, sections = split_sections(text)
    problems = [f"missing section: {heading}" for heading in REQUIRED_SECTIONS if find_section(sections, heading) is None]
    positions = [find_section(sections, heading) for heading in REQUIRED_SECTIONS]
    found_positions = [position for position in positions if position is not None]
    if found_positions != sorted(found_positions):
        problems.append("required sections are out of order")
    is_open_questions_last = bool(sections) and sections[-1][0].startswith(LAST_SECTION)
    if not is_open_questions_last:
        problems.append(f"'{LAST_SECTION}' must be the last section")
    return problems


def print_layout_problems(problems: list[str]) -> int:
    for problem in problems:
        print(f"LAYOUT: {problem}")
    print("layout ok" if not problems else f"{len(problems)} layout problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
