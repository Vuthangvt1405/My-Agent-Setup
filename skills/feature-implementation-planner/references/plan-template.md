## Output template

The plan file uses these exact headings so it is easy to scan:

```
# Feature Plan: [Feature name]
Status: Draft — awaiting answers · v1 · Source: [link to story/ticket] · Date: YYYY-MM-DD
## 1. Requirement (User Stories & Acceptance Criteria)
## 2. Codebase Patterns
## 3. Schema & Relationships
### 3.1 Existing Tables
### 3.2 Relationships (+ ER diagram)
### 3.3 Proposed Schema Changes
## 4. Implementation Idea
### 4.1 Approach & Files Affected
### 4.2 Endpoints
### 4.3 DTOs
## 5. Security Review
## 6. Workflow Diagram
## 7. TDD Test Plan
### Functional groups
### Security groups
## 8. Questions & Confirmations
## Decision log            (added once the user answers: | D# | Question | Answer | What changed in the plan |)
## 9–10. Scaffold report & verification   (link to <ID>-scaffold-report.md, added after the scaffold)
```

Step 9 (after approval) uses its own report format, "Scaffold report" in `steps-9-10-scaffold.md`, and is always followed by the Step 10 checkpoint in the same response. Both go into the separate scaffold report file; the plan only links to it.
