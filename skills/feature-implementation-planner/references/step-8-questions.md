## Step 8 — Questions and confirmations

End with a numbered list of everything the user needs to decide or confirm, split into two groups:
- **Questions**: genuine unknowns, such as business rules, edge cases, data ownership, security trade-offs (e.g. detailed error codes vs. hiding what exists), or what to do with existing data during a migration.
- **Assumptions to confirm**: choices you made so the plan could proceed, so the user can just say "yes". Every assumption must have these three parts, each as its own labelled line:
  - **Context:** the situation in the code or requirement that forced a choice, with file:line evidence where it exists (what exists today, what constraint applies).
  - **Decision:** the default you chose, stated concretely (names, values, limits), plus the realistic alternative and what would change if the user picks it.
  - **Why:** the reason this default beats the alternative (the risk it avoids, the rule it follows, the cost it saves).

  Example:
  ```
  **A3 — Ids look like `file-iris-csv`.**
  - *Context:* ids must match `^[a-z0-9][a-z0-9-]{0,79}$` (`datasets_store.py:35`), so a file name like `Iris.csv` can't be an id.
  - *Decision:* `file-` + a slug of the path, `-2`, `-3` on clashes. Alternative: a random id (`file-7f3a9c`).
  - *Why:* the prefix can't clash with catalog ids, so the existing Delete action works unchanged, and a readable id helps in logs.
  ```
  Questions get the same three parts when they need background (context, your suggested default, why).

Finish the plan file with one line confirming that no files or data were changed other than the plan file. Write the file, reply in chat as described in "Plan file", then stop and wait for answers.

When the user answers, run the **Plan update procedure** below on the plan file. If an answer also implies a change to the story file, or a new story or backlog item, don't make it: list it in chat and ask first (see "Scope: one story, one plan file"). Then ask: **"Plan updated in `<plan file>` (vN) — approved, shall I create the scaffold?"** Go to Step 9 only on an explicit yes. Answering the questions is not approval by itself.

## Plan update procedure

Run this on **every** round of answers, including partial answers and later corrections, and whenever the user asks for a change at the Step 10 checkpoint. One decision usually ripples through several sections; a plan where §1 says one thing and §4 or §7 still says the old thing is the main way this skill fails, so do every step.

1. **List the decisions.** Turn the user's message into one decision per question or assumption (Q1 → D1, A6–A12 → D6). "Use your default" is a decision too: the default you proposed. A question the user skipped stays open: say so and ask it again; don't guess it.
2. **Trace the impact.** For each decision, walk this chain and note every section it touches. Skip a section only if you can say why it is unaffected:
   `§1 US/AC + Out of scope → §3.1/3.2 schema → §3.3 migration → §4.1 files → §4.2 endpoints (status/errors) → §4.3 DTO fields, validation, error codes, error example → §5 security rows → §6 diagram branches → §7 test groups (baseline, ✅ edges, ❌ rows) → §7 coverage tables and test count → §8 questions`
3. **Edit the plan file in place.** Apply every change from step 2 so each section reads as if the decision had been there from the start. No "Update:" notes at the bottom and no old and new versions side by side; history lives only in the Decision log. In §8, mark each answered item instead of deleting it: `~~4.~~ Answered → D4`. Update the status line: bump `vN`, keep the status `Draft — awaiting approval`.
4. **Add Decision log rows.** One row per decision: `| D# | Question | Answer | What changed in the plan |`. "What changed" names exactly the sections edited in step 3, so a reviewer can check them. A decision that changes nothing still gets a row (`no change; confirms §4.3`).
5. **Re-read the plan file from disk and check it.** Don't trust your memory of the edit:
   - every section listed in step 2 really changed;
   - the old value is gone: search the file for it, e.g. `grep -n "COUPON_EXPIRED" <plan file>` must only hit the Decision log;
   - every AC in §1 appears in the coverage table, every §5 risk has a test, and the test count in §7 matches the groups.
   Any miss: fix the file and check again. Never ask for approval while a check fails.
6. **Reply in chat** with the new Decision log rows, the sync table (below), and a short list of the changed sections, plus the link to the plan file. Don't paste the whole plan again.

Sync table, one row per decision (see the worked example in `examples/plan-8-questions.md`):

| Decision | Sections that had to change | Updated in file? |
|---|---|---|
| D4 (Q4: one generic error) | §1 AC2, §4.1, §4.2, §4.3, §5 SEC6, §6, §7 G1 ❌1–3 | ✅ ✅ ✅ ✅ ✅ ✅ ✅ |
| Checks | old codes gone · all ACs covered · test count 55 → 56 | ✅ |
