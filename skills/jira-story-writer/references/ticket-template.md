# Step 3 — Write each ticket

Use this template for every story:

```
# [TICKET-ID] — [Summary: verb-first, specific, ≤ 80 chars, e.g. "Apply discount coupon to pending order"]

**Type:** Story | **Epic:** [name] | **Priority:** [Highest/High/Medium/Low] | **Labels:** [...] | **Components:** [...]
**Story points (suggested):** [1/2/3/5] — Complexity [L/M/H], Uncertainty [L/M/H], Effort [L/M/H] — [one-line reason]
**Depends on:** [TICKET-IDs or —]
**Status:** Backlog

### User Story
As a **[specific role]**, I want **[capability]**, so that **[business value]**.

### Background
[2–4 sentences: why this exists now, the business context, and what users do today without it]

### Current Behaviour
[Only when Step 1b ran: what the system does today for this story, with file references, and what is missing or must change. Write "Not implemented today" for new work.]

### Acceptance Criteria
**AC1 — [short name]**
Given [precondition]
When [action]
Then [observable, measurable result]

### Developer Notes
[See the rules below]

### Out of Scope
- ...

### Dependencies
- ...

### Open Questions
- [ ] ... (@who should answer, if known)
```

### Writing the User Story
- **Role**: be specific ("logged-in customer", not "user").
- **Capability**: what they do, not how the system does it ("apply a coupon code", not "call the coupon API").
- **Value**: a real benefit ("pay a lower price"), not a restatement of the capability ("so that the coupon is applied").
- If one story has two "I want"s joined by "and", it is probably two stories.

### Writing the Acceptance Criteria
- Use Given / When / Then, numbered AC1, AC2… so the developer, QA, and tests can reference them.
- **Cover more than the happy path.** For each story, go through this checklist and write an AC for every item that applies:

| Category | Ask |
|---|---|
| Happy path | Does the main success case work, with the exact expected result? |
| Validation | What about empty, too long, or wrong-format input? |
| Business rules | One AC per rule (expired, limit reached, minimum not met) |
| State | What if the item is in the wrong status (paid, cancelled, deleted)? |
| Permissions & security | Not logged in? Someone else's data? Missing role? Too many attempts? |
| Errors shown to the user | What message does the user see? Does the data stay unchanged? |
| Boundaries | Exactly at the limit vs just past it |
| Non-functional | Performance, audit, accessibility, mobile, only when they matter for this story |
| Regression | If the story changes existing code (🟡 / 🔄), what must keep working? Write one AC per existing behaviour at risk |

- **Make it testable.** Replace vague words with measurable ones:

| Vague ❌ | Testable ✅ |
|---|---|
| "should be fast" | "responds within 500 ms at p95" |
| "show an error" | "shows 'This coupon has expired' and the total stays unchanged" |
| "user-friendly" | (drop it, or name the specific behavior) |
| "handle invalid input" | one AC per invalid case, with its message |
| "etc." | list every case, or move the rest to Open Questions |

- Describe **behavior the user or tester can observe** (screen, response, email, data state), not implementation ("uses Redis", "calls validateCoupon()").
- Aim for 3–8 ACs per story. More than about 10 ACs usually means the story is too big. Check its points, and split it if they are above 5. A small story usually has 2–5 ACs.

### Writing the Developer Notes
These help a developer start quickly. Include only the items that are relevant, and keep each one short:

- **Context & intent**: the "why" behind tricky rules, so the developer makes the right call on cases the ticket doesn't cover.
- **Affected areas (likely)**: modules, screens, services, or tables that are probably involved, phrased as hints ("probably touches the orders module and checkout page"), not commands.
- **Data & fields**: entities/fields involved, formats, units, precision (e.g. money with 2 decimals, dates in UTC).
- **Business rule details**: formulas, rounding, ordering of checks, examples with real numbers (e.g. "10% of 33.33 = 3.33").
- **Edge cases to watch**: concurrency, empty states, timezones, very large values.
- **Security considerations**: ownership checks, role required, sensitive data not to expose or log, brute-force risk.
- **Non-functional**: performance targets, audit logging, feature flag, backward compatibility.
- **Related tickets / docs / designs**: links if the user provided them. Never invent links or ticket keys; use placeholders like `[link to Figma]`.
- **Testing hints**: test data needed, how QA can reproduce.

If Step 1b checked the code, name the real files, functions and endpoints it found as affected areas, and say what to **reuse** and what to **change**. If no codebase or system info was given, label technical hints as *(assumption: verify against the codebase)*.

### Other fields
- **Out of Scope**: always fill it. It prevents scope creep and answers "what about X?" before anyone asks.
- **Dependencies**: other stories, teams, APIs, data migration, design assets.
- **Priority / story points**: suggestions with reasons; the team has the final say. If the team's own estimate comes out above 5, apply the same split rule.
- **Open Questions**: every Unknown from Step 1. Each should be a closed, answerable question ("Is the minimum inclusive?"), not a vague one ("What about minimums?"). Business questions only; technical unknowns go in Developer Notes as dev decisions (see "Never ask the customer technical questions").
