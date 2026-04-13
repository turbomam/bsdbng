from pathlib import Path

import pytest

from bsdbng.ingest import assert_required_exports


def test_assert_required_exports_reports_missing_files(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"experiments\.csv"):
        assert_required_exports(tmp_path)
