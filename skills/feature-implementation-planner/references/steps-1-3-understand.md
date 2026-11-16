## Step 1 — Understand the requirement (US + AC)

Restate the requirement in your own words so the user can catch misunderstandings early.

**User Stories**: write one per distinct actor or goal.
> As a **[role]**, I want **[capability]**, so that **[business value]**.

**Acceptance Criteria**: write them as Given/When/Then and number them, so tests can reference them (AC1, AC2, ...).
> **AC1**: Given [precondition], When [action], Then [observable result].

**Input from `jira-story-writer`**: if the requirement is a ticket in that skill's format (Summary, User Story, numbered Given/When/Then ACs, Developer Notes, Out of Scope, Dependencies, Open Questions, story points), or a story file in `docs/features/user-story/`, use it as the source of truth:
- Copy the User Story and ACs as-is, keeping their numbers (AC1, AC2…), so tests and the ticket reference the same IDs.
- Treat Developer Notes as hints to check in Step 2, not as decisions. Anything marked *(assumption)* must be confirmed against the codebase.
- Copy Out of Scope and Dependencies as they are.
- Carry the ticket's Open Questions into Step 8, unless the codebase answers them (then say so and cite the file).
- If the plan shows the story is clearly bigger than its points (e.g. a schema change on a 2-pointer), say so in Step 8 and suggest re-estimating or splitting it with `jira-story-writer`.
- Link the ticket/story in the plan file's `Source:` line.

If there is no ticket and the requirement is rough (a client message, notes, an idea), suggest running `jira-story-writer` first. If the user wants to go on without it, write the US/AC yourself as described here.

Rules:
- If the user supplied US/AC, keep their wording and number them. Add missing ones only as "Proposed AC" so the user can approve them.
- Cover the unhappy paths too: invalid input, not found, unauthorized, conflicts, limits. Missing negative AC is the most common gap.
- List **Out of scope** items explicitly, so scope doesn't creep.
- Anything ambiguous goes into the Step 8 questions. Don't silently guess.

## Step 2 — Explore the codebase and learn its patterns

The new feature should look like it was written by the same team. Before designing anything, find 1–3 existing features most similar to this one and read them end to end.

Look for these, and report what you find:

| Area | What to find |
|---|---|
| Architecture / layering | e.g. controller → service → repository, hexagonal, CQRS |
| Folder & naming conventions | where files live, suffixes (`*Request`, `*Dto`, `*Handler`) |
| API conventions | URL style (plural nouns, kebab-case, versioning `/api/v1`), pagination, response envelope |
| Validation | annotations, validator classes, schema libs |
| Error handling | exception types, global handler, error response shape, error codes |
| Persistence | ORM, migration tool, transaction handling |
| Auth & security | how endpoints are protected (filters, guards, annotations), how the current user/roles are read, existing rate limiting, audit logging, CORS/CSRF config |
| Testing | framework, unit vs integration split, mocks/fakes, test naming, fixtures/builders |

Present your findings as a table, with **file paths as evidence** (e.g. `src/order/OrderController.java:42`). If no codebase is available, say so, state the stack you are assuming, and add "confirm stack" to Step 8.

## Step 3 — Understand the schema and relationships

Most feature bugs come from misunderstanding the data model, so map it before designing the API. Find the schema from the source of truth the project uses: migration files (Flyway, Liquibase, Alembic, Prisma, knex…), ORM entities/models, `schema.sql`, or DB docs.

### 3a. Existing tables/entities involved
For each table the feature reads or writes:

| Table / Entity | Key columns (type, nullable) | Constraints & indexes | Evidence |
|---|---|---|---|

Include primary keys, foreign keys, unique constraints, enums/status columns, soft-delete flags, audit columns (`created_at`, `version` for optimistic locking), and money/time types.

### 3b. Relationships
List every relationship the feature touches:

| From | To | Cardinality | FK / join | Owning side & cascade/fetch | Business meaning |
|---|---|---|---|---|---|

Then add a Mermaid `erDiagram` of only the involved entities. This is a data map, separate from the single workflow diagram in Step 6. Call out risks you notice: N+1 queries from lazy loading, cascades that could delete too much, missing indexes on FKs or lookup columns, nullable columns that the feature assumes are filled.

### 3c. Proposed schema changes (described, not applied)
- New tables/columns: name, type, nullable, default, constraints, and **why** each is needed.
- New indexes and why (which query they serve).
- Migration plan: file name following the project convention, whether it is backward-compatible, how existing rows are backfilled, and how to roll back.
- If no schema change is needed, say so explicitly.
