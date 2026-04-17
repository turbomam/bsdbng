## bsdbng project instructions for GitHub Copilot

This project uses `uv` for Python dependencies and `just` for commands.

### Required workflow

1. Run `just check` after making changes — all checks must pass
2. Put source code in `src/bsdbng/`, tests in `tests/`
3. Create branches named `issue-<number>-<slug>` from `main`
4. Reference the issue in PR body (`Closes #N`)

### Do not

- Add `# noqa`, `# type: ignore`, or `# nosec` comments
- Add dependencies without discussing in an issue first
- Hardcode file paths — use `from bsdbng.paths import ...`
- Commit generated output files (data/raw/*.csv, data/studies/*.yaml)
- Use `pip install` — use `uv sync`
- Put scripts in the repo root — use `src/bsdbng/`
- Use an LLM in the data pipeline — all processing must be deterministic
- Work around missing tools — if something isn't installed, tell the user

### Project conventions

- Schema source of truth: `schema/bsdbng.yaml`
- Generated Pydantic models: `src/bsdbng/datamodel/bsdbng_pydantic.py` (do not edit)
- Load YAML via Pydantic: `from bsdbng.datamodel import Study`
- File types: CSV (input), YAML (output/schema), Python (code), JSON (logs)
- No DuckDB, no Parquet, no Jupyter notebooks
- No sentinel values — if data is missing, use `null`

### See also

- `AGENTS.md` for the full workaround policy
- `CONTRIBUTING.md` for setup and development workflow
