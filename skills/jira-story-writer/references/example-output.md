# Example output

**Raw requirement from the user (a pasted Slack message from the marketing lead):**
> "We want customers to be able to use discount codes when they buy. Marketing should be able to create codes, like 10% off or $20 off, with an end date, and some codes only work if the order is big enough. Also we don't want people abusing it. Need this before the Black Friday campaign."

---

# Discount Coupons

## Requirement Analysis

| Item | Finding |
|---|---|
| Actors | **Customer** (applies codes), **Marketing admin** (creates codes) |
| Goals | Customer: pay less using a code. Marketing: create and control campaign codes |
| Business value | Drive Black Friday sales via campaigns *(stated: deadline is Black Friday)* |
| Rules (stated) | Types: percentage or fixed amount · has an end date · optional minimum order amount |
| Rules (assumed) | One coupon per order *(assumption)* · only on unpaid orders *(assumption)* · discount can't exceed order total *(assumption)* |
| Data | Coupon (code, type, value, end date, min order), Order (subtotal, discount, total) |
| Ambiguities | "abusing it": rate limiting? usage limits per customer? total uses? · "end date": inclusive? which timezone? · can codes stack? · can admins edit or deactivate codes? |

## Estimation Log

First pass: the requirement naturally falls into two big candidate stories, both too large. Each is split until every story does one observable thing and is ≤ 5 points.

| Candidate story | Complexity | Uncertainty | Effort | Points | Action |
|---|---|---|---|---|---|
| Marketing manages coupons (create, deactivate) | Medium | Medium | High | 13 | ✂️ Split by operation |
| ↳ DC-1: Create discount coupon | Medium | Low | Medium | 5 | ⚠️ At the limit, keep |
| ↳ DC-6: Deactivate coupon before expiry | Low | Medium (Q3) | Low | 2 | ✅ Keep, pending Q3 |
| Customer uses coupon at checkout | High | High (7 open questions) | High | 21 | ✂️ Split by operation, then by business rule |
| ↳ DC-2: Apply a basic coupon (valid / unknown / expired / paid order, plus security) | Medium | Medium | Medium | 5 | ⚠️ At the limit, keep |
| ↳ DC-3: Enforce minimum order and discount cap | Low | Low (Q2) | Low | 2 | ✅ Keep |
| ↳ DC-4: Replace an applied coupon | Low | Low | Low | 2 | ✅ Keep |
| ↳ DC-5: Remove applied coupon | Low | Low | Low | 1 | ✅ Keep |

Notes:
- DC-2 keeps the abuse protection on purpose. Splitting it out would let an unprotected coupon feature ship on Black Friday.
- The children add up to less than the parents (17 vs 34), because splitting removed most of the uncertainty.

## Ticket Structure
```
Epic: Discount Coupons for Black Friday   (prefix DC, total: 17 points)
├── DC-1: Create discount coupon (admin)              (5 pts ⚠️ at limit, Highest, depends on: —)
├── DC-2: Apply discount coupon to pending order      (5 pts ⚠️ at limit, Highest, depends on: DC-1)
├── DC-3: Enforce minimum order and discount cap      (2 pts, Highest, depends on: DC-2)
├── DC-4: Replace an applied coupon                   (2 pts, High, depends on: DC-2)
├── DC-5: Remove applied coupon from order            (1 pt, High, depends on: DC-2)
└── DC-6: Deactivate coupon before expiry (admin)     (2 pts, Medium, depends on: DC-1) — pending Q3
```
DC-1 comes first, because customers can't apply codes until codes exist.

## Files written
```
docs/tasks/discount-coupons/
├── README.md                                  ← backlog index (id, summary, points, depends on, status)
└── backlog/
    ├── DC-1-create-discount-coupon.md
    ├── DC-2-apply-coupon-to-order.md
    ├── DC-3-minimum-order-and-cap.md
    ├── DC-4-replace-applied-coupon.md
    ├── DC-5-remove-applied-coupon.md
    └── DC-6-deactivate-coupon.md
```

---

## File: `backlog/DC-3-minimum-order-and-cap.md`

