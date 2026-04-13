set shell := ["bash", "-cu"]

schema := "schema/bsdbng.yaml"
lintconfig := "schema/.linkmllint.yaml"

default: check

sync:
	uv sync --all-extras --group dev

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

validate-schema:
	uv run linkml validate -s {{schema}}

lint-schema:
	uv run linkml lint --config {{lintconfig}} --validate --ignore-warnings {{schema}}
	uv run linkml lint --config {{lintconfig}} --ignore-warnings {{schema}}

check-schema: validate-schema lint-schema

check: lint typecheck test check-schema
