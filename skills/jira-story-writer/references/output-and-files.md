# Step 4 — Quality check, files and chat response

## Quality check before output

Silently check every story against this list and fix any problems before showing it:
- [ ] Summary is verb-first, specific, and ≤ 80 chars
- [ ] The role is specific, and the value is a real benefit
- [ ] Every AC is Given/When/Then, numbered, observable, and free of vague words
- [ ] Negative, permission, and security ACs are present where relevant
- [ ] No invented rules; every assumption is marked *(assumption)*
- [ ] Developer notes are hints, not a technical design
- [ ] Out of Scope and Open Questions are filled
- [ ] No Open Question is technical (models, APIs, timeouts, counts, formats); those are dev decisions in Developer Notes
- [ ] Every story is estimated, with its Complexity/Uncertainty/Effort reason
- [ ] If code was reachable, every requirement item has a status with evidence, and no story re-builds something already implemented or duplicates an open ticket
- [ ] Stories that touch existing code have a Current Behaviour section and regression ACs
- [ ] **No story is above 5 points**; anything bigger was split and re-estimated, and 5s are marked "at the limit"
- [ ] Every story has its own ticket id and is in its own file `docs/tasks/<epic-slug>/backlog/<TICKET-ID>-<slug>.md`, with `# <TICKET-ID> — <Summary>` as the first line
- [ ] The chat response stays concise; full ACs and dev notes live in the files

## Output & Documentation Architecture

**Do NOT dump all full stories, ACs, or tasks into the chat output.** Writing walls of text in chat overwhelms the user and makes requirements hard to track, review, and paste into Jira. Instead, write the full tickets to structured Markdown files in `docs/` and provide a clean executive summary in chat with clickable file links.

### Directory Structure

```text
docs/
├── research/                       # Research documents, architectural spikes, and deep dives
├── requirements/                   # Product requirements & Epic PRDs (high-level vision, analysis, estimation logs)
│   └── <epic-slug>/
│       └── README.md               # Epic PRD: Background, Actors, Scope, Open Questions, Ticket Tree
└── tasks/                          # The Ready-to-Do User Stories for developers ("what developers need to work on right now")
    ├── done/                       # Finished epics, moved here whole (see close-done.md)
    └── <epic-slug>/
        ├── README.md               # Backlog index: ticket id, summary, points, depends on, status
        └── backlog/                # One file per User Story, one ticket per file
            ├── PCD-1-<slug>.md     # First line: "# PCD-1 — <Summary>"
            ├── PCD-2-<slug>.md
            └── ...
```

For a single standalone story (no epic):
```text
docs/
└── tasks/
    └── backlog/
        └── <PREFIX>-1-<slug>.md    # Standalone User Story; prefix from its feature name
```

### File Writing Rules

1. **Requirements PRD (`docs/requirements/<epic-slug>/README.md`)**:
   - Acts as the Product Requirement Document (PRD) for the Epic.
   - Contains: Epic Summary, Suggested Total Points, Requirement Analysis table, Implementation Check table (with "Already implemented, no ticket needed"), Estimation Log, and links to all User Stories in `docs/tasks/<epic-slug>/`.
2. **Ready-to-Do User Stories (`docs/tasks/<epic-slug>/`)**:
   - Developers only care about the **User Stories they need to do right now**! Put the sprint-ready user story files directly in this folder.
   - `README.md`: backlog index table listing every ticket id (linked to its file), summary, points, dependencies, and status (`Backlog`, `Ready`, `In Progress`, `Done`).
   - `backlog/<TICKET-ID>-<slug>.md`: one complete, standalone User Story per file, never several stories in one file. `<slug>` is 2–5 lowercase kebab-case words:
     - **First line**: `# <TICKET-ID> — <Summary>` (summary verb-first, specific, ≤ 80 chars)
     - **Metadata**: Type, Epic, Priority, Story Points (suggested with Complexity/Uncertainty/Effort), Depends on, Status
     - **User Story**: "As a [role], I want [capability], so that [business value]"
     - **Background**: Brief context of the feature
     - **Acceptance Criteria**: Numbered Given/When/Then ACs covering happy path, validation, errors, security, and edge cases
     - **Developer Notes**: Architectural hints, data schemas, affected areas, dev decisions, testing tips
     - **Out of Scope & Dependencies**
     - Links back to `[Epic PRD](../../../requirements/<epic-slug>/README.md)`.

### Chat Response Format

As the **Product Owner (PO)**, keep your chat response concise, professional, and stakeholder-aligned:

```markdown
# [Epic Name]

> 📋 **Sprint Backlog Ready**: As your Product Owner, I have organized the Epic PRD in [`docs/requirements/<epic-slug>/`](file:///absolute/path/to/docs/requirements/<epic-slug>/README.md) and placed the ready-to-do User Stories directly into [`docs/tasks/<epic-slug>/`](file:///absolute/path/to/docs/tasks/<epic-slug>/README.md) for developers to pick up immediately.

## Requirement Analysis
(Table from Step 1: actors, goals, value, rules, data, ambiguities)

## Implementation Check
(Table from Step 1b with evidence and search coverage, plus what is already implemented or planned. If no code was reachable, say "Not checked: no codebase available")

## Estimation Log
(Table from Step 2, showing every split)

## Sprint Backlog (User Stories Ready to Do)
- [Sprint Backlog README](file:///absolute/path/to/docs/tasks/<epic-slug>/README.md)
- ├── [PCD-1: Summary](file:///absolute/path/to/docs/tasks/<epic-slug>/backlog/PCD-1-<slug>.md) (3 pts, Priority: High)
- ├── [PCD-2: Summary](file:///absolute/path/to/docs/tasks/<epic-slug>/backlog/PCD-2-<slug>.md) (2 pts, Priority: Highest)
- └── ...

## Open Questions / PO Notes
(Consolidated list for stakeholders to clarify, or confirmed requirements checklist)
```

Use Markdown by default, since Jira Cloud's editor accepts Markdown when pasted. If the user says they use **Jira Server/Data Center** or asks for **wiki markup**, convert it: `h2.` for headings, `*bold*`, `# ` for numbered lists, `* ` for bullets, `||header||` / `|cell|` for tables, and `{code}...{code}` for code blocks.

Write the tickets in the same language the user used for the requirement, unless they ask for another language (many teams want Jira in English even when discussing in another language, so ask if unclear).

End by offering: "Want me to adjust anything, or take one of these stories into implementation planning?" That hand-off goes to `feature-implementation-planner` if it's installed.
