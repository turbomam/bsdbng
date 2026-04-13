# bsdbng

`bsdbng` is a clean-room BugSigDB ingestion and normalization project.

The initial design constraints are:

- one canonical schema
- one canonical per-study YAML artifact
- the smallest practical set of durable file types
- strict Python and LinkML guardrails from the first commit

## Guardrails

- `uv` for environment and dependency management
- `just` for stable developer commands
- `ruff` for linting and formatting checks
- `mypy --strict` for type checking
- `pytest` for tests
- `bandit` for Python security linting
- `deptry` for dependency hygiene
- `pip-audit` for vulnerability scanning
- `linkml lint` and `linkml validate` for schema checks
- CI runs the full check suite on every push and PR

## Intended artifacts

- `data/raw/*.csv`
  BugSigDB source exports
- `data/studies/*.yaml`
  canonical per-study records
- `data/derived/`
  optional aggregate artifacts, only when they are materially necessary

## Current scope

The current scaffold is intentionally narrow. It establishes:

- a strict LinkML schema for normalized BugSigDB records
- a typed Python package layout
- a deterministic command surface via `Justfile`

It does not yet implement the full ingestion pipeline.
