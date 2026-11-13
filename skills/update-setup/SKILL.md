---
name: update-setup
description: Automatically sync, update, commit, and push the global Claude & agent configuration in ~/.claude (My-Agent-Setup repository). Syncs skills between local workspaces (.agents/skills, .claude/skills) and global ~/.claude/skills, pulls remote updates, validates skill frontmatter, commits with conventional commit messages, and pushes to GitHub. Use whenever the user wants to update setup, sync setup, backup Claude configuration, push skills to GitHub, or pull changes on a new machine.
---

# Update Setup — Global Claude & Agent Sync

Keep your global Claude setup (`~/.claude`) synchronized, version-controlled, and backed up to GitHub ([`My-Agent-Setup`](https://github.com/Vuthangvt1405/My-Agent-Setup.git)).

---

## Capabilities & Workflows

| Trigger | Action |
|---|---|
| "update setup", "sync setup", "push setup" | **A. Full Sync & Push** (detects workspace skill changes, syncs to global, commits, and pushes) |
| "pull setup", "update from github" | **B. Pull & Fast-Forward** (pulls latest skills/settings from `origin/main`) |
| "check setup", "setup status" | **C. Status & Audit** (lists installed skills, modified files, and sync status) |

---

## Security & Exclusion Rules

**NEVER stage or commit sensitive user session data or credentials:**
- `.credentials.json`
- `sessions/`
- `file-history/`
- `backups/`
- `cache/`
- `shell-snapshots/`
- Local `.env` files

Only track clean, reusable configuration:
- `skills/*` (custom skills)
- `settings.json` (global user preferences, with tokens omitted)
- `README.md` and `.gitignore`
- `CLAUDE.md` (global coding rules and instructions)

---

## Workflow A: Full Sync & Push (Step-by-Step)

Work through these steps in order:

### 1. Identify Workspace Skill Updates
Check if the user modified a skill in the current project workspace:
- `.agents/skills/<skill-name>/`
- `.claude/skills/<skill-name>/`

If workspace skills are newer or updated compared to `~/.claude/skills/<skill-name>/`, sync the updated files to `~/.claude/skills/<skill-name>/`.

### 2. Check Repository Status
Check the git status of the global Claude repository:
```bash
git -C "$HOME/.claude" status
```
Identify all staged, unstaged, and untracked skill or setting files.

### 3. Validate Skill Frontmatter
Ensure any new or modified skill has valid YAML frontmatter in `SKILL.md`:
```yaml
---
name: <kebab-case-name>
description: <concise actionable description of what the skill does and when to use it>
---
```

### 4. Stage and Commit
Stage only the clean configuration files:
```bash
git -C "$HOME/.claude" add skills/<skill-name>
# If settings.json was modified:
git -C "$HOME/.claude" add settings.json
# If CLAUDE.md was modified:
git -C "$HOME/.claude" add CLAUDE.md
```

Commit using the Conventional Commits format:
- New skill: `feat(skills): add <skill-name> skill`
- Updated skill: `feat(skills): update <skill-name> skill (<short summary of change>)`
- Settings change: `chore(config): update settings.json (<setting name>)`
- CLAUDE.md change: `docs(config): update CLAUDE.md (<short summary of change>)`

### 5. Pull & Rebase (Linear History)
Ensure no remote changes collide before pushing:
```bash
git -C "$HOME/.claude" pull --rebase origin main
```

### 6. Push to GitHub
```bash
git -C "$HOME/.claude" push origin main
```

### 7. Report Summary
Display a concise summary to the user:
- Pushed commit hash and message
- List of synced skills
- Link to GitHub repository (`https://github.com/Vuthangvt1405/My-Agent-Setup`)

---

## Workflow B: Pull & Fast-Forward (New Machine Setup)

When setting up a new environment or syncing from another computer:

```bash
git -C "$HOME/.claude" fetch origin
git -C "$HOME/.claude" pull --ff-only origin main
```

Verify that all skills in `~/.claude/skills/` are present and readable.
