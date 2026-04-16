"""Download BugSigDB raw CSV exports."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from bsdbng.paths import RAW_DATA_DIR

EXPORT_BASE = "https://bugsigdb.org/w/images/csv_reports"
EXPORT_FILES = ("studies.csv", "experiments.csv", "signatures.csv")
FULL_DUMP_URL = "https://raw.githubusercontent.com/waldronlab/BugSigDBExports/devel/full_dump.csv"
PROVENANCE_FILE = "download_provenance.json"

MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 2.0


def _fetch_with_retry(client: httpx.Client, url: str) -> httpx.Response:
    """Fetch a URL with exponential backoff on 429 and 5xx responses."""
    delay = INITIAL_BACKOFF_SECONDS
    for attempt in range(MAX_RETRIES):
        resp = client.get(url)
        is_retryable = resp.status_code == 429 or resp.status_code >= 500
        if is_retryable and attempt < MAX_RETRIES - 1:
            time.sleep(delay)
            delay *= 2
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp  # unreachable, but keeps mypy happy


def download_exports(raw_dir: Path | None = None, *, force: bool = False) -> list[Path]:
    """Download the three BugSigDB CSV exports and full_dump.csv into *raw_dir*.

    Skips files that already exist unless *force* is True.
    Retries with exponential backoff on rate-limit (429) or server errors.
    Writes a provenance JSON sidecar recording download timestamps.
    """
    raw_dir = raw_dir or RAW_DATA_DIR
    raw_dir.mkdir(parents=True, exist_ok=True)

    provenance_path = raw_dir / PROVENANCE_FILE
    provenance: dict[str, str] = {}
    if provenance_path.exists():
        provenance = json.loads(provenance_path.read_text())

    urls: dict[str, str] = {name: f"{EXPORT_BASE}/{name}" for name in EXPORT_FILES}
    urls["full_dump.csv"] = FULL_DUMP_URL

    downloaded: list[Path] = []
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        for name, url in urls.items():
            dest = raw_dir / name
            if dest.exists() and not force:
                downloaded.append(dest)
                continue
            resp = _fetch_with_retry(client, url)
            dest.write_bytes(resp.content)
            provenance[name] = datetime.now(tz=UTC).isoformat()
            downloaded.append(dest)

    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    return downloaded
