"""BugSigDB ingestion entrypoints."""

from __future__ import annotations

from pathlib import Path

REQUIRED_EXPORTS = ("studies.csv", "experiments.csv", "signatures.csv")


def assert_required_exports(raw_dir: Path) -> None:
    """Fail fast when the expected BugSigDB CSV exports are missing."""

    missing = [name for name in REQUIRED_EXPORTS if not (raw_dir / name).exists()]
    if missing:
        missing_display = ", ".join(sorted(missing))
        raise FileNotFoundError(f"Missing required BugSigDB exports: {missing_display}")
