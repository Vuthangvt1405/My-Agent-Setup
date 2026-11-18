# Step 1b — Check what already exists in the code

A requirement may be fully built, partly built, or in conflict with what the code does today. Writing a story for behaviour that already exists wastes estimation and confuses developers, so check before splitting.

## When to run

- **Run it** whenever a codebase is reachable: the current repo, a connected folder, attached source files, or code the user pasted.
- **Skip it** when the user says the feature is brand new (greenfield).
- **No code reachable:** don't guess. Mark every item *Status: unverified*, and tell the user in the chat that implementation was not checked and which repo or folder would let you check it. This is a question for the user, not a customer Open Question (see "Never ask the customer technical questions").

## How

1. **Break the requirement into checkable items**: each goal, rule, field, screen, permission and error case from Step 1. Number them R1, R2…
2. **Check the backlog first.** Look in `docs/tasks/` and `docs/tasks/done/` for tickets that already cover an item. A Done ticket is a strong hint that the item is built, but confirm it in the code. An open ticket means the item is already planned: link it instead of writing a duplicate.
3. **Search the code for each item:**
   - domain nouns **and synonyms** (coupon / voucher / promo / discount)
   - routes and endpoints, controller and service names
   - entity, table and column names, migrations, enum values
   - UI text and i18n keys, config keys, feature flags
   - **tests**: test names often describe existing behaviour best

   Use grep / ripgrep, then **read the matching code** to confirm what it actually does. A name match alone is not proof.
4. **Classify each item:**

| Status | Meaning | What to do |
|---|---|---|
| ✅ Implemented | Code already behaves as the requirement says | No story. List it under "Already implemented" with evidence. Optionally add a QA verification note |
| 📋 Already planned | An open ticket in `docs/tasks/` covers it | No new story. Link the existing ticket; update it only if the requirement adds scope |
| 🟡 Partial | Exists but a rule, field, state or error case is missing | Story for the **gap only**. Its Current Behaviour section says what exists |
| 🔄 Conflicts | Code does something different from what the requirement asks | Story to change behaviour, with regression ACs, plus an Open Question confirming the change is intended (asked as visible behaviour, not code) |
| ❌ Not implemented | Nothing related found | Normal new story |
| ❓ Unclear | Can't confirm (behind a feature flag, dead code, lives in an external service) | Note it for the developer; ask the customer only if the answer is visible behaviour |

5. **Evidence is required.** Every ✅ / 🟡 / 🔄 needs a file path plus a function, endpoint or line. Never claim something is implemented without evidence. "Not found" is only as good as the search, so always list what you searched (keywords and folders).
6. **Show the result** to the user together with the Step 1 analysis:

```
## Implementation Check
| # | Requirement item | Status | Evidence | Gap / note |
|---|---|---|---|---|
| R1 | Customer enters a coupon code at checkout | ✅ Implemented | `checkout/coupon_controller.py` → `POST /orders/{id}/coupon` | — |
| R2 | Expired coupons are rejected | 🟡 Partial | `CouponService.validate()` checks `expires_at` in server time | Must use the store's timezone |
| R3 | Admin sees coupon usage report | 📋 Already planned | `docs/tasks/coupons/backlog/CP-4-usage-report.md` | — |
| R4 | One coupon per customer | ❌ Not implemented | — | New story |
Searched: coupon, voucher, promo, discount, redemption, usage in src/, tests/ and docs/tasks/
```

This step is read-only: never change code. If the user wants a deep walkthrough of the existing feature, that belongs to the `feature-explainer` skill.

If **every** item is ✅ Implemented or 📋 Already planned, say so plainly and don't create stories. Offer a QA verification task instead, or ask whether the requirement means something different from what exists.
