---
name: update-setup
description: Sync this project's Claude setup (CLAUDE.md, .claude/settings.json, .claude/skills/) with the My-Agent-Setup GitHub repo using one explicit mode - push, pull or status. Run only when the user invokes /update-setup with a mode.
argument-hint: push | pull | status
disable-model-invocation: true
---

# Update Setup - Project <-> My-Agent-Setup

Keeps the Claude setup of **this project** in sync with [My-Agent-Setup](https://github.com/Vuthangvt1405/My-Agent-Setup) (`main`). It does not touch `~/.claude` or commit anything to this project's own git repo.

| Project path | My-Agent-Setup path |
|---|---|
| `CLAUDE.md` | `CLAUDE.md` |
| `.claude/settings.json` | `settings.json` |
| `.claude/skills/` | `skills/` |

Everything else (`launch.json`, `settings.local.json`, `.env*`, memory, sessions) is never synced.

All work goes through `scripts/sync_setup.sh` in this skill's folder. It keeps a working clone in `~/.cache/my-agent-setup` and always resets it to the newest `origin/main` first.

## Mode

The mode is `$ARGUMENTS`:

- `status` or empty -> **Status**
- `pull` -> **Pull**
- `push` -> **Push**
- anything else -> run **Status** and tell the user the valid modes. Never choose push or pull on your own.

## Status

Run `scripts/sync_setup.sh status`. Report the newest remote commit and either "in sync" or the list of differing files (`Only in project:` = local only, `Only in remote:` = remote only, `differ` = changed on one side). Suggest `/update-setup push` or `/update-setup pull`.

## Pull (remote -> project)

1. Run `status` first. Files that exist only in the project's `.claude/skills/` will be **deleted** by pull (it mirrors the remote). If any exist, or project files differ, list them and ask the user to confirm before pulling.
2. Run `scripts/sync_setup.sh pull`.
3. Report the remote commit pulled and the files changed. Changes to `CLAUDE.md` and `settings.json` apply from the next session.

## Push (project -> remote)

1. Run `status`. If in sync, report "nothing to push" and stop.
2. Validate each changed `.claude/skills/<name>/SKILL.md`: YAML frontmatter with `name` (kebab-case, same as folder) and `description`. Scan the changed files for secrets (API keys, tokens); stop if any are found.
3. Files that exist only in the remote will be **deleted** by push (it mirrors the project). If any exist, list them and ask the user to confirm.
4. Write a Conventional Commit message for the change:
   - New skill: `feat(skills): add <skill-name> skill`
   - Updated skill: `feat(skills): update <skill-name> skill (<short summary>)`
   - Settings: `chore(config): update settings.json (<setting>)`
   - Rules: `docs(config): update CLAUDE.md (<short summary>)`
   - Several kinds at once: one message summarising them.
5. Run `scripts/sync_setup.sh push "<message>"`. It commits to `main` and pushes.
6. Report the pushed commit hash and message, the files changed, and the repo link.
