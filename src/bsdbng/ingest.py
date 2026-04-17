"""BugSigDB CSV to per-study YAML ingestion."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from bsdbng.datamodel import Study
from bsdbng.paths import DERIVED_DATA_DIR, RAW_DATA_DIR, STUDY_DATA_DIR

REQUIRED_EXPORTS = ("studies.csv", "experiments.csv", "signatures.csv")


def assert_required_exports(raw_dir: Path) -> None:
    """Fail fast when the expected BugSigDB CSV exports are missing."""
    missing = [name for name in REQUIRED_EXPORTS if not (raw_dir / name).exists()]
    if missing:
        missing_display = ", ".join(sorted(missing))
        raise FileNotFoundError(f"Missing required BugSigDB exports: {missing_display}")


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV, skipping comment lines that start with ``#``."""
    with path.open(encoding="utf-8", newline="") as handle:
        lines = (line for line in handle if not line.startswith("#"))
        return list(csv.DictReader(lines))


def _parse_study_id(bsdb_id: str) -> str:
    """Extract the numeric study id from a BSDB ID like ``bsdb:11/1/1``.

    The first number after ``bsdb:`` is the study number.
    """
    raw = bsdb_id.removeprefix("bsdb:").split("/")[0]
    return f"bsdb:{raw}"


def _parse_experiment_id(bsdb_id: str) -> str:
    """Extract study/experiment id from ``bsdb:11/1/1`` → ``bsdb:11/1``."""
    parts = bsdb_id.removeprefix("bsdb:").split("/")
    return f"bsdb:{parts[0]}/{parts[1]}" if len(parts) >= 2 else bsdb_id


def _parse_signature_id(bsdb_id: str) -> str:
    """Return the full BSDB ID as the signature id."""
    return bsdb_id


def _taxon_name_to_rank(name: str) -> str:
    """Heuristic for taxonomic rank from the taxon name string.

    BugSigDB signatures use names at varying ranks. This is a rough
    heuristic — proper resolution belongs in issue #29.
    """
    parts = name.strip().split()
    if len(parts) >= 3:
        return "strain"
    if len(parts) == 2:
        return "species"
    return "genus"


def ingest(
    raw_dir: Path | None = None,
    study_dir: Path | None = None,
    derived_dir: Path | None = None,
) -> list[Path]:
    """Parse raw CSVs and emit per-study YAML files.

    Each YAML file is a bare Study validated through the Pydantic model
    before writing. Writes an ingest log to derived_dir/ingest_log.json
    documenting every skipped row, signature, experiment, and study.
    Returns the list of written file paths.
    """
    raw_dir = raw_dir or RAW_DATA_DIR
    study_dir = study_dir or STUDY_DATA_DIR
    derived_dir = derived_dir or DERIVED_DATA_DIR
    study_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)

    log: list[dict[str, str]] = []

    full_dump = raw_dir / "full_dump.csv"
    if full_dump.exists():
        rows = _read_csv(full_dump)
    else:
        assert_required_exports(raw_dir)
        rows = _build_rows_from_separate_csvs(raw_dir)

    # Group rows by study id
    studies: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        bsdb_id = row.get("BSDB ID", "").strip()
        if not bsdb_id:
            log.append({"level": "skip", "entity": "row", "reason": "empty BSDB ID"})
            continue
        sid = _parse_study_id(bsdb_id)
        studies[sid].append(row)

    written: list[Path] = []
    for study_id, study_rows in sorted(studies.items()):
        record = _build_study_record(study_id, study_rows, log)
        if not record["experiments"]:
            log.append(
                {
                    "level": "skip",
                    "entity": "study",
                    "id": study_id,
                    "reason": "no valid experiments/signatures",
                }
            )
            print(f"skipped {study_id}: no valid experiments/signatures", file=sys.stderr)
            continue

        # Validate through Pydantic before writing
        Study.model_validate(record)

        filename = study_id.replace(":", "_").replace("/", "_") + ".yaml"
        dest = study_dir / filename
        dest.write_text(yaml.dump(record, default_flow_style=False, sort_keys=False))
        written.append(dest)

    # Write ingest log
    log_path = derived_dir / "ingest_log.json"
    log_path.write_text(json.dumps(log, indent=2) + "\n")

    # Print summary
    from collections import Counter

    skips = [e for e in log if e["level"] == "skip"]
    infos = [e for e in log if e["level"] == "info"]
    skip_counts = Counter(e["reason"] for e in skips)
    print(
        f"wrote {len(written)} studies, {len(skips)} skips, {len(infos)} info entries:",
        file=sys.stderr,
    )
    for reason, count in skip_counts.most_common():
        print(f"  {count:>5}  {reason}", file=sys.stderr)

    return written


def _build_rows_from_separate_csvs(raw_dir: Path) -> list[dict[str, str]]:
    """Merge the three separate CSV exports into a flat row list.

    This mimics what BugSigDBExports does in dump_release.R but in Python.
    For now we only use full_dump.csv — this is a stub for #27 raw CSV support.
    """
    msg = "Separate CSV merging not yet implemented. Please use full_dump.csv from BugSigDBExports."
    raise NotImplementedError(msg)


