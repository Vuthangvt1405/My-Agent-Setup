---
name: maintain-codebase
description: Maintain a Python codebase - find and remove dead code with Vulture, verify nothing broke (tests, imports, lint, types), lock in maintenance rules, and review/refactor the code against the SOLID principles. Use this skill whenever the user asks to maintain, clean up, tidy, prune, or refactor a Python project, remove dead/unused code, unused imports, functions, classes or variables, run vulture, reduce tech debt, check or enforce SOLID, or says things like "clean this repo", "what code is unused", "is this still used", or "make this codebase healthier", even if they never mention Vulture or SOLID by name.
---

# Maintain a Python codebase

A four-phase maintenance pass: **remove dead code → verify → lock in rules → SOLID review**. The order matters. Deleting dead code first shrinks the surface you have to reason about, so the SOLID review is done on code that actually runs.

Two principles drive everything below:

1. **Vulture's output is a list of suspects, not a verdict.** It matches names across the files you give it and ignores scope, so dynamic Python (`getattr`, framework hooks, entry points, plugins, templates) produces false positives. Every finding below 100% confidence needs evidence before deletion.
2. **Behaviour must not change.** This is maintenance. Each change is small, verified, and revertible. If you cannot verify a change, do not make it silently; report it.

## Phase 0 - Preflight

Before touching anything:

- **Git state.** Run `git status`. If the tree is dirty, tell the user and ask whether to continue (their uncommitted work would get mixed into your changes). Work on a new branch such as `chore/maintain-codebase` unless the user says otherwise.
- **Project shape.** Read `pyproject.toml` / `setup.cfg` / `setup.py` to learn: source paths (`src/`, package dirs), test paths, how tools are run (`uv run`, `poetry run`, `hatch run`, plain venv), declared entry points and plugins (`[project.scripts]`, `[project.entry-points]`), and whether this is a **library** (public API consumed by others) or an **application**. For a library, anything exported publicly is used by definition even if nothing in the repo calls it.
- **Frameworks.** Note Django, FastAPI/Flask, Celery, Click/Typer, pytest, Pydantic, SQLAlchemy, etc. Each one calls code implicitly. See `references/vulture.md` for the per-framework list.
- **Baseline.** Run the project's existing checks and record the results *before* any change: test suite, linter (ruff/flake8), type checker (mypy/pyright) if configured. Pre-existing failures are not yours to fix, but you need to know them so you can tell a regression from old breakage. If there are no tests at all, say so now: verification will be weaker and you should be more conservative in Phase 1.
- **Install Vulture** if missing, using the project's own tool runner as a dev dependency (`uv add --dev vulture`, `poetry add --group dev vulture`, or `pip install vulture`). Reuse any existing `[tool.vulture]` config and whitelist.

## Phase 1 - Find and remove dead code

### 1. Scan

Scan source **and tests together** so code exercised only by tests is not flagged for deletion:

```bash
vulture <src_paths> <test_paths> [whitelist.py] --min-confidence 60 --sort-by-size
```

Exclude generated and vendored code (`--exclude "*/migrations/*,*/.venv/*,*_pb2.py"`). Exit code 3 means dead code was found, 0 means clean, 1/2 mean bad input or arguments.

Optionally also scan source alone. Anything reported there but not in the combined scan is used *only by tests*: possibly dead in production. Do not delete these on your own; list them for the user.

### 2. Triage every finding

Confidence tells you how much evidence you need:

| Confidence | What it is | How to treat it |
|---|---|---|
| 100% | unreachable code, unused function/method/class arguments | Unreachable code: remove. Arguments: usually **keep the signature** (see below). |
| 90% | unused imports | Remove after checking for re-exports and side-effect imports. |
| 60% | unused attribute, class, function, method, property, variable | Suspect only. Prove it is unused before deleting. |

For each 60% and 90% finding, search for evidence of use that Vulture cannot see:

- `grep -rn "<name>"` across the **whole repo, not just `.py` files**: templates, YAML/TOML/JSON config, docs, shell scripts, CI files, SQL, notebooks.
- String-based access: `getattr`, `globals()`, `importlib.import_module`, dotted-path strings in settings, `__all__`.
- Implicit callers: framework hooks, decorators that register things, dunder methods, overrides of a base class or Protocol method, serializer/ORM/Pydantic fields, pytest fixtures and hooks, entry points.
- Public API of a library: anything exported from a package `__init__.py` or documented.

Then classify each finding as exactly one of:

- **Remove** - no use found anywhere.
- **False positive** - it is used implicitly. Add it to the whitelist (Phase 3), do not touch the code.
- **Uncertain** - plausible dynamic or external use you cannot rule out. Leave it and list it for the user. A wrongly kept function costs a few lines; a wrongly deleted one costs a production incident.

Special cases:

- **Unused arguments.** If the function is an override, callback, hook, fixture, or part of a public API, the signature is a contract. Keep the parameter and rename it with a leading underscore (`_event`) or add `del event`. Only drop the parameter when you can update every caller.
- **Unused imports in `__init__.py`** are usually re-exports. Keep them and make it explicit with `__all__`.
- **Side-effect imports** (registering models, signals, plugins) must stay; whitelist them.
- **Unused local variables** whose right-hand side has side effects: keep the call, drop only the binding.

### 3. Remove in small batches

Remove in order of certainty (unreachable code → imports → functions/classes), one coherent batch at a time (per module or per feature), and run Phase 2 after each batch. Small batches make a failure trivial to locate and revert.

