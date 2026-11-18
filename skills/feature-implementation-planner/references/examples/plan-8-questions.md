# Example plan (continued): Apply Coupon to Order

Part of the worked example; earlier sections are in the other `plan-*.md` files.

## 8. Questions & Confirmations

**Questions**
1. Should a coupon have a global usage limit (e.g. first 100 uses)? If yes, is a use counted at apply or at payment?
2. Is coupon code matching case-insensitive from the business's point of view?
3. If the cart changes after a coupon is applied and drops below the minimum, should the coupon be removed automatically or blocked at checkout?
4. **Security trade-off:** separate error codes (`COUPON_EXPIRED` vs `COUPON_NOT_FOUND`) are friendlier, but they reveal that a code exists. Is that acceptable with the rate limit in place, or should all invalid codes return one generic error?
5. Is 10 attempts per minute per user the right rate limit? Should there also be a per-IP limit?

**Assumptions to confirm** (default in brackets)
6. One coupon per order; a new one replaces the old [yes].
7. Not-owner returns 404, not 403 [yes].
8. Discount is rounded HALF_UP to 2 decimals [yes].
9. PUT for apply; DELETE returns 200 with the pricing body [yes].
10. The `coupon_id` FK uses ON DELETE RESTRICT [yes].
11. The migration is `V12`, the next free Flyway number [yes].
12. Unknown JSON fields are ignored, not rejected with 400 [yes].

_Plan mode: no files, migrations, or data were changed other than this plan file._

Once you've answered, I'll update the plan and ask for approval before creating the scaffold (Step 9, see `scaffold.md`).

---

# After the user answers (Plan update procedure)

**User:** "1: not now, later ticket. 2: yes. 3: block at checkout, that's the checkout team's work. 4: one generic error. 5: 10/min per user plus 30/min per IP. Rest as you proposed."

### Decisions
D1 = Q1 no usage limit now · D2 = Q2 case-insensitive · D3 = Q3 blocked at checkout, other team · D4 = Q4 one generic `COUPON_INVALID` · D5 = Q5 per-user + per-IP limit · D6 = A6–A12 as proposed.

### Decision log (new rows, written to the plan file)
| # | Question | Answer | What changed in the plan |
|---|---|---|---|
| D1 | Q1: global usage limit? | Not now; later ticket | §1 Out of scope + "global usage limit (follow-up)" · §8 Q1 marked answered |
| D2 | Q2: case-insensitive? | Yes | No change; confirms §4.3 `couponCode` normalization and the G1 lowercase edge test · §8 Q2 marked |
| D3 | Q3: cart drops below minimum? | Blocked at checkout, checkout team | §1 Out of scope + "re-check minimum at checkout (checkout team)" · §8 Q3 marked |
| D4 | Q4: separate error codes? | No, one generic `COUPON_INVALID` | §1 AC2 error code · §4.1 `ErrorCode` (3 codes → 1) · §4.2 PUT errors · §4.3 error codes + error-response example · §5 SEC6 mitigation · §6 422 branch · §7 G1 ❌1–3 expect `COUPON_INVALID` · §8 Q4 marked |
| D5 | Q5: rate limit? | 10/min per user + 30/min per IP | §5 SEC6 mitigation · §6 429 branch note · §7 new S5 ❌3 `should_return_429_when_ip_exceeds_30_per_minute` · §7 coverage + test count 55 → 56 · §8 Q5 marked |
| D6 | A6–A12 | Confirmed as proposed | §8 A6–A12 marked |

### Sync table (shown in chat after re-reading the file)
| Decision | Sections that had to change | Updated in file? |
|---|---|---|
| D1 | §1, §8 | ✅ ✅ |
| D2 | §8 (§4.3 and G1 already correct) | ✅ |
| D3 | §1, §8 | ✅ ✅ |
| D4 | §1 AC2, §4.1, §4.2, §4.3, §5, §6, §7 G1, §8 | ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ |
| D5 | §5, §6, §7 S5, §7 coverage, §8 | ✅ ✅ ✅ ✅ ✅ |
| D6 | §8 | ✅ |
| Checks | `grep -nE "COUPON_(EXPIRED\|NOT_FOUND\|INACTIVE)"` hits only the Decision log · AC1–AC7 all in coverage · SEC1–SEC8 all have tests · count 56 | ✅ |

> Plan updated in `docs/plans/apply-coupon-plan.md` (v1 → v2). All questions answered. Approved — shall I create the scaffold?

**The wrong version** logs D4 as "AC2 and G1 changed" and stops there. The plan still lists `COUPON_EXPIRED` in §4.3, §5 and the diagram, and the scaffold then ships three error codes instead of one. The trace in step 2 and the grep in step 5 exist to catch exactly that.