def _build_study_record(
    study_id: str,
    rows: list[dict[str, str]],
    log: list[dict[str, str]],
) -> dict[str, object]:
    """Build a nested study record dict from flat rows sharing a study id."""
    first = rows[0]

    # Group by experiment
    experiments: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        eid = _parse_experiment_id(row.get("BSDB ID", ""))
        experiments[eid].append(row)

    experiment_records: list[dict[str, object]] = []
    for exp_id, exp_rows in sorted(experiments.items()):
        exp_first = exp_rows[0]
        sig_records: list[dict[str, object]] = []
        for row in exp_rows:
            sig_id = _parse_signature_id(row.get("BSDB ID", ""))
            taxa_str = row.get("NCBI Taxonomy IDs", "")
            names_str = row.get("MetaPhlAn taxance", "") or row.get("Taxon", "") or ""
            direction_raw = (row.get("Abundance in Group 1", "") or "").strip().lower()
            if direction_raw not in ("increased", "decreased"):
                log.append(
                    {
                        "level": "skip",
                        "entity": "signature",
                        "id": sig_id,
                        "reason": f"unparseable direction: {direction_raw!r}",
                    }
                )
                continue

            taxa = _parse_taxa(taxa_str, names_str, sig_id, log)
            if not taxa:
                log.append(
                    {
                        "level": "skip",
                        "entity": "signature",
                        "id": sig_id,
                        "reason": "no parseable taxa",
                    }
                )
                continue

            sig_records.append(
                {
                    "id": sig_id,
                    "direction": direction_raw,
                    "taxa": taxa,
                }
            )

        if not sig_records:
            log.append(
                {
                    "level": "skip",
                    "entity": "experiment",
                    "id": exp_id,
                    "reason": "no valid signatures",
                }
            )
            continue

        experiment_records.append(
            {
                "id": exp_id,
                "experiment_name": exp_first.get("Experiment", "").strip() or None,
                "group_0_name": exp_first.get("Group 0 name", "").strip() or None,
                "group_1_name": exp_first.get("Group 1 name", "").strip() or None,
                "signatures": sig_records,
            }
        )

    year_str = first.get("Year", "").strip()
    pub_year: int | None = None
    if year_str.isdigit():
        pub_year = int(year_str)

    pmid_raw = first.get("PMID", "").strip()
    pmid: int | None = int(pmid_raw) if pmid_raw.isdigit() else None

    doi_raw = first.get("DOI", "").strip()
    # Some DOIs are stored as full URLs — normalize to bare DOI
    doi_clean = doi_raw.removeprefix("https://doi.org/").removeprefix("http://doi.org/")
    doi: str | None = doi_clean if doi_clean.startswith("10.") else None

    url_raw = first.get("URL", "").strip()
    url: str | None = url_raw if url_raw.startswith("http") else None

    return {
        "id": study_id,
        "source_record_id": first.get("Study", "").strip(),
        "pmid": pmid,
        "title": first.get("Title", "").strip() or None,
        "publication_year": pub_year,
        "doi": doi,
        "url": url,
        "experiments": experiment_records,
    }


def _parse_taxa(
    tax_ids: str,
    names: str,
    sig_id: str,
    log: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Parse pipe-separated taxon IDs and names into Taxon dicts."""
    ids = [t.strip() for t in tax_ids.split("|") if t.strip()] if tax_ids else []
    name_list = [n.strip() for n in names.split("|") if n.strip()] if names else []

    taxa: list[dict[str, str]] = []
    for i, tid in enumerate(ids):
        # BugSigDB sometimes includes lineage info as "taxon_id;parent_id".
        # Take the first component as the actual taxon ID.
        tid_raw = tid.strip()
        if ";" in tid_raw:
            log.append(
                {
                    "level": "info",
                    "entity": "taxon",
                    "id": tid_raw.split(";")[0].strip(),
                    "signature": sig_id,
                    "reason": f"semicolon-separated taxon ID, used first component: {tid_raw!r}",
                }
            )
        tid_clean = tid_raw.split(";")[0].strip()
        if tid_clean.isdigit():
            curie = f"NCBITaxon:{tid_clean}"
        elif tid_clean.startswith("NCBITaxon:"):
            curie = tid_clean
        else:
            log.append(
                {
                    "level": "skip",
                    "entity": "taxon",
                    "id": tid_clean,
                    "signature": sig_id,
                    "reason": f"unparseable taxon ID: {tid_clean!r}",
                }
            )
            continue

        name = name_list[i] if i < len(name_list) else f"taxon_{tid_clean}"
        rank = _taxon_name_to_rank(name)
        taxa.append(
            {
                "id": curie,
                "taxon_name": name,
                "taxonomic_rank": rank,
            }
        )

    return taxa
