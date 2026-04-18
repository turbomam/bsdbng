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
- Open a draft PR after the first push to a branch — do not let branches
  sit without PRs. A branch without a PR is invisible to the team.
- Keep branches short-lived. If a branch hasn't been updated in a week,
  either push progress or close the PR with a comment explaining why.

## Data fidelity rules

Every data pipeline step must be checked for silent data loss or corruption:

- **Look at actual output before declaring success.** Open a YAML file.
  Check that taxon names are real names, not placeholder codes. Check that
  fields you expect to be populated aren't all null. If 77% of your output
  has placeholder values, the pipeline is broken — not "mostly working."
- **High-volume log entries are bugs, not noise.** If the ingest log has
  87,000 entries saying "using placeholder name," that's not an edge case.
  That's the majority of the data failing silently. Investigate before
  moving on.
- **Verify encoding assumptions against real data.** Don't assume two
  columns use the same delimiter. Don't assume a column labeled "EFO ID"
  only contains EFO terms. Check with code: count unique values, check
  prefixes, compare counts across columns.
- **The ingest will fail on placeholder values.** If any taxon gets a
  placeholder name (`taxon_<ID>`), the pipeline raises an error. This is
  intentional. Fix the parser, don't suppress the error.
- **Every field in the output YAML must be traceable to a specific CSV
  column.** If you can't say which column a value came from, the mapping
  is undocumented and fragile.

## After a release

When a new release is tagged, check the release assets:

1. Check for new releases: `gh release list --repo turbomam/bsdbng --limit 1`
2. **Ask the user before downloading** — releases can be large
3. Download selected assets:
   ```bash
   mkdir -p release-assets
   gh release download <tag> --repo turbomam/bsdbng --dir release-assets \
     --pattern 'bsdbng-studies-*.tar.gz' \
     --pattern 'bsdbng-stats-*.txt' \
     --pattern 'bsdbng-ingest-log-*.json'
   ```
4. Unpack archives:
   ```bash
   mkdir -p studies
   tar xzf release-assets/bsdbng-studies-*.tar.gz -C studies/
   ```
5. Assess the output:
   - Read `release-assets/bsdbng-stats-*.txt` — compare counts against previous release
   - Spot-check a study YAML — are taxon names real or placeholders?
   - Check the ingest log — are skip counts reasonable?
   - Compare study count against BugSigDB live (https://bugsigdb.org/Main_Page)
6. Report any anomalies to the user before they share the release

## What to tell your agent

If your agent doesn't know about this project's conventions, tell it:

> This project uses `uv` for Python dependencies and `just` for commands.
> Run `just check` to verify changes. Do not add `noqa`, `type: ignore`,
> or `nosec` comments. Do not work around missing tools — tell me what's
> missing so I can install it.
