# My-Agent-Setup

My global Claude Code setup (`~/.claude`): settings and custom skills.

## What's here

| Path | What it is |
|---|---|
| `settings.json` | Global settings: model, effort level, no commit/PR attribution, SessionStart hook (`gh-axi`) |
| `skills/feature-explainer/` | Explains an existing feature for a new developer; writes `docs/features/explained/<slug>-explained.md` |
| `skills/feature-implementation-planner/` | Plan → scaffold → verify workflow for new features (US/AC, schema, DTOs, OWASP review, TDD test tables) |

Not tracked (see `.gitignore`): login credentials, chat history, sessions, caches, and skills synced from claude.ai.

## Install on a new machine

```bash
git clone https://github.com/Vuthangvt1405/My-Agent-Setup.git ~/.claude
```

If `~/.claude` already exists:

```bash
cd ~/.claude
git init
git remote add origin https://github.com/Vuthangvt1405/My-Agent-Setup.git
git fetch origin
git checkout -f -B main origin/main
```

## Update

```bash
cd ~/.claude
git add -A
git commit -m "Update setup"
git push
```
