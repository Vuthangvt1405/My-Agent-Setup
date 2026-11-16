# Step 1 — Analyze the raw requirement

Read everything the user gave you and extract it into a short analysis. Show this analysis to the user, because it is where misunderstandings get caught:

| Item | What to find |
|---|---|
| Actors | Who uses this? (customer, admin, guest, system/cron, external service) Different actors usually mean different stories |
| Goals | What each actor wants to do |
| Business value | Why it matters: revenue, time saved, compliance, fewer support tickets. If it isn't stated, propose one and mark it *assumed* |
| Rules & constraints | Limits, formats, permissions, deadlines, numbers mentioned |
| Data involved | Entities/fields mentioned (order, coupon, expiry date…) |
| Ambiguities | Vague words ("fast", "easy", "some", "etc.", "and so on"), missing numbers, undefined behavior on failure |

**Never invent business rules.** Keep three kinds of statement visibly separate:
- **Stated**: the requirement says it.
- **Assumed**: a reasonable default you chose, marked *(assumption)* so the PO can confirm or reject it.
- **Unknown**: goes into Open Questions.

### Never ask the customer technical questions
The person answering Open Questions is the customer / PO. They decide **what** the product does, not **how** it is built. Only ask them about things they can see, choose, or care about: behavior, wording, defaults, priorities, cost/budget, risk they accept, what happens to the user on failure.

Never ask them about: models, providers, libraries, APIs, timeouts in seconds, retry counts, data formats, context/message counts, caching, schema, endpoints, or how many items a component processes. For these, pick a sensible default yourself, write it in the **Developer Notes** as "dev decision" (or "tune in the spike"), and do not list it in Open Questions.

If a technical choice has a visible effect (e.g. "replies with search may be ~10 s slower"), ask about the **effect** in plain language, not the technical setting behind it. When in doubt, ask yourself: "Could a non-technical customer answer this without asking a developer?" If not, it's a dev decision.

If the requirement is too thin to write even one meaningful story (e.g. "add payments"), ask 2–4 focused questions first instead of producing a ticket full of guesses.
