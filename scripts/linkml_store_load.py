#!/usr/bin/env python3
"""Load bsdbng study YAML files into MongoDB via linkml-store.

One-time operation -- data persists in MongoDB between sessions.

Does NOT build any search indexes. Use linkml_store_index.py for that.

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
INDEX_COLLECTIONS = [
    f"internal__index__{COLLECTION_NAME}__simple",
    f"internal__index__{COLLECTION_NAME}__simple__metadata",
    f"internal__index__{COLLECTION_NAME}__llm",
    f"internal__index__{COLLECTION_NAME}__llm__metadata",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing collection and indexes before loading",
    )
    args = parser.parse_args()

    client = Client()
    db = client.attach_database(MONGO_URI, alias="bsdbng")

    if args.drop:
        from pymongo import MongoClient

        mongo = MongoClient(MONGO_URI)
        mdb = mongo.get_database()
        for name in [COLLECTION_NAME, *INDEX_COLLECTIONS]:
            mdb.drop_collection(name)
        print(f"Dropped {COLLECTION_NAME} and its indexes")

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

    print(f"Loaded {len(files)} studies in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
