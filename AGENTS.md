# Agent-assisted development

This project welcomes contributions made with coding agents (Codex, Copilot,
Claude Code, ChatGPT, or similar). The same rules apply to agent-generated
code as to hand-written code: it must pass `just check` before committing.

## Do not accept workarounds

If your agent works around a missing tool, a broken path, or a failing check
instead of fixing the root cause:

1. Stop and note what the agent worked around
2. Open an issue describing the workaround and what should have worked
3. Fix the root cause, or ask for help

### Examples of workarounds that should become issues

- Agent runs `python -c '...'` instead of `just <recipe>` because `just`
  isn't installed
- Agent skips `just check` because a check fails
- Agent hardcodes a path because a config file is missing
- Agent adds `# noqa`, `# type: ignore`, or `# nosec` instead of fixing
  the code
- Agent installs a dependency that isn't in `pyproject.toml`
- Agent uses `pip install` instead of `uv sync`
- Agent creates a `.py` script in the repo root instead of putting it in
  `src/bsdbng/`

### Why this matters

A workaround that lets one person keep working creates a trap for the next
person. If the agent can't use the standard workflow, the standard workflow
is broken and we need to fix it — not paper over it.

## What agents should do

- Run `just check` after making changes
- Use Justfile recipes (`just download`, `just ingest`, etc.) instead of
  running Python commands directly
- Follow the branch naming convention: `issue-<number>-<short-slug>`
- Reference the issue in commit messages and PR bodies

## What to tell your agent

If your agent doesn't know about this project's conventions, tell it:

> This project uses `uv` for Python dependencies and `just` for commands.
> Run `just check` to verify changes. Do not add `noqa`, `type: ignore`,
> or `nosec` comments. Do not work around missing tools — tell me what's
> missing so I can install it.
