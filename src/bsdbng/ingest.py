"""BugSigDB CSV to per-study YAML ingestion."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from bsdbng.paths import RAW_DATA_DIR, STUDY_DATA_DIR

REQUIRED_EXPORTS = ("studies.csv", "experiments.csv", "signatures.csv")


def assert_required_exports(raw_dir: Path) -> None:
    """Fail fast when the expected BugSigDB CSV exports are missing."""
    missing = [name for name in REQUIRED_EXPORTS if not (raw_dir / name).exists()]
    if missing:
        missing_display = ", ".join(sorted(missing))
        raise FileNotFoundError(f"Missing required BugSigDB exports: {missing_display}")


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV, skipping comment lines that start with ``#``."""
    lines = [line for line in path.read_text().splitlines() if not line.startswith("#")]
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


def ingest(raw_dir: Path | None = None, study_dir: Path | None = None) -> list[Path]:
    """Parse raw CSVs and emit per-study YAML files.

    Each YAML file is a ``BugSigDBDataset`` containing one ``StudyRecord``.
    Returns the list of written file paths.
    """
    raw_dir = raw_dir or RAW_DATA_DIR
    study_dir = study_dir or STUDY_DATA_DIR
    assert_required_exports(raw_dir)
    study_dir.mkdir(parents=True, exist_ok=True)

    # The full_dump.csv from BugSigDBExports is a pre-merged flat table.
    # The raw Help:Export CSVs are three separate files, but the recommended
    # upstream path uses full_dump.csv which is already merged. We support both:
    # if full_dump.csv exists, use it; otherwise fall back to the three CSVs.
    full_dump = raw_dir / "full_dump.csv"
    rows = _read_csv(full_dump) if full_dump.exists() else _build_rows_from_separate_csvs(raw_dir)

    # Group rows by study id
    studies: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        bsdb_id = row.get("BSDB ID", "").strip()
        if not bsdb_id:
            continue
        sid = _parse_study_id(bsdb_id)
        studies[sid].append(row)

    written: list[Path] = []
    for study_id, study_rows in sorted(studies.items()):
        record = _build_study_record(study_id, study_rows)
        if not record["experiments"]:
            print(f"skipped {study_id}: no valid experiments/signatures", file=sys.stderr)
            continue
        filename = study_id.replace(":", "_").replace("/", "_") + ".yaml"
        dest = study_dir / filename
        dest.write_text(yaml.dump(record, default_flow_style=False, sort_keys=False))
        written.append(dest)

    return written


def _build_rows_from_separate_csvs(raw_dir: Path) -> list[dict[str, str]]:
    """Merge the three separate CSV exports into a flat row list.

    This mimics what BugSigDBExports does in dump_release.R but in Python.
    For now we only use full_dump.csv — this is a stub for #27 raw CSV support.
    """
    msg = "Separate CSV merging not yet implemented. Please use full_dump.csv from BugSigDBExports."
    raise NotImplementedError(msg)


def _build_study_record(study_id: str, rows: list[dict[str, str]]) -> dict[str, object]:
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
            direction = (
                direction_raw if direction_raw in ("increased", "decreased") else "increased"
            )

            taxa = _parse_taxa(taxa_str, names_str)
            if not taxa:
                continue

            sig_records.append(
                {
                    "id": sig_id,
                    "direction": direction,
                    "taxa": taxa,
                }
            )

        if not sig_records:
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


def _parse_taxa(tax_ids: str, names: str) -> list[dict[str, str]]:
    """Parse pipe-separated taxon IDs and names into TaxonRecord dicts."""
    ids = [t.strip() for t in tax_ids.split("|") if t.strip()] if tax_ids else []
    name_list = [n.strip() for n in names.split("|") if n.strip()] if names else []

    taxa: list[dict[str, str]] = []
    for i, tid in enumerate(ids):
        # Ensure it's a bare integer — build the CURIE ourselves
        tid_clean = tid.strip()
        if tid_clean.isdigit():
            curie = f"NCBITaxon:{tid_clean}"
        elif tid_clean.startswith("NCBITaxon:"):
            curie = tid_clean
        else:
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
