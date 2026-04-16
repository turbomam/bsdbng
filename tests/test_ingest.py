from pathlib import Path

import pytest
import yaml

from bsdbng.ingest import assert_required_exports, ingest


def test_assert_required_exports_reports_missing_files(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"experiments\.csv"):
        assert_required_exports(tmp_path)


FULL_DUMP_HEADER = (
    "# BugSigDB 2026-04-16, License: CC-BY-4.0\n"
    "BSDB ID,Study,Study design,PMID,DOI,URL,Authors list,Title,Journal,Year,"
    "Keywords,Experiment,Location of subjects,Host species,Body site,UBERON ID,"
    "Condition,EFO ID,Group 0 name,Group 1 name,Group 1 definition,"
    "Group 0 sample size,Group 1 sample size,Antibiotics exclusion,"
    "Sequencing type,16S variable region,Sequencing platform,"
    "Data transformation,Statistical test,Significance threshold,"
    "MHT correction,LDA Score above,Matched on,Confounders controlled for,"
    "Pielou,Shannon,Chao1,Simpson,Inverse Simpson,"
    "Abundance in Group 1,NCBI Taxonomy IDs,MetaPhlAn taxance,Taxon\n"
)

FULL_DUMP_ROW_1 = (
    "bsdb:99/1/1,Study 99,case-control,12345678,10.1234/test,,,"
    "Test Study Title,Test Journal,2024,keyword1,"
    "Experiment 1,USA,Homo sapiens,stool,UBERON:0001988,"
    "obesity,EFO:0001073,lean,obese,obese subjects,10,10,yes,"
    "16S,V4,Illumina,relative abundances,Mann-Whitney,0.05,"
    "BH,NA,age,BMI,,,,,,"
    "increased,9606|1234,Homo sapiens|Lactobacillus,\n"
)

FULL_DUMP_ROW_2 = (
    "bsdb:99/1/2,Study 99,case-control,12345678,10.1234/test,,,"
    "Test Study Title,Test Journal,2024,keyword1,"
    "Experiment 1,USA,Homo sapiens,stool,UBERON:0001988,"
    "obesity,EFO:0001073,lean,obese,obese subjects,10,10,yes,"
    "16S,V4,Illumina,relative abundances,Mann-Whitney,0.05,"
    "BH,NA,age,BMI,,,,,,"
    "decreased,5678,Bacteroides fragilis,\n"
)


def _write_full_dump(raw_dir: Path) -> None:
    (raw_dir / "full_dump.csv").write_text(FULL_DUMP_HEADER + FULL_DUMP_ROW_1 + FULL_DUMP_ROW_2)
    # Create the required exports so assert_required_exports passes
    for name in ("studies.csv", "experiments.csv", "signatures.csv"):
        (raw_dir / name).touch()


def test_ingest_produces_yaml(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    study_dir = tmp_path / "studies"
    raw_dir.mkdir()
    _write_full_dump(raw_dir)

    written = ingest(raw_dir, study_dir)
    assert len(written) == 1

    study = yaml.safe_load(written[0].read_text())
    assert study["id"] == "bsdb:99"
    assert study["pmid"] == 12345678
    assert study["publication_year"] == 2024
    assert study["doi"] == "10.1234/test"
    assert len(study["experiments"]) == 1

    exp = study["experiments"][0]
    assert exp["id"] == "bsdb:99/1"
    assert len(exp["signatures"]) == 2

    sig_increased = next(s for s in exp["signatures"] if s["direction"] == "increased")
    assert len(sig_increased["taxa"]) == 2
    assert sig_increased["taxa"][0]["id"] == "NCBITaxon:9606"

    sig_decreased = next(s for s in exp["signatures"] if s["direction"] == "decreased")
    assert sig_decreased["taxa"][0]["id"] == "NCBITaxon:5678"


def test_ingest_yaml_round_trips_through_pydantic(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    study_dir = tmp_path / "studies"
    raw_dir.mkdir()
    _write_full_dump(raw_dir)

    written = ingest(raw_dir, study_dir)
    study_data = yaml.safe_load(written[0].read_text())

    from bsdbng.datamodel import StudyRecord

    study = StudyRecord.model_validate(study_data)
    assert study.id == "bsdb:99"
    assert study.pmid == 12345678
