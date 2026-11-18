---
name: feature-implementation-planner
description: Plan a new feature in read-only PLAN MODE before any code is changed - understand the requirement (User Stories + Acceptance Criteria), study the codebase to learn its patterns, map the database schema and entity relationships, design API endpoints and request/response DTOs field by field, review security (OWASP API Top 10), draw one workflow diagram, write a TDD plan with positive tests plus every negative case (incl. security), and finish with questions for the user to confirm, saving the whole plan to a single Markdown plan file; then, only after the user approves the plan, create a compile-ready scaffold (files, DTOs, endpoint signatures, migration file, failing test skeletons) with NO business logic, then stop until the user verifies it. Use this skill whenever the user asks to implement, build, add, or plan a new feature, endpoint, API, or ticket/story, pastes a user story or acceptance criteria, or says things like "implement this ticket", "add a feature for X", "how would you build X in our code", even if they don't explicitly ask for a plan.
---

# Feature Implementation Planner

## The mental model

You are a senior engineer joining this team. Your job is not to write code fast. It is to make sure the user **agrees with the design before it is expensive to change**.

The cost of a change grows with every phase:

**Plan** (cheap: edit text) → **Scaffold** (medium: rename files) → **Logic** (expensive: rework tests and code)

So think hard early, and let the user correct you at each boundary before you go further. This skill covers the first two phases and ends at a hard stop before any logic.

Three ideas drive everything:

1. **The plan file is the contract.** Everything goes into one Markdown file; the chat only gets a pointer. When a decision changes, the file changes in the same reply, edited in place so each section reads as if the decision had always been there (history lives only in the `## Decision log`). The scaffold is built from the file, not from your memory, so re-read it from disk before each gate.
2. **One decision ripples.** A changed error code touches the AC, DTOs, security, diagram and tests. When anything changes, follow it through every section, and grep the file for the old value before saying you're done. Partial updates are the main way this process fails.
3. **Tests are the spec.** Every acceptance criterion and every security risk is proven by a test. Negative cases matter more than the happy path: each way a rule can fail is its own test, changing one condition from a shared valid baseline and asserting both the error *and* that nothing was written.

Scale to the feature. A new payment flow deserves every section in depth; a one-field change might need a few lines per step. Skip or merge what adds nothing, and say so.

## Hard rules (these override your judgment)

- **Plan mode (Steps 1–8) is read-only.** Read, search, read-only git and DB (never production unless told it's safe). The only file you may write is the plan file. No migrations, installs, generators, formatters, commits.
- **One story, one plan.** Don't edit the story/ticket file, other stories, epics, backlogs or sprint files without asking. If an answer changes the story, put it in the plan as a *Proposed AC* and ask "Shall I also update the story file?". Anything for another topic or sprint goes in Step 8 as *Out of scope — follow-up*; ask before creating a story for it. A "yes" covers only the file it was given for.
- **Stop at every gate and wait for an explicit word.** Answering questions is not approval; silence or "looks ok?" is not verification.
  - Plan → scaffold: the user says **approved**.
  - Scaffold → logic: the user says **verified**. This skill ends there.
- **The scaffold has no logic.** Shape only: the files listed in the plan and nothing else, signatures, DTO fields + declarative validation, wiring, security annotations, the migration file (never run), and every planned test as a failing stub (never skipped). Logic bodies throw the language's not-implemented error. It must compile; new tests fail, existing tests pass.
- **No plan or ticket references in code.** `docs/` doesn't ship. Comments, docstrings, TODOs, test names and messages never mention AC/SEC/group numbers, ticket ids, plan sections or plan paths. Write the intent instead (`# a re-save keeps the same card`, not `# (AC4)`). The code → plan trace lives only in the scaffold report's TODO map. Before reporting done: `git diff | grep -nE '\b(AC|SEC)[0-9]+|\b[A-Z]{2,5}-[0-9]+\b|§[0-9]|docs/(plans|tasks|requirements)'` finds nothing in added lines.
- **Report only real results** from commands you ran. Say "not run" otherwise.

## Where things go

- **Plan file:** `docs/features/plans/<ID>-<slug>-plan.md` if the project keeps feature docs, otherwise `docs/plans/<ID>-<slug>-plan.md` (slug only without an id). Update an existing one rather than making a second.
- **Status line** under the title, `vN` bumped on every update: `Draft — awaiting answers` → `Approved — scaffold pending` → `Scaffolded — awaiting verification` → `Verified — implementing`.
- **Scaffold report:** a separate `<ID>-scaffold-report.md` next to the plan (Step 9 report, then Step 10 verification appended). The plan only links to it.
- **Chat reply:** a link to the file, a 3–5 line summary (approach, files affected, test count, schema change yes/no), and the Step 8 questions as a numbered list. Never paste the whole plan.

## Steps

Run them in order; each depends on the one before. Load a step's reference file when you reach it, and its example only if you need to see the finished shape. Don't read them all up front.

| Step | What to get right | Rules | Example |
|---|---|---|---|
| 1. Requirement | US + numbered Given/When/Then AC, unhappy paths, out of scope | [steps-1-3-understand.md](references/steps-1-3-understand.md) | [plan-1-3-understand.md](references/examples/plan-1-3-understand.md) |
| 2. Codebase patterns | Look like the same team wrote it; cite file paths | ↑ | ↑ |
| 3. Schema | The data it touches, relationships, any change (described, not applied) | ↑ | ↑ |
| 4. Endpoints & DTOs | What each field *means* and where it maps | [steps-4-6-design.md](references/steps-4-6-design.md) | [plan-4-6-design.md](references/examples/plan-4-6-design.md) |
| 5. Security | Only the risks that apply; each one gets a test | ↑ | ↑ |
| 6. One diagram | How it runs, incl. error and security branches; must render | ↑ | ↑ |
| 7. TDD plan | One baseline per rule, every way it can fail, coverage tables | [step-7-tdd-plan.md](references/step-7-tdd-plan.md) | [plan-7-tdd.md](references/examples/plan-7-tdd.md) |
| 8. Questions | Real unknowns + assumptions with your default; then the update procedure on every answer round | [step-8-questions.md](references/step-8-questions.md) | [plan-8-questions.md](references/examples/plan-8-questions.md) |
| Plan file headings | — | [plan-template.md](references/plan-template.md) | — |
| 9. Scaffold · 10. Verification stop | Shape only, self-check against the plan, then stop for "verified" | [steps-9-10-scaffold.md](references/steps-9-10-scaffold.md) | [scaffold.md](references/examples/scaffold.md) |
