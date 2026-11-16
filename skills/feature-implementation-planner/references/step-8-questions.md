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

When the user answers, update **only the plan file** in place with their decisions and add them to `## Decision log` (question → answer → what changed in the plan). If an answer also implies a change to the story file, or a new story or backlog item, don't make it: list it in chat and ask first (see "Scope: one story, one plan file"). In chat, show only what changed. Then ask: **"Plan approved — shall I create the scaffold?"** Go to Step 9 only on an explicit yes. Answering the questions is not approval by itself.
