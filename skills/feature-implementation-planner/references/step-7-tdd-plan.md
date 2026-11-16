## Step 7 — TDD test plan (positive baseline + all negative cases)

Tests are written **first** when implementation starts (Red → Green → Refactor). In plan mode you only *describe* them. List groups in the order they should be written: start with the simplest test that forces the core behavior to exist, then add the rules one by one.

### Test groups: one baseline, every way it can fail

Don't trust a single positive/negative pair. A rule usually breaks in several ways, and one negative test only proves one of them. So organize tests in **groups**, one group per rule:

1. **Baseline positive (✅)**: the valid case. Every test in the group shares this setup.
2. **Edge positives (✅, optional)**: other inputs that must still succeed, such as an exact boundary, input normalization (trimmed or lowercase), or an optional field that is absent.
3. **Negatives (❌), as many as needed to cover all the ways the rule can fail.** Each negative changes **exactly one condition** from the baseline. Because only one thing differs, each test proves that *that* condition causes the failure; changing two things at once hides which one mattered.

To find all the negatives, go through this checklist for each rule. Skip only the items that are truly impossible for that rule:

| Category | Typical negative cases |
|---|---|
| Missing / empty | null, absent field, empty string, whitespace only, empty list |
| Format & size | too long, too short, wrong type, invalid characters, wrong enum value |
| Boundaries | just past min/max, just past a date limit, zero, negative numbers |
| Existence | id/code does not exist, soft-deleted, belongs to another tenant |
| State | every disallowed status, not just one (e.g. PAID **and** CANCELLED **and** SHIPPED) |
| Business rules | each rule separately (expired, inactive, limit reached, minimum not met) |
| Conflicts & concurrency | duplicate (unique constraint), stale version (optimistic lock), double submit |
| Security | from Step 5: no/expired/malformed token, other user's resource, missing role, mass-assignment fields, injection payloads, rate limit exceeded, leaked fields in the response |

### Format for each group

Every test goes in **one table per group**: the baseline, edge positives, and negatives, in that order. Don't write tests as prose lines or bullets; a table keeps them easy to scan and compare.

```
### Group N — [rule being proven]  (covers AC#, Security #)  · [unit | integration | API]
Baseline: Given [the shared valid setup] · When [the action under test]

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `test_name` | — | [observable result] | [what this proves about the system] |
| ✅2 | edge | `test_name` | [the one condition changed] | [still succeeds, and how] | ... |
| ❌1 | negative | `test_name` | [the one condition changed] | status + error code, and state unchanged | ... |
| ❌2 | negative | `test_name` | ... | ... | ... |
```

- `#` numbers ✅ and ❌ rows separately, so tests can be referenced as `G1✅2` or `G1❌3` in scaffold TODOs.
- `Type` is `baseline`, `edge`, or `negative`. Each group has exactly one `baseline` row. A negatives-only group (such as injection payloads) may skip it and say so in the Baseline line.
- The Baseline line holds the shared Given and When. Each row only states what it changes and its expected Then; the scaffold test comments in Step 9 are built from these.
- Keep cells short. If a row needs more explanation, add a one-line note under the table.

Put security tests in their own groups (e.g. "Group S1 — Authentication"). This keeps them visible and makes it easy to check that every Step 5 risk has a test.

Guidelines:
- Every negative's expected result should state the response **and** that nothing changed (no DB write, total unchanged). A rejected request that still writes data is a real bug that "returns 422" alone won't catch.
- Include schema-level rules from Step 3 (unique constraints, FK integrity, optimistic-lock conflicts, cascades). These usually need integration tests against a real or test-container DB.
- State the test level for each group, following the codebase's existing test style from Step 2. Security tests for authentication and authorization should go through the real HTTP/security layer (API tests), because mocks can bypass the filters you are trying to test.
- Test names follow the codebase convention. If there is none, use `should_[expected]_when_[condition]`.
- A "Demonstrates" cell must describe behavior, not code. Good: "an expired coupon never reduces the price". Bad: "tests validateCoupon()".

Check silently that every AC has a baseline plus at least one negative, and every Step 5 risk has at least one test; don't add coverage tables to the plan.
