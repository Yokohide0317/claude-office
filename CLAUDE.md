# CLAUDE.md

This file provides guidance to AI assistants when working with code in this repository.

## Overview

OpenCode Office Visualizer transforms OpenCode operations into a real-time pixel art office simulation. A "boss" character (main OpenCode agent) manages work, spawns "employee" agents (subagents), and orchestrates tasks visually.

This is a fork of [Claude Office](https://github.com/paulrobello/claude-office) adapted to work with OpenCode's server architecture.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system architecture and component details.

## Commands

```bash
# Root
make install       # Install all dependencies
make dev-tmux      # Run in tmux (recommended) - backend :8000, frontend :3000
make dev-tmux-kill # Kill tmux session
make checkall      # Lint, typecheck, test all components
make simulate      # Run event simulation

# Component-specific (run from backend/ or frontend/)
make dev           # Start dev server
make checkall      # Check single component (faster)
uv run pytest tests/test_file.py::test_name  # Single backend test

# Test OpenCode adapter
uv run python scripts/test_opencode_adapter.py
```

## Development Workflow

**Preferred:** Use `make dev-tmux` - creates separate windows for backend/frontend.
- Read logs: `tmux capture-pane -t opencode-office:backend -p`
- Switch windows: `Ctrl-b n` / `Ctrl-b p`
- Hot reload enabled on both servers

**Debugging:** Backend logs show OpenCode adapter events and transformations.

## Project Skills

- **/office-sprite** - Generate office furniture sprites
- **/character-sprite** - Generate character sprite sheets
- **/desk-accessory** - Generate tintable desk items

See `.claude/skills/*/SKILL.md` for details.

## Workflow Guidelines

**Commit after every batch of work:** Always commit after completing each logical unit.

**Use subagents for validation:** Spawn a Bash subagent to run `make checkall` and commit:
```
"Run 'make checkall' from the project root. If successful, commit with message: '<message>'"
```

## Version Management

**Keep all version locations in sync** when bumping versions:

| Location | File |
|----------|------|
| Backend | `backend/pyproject.toml` |
| Frontend package | `frontend/package.json` |
| Frontend display | `frontend/src/app/page.tsx` (header badge) |
