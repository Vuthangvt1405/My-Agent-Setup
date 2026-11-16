# Example plan (continued): Apply Coupon to Order

Part of the worked example; earlier sections are in the other `plan-*.md` files.

## 7. TDD Test Plan

Write groups in order: 1 → 7, then S1 → S6. Every ❌ changes **one** condition from its group's baseline, and expects **no change to the order** (same total, no DB write).

### Functional groups

### Group 1 — Coupon must be valid (AC1, AC2) · unit
Baseline: Given a PENDING order, subtotal 120; coupon `SUMMER10`, 10%, active, expires tomorrow · When apply "SUMMER10"

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_apply_discount_when_coupon_is_valid` | — | discount 12, total 108, `coupon_id` saved | A valid coupon actually changes what the customer pays, by the right amount |
| ✅2 | edge | `should_apply_when_coupon_expires_exactly_now` | `expiresAt` = now | applied | The expiry instant itself is still valid |
| ✅3 | edge | `should_apply_when_code_has_spaces_and_lowercase` | code " summer10 " | applied | Normalization lets customers type naturally |
| ❌1 | negative | `should_reject_when_code_does_not_exist` | code "NOPE10" | 422 `COUPON_NOT_FOUND`, total 120 | Unknown codes never discount |
| ❌2 | negative | `should_reject_when_coupon_expired_one_second_ago` | `expiresAt` = now − 1s | 422 `COUPON_EXPIRED` | Expiry is enforced at the exact boundary |
| ❌3 | negative | `should_reject_when_coupon_is_inactive` | `active` = false | 422 `COUPON_INACTIVE` | Admin can switch off a coupon instantly, even before expiry |
| ❌4 | negative | `should_return_400_when_code_is_null` | code null | 400 `VALIDATION_ERROR` | A missing field is caught before any DB lookup |
| ❌5 | negative | `should_return_400_when_code_is_blank` | code "   " | 400 | Whitespace-only isn't treated as a code |
| ❌6 | negative | `should_return_400_when_code_exceeds_32_chars` | 33 chars | 400 | Oversized input is rejected (matches the `varchar(32)` column) |

### Group 2 — Minimum order amount (AC3) · unit
Baseline: Given coupon `min_order_amount` = 50.00, subtotal 50.00 · When apply the coupon

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_apply_when_subtotal_equals_minimum` | — | applied | The minimum is inclusive |
| ✅2 | edge | `should_apply_when_coupon_has_no_minimum` | `min_order_amount` = null | applied | A null minimum means "no minimum", not an error |
| ❌1 | negative | `should_reject_when_subtotal_one_cent_below_minimum` | subtotal 49.99 | 422 `MIN_ORDER_NOT_MET` | The boundary is exact to the cent |
| ❌2 | negative | `should_reject_when_order_has_no_items` | subtotal 0.00 | 422 `MIN_ORDER_NOT_MET` | Empty orders can't receive a discount |

### Group 3 — Only PENDING orders are editable (AC5) · unit
Baseline: Given order status PENDING · When apply a valid coupon

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_apply_when_order_is_pending` | — | applied | The normal checkout flow works |
| ❌1 | negative | `should_reject_when_order_is_paid` | status PAID | 409 `ORDER_NOT_EDITABLE` | A paid price can't be changed afterwards |
| ❌2 | negative | `should_reject_when_order_is_cancelled` | status CANCELLED | 409 | Dead orders can't be modified |
| ❌3 | negative | `should_reject_when_order_is_shipped` | status SHIPPED | 409 | Every non-PENDING status is blocked, not just PAID |

### Group 4 — Discount calculation (AC7) · unit
Baseline: Given a FIXED coupon 20, subtotal 50 · When apply the coupon

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_subtract_full_value_when_subtotal_exceeds_coupon` | — | discount 20, total 30 | A fixed coupon takes off exactly its value |
| ✅2 | edge | `should_round_half_up_for_percentage_discount` | 15% of 33.33 | discount 5.00 | Money is rounded consistently with the rest of the codebase |
| ❌1 | negative | `should_cap_discount_at_subtotal_when_coupon_exceeds_it` | coupon value 80 | discount 50, total 0.00 | The total never goes negative |

### Group 5 — Replace & remove (AC4, US2) · unit
Baseline: Given the order already has `SUMMER10` applied · When apply another coupon / remove the coupon

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_replace_existing_coupon_when_applying_new_one` | — | new coupon applied, old one gone | Only one coupon per order; the new one wins |
| ✅2 | edge | `should_reset_discount_when_coupon_removed` | DELETE instead of apply | discount 0, full price | DELETE restores the full price |
| ❌1 | negative | `should_keep_old_coupon_when_new_one_is_invalid` | new code expired | 422; `SUMMER10` still applied | A failed replace doesn't lose the customer's existing discount |
| ❌2 | negative | `should_reject_remove_when_order_is_paid` | status PAID | 409 | Removing is also blocked after payment |

### Group 6 — Concurrency (schema: `orders.version`) · integration (Testcontainers)
Baseline: Given the order version matches · When apply a valid coupon

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_persist_coupon_and_discount_together` | — | `coupon_id` and `discount_amount` both saved | Both are written in one transaction |
| ❌1 | negative | `should_return_409_when_order_modified_concurrently` | stale version | 409 `CONCURRENT_MODIFICATION` | Two simultaneous applies can't overwrite each other |

