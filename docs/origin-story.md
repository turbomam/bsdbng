# Where bsdbng came from

## The short version

bsdbng is a clean-room reimplementation of work that was prototyped in
[CultureBotAI/KG-Microbe-search](https://github.com/CultureBotAI/KG-Microbe-search).
The prototyping was done by undergraduate researchers. Their exploratory
work proved the concept and revealed the data structure; bsdbng packages
those findings into a schema-first, guardrails-first pipeline.

## What the prototyping proved

The KG-Microbe-search work demonstrated that:

1. **BugSigDB data can be structured into per-study records** with
   nested experiments, signatures, and taxa. This hierarchy was discovered
   through hands-on exploration of the BugSigDB CSV exports.

2. **LinkML schemas can validate BugSigDB data**. A schema was written
   and used with `linkml validate` to check study outputs against a
   formal specification.

3. **Trait profile tables can be generated from structured study data**.
   A script was built to produce wide and long TSV formats summarizing
   taxa and their abundance directions across studies.

4. **KG-Microbe phenotype data can be cross-referenced with BugSigDB taxa**.
   An analysis pipeline looked up taxa in KG-Microbe's knowledge graph
   edges to find phenotypic traits associated with differentially abundant
   organisms.

5. **BugSigDB uses MetaPhlAn lineage encoding** — pipes separate
   taxonomic levels within one taxon, semicolons separate distinct taxa.
   This is not documented in BugSigDB's own docs and was learned through
   data exploration.

6. **1,743 BugSigDB studies were successfully analyzed**, validating the
   approach at scale.

## What bsdbng adds

bsdbng takes the proven concepts and packages them with:

- **A single LinkML schema** as the source of truth, with generated Pydantic
  models enforcing validation on every write
- **Automated checks** (ruff, mypy strict, pytest, linkml lint/validate,
  bandit, deptry, pip-audit) running in CI
- **Deterministic ingestion** — the same input always produces the same
  output, with no LLM in the critical path
- **Comprehensive logging** of every data drop and transformation assumption
- **Correct taxon parsing** based on the MetaPhlAn lineage encoding
  discovered during prototyping
- **HTTP caching** with ETag/If-Modified-Since for efficient re-downloads
- **A reproducible command surface** via Justfile

## How to demonstrate your contribution

If you contributed to KG-Microbe-search or bsdbng, here is how the work
maps and how you can talk about it:

### For interview conversations

Your KG-Microbe-search work is visible in the git history of that repo.
Your bsdbng contributions will be visible in the git history of this repo.
Both repos are public on GitHub.

When discussing your work:

- Point to your **PRs and issues** — they show what you built, what feedback
  you received, and how you responded
- Point to the **schema** — if you contributed to the data model, that's a
  durable artifact that demonstrates understanding of the domain
- Point to the **ingest log** — if you improved data quality (taxon
  normalization, edge case handling), the log shows the before/after
- Point to the **tests** — they show you can verify your own work
- Point to the **Justfile recipes** — they show you can make your work
  reproducible for others

### Specific contributions that transfer

| Skill | Where it's demonstrated |
|-------|------------------------|
| Data modeling with LinkML | `schema/bsdbng.yaml` |
| Python packaging and typing | `src/bsdbng/`, `pyproject.toml` |
| ETL pipeline design | `src/bsdbng/ingest.py` |
| Data quality analysis | `data/derived/ingest_log.json`, issue #44 |
| Scientific data interpretation | Trait tables, phenotype cross-references |
| Code review and collaboration | PR history, issue discussions |
| Working with biological ontologies | NCBITaxon, METPO, biolink predicates |

### What to say about the repo transition

> "We started with an exploratory prototype to understand the BugSigDB data.
> That prototype proved the concept and helped us discover things like the
> MetaPhlAn lineage encoding. Then we restructured into a new repo with
> formal schema validation, automated quality checks, and a reproducible
> pipeline. I contributed [specific thing] to the new repo, building on
> what we learned in the prototype."
