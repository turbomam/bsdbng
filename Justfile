set shell := ["bash", "-cu"]

schema := "schema/bsdbng.yaml"
lintconfig := "schema/.linkmllint.yaml"

default: check

gen-pydantic:
	mkdir -p src/bsdbng/datamodel
	uv run gen-pydantic {{schema}} > src/bsdbng/datamodel/bsdbng_pydantic.py

gen-derived: gen-pydantic

check-generated:
	tmpfile="$(mktemp)" && \
	trap 'rm -f "$tmpfile"' EXIT && \
	uv run gen-pydantic {{schema}} > "$tmpfile" && \
	diff -u src/bsdbng/datamodel/bsdbng_pydantic.py "$tmpfile"

sync:
	uv sync --all-extras --group dev --group qa

lint:
	uv run ruff check src tests scripts
	uv run ruff format --check src tests scripts

format:
	uv run ruff check --fix src tests scripts
	uv run ruff format src tests scripts

typecheck:
	uv run mypy src tests

test:
	uv run pytest

install-hooks:
	uv run pre-commit install

security:
	uv run bandit -c pyproject.toml -r src scripts
	uv run deptry src
	uv run pip-audit

precommit:
	uv run pre-commit run --all-files

validate-schema:
	uv run linkml validate -s {{schema}}

lint-schema:
	uv run linkml lint --config {{lintconfig}} --validate --ignore-warnings {{schema}}
	uv run linkml lint --config {{lintconfig}} --ignore-warnings {{schema}}

check-schema: validate-schema lint-schema

check: check-generated lint typecheck test check-schema security
