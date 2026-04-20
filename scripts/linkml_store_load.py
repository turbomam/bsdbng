#!/usr/bin/env python3
"""Load bsdbng study YAML files into MongoDB via linkml-store.

One-time operation — data persists in MongoDB between sessions.
Subsequent queries (linkml_store_query.py) connect without reloading.

Usage:
    uv run python scripts/linkml_store_load.py
    uv run python scripts/linkml_store_load.py --drop  # drop and reload
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import yaml
from linkml_store import Client

MONGO_URI = "mongodb://localhost:27017/bsdbng"
COLLECTION_NAME = "studies"
SCHEMA_PATH = "schema/bsdbng.yaml"
STUDY_DIR = Path("data/studies")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--drop", action="store_true", help="Drop existing collection before loading"
    )
    args = parser.parse_args()

    client = Client()
    db = client.attach_database(MONGO_URI, alias="bsdbng")

    if args.drop:
        from pymongo import MongoClient

        mongo = MongoClient(MONGO_URI)
        mongo.get_database().drop_collection(COLLECTION_NAME)
        print(f"Dropped {COLLECTION_NAME}")

    collection = db.create_collection(
        COLLECTION_NAME, schema_path=SCHEMA_PATH, target_class="Study"
    )

    files = sorted(STUDY_DIR.glob("*.yaml"))
    if not files:
        print(f"No YAML files found in {STUDY_DIR}")
        return

    t0 = time.time()
    for i, path in enumerate(files):
        collection.insert(yaml.safe_load(path.read_text(encoding="utf-8")))
        if (i + 1) % 500 == 0:
            print(f"  loaded {i + 1}/{len(files)}...")

    elapsed = time.time() - t0
    print(f"Loaded {len(files)} studies in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