When deleting something, also delete what only existed for it: its now-unused imports, private helpers, tests that test only the removed code, fixtures, docs and config entries. Do not leave commented-out code behind; git history is the archive.

### 4. Re-scan until stable

Deleting code exposes more dead code (helpers of the deleted function). Re-run Vulture and repeat triage until a scan produces no new **Remove** findings.

## Phase 2 - Verify nothing broke

Run after every batch, cheapest check first:

1. `python -m compileall -q <src_paths>` - syntax.
2. Import smoke test - import the top-level package(s) and CLI entry points (`python -c "import mypkg"`, `mypkg --help`). Catches removed names that are imported elsewhere.
3. Linter - `ruff check` / `flake8`, mainly for undefined names (F821) and broken imports.
4. Type checker, if the project uses one.
5. Full test suite.

Compare with the Phase 0 baseline. The rule is **no new failures**. If something fails:

- Revert that batch (`git checkout -- <files>` or `git revert`), find the specific deletion responsible, reclassify it as a false positive, add it to the whitelist, and re-apply the rest.
- Never "fix" a failure by deleting or weakening the test, and never push forward with a red suite.

When a batch is green, commit it with a message that says what was removed and why (`chore: remove unused export helpers (vulture)`). One commit per batch keeps every step revertible.

## Phase 3 - Lock in the maintenance rules

Make the clean state stay clean, so the next run starts from signal rather than noise:

- **Whitelist.** Put confirmed false positives in a `vulture_whitelist.py` at the repo root (start from `vulture <paths> --make-whitelist`, then keep only the entries you classified as false positives). Prefer the whitelist over `--ignore-names` or `# noqa`: it is plain Python, lives in one reviewable place, and adds no noise to the code.
- **Config.** Persist the scan settings in `pyproject.toml` so `vulture` with no arguments reproduces your scan:

  ```toml
  [tool.vulture]
  paths = ["src", "tests", "vulture_whitelist.py"]
  exclude = ["*/migrations/*"]
  min_confidence = 80
  sort_by_size = true
  ```

  Use 60 for manual maintenance passes; a higher value such as 80 suits automated gates, where false positives block people.
- **Automation.** If the repo already uses pre-commit or CI, *offer* to add Vulture there (snippets in `references/vulture.md`). Do not add new infrastructure the user did not ask for.

## Phase 4 - SOLID review

Now review the remaining code against SOLID. Read `references/solid-python.md` first: it has the Python-specific smells, detection hints, and fix patterns for each principle.

| Principle | Question to ask of each module/class |
|---|---|
| **S**ingle Responsibility | Does it have more than one reason to change (e.g. business rules + I/O + formatting)? |
| **O**pen/Closed | Does adding a new variant mean editing an `if/elif` or `isinstance` chain in existing code? |
| **L**iskov Substitution | Can every subclass stand in for its base without callers noticing (same signature, no `NotImplementedError`, no stricter preconditions)? |
| **I**nterface Segregation | Are implementers forced to provide methods they do not need? Do callers depend on a fat interface for one method? |
| **D**ependency Inversion | Does high-level logic construct its own concrete dependencies (DB clients, HTTP sessions, `datetime.now()`) instead of receiving them? |

How to apply it:

- **Scope.** Default to the modules you touched plus the highest-traffic core modules; review the whole codebase if the user asked for a full pass. Say which scope you used.
- **Your own changes always comply.** Any code you write or restructure during this skill must satisfy SOLID. Never introduce a new violation while fixing something else.
- **Fix what is clear and safe now.** Small, mechanical, behaviour-preserving refactors with test coverage (extract a class or function, inject a dependency through the constructor with the old default, replace a type-switch with a registry or polymorphism, split a fat ABC into Protocols). After each refactor run Phase 2 again and commit separately from dead-code commits (`refactor: ...`).
- **Propose what is large or risky.** Refactors that change public APIs, span many modules, or touch code without tests go in the report as recommendations with a concrete plan, and wait for the user's go-ahead.
- **Stay pragmatic.** SOLID serves changeability; it is not a goal in itself. Do not add an interface for a single implementation with no foreseeable second one, and do not split a small cohesive class to hit a rule. If satisfying a principle would add more complexity than it removes, say so in the report instead of doing it. A violation is something that makes a realistic change harder, not merely something that deviates from a textbook shape.
- **Refactors can create dead code.** After Phase 4 changes, run Vulture once more and close the loop.

## Final report

End with this report (keep it concise; use the real numbers):

```markdown
# Maintenance report: <project>

## Summary
<2-3 sentences: what was done, net lines removed, overall health>

## Dead code removed
| File | Item | Type | Confidence | Evidence it was unused |

## Kept (false positives - whitelisted)
| Item | Why it is actually used |

## Needs your decision (uncertain / test-only)
| Item | Why it is uncertain | Suggested action |

## Verification
| Check | Baseline | After | 
(compile, imports, lint, types, tests - with counts; note pre-existing failures)

## Maintenance rules added
<whitelist, pyproject config, hooks/CI - or "none, offered: ...">

## SOLID review (scope: <scope>)
### Fixed
| Location | Principle | Problem | Change made |
### Recommended (not done)
| Location | Principle | Problem | Proposed refactor | Risk/effort |

## Commits
<list of commits on branch>
```

If the user asked only for part of this (for example "just find dead code, don't delete"), run only the relevant phases, but still do Phase 0, and still verify after any change you make.