### Group 7 — Schema integrity · integration
Baseline: Given an order with a coupon applied

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_set_coupon_fk_when_applied` | — | `orders.coupon_id` references the coupon | The link is stored as a real FK |
| ❌1 | negative | `should_block_deleting_coupon_used_by_order` | delete the coupon row | FK violation (RESTRICT) | Order history can't lose its coupon reference |

### Security groups (API level, `@SpringBootTest` + MockMvc with the real security filters)

### Group S1 — Authentication (SEC1)
Baseline: Given a valid JWT for the order's owner · When apply a valid coupon

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_return_200_with_valid_token` | — | 200 | Logged-in owners can apply coupons |
| ❌1 | negative | `should_return_401_when_no_token` | no `Authorization` header | 401, order unchanged | Anonymous users can't touch orders |
| ❌2 | negative | `should_return_401_when_token_expired` | expired JWT | 401 | Old stolen tokens stop working |
| ❌3 | negative | `should_return_401_when_token_signature_invalid` | tampered signature | 401 | Forged tokens are rejected |

### Group S2 — Ownership / IDOR (SEC2, AC6)
Baseline: Given customer A · When A applies a coupon to A's order

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_return_200_when_caller_owns_order` | — | 200 | Owners can change their own orders |
| ❌1 | negative | `should_return_404_when_order_belongs_to_another_customer` | B's orderId | 404, B's order unchanged | Users can't modify other users' orders |
| ❌2 | negative | `should_return_identical_404_for_missing_and_foreign_order` | random orderId vs B's orderId | Same status and body for both | Attackers can't tell which order ids exist |
| ❌3 | negative | `should_return_404_on_delete_of_foreign_order` | DELETE on B's order | 404 | The remove endpoint is protected too, not just apply |

### Group S3 — Mass assignment & data exposure (SEC3, SEC4)
Baseline: Given body `{ "couponCode": "SUMMER10" }` · When apply

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_return_only_documented_fields` | — | response has exactly the DTO fields | No internal ids or `min_order_amount` leak |
| ❌1 | negative | `should_ignore_client_supplied_discount` | body adds `"discountAmount": 999` | discount still 12 | Clients can't set their own discount |
| ❌2 | negative | `should_ignore_client_supplied_total` | body adds `"total": 0` | total still 108 | Clients can't set their own price |
| ❌3 | negative | `should_not_leak_stack_trace_on_error` | force a repository exception | 500 with a generic body only | Errors don't reveal internals |

### Group S4 — Injection (SEC5)
Baseline: Given code "SUMMER10" · When apply. Negatives only: the valid case is G1✅1.

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ❌1 | negative | `should_return_400_for_sql_injection_payload` | `"' OR '1'='1"` | 400, no DB error | SQL payloads are blocked by validation, and binding would block them anyway |
| ❌2 | negative | `should_return_400_for_script_payload` | `"<script>alert(1)</script>"` | 400 | HTML/JS can't be stored or echoed back |
| ❌3 | negative | `should_return_400_for_unicode_lookalike_code` | `"SUMMER１０"` (full-width digits) | 400 | The allow-list rejects tricky characters |

### Group S5 — Brute force protection (SEC6)
Baseline: Given the same user · When they make their 10th attempt within one minute

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_allow_requests_within_rate_limit` | — | 200 | Normal users are never blocked |
| ❌1 | negative | `should_return_429_on_11th_attempt_within_a_minute` | 11th request | 429 with `Retry-After` | Coupon codes can't be guessed by mass trial |
| ❌2 | negative | `should_count_failed_attempts_toward_limit` | 11 invalid codes | 429 | Failed guesses aren't free |

### Group S6 — Audit (SEC8) · unit
Baseline: Given a valid coupon · When apply

| # | Type | Test name | Changed condition (vs baseline) | Expected result (Then) | Demonstrates |
|---|---|---|---|---|---|
| ✅1 | baseline | `should_write_audit_log_when_coupon_applied` | — | one `COUPON_APPLIED` entry with user id | Every price change is traceable to a user |
| ❌1 | negative | `should_not_write_audit_log_when_apply_fails` | expired coupon | No `COUPON_APPLIED` entry | The audit log only records real changes |
| ❌2 | negative | `should_not_log_jwt_token` | any request | Log output has no `Bearer` value | Tokens never end up in the logs |
