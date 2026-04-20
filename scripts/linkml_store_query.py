#!/usr/bin/env python3
"""Query bsdbng studies in MongoDB via linkml-store.

Requires data loaded by linkml_store_load.py. Data persists between sessions.

Examples:
    # Exact field match
    uv run python scripts/linkml_store_query.py \
        --field experiments.condition --value "Colorectal cancer"

    # CURIE match
    uv run python scripts/linkml_store_query.py \
        --field experiments.condition_ontology_id --value "EFO:0005842"

    # Trigram text similarity (no API key needed)
    uv run python scripts/linkml_store_query.py \
        --search "gut bacteria in elderly patients"

    # LLM embedding search (requires OPENAI_API_KEY)
    uv run python scripts/linkml_store_query.py \
        --embed "autoimmune conditions linked to oral bacteria"
"""

from __future__ import annotations

import argparse
import time

from dotenv import load_dotenv
from linkml_store import Client
from linkml_store.api.queries import Query

MONGO_URI = "mongodb://localhost:27017/bsdbng"
COLLECTION_NAME = "studies"


def _dedup_by_id(rows: list[dict]) -> list[dict]:
    """Drop rows with a duplicate `id`, preserving first-seen order.

    The LLM indexer splits each study into multiple chunks, so a single
    logical study can appear several times in ranked search results.
    """
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        k = r.get("id")
        if k in seen:
            continue
        if k is not None:
            seen.add(k)
        out.append(r)
    return out


def print_results(rows: list[dict], label: str, elapsed: float) -> None:
    """Print query results in a readable format."""
    print(f"\n=== {label} ({len(rows)} results, {elapsed:.2f}s) ===")
    for r in rows:
        cond = next(
            (e.get("condition") for e in r.get("experiments", []) if e.get("condition")),
            None,
        )
        host = next(
            (e.get("host_species") for e in r.get("experiments", []) if e.get("host_species")),
            None,
        )
        body = next(
            (e.get("body_site") for e in r.get("experiments", []) if e.get("body_site")),
            None,
        )
        title = r.get("title") or "no title"
        print(f"  {r.get('id')}: {title}")
        print(f"    condition={cond}, host={host}, body_site={body}")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--field", help="Field name for exact match query")
    parser.add_argument("--value", help="Value for exact match query")
    parser.add_argument("--search", help="Trigram text similarity search (no API key)")
    parser.add_argument("--embed", help="LLM embedding semantic search (requires OPENAI_API_KEY)")
    parser.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")
    args = parser.parse_args()

    client = Client()
    db = client.attach_database(MONGO_URI, alias="bsdbng")
    collection = db.get_collection(COLLECTION_NAME)

    if args.field and args.value:
        t0 = time.time()
        qr = collection.query(Query(where_clause={args.field: args.value}), limit=args.limit)
        rows = list(qr.rows)
        print_results(rows, f"{args.field} = {args.value!r}", time.time() - t0)

    elif args.search:
        t0 = time.time()
        qr = collection.search(args.search, index_name="simple", limit=args.limit * 4)
        rows = _dedup_by_id(qr.rows)[: args.limit]
        print_results(rows, f"trigram: {args.search!r}", time.time() - t0)

    elif args.embed:
        t0 = time.time()
        qr = collection.search(args.embed, index_name="llm", limit=args.limit * 4)
        rows = _dedup_by_id(qr.rows)[: args.limit]
        print_results(rows, f"embedding: {args.embed!r}", time.time() - t0)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
