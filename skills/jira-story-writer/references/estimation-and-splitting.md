# Step 2 — Decide the ticket structure, estimate, split, assign ids

Each story should be **INVEST**: Independent, Negotiable, Valuable, Estimable, Small (doable in one sprint, ideally 1–5 days), Testable.

Only items marked 🟡 Partial, 🔄 Conflicts, ❌ Not implemented or unverified in Step 1b become stories. Items marked ✅ Implemented or 📋 Already planned get no new story.

If the requirement is bigger than one story, create an **Epic** and split it into stories. Good ways to split:
- **By actor**: customer applies a coupon / admin creates coupons.
- **By workflow step**: create → apply → remove → report.
- **By business rule**: basic flow first, then extra rules (limits, minimums) as separate stories.
- **By operation**: create / view / edit / delete.
- **Happy path first, edge cases later**, but only if the first story is still releasable and safe on its own.

Don't split by technical layer (a "backend story" plus a "frontend story"). Each story should deliver something a user can see or use. If the team really works that way, use **sub-tasks** under a story instead.

### Estimate story points, and split anything over 5

Estimate every candidate story with the Fibonacci scale. Points measure **size and risk**, not hours, so judge three factors:

| Factor | Low | Medium | High |
|---|---|---|---|
| **Complexity**: rules, calculations, states, integrations | 1–2 simple rules, one screen/endpoint | several rules or states, 2–3 components | many rules, external systems, money/security-critical |
| **Uncertainty**: unknowns, open questions, new tech | everything is clear | a few open questions with likely answers | key rules unknown, new technology, unclear data |
| **Effort**: amount of work incl. tests | small change | a normal feature | many files/layers, lots of test cases, migration |

| Points | Meaning |
|---|---|
| 1 | Trivial: a text or config change, all clear |
| 2 | Small: one simple rule, low risk |
| 3 | Small–medium: a few rules, well understood |
| 5 | Medium: **the maximum for one story**, several rules/states, some unknowns |
| 8+ | **Too big: must be split** |

**Estimate the delta, not the whole feature.** Existing code usually lowers Effort. Changing existing behaviour raises Uncertainty, because other features may depend on it and need regression testing. Reflect both in the factors.

**The rule: keep every story as small as possible, aim for 1–3 points, and break anything estimated above 5 points into smaller stories.** One observable behaviour per ticket: if a story covers "do X" and "show the error when X fails", those are two tickets. The reason: a big story rarely fits in one sprint, hides too many unknowns to estimate honestly, and is hard to review and test as one unit.

How to split:
1. Pick a split method from the list above (actor, workflow step, business rule, operation, happy path first).
2. Each child story must still be INVEST: independently releasable, with real user value, and with its own ACs. Never split into "backend" and "frontend" halves.
3. **Re-estimate each child from scratch.** Don't divide the parent's number; children often add up to less than the parent, because splitting removes uncertainty.
4. If a child is still above 5, split it again. Repeat until every story is ≤ 5.
5. If high **uncertainty** is what makes a story big (not the amount of work), propose a time-boxed **Spike** ticket to answer the unknowns first, then re-estimate the story.
6. If a story genuinely cannot be split without losing its value (rare), keep it, and explain why in the Estimation Log for the team to decide.

A 5 is allowed, but mark it as **"at the limit"** and mention the split you would use if the team's estimate comes out higher.

Show the estimation before writing the details:

```
## Estimation Log
| Candidate story | Complexity | Uncertainty | Effort | Points | Action |
|---|---|---|---|---|---|
| Customer uses coupon at checkout | High | Medium | High | 8 | ✂️ Split (by operation) → Story 2 + Story 3 |
| ↳ Story 2: Apply coupon | Medium | Medium | Medium | 5 | ✅ Keep |
| ↳ Story 3: Remove coupon | Low | Low | Low | 2 | ✅ Keep |
```

Then show the final structure. It may only contain stories of ≤ 5 points:
```
Epic: [name]  (total: N points)
├── PCD-1: [summary]  (3 pts, priority, depends on: —)
├── PCD-2: [summary]  (2 pts, priority, depends on: PCD-1)
└── PCD-3: ...
```

**Re-estimate when answers arrive.** If answers to the Open Questions add scope (e.g. "yes, we need usage limits"), re-estimate the affected story. If it rises above 5, split it again and show the updated log.

### Ticket ids (no Jira lookup)

Give every story its ticket id yourself; never ask for or look it up in Jira.
- **Prefix:** the initials of the epic name in uppercase, 2–4 letters (`Project Created Datasets` → `PCD`, `Faster Replies` → `FR`). If the epic's `backlog/` or README already uses a prefix, keep it. If the prefix is already used by another epic in `docs/tasks/`, add a letter to make it unique.
- **Number:** 1, 2, 3… in priority order within the epic. When adding to an existing backlog, continue after the highest number there; never renumber or reuse an id.
- The id is the ticket name: it is the first line of the file, starts the file name, and is how stories refer to each other in Depends on / Out of Scope (`see PCD-4`).