```markdown
# DC-3 — Enforce minimum order and discount cap

**Type:** Story | **Epic:** Discount Coupons for Black Friday | **Priority:** Highest | **Labels:** `checkout`, `black-friday` | **Components:** Orders, Checkout
**Story points (suggested):** 2 — Complexity Low, Uncertainty Low, Effort Low — two pricing rules on top of DC-2
**Depends on:** DC-2
**Status:** Backlog

[Epic PRD](../../../requirements/discount-coupons/README.md)

## User Story
As a **logged-in customer**, I want **a coupon to apply only when my order qualifies and never to cost more than my order**, so that **I always see a correct, honest total before paying**.

## Background
Some campaign codes only work on bigger orders, and fixed-amount codes can be larger than a small order. DC-2 applies a basic coupon; this story adds the two rules that keep the price correct.

## Acceptance Criteria
**AC1 — Minimum order not met**
Given the coupon "BIG20" requires a minimum order of $50.00
And my subtotal is $49.99
When I apply "BIG20"
Then I see "Add $0.01 more to use this code"
And my total is unchanged

**AC2 — Minimum met exactly** *(assumption, see Q2)*
Given the coupon "BIG20" requires a minimum order of $50.00
And my subtotal is $50.00
When I apply "BIG20"
Then the coupon is applied

**AC3 — Discount never exceeds the order total** *(assumption)*
Given my subtotal is $15.00
And the coupon "FLAT20" gives $20.00 off
When I apply it
Then the discount is $15.00 and the total is $0.00

## Developer Notes
- **Business rule details:** check the minimum after DC-2's checks (ownership → status → exists → active → not expired), so users only see messages about orders they own.
- **Security considerations:** calculate the discount on the server only; don't reveal the minimum beyond the error message.
- **Testing hints:** coupons with a minimum, and a fixed coupon larger than the order.

## Out of Scope
- Removing the coupon automatically when items are removed and the order drops below the minimum (Q5)
- Usage limits per customer or in total (Q1, would be its own ticket)

## Open Questions
- [ ] Q2: Is the minimum order amount inclusive ($50.00 qualifies for a $50 minimum)? (@Marketing lead)
- [ ] Q5: If items are removed and the order drops below the minimum, should the coupon be removed automatically? (@PO)
```

The other files follow the same template. Example of the backlog index:

## File: `README.md`

```markdown
# Discount Coupons — Backlog

| Ticket | Summary | Points | Depends on | Status |
|---|---|---|---|---|
| [DC-1](backlog/DC-1-create-discount-coupon.md) | Create discount coupon (admin) | 5 | — | Backlog |
| [DC-2](backlog/DC-2-apply-coupon-to-order.md) | Apply discount coupon to pending order | 5 | DC-1 | Backlog |
| [DC-3](backlog/DC-3-minimum-order-and-cap.md) | Enforce minimum order and discount cap | 2 | DC-2 | Backlog |
| [DC-4](backlog/DC-4-replace-applied-coupon.md) | Replace an applied coupon | 2 | DC-2 | Backlog |
| [DC-5](backlog/DC-5-remove-applied-coupon.md) | Remove applied coupon from order | 1 | DC-2 | Backlog |
| [DC-6](backlog/DC-6-deactivate-coupon.md) | Deactivate coupon before expiry (admin) | 2 | DC-1 | Backlog |
```

---

## Open Questions (all stories)
- [ ] Q1: Can a customer use the same code on multiple orders? Is there a total usage limit (e.g. first 500 uses)? (@Marketing lead)
- [ ] Q2: Is the minimum order amount inclusive? (@Marketing lead)
- [ ] Q3: Should admins be able to deactivate a code early, e.g. if it leaks? (@Marketing lead)
- [ ] Q4: If a code expires after it's applied but before payment, should the discount still be honored? (@PO)
- [ ] Q5: If items are removed and the order drops below the minimum, should the coupon be removed automatically? (@PO)
- [ ] Q6: Which timezone defines the end date, the store's or UTC? (@PO)
- [ ] Q7: Are separate error messages ("expired" vs "not valid") acceptable, given they reveal that a code exists? (@Security / PO)
