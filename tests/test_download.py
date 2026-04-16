import json
from pathlib import Path

from bsdbng.download import EXPORT_FILES, PROVENANCE_FILE, download_exports


def test_download_skips_existing_files(tmp_path: Path) -> None:
    """When all target files exist, download_exports should not overwrite them."""
    for name in EXPORT_FILES:
        (tmp_path / name).write_text("existing")
    (tmp_path / "full_dump.csv").write_text("existing")

    result = download_exports(tmp_path)

    assert len(result) == 4
    # Files should still have original content (not re-fetched)
    assert (tmp_path / "studies.csv").read_text() == "existing"


def test_provenance_written(tmp_path: Path) -> None:
    """Provenance file should exist after download, even when all files are cached."""
    for name in EXPORT_FILES:
        (tmp_path / name).write_text("existing")
    (tmp_path / "full_dump.csv").write_text("existing")

    download_exports(tmp_path)

    prov_path = tmp_path / PROVENANCE_FILE
    assert prov_path.exists()
    data = json.loads(prov_path.read_text())
    assert isinstance(data, dict)
