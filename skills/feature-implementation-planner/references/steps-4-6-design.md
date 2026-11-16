## Step 4 — Implementation idea: endpoints and DTOs

### 4a. Approach summary
Write 3–6 sentences. Say which components are added or changed, which existing pattern is reused (cite the file from Step 2), how it uses the schema from Step 3, and any key design decision with its reason. List the files that **would** be created or modified, but do not touch them.

### 4b. Endpoint design
Fill in this table for each endpoint:

| Method | URL | Purpose | Success | Errors |
|---|---|---|---|---|

Then briefly explain the design choices:
- Why this HTTP method (idempotency, safe vs unsafe)
- Why this URL shape (resource vs action sub-resource, nesting that reflects the Step 3 relationships)
- Versioning
- How it matches the codebase convention

### 4c. DTOs
For **every** request and response DTO, give the JSON shape and then a field table:

| Field | Type | Required | Validation / Format | Maps to (table.column) | Meaning (why it exists) |
|---|---|---|---|---|---|

The "Meaning" column is the important one. Explain what the field represents for the business and why the client needs it; don't just repeat the field name. The "Maps to" column links the API back to the schema. Write "derived" for computed fields.

Also show the **error response** shape, reusing the codebase's existing one. Never expose internal fields in responses (non-public DB ids, password hashes, internal flags), and mention it when you deliberately leave something out.

## Step 5 — Security review

Every new endpoint is new attack surface, so review it before the tests are designed. Then every risk found here becomes a test in Step 7. Use the OWASP API Security Top 10 as a checklist, and only report items that actually apply to this feature. Saying "not applicable, because…" is fine and useful.

| Check | Questions to answer for this feature |
|---|---|
| Authentication | Which endpoints need a logged-in user? What happens with a missing, expired, or malformed token? |
| Object-level authorization (BOLA/IDOR) | Can user A read or modify user B's resource by changing an id in the URL or body? Is ownership checked in the query, not after loading? Do "not yours" and "doesn't exist" return the same response, so ids can't be enumerated? |
| Function-level authorization | Does the endpoint need a role (admin, staff)? Can a normal user call it? |
| Mass assignment / property-level auth | Can the client send fields it must not control (price, discount, status, ownerId, role)? The request DTO must only contain fields the client is allowed to set. |
| Excessive data exposure | Does the response leak internal ids, other users' data, business rules, or stack traces? |
| Input validation & injection | Are all inputs validated (length, format, allow-list)? Are queries parameterized (no string-built SQL/JPQL)? Is any output rendered as HTML (XSS)? Is any input used in file paths, shell, or URLs (SSRF)? |
| Resource consumption & brute force | Can someone guess codes, ids, or passwords by trying many values? Is there rate limiting, pagination with a max size, and a payload size limit? |
| Business logic abuse | Can the flow be replayed, raced (double-apply, double-spend), or done out of order? |
| Sensitive data & logging | Are secrets or tokens kept out of logs? Is the security-relevant action audit-logged (who, what, when)? |

Output a table:

| # | Risk | Where (endpoint/field) | Mitigation in this plan | Test ref |
|---|---|---|---|---|

Each mitigation should name the concrete mechanism and the existing codebase pattern it reuses, from Step 2. Any risk that needs a product decision goes into Step 8, for example whether error messages may reveal that a coupon exists.

## Step 6 — One workflow diagram

Choose **exactly one** diagram, the one that best explains how the feature runs, and say in one sentence why you chose it:
- **Sequence diagram** (default for API features): shows the request flow across client → controller → service → repository/external systems, with error branches drawn using `alt`.
- **Flowchart**: when the feature is mostly decision logic or validation rules.
- **State diagram**: when the feature changes an entity's lifecycle status.

Write it in Mermaid. Include the main error branches and the security checks from Step 5 (authentication, rate limiting, ownership), not only the happy path.

**Check that every diagram (including any `erDiagram`) renders before you finish.** A diagram with a syntax error shows up as an error box, not a picture. After writing the report file, run `bash <this skill's dir>/scripts/check_mermaid.sh <report file>`. It renders every ```` ```mermaid ```` block with the Mermaid CLI and prints `OK`/`FAIL` with the block's line. Fix each `FAIL` and re-run until all pass. Common causes: unquoted labels with `()`, `:`, `/`, `{}` or `"` (wrap them as `A["label (x)"]`), `end` used as a node name, `alt`/`opt`/`loop` without a matching `end`, and arrows with a missing message (`A->>B: msg`). If the check cannot run (no Node/network), say so in the report instead of claiming the diagram was verified.
