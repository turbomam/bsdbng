# BugSigDB Data Access Methods

This note documents the currently available ways to access BugSigDB data and
the criteria for choosing among them in `bsdbng`.

## Available methods

### 1. Raw CSV exports from BugSigDB

BugSigDB exposes three raw export tables on `Help:Export`:

- `studies.csv`
- `experiments.csv`
- `signatures.csv`

These are the closest public exports to the current operational state of the
database. They are the least transformed input surface available to us.

Current live sizes on 2026-04-13:

- `studies.csv`: 4,419,974 bytes
- `experiments.csv`: 3,205,728 bytes
- `signatures.csv`: 17,186,766 bytes
- total: 24,812,468 bytes across 3 files

### 2. BugSigDBExports repository

The `waldronlab/BugSigDBExports` repository is a derived export layer built
from the three raw BugSigDB CSV tables.

Its README says the export workflow:

1. obtains and merges the study, experiment, and signature tables from
   `Help:Export`
2. filters incomplete records
3. adds signature IDs
4. writes `full_dump.csv`
5. writes GMT files for multiple identifier schemes and taxonomic levels

Current derived artifacts visible in the repo:

- `full_dump.csv`: 27,365,297 bytes
- `.gmt` files: 15 files, 45,403,996 bytes total

This is convenient, but it is not the raw source export. It is already merged
and transformed upstream.

### 3. Stable snapshot releases

BugSigDB also publishes stable snapshot releases, including Zenodo releases
linked from the paper and the `BugSigDBExports` README.

These are useful when reproducibility matters more than freshness.

Example release sizes:

- Zenodo `v1.3.0`: 51.6 MB total files
- Zenodo `v1.2.2`: 31.0 MB total files
- Zenodo `v1.2.0`: 19.1 MB total files

### 4. `bugsigdbr`

`bugsigdbr` is the Bioconductor R package for programmatic access to BugSigDB.

It is useful for R-centric analysis workflows, but it is not the preferred
starting point for a LinkML-first Python ingestion repo.

## What GMT is

`GMT` means Gene Matrix Transposed. It is a simple tab-delimited set format
used widely in enrichment workflows.

Each row represents one set:

- column 1: set name
- column 2: description
- remaining columns: members of the set

In BugSigDB exports, the members are microbial taxa rather than genes.

GMT is useful for signature-set analysis. It is not a good canonical ingestion
format when we need full study, experiment, and provenance metadata.

## Selection criteria

We should choose an access path using these criteria:

- source fidelity
- reproducibility
- freshness
- developer time
- machine-time performance
- good citizenship toward upstream infrastructure
- fit for purpose

## Recommendation for `bsdbng`

For canonical ingestion in `bsdbng`, prefer the raw CSV exports from
`Help:Export`.

Why:

- they are the least transformed public exports
- they keep LinkML as the first real structuring layer in this repo
- they avoid inheriting upstream merge and filtering decisions
- they are still small enough that performance is not a serious concern

Use the other methods for narrower purposes:

- use `full_dump.csv` for convenience or exploratory comparison
- use GMT only for set-based enrichment workflows
- use Zenodo snapshots for frozen reproducible builds
- use `bugsigdbr` for R workflows, not as the primary ingestion surface here

## Sources

- BugSigDB `Help:Export`: https://bugsigdb.org/Help:Export
- BugSigDBExports README:
  https://github.com/waldronlab/BugSigDBExports/blob/devel/README.md
- BugSigDB paper:
  https://doi.org/10.1038/s41587-023-01872-y
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11098749/
- Stable releases:
  https://zenodo.org/records/15272273
  https://zenodo.org/records/13997429
  https://zenodo.org/records/10407666
