set shell := ["bash", "-cu"]

schema := "schema/bsdbng.yaml"
lintconfig := "schema/.linkmllint.yaml"
logdir := "logs"

default: check

# --- timed wrapper (logs wall-clock seconds per step) ---

[private]
timed step +cmd:
	mkdir -p {{logdir}}
	start=$(date +%s) && \
	{{cmd}} && \
	elapsed=$(($(date +%s) - start)) && \
	echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) {{step}} ${elapsed}s" | tee -a {{logdir}}/pipeline.log

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

test-cov:
	uv run pytest --cov=bsdbng --cov-report=term-missing

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

# --- pipeline steps (timed, logged) ---

download:
	just timed download "uv run python -c 'from bsdbng.download import download_exports; download_exports()'"

ingest:
	just timed ingest "uv run python -c 'from bsdbng.ingest import ingest; ingest()'"

validate-studies:
	just timed validate-studies "uv run python -c 'from bsdbng.validate import validate_all_studies; validate_all_studies()'"

validate-studies-linkml:
	just timed validate-studies-linkml "uv run linkml validate -s {{schema}} -C Study data/studies/*.yaml"

pipeline: download ingest

# --- cleanup ---

clean-raw:
	rm -f data/raw/*.csv data/raw/download_provenance.json

clean-studies:
	rm -f data/studies/*.yaml

clean-derived:
	find data/derived -type f ! -name .gitkeep -delete

clean-logs:
	rm -f {{logdir}}/pipeline.log

clean-all: clean-raw clean-studies clean-derived clean-logs
