---
name: feature-implementation-planner
description: Plan a new feature in read-only PLAN MODE before any code is changed - understand the requirement (User Stories + Acceptance Criteria), study the codebase to learn its patterns, map the database schema and entity relationships, design API endpoints and request/response DTOs field by field, review security (OWASP API Top 10), draw one workflow diagram, write a TDD plan with positive tests plus every negative case (incl. security), and finish with questions for the user to confirm, saving the whole plan to a single Markdown plan file; then, only after the user approves the plan, create a compile-ready scaffold (files, DTOs, endpoint signatures, migration file, failing test skeletons) with NO business logic, then stop until the user verifies it. Use this skill whenever the user asks to implement, build, add, or plan a new feature, endpoint, API, or ticket/story, pastes a user story or acceptance criteria, or says things like "implement this ticket", "add a feature for X", "how would you build X in our code", even if they don't explicitly ask for a plan.
---

# Feature Implementation Planner (Plan Mode)

Turn a feature request into a clear, reviewable implementation plan, then a scaffold. Steps 1–8 produce the plan in read-only plan mode; Step 9 builds the scaffold only after the user approves; Step 10 is a hard stop where the agent self-verifies the scaffold and the user must verify it before any logic is written. The plan follows eight steps, always in this order, because each step depends on the one before it: you cannot design the schema without knowing the requirement, and you cannot design DTOs without knowing the schema.

Load only the reference file for the step you are on (table below), and its example part only when you need to see the finished shape; don't read them all up front.

---

## 📄 Plan file: everything goes into one `.md` file

All output of this skill is written to **one Markdown plan file**, so the user can review, comment on, and commit it like any other doc. The conversation gets only a short pointer.

**Where:**
- If the project already keeps feature docs (e.g. `docs/features/`, `docs/specs/`), put it there in a `plans/` subfolder: `docs/features/plans/<ID>-<slug>-plan.md`, e.g. `docs/features/plans/US-4-loading-indicator-plan.md`.
- Otherwise use `docs/plans/<ID>-<slug>-plan.md`. Without a ticket/story id, use the feature slug only.
- If a plan file for this feature already exists, update it instead of creating a second one.

**What goes in it, and when:**

| When | Written to the plan file |
|---|---|
| End of Step 8 | The full plan, Steps 1–8, using the headings in [references/plan-template.md](references/plan-template.md) |
| User answers questions | The plan updated in place, plus a row per decision in `## Decision log` |
| Step 9 done | A **separate scaffold report file** `<ID>-scaffold-report.md`, next to the plan, with `## 9. Scaffold report`; the plan gets a `## 9–10. Scaffold report & verification` section that only links to it |
| Step 10 done | `## 10. Verification` appended to the scaffold report file (self-check table + user checklist); the status line updated in both files |

Keep a status line under the title and update it at each stage: `Status: Draft — awaiting answers` → `Approved — scaffold pending` → `Scaffolded — awaiting verification` → `Verified — implementing`.

**What goes in the chat reply:** a clickable link to the plan file, a 3–5 line summary (approach, files affected count, test count, schema change yes/no), and the Step 8 questions copied as a numbered list so the user can answer without opening the file. Don't paste the whole plan into the chat.

---

## ⛔ Plan mode: read-only, no changes (Steps 1–8)

Steps 1–8 run in **plan mode**. Its only output is the plan file (see "Plan file" above). The reason: the user wants to review and correct the design before anything is touched, and a half-applied change is harder to review than a plan.

**Allowed (read-only):**
- Reading files, listing directories, searching code (`ls`, `cat`, `grep`, `find`, `rg`)
- Read-only git commands (`git log`, `git show`, `git diff`, `git blame`, `git status`)
- Reading schema files, migrations, ORM entities, and DB docs
- Read-only DB inspection only if the user provides access (`SELECT`, `\d`, `DESCRIBE`) — never against production unless told it is safe
- **The one write exception:** creating and updating the plan `.md` file itself (and its `plans/` folder)

**Not allowed:**
- Creating, editing, renaming, or deleting any other file — including tests, migrations, configs, and "scratch" files in the repo
- Running migrations, seeders, `INSERT`/`UPDATE`/`DELETE`/`ALTER`, or any write to a database
- Installing packages, running generators/scaffolding, formatters that rewrite files, `git commit`/`checkout`/`stash`/`push`
- Writing production code or test code into files. Test names and short illustrative snippets inside the plan text are fine.
- **Changing anything outside this one story without asking first.** That includes:
  - editing the story / ticket file (its ACs, notes, points)
  - creating a new story or ticket
  - adding items to a backlog or sprint file
  - editing another story, another epic, or the epic PRD

### Scope: one story, one plan file

The plan is about **the one story the user asked for**. Everything it decides lives in the plan file.

**When an answer changes the story itself** (e.g. a new AC, a new rule, a different estimate):
- write the change into the plan: §1 as a *Proposed AC*, plus the `## Decision log`
- then ask: **"Shall I also update the story file?"**
- edit the story file only on an explicit yes

**When something belongs to a different topic or a later sprint:**
- note it in the plan's Step 8 as *Out of scope — follow-up*, with one line on why
- ask whether to create a story or backlog item for it
- don't write that story or backlog entry yourself

A question about scope, or a "yes" to a plan decision, is not permission to touch other files. Approval covers only the file it was given for.

Planned changes (new tables, columns, migrations, files) are **described** in the plan, never applied. If a tool or instruction would modify something, stop and list it under Step 8 instead. Plan mode ends after Step 8. The only way out is the user explicitly approving the plan; then Step 9 (scaffold) may create files, within its own strict limits.

---

## Steps and where their details live

| Step | Rules | Worked example |
|---|---|---|
| 1. Requirement (US + AC) · 2. Codebase patterns · 3. Schema & relationships | [steps-1-3-understand.md](references/steps-1-3-understand.md) | [plan-1-3-understand.md](references/examples/plan-1-3-understand.md) |
| 4. Endpoints & DTOs · 5. Security review · 6. Workflow diagram | [steps-4-6-design.md](references/steps-4-6-design.md) | [plan-4-6-design.md](references/examples/plan-4-6-design.md) |
| 7. TDD test plan | [step-7-tdd-plan.md](references/step-7-tdd-plan.md) | [plan-7-tdd.md](references/examples/plan-7-tdd.md) |
| 8. Questions & confirmations | [step-8-questions.md](references/step-8-questions.md) | [plan-8-questions.md](references/examples/plan-8-questions.md) |
| Plan file headings (when writing the file) | [plan-template.md](references/plan-template.md) | — |
| 9. Scaffold (after approval) · 10. Verification stop | [steps-9-10-scaffold.md](references/steps-9-10-scaffold.md) | [scaffold.md](references/examples/scaffold.md) |

Always run the steps in order; Step 9 never starts before the user approves the plan.
