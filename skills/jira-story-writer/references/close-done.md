# Close finished work (`done` mode)

Use this instead of Steps 1–4 when the user says a ticket or epic is finished ("it's merged", "move it to done", "close the epic"). Take their word that it's done; don't re-check git.

**Command form:** `/jira-story-writer done [ticket ids or epic]`. When the skill's arguments start with `done`, run this mode, never Steps 1–4.
- `/jira-story-writer done SS-1 PCD-3`: mark those tickets Done, then close any epic whose tickets are now all Done.
- `/jira-story-writer done 01-sqlite-storage` (or the epic's prefix, `SS`): mark every ticket in that epic Done and close it.
- `/jira-story-writer done` with nothing after it: list the open epics in `docs/tasks/` with each ticket's status, and ask which tickets or epic are done.

1. **Mark tickets Done:** set `**Status:** Done` in each finished ticket file and in the epic's `README.md` table.
   - Move that ticket's plan files to `docs/plans/done/` right away: files in `docs/plans/` whose name starts with the ticket id (`PCD-1-*.md`), or that the ticket or plan names as its plan / scaffold report (older plans may not carry the id, e.g. `sqlite-alembic-storage-plan.md`). If you can't tell which plan belongs to the ticket, ask.
2. **Close the epic** once every ticket in it is Done (spikes included). If some are still open, list them and ask before moving.
   - Move `docs/tasks/<epic-slug>/` to `docs/tasks/done/<epic-slug>/`.
   - Move any of the epic's plan files still in `docs/plans/` to `docs/plans/done/`.
   - Leave `docs/requirements/<epic-slug>/` where it is; the PRD stays the record of the decision.
3. **Fix every link** in `docs/` that pointed to or from the moved files (relative paths change by one level), then check that no `.md` link in `docs/` is broken.
4. **"Later sprints" items** in the epic README are not tickets; mention them so the user can turn them into a new epic if wanted.
5. Report what moved where in a short list.
