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

_Plan mode: no files, migrations, or data were changed._

Once you've answered, I'll update the plan and ask for approval before creating the scaffold (Step 9, see `scaffold.md`).
