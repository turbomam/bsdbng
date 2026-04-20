# BugSigDB Live Counts

This note records a small set of current live BugSigDB counts and the source
used for each count.

As of 2026-04-13, using the raw `Help:Export` CSV tables:

- studies: 1,993
- experiments: 7,765
- signatures: 12,319

## Source mapping

- `studies` count
  Source: row count of `studies.csv` from `https://bugsigdb.org/Help:Export`
- `experiments` count
  Source: row count of `experiments.csv` from `https://bugsigdb.org/Help:Export`
- `signatures` count
  Source: row count of `signatures.csv` from `https://bugsigdb.org/Help:Export`

## Notes

- These counts come from the raw export tables, not from derived exports such
  as `full_dump.csv`.
- The BugSigDB main page is a useful place to view top-level site statistics,
  but `Help:Export` is the cleaner source for exact table counts.
- BugSigDB also exposes a MediaWiki API at `https://bugsigdb.org/w/api.php`,
  but this note is based on the public CSV exports.

## Sources

- BugSigDB `Help:Export`: https://bugsigdb.org/Help:Export
- BugSigDB main page: https://bugsigdb.org/
- BugSigDB MediaWiki API: https://bugsigdb.org/w/api.php?action=query&meta=siteinfo&format=json
